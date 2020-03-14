import os
import sys
import publisher

def release():
    SERVICE_ACCOUNT_EMAIL = os.environ['SERVICE_ACCOUNT_EMAIL']
    KEY_FILE = os.environ['KEY_FILE']

    PACKAGE_NAME = os.environ['PACKAGE_NAME']
    TRACK = os.environ['RELEASE_TRACK']
    VERSION_NAME = os.environ['VERSION_NAME']
    VERSION_CODE = os.environ['VERSION_CODE']
    VERSION_NOTES = os.environ['VERSION_NOTES']

    version = {
        'name': VERSION_NAME,
        'code': VERSION_CODE,
        'notes': VERSION_NOTES,
    }

    service = publisher.build_service(SERVICE_ACCOUNT_EMAIL, KEY_FILE)
    edit_id = publisher.create_edit(service)
    if len(sys.argv) == 2:
        apk_file = sys.argv[1]
        publisher.upload_bundle(service, PACKAGE_NAME, edit_id, apk_file)
    publisher.update_track(service, PACKAGE_NAME, edit_id, TRACK, version)
    publisher.validate_and_commit_edit(service, PACKAGE_NAME, edit_id)
    print('bye')

if __name__ == '__main__':
    release()
