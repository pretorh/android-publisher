import publisher

def release():
    service = publisher.build_service()
    edit_id = publisher.create_edit(service)
    publisher.update_track(service, edit_id)
    publisher.valid_and_commit_edit(service, edit_id)
    print('bye')

if __name__ == '__main__':
    release()
