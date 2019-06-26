import sys
import publisher

def upload():
    apk_file = sys.argv[1]

    service = publisher.build_service()
    edit_id = publisher.create_edit(service)
    publisher.upload_bundle(service, edit_id, apk_file)
    publisher.validate_and_commit_edit(service, edit_id)
    print('bye')

if __name__ == '__main__':
    upload()
