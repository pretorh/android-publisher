import os
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

SERVICE_ACCOUNT_EMAIL = os.environ['SERVICE_ACCOUNT_EMAIL']
KEY_FILE = os.environ['KEY_FILE']
PACKAGE_NAME = os.environ['PACKAGE_NAME']

SCOPE = 'https://www.googleapis.com/auth/androidpublisher'

def build_service():
    print('setup credentials')
    # build service acount using p12 file, based on
    # https://stackoverflow.com/a/35666374/1016377
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL, KEY_FILE, scopes=[SCOPE])

    print('setup service')
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('androidpublisher', 'v3', http=http)

def create_edit(service):
    print('setup edit')
    request = service.edits().insert(body={}, packageName=PACKAGE_NAME)
    result = request.execute()
    edit_id = result['id']
    print('setup edit: %s' % (edit_id))
    return edit_id

def update_track(service, edit_id, track, version):
    print('update track %s' % (track))
    request = service.edits().tracks().update(
        editId=edit_id,
        track=track,
        packageName=PACKAGE_NAME,
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

def validate_and_commit_edit(service, edit_id):
    print('validating')
    response = service.edits().validate(editId=edit_id, packageName=PACKAGE_NAME).execute()
    print('validated %s' % (response))

    print('commiting')
    response = service.edits().commit(editId=edit_id, packageName=PACKAGE_NAME).execute()
    print('commited %s' % (response))

def upload_bundle(service, edit_id, apk_file):
    print('uploading')
    apk_response = service.edits().bundles().upload(
        editId=edit_id,
        packageName=PACKAGE_NAME,
        media_body=apk_file,
        media_mime_type='application/octet-stream',
        ).execute()
    print('uploaded, %s' % (apk_response))
