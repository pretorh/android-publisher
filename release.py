import os
import sys
import publisher

TRACK = os.environ['RELEASE_TRACK']
VERSION_NAME = os.environ['VERSION_NAME']
VERSION_CODE = os.environ['VERSION_CODE']
VERSION_NOTES = os.environ['VERSION_NOTES']

def release():
    version = {
        'name': VERSION_NAME,
        'code': VERSION_CODE,
        'notes': VERSION_NOTES,
    }

    service = publisher.build_service()
    edit_id = publisher.create_edit(service)
    if len(sys.argv) == 2:
        apk_file = sys.argv[1]
        publisher.upload_bundle(service, edit_id, apk_file)
    publisher.update_track(service, edit_id, TRACK, version)
    publisher.validate_and_commit_edit(service, edit_id)
    print('bye')

if __name__ == '__main__':
    release()
