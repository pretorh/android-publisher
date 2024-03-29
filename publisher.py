#!/usr/bin/env python3
import argparse
import sys
import os
import stat
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import apiclient

SCOPE = 'https://www.googleapis.com/auth/androidpublisher'
SCRIPT_VERSION = '2023-09-25'

def print_info():
    print(f'publisher.py: {SCRIPT_VERSION}')
    print('')

def build_service_from_p12(service_account_email, key_file):
    print('setup credentials and building service')
    # build service acount using p12 file, based on
    # https://stackoverflow.com/a/35666374/1016377
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email, key_file, scopes=[SCOPE])

    http = httplib2.Http()
    http = credentials.authorize(http)
    return apiclient.discovery.build('androidpublisher', 'v3', http=http)

def build_service_from_json_file(json_key_file):
    print(f'setup credentials and building service from {json_key_file}')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scopes=[SCOPE])

    http = httplib2.Http()
    http = credentials.authorize(http)
    return apiclient.discovery.build('androidpublisher', 'v3', http=http)

def create_edit(service, package_name):
    request = service.edits().insert(body={}, packageName=package_name)
    result = request.execute()
    edit_id = result['id']
    print(f'setup edit: {edit_id}')
    return edit_id

def update_track(service, package_name, edit_id, track, version):
    print(f'update track {track}')
    request = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=package_name,
        body={
            'track': track,
            'releases': [{
                'name': version['name'],
                'versionCodes': [version['code']],
                'releaseNotes': [{
                    'language': 'en-GB',
                    'text': version['notes']
                }],
                'status': 'completed',
            }]
        })
    response = request.execute()
    releases = str(response['releases'])
    print(f'setup with: {releases}')

def validate_and_commit_edit(service, package_name, edit_id):
    response = service.edits().validate(editId=edit_id, packageName=package_name).execute()
    print(f'validated {response}')

    response = service.edits().commit(editId=edit_id, packageName=package_name).execute()
    print(f'commited {response}')

def upload_bundle(service, package_name, edit_id, aab_file):
    print(f'uploading {aab_file}')
    request = service.edits().bundles().upload(
        editId=edit_id,
        packageName=package_name,
        media_body=aab_file,
        media_mime_type='application/octet-stream',
    )
    response = request.execute()
    print(f'uploaded, {response}')

# running as cli

def __run_from_cli_args(flags):
    if flags.authentication_type == 'p12':
        service = build_service_from_p12(flags.p12_service_account_email, flags.p12_key_path)
    elif flags.authentication_type == 'json':
        service = build_service_from_json_file(flags.json_key_file)
    else:
        raise ValueError(f'Unknown authentication type {flags.authentication_type}')

    edit_id = create_edit(service, flags.package_name)
    if flags.upload_aab:
        upload_bundle(service, flags.package_name, edit_id, flags.upload_aab)
    update_track(service, flags.package_name, edit_id, flags.track, version={
        'name': flags.play_console_release_name,
        'code': flags.version_code,
        'notes': flags.release_notes,
    })
    validate_and_commit_edit(service, flags.package_name, edit_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    # authentication and app details
    auth_params = parser.add_mutually_exclusive_group(required=True)
    auth_params.add_argument('--p12',
                             nargs=2,
                             metavar=('someone@api-xxx.iam.gserviceaccount.com', 'p12keyfile'),
                             help='Use a service account email and p12 key file for authentication')
    auth_params.add_argument('--json',
                             nargs=1,
                             metavar=('json-key-file'),
                             help='Use a json key file for authentication')
    parser.add_argument('package_name',
                        metavar='package-name',
                        help='Android package name (applicationId, reverse domain name)')

    # release details
    release = parser.add_argument_group('release')
    release.add_argument('version_code',
                         metavar='version-code',
                         type=int,
                         help='Android Version Code (int)')
    release.add_argument('--track',
                         default='internal',
                         help='The Play Store track that should be updated (default: "internal")')
    release.add_argument('--play-console-release-name',
                         metavar='release-name',
                         help='The name of the release in the Play store console ' +
                              '(default: same as the version code)')
    release.add_argument('--release-notes-file',
                         metavar='file',
                         type=argparse.FileType('r'),
                         default=sys.stdin,
                         help='Read release notes from file. (default: read from stdin)')

    # upload bundle
    release.add_argument('--upload-aab',
                         metavar='aab-file',
                         help='The path to a bundle (*.aab) file that to upload ' +
                              'as part of the release')

    print_info()
    args = parser.parse_args()

    if not args.play_console_release_name:
        args.play_console_release_name = str(args.version_code)

    # authentication type
    if args.p12:
        args.p12_service_account_email, args.p12_key_path = args.p12
        args.p12 = None
        args.authentication_type = 'p12'
        if not os.path.isfile(args.p12_key_path):
            raise FileNotFoundError(f'p12 key file not found: {args.p12_key_path}')
    elif args.json:
        args.json_key_file = args.json[0]
        args.json = None
        args.authentication_type = 'json'
        if not os.path.isfile(args.json_key_file):
            raise FileNotFoundError(f'json key file not found: {args.json_key_file}')

    if args.release_notes_file == sys.stdin:
        mode = os.fstat(sys.stdin.fileno()).st_mode
        if stat.S_ISFIFO(mode) or stat.S_ISREG(mode):
            pass # piped or redirected
        else:
            print("Enter release notes:")
    args.release_notes = args.release_notes_file.read()
    args.release_notes_file.close()

    if args.upload_aab:
        # using a file type causes issues on ci, so check file exist here
        if not os.path.isfile(args.upload_aab):
            raise FileNotFoundError(f'File not found for --upload-aab: {args.upload_aab}')

    __run_from_cli_args(args)
