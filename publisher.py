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

def main():
    service = build_service()
    edit_id = create_edit(service)
    print('bye')

if __name__ == '__main__':
    main()
