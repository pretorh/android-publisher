#!/usr/bin/env python3
import argparse
import sys
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import apiclient

SCOPE = 'https://www.googleapis.com/auth/androidpublisher'
SCRIPT_VERSION = '2021-08-13'

def print_info():
    print('publisher.py: %s' % SCRIPT_VERSION)
    print('')

def build_service(service_account_email, key_file):
    print('setup credentials and building service')
    # build service acount using p12 file, based on
    # https://stackoverflow.com/a/35666374/1016377
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email, key_file, scopes=[SCOPE])

    http = httplib2.Http()
    http = credentials.authorize(http)
    return apiclient.discovery.build('androidpublisher', 'v3', http=http)

def create_edit(service, package_name):
    request = service.edits().insert(body={}, packageName=package_name)
    result = request.execute()
    edit_id = result['id']
    print('setup edit: %s' % (edit_id))
    return edit_id

def update_track(service, package_name, edit_id, track, version):
    print('update track %s' % (track))
    request = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=package_name,
        body={
            u'track': track,
            u'releases': [{
                u'name': version['name'],
                u'versionCodes': [version['code']],
                u'releaseNotes': [{
                    u'language': u'en-GB',
                    u'text': version['notes']
                }],
                u'status': u'completed',
            }]
        })
    response = request.execute()
    print('setup with: %s' % (str(response['releases'])))

def validate_and_commit_edit(service, package_name, edit_id):
    response = service.edits().validate(editId=edit_id, packageName=package_name).execute()
    print('validated %s' % (response))

    response = service.edits().commit(editId=edit_id, packageName=package_name).execute()
    print('commited %s' % (response))

def upload_bundle(service, package_name, edit_id, aab_file):
    print('uploading %s' % (aab_file))
    request = service.edits().bundles().upload(
        editId=edit_id,
        packageName=package_name,
        media_body=aab_file,
        media_mime_type='application/octet-stream',
    )
    response = request.execute()
    print('uploaded, %s' % (response))

# running as cli

def __run_from_cli_args(flags):
    print_info()

    service = build_service(flags.service_account_email, flags.p12key_path)
    edit_id = create_edit(service, flags.package_name)
    update_track(service, flags.package_name, edit_id, flags.track, version={
        'name': flags.play_console_release_name,
        'code': flags.version_code,
        'notes': flags.release_notes,
    })
    validate_and_commit_edit(service, flags.package_name, edit_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    # authentication and app details
    parser.add_argument('service_account_email',
                        metavar='service-account-email',
                        help='The email address of the service account used for authentication ' +
                            '(something like ...@api-...-...iam.gserviceaccount.com)')
    parser.add_argument('p12key',
                        type=argparse.FileType('r'),
                        help='Path to the p12 certificate key file for authentication')
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
                         help='The name of the release in the Play store console ' +
                              '(default: same as the version code)')
    release.add_argument('--release-notes-file',
                         type=argparse.FileType('r'),
                         default=sys.stdin,
                         help='Read release notes from file. (default: read from stdin)')

    args = parser.parse_args()
    if not args.play_console_release_name:
        args.play_console_release_name = str(args.version_code)
    args.p12key_path = args.p12key.name
    args.p12key.close()
    args.release_notes = args.release_notes_file.read()
    args.release_notes_file.close()

    __run_from_cli_args(args)
