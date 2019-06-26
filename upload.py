import sys
import publisher

def upload():
    apk_file = sys.argv[1]

    service = publisher.build_service()
    edit_id = publisher.create_edit(service)
    publisher.upload(service, edit_id, apk_file)
    print('bye')

if __name__ == '__main__':
    upload()
