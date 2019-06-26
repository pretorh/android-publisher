import os
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
    publisher.update_track(service, edit_id, TRACK, version)
    publisher.valid_and_commit_edit(service, edit_id)
    print('bye')

if __name__ == '__main__':
    release()
