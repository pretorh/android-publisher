import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import apiclient

SCOPE = 'https://www.googleapis.com/auth/androidpublisher'
SCRIPT_VERSION = '2021-08-13'

def print_info():
    print('publisher.py: %s' % SCRIPT_VERSION)
    print('')

def build_service(service_account_email, key_file):
    print('setup credentials')
    # build service acount using p12 file, based on
    # https://stackoverflow.com/a/35666374/1016377
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email, key_file, scopes=[SCOPE])

    print('setup service')
    http = httplib2.Http()
    http = credentials.authorize(http)
    return apiclient.discovery.build('androidpublisher', 'v3', http=http)

def create_edit(service, package_name):
    print('setup edit')
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
    print('validating')
    response = service.edits().validate(editId=edit_id, packageName=package_name).execute()
    print('validated %s' % (response))

    print('commiting')
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
