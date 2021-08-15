# Android Publisher

A Python3 script to publish Android bundle files to the Play store

## Requirements

system:

- python3
- python3-pip
- python3-openssl

pip3:

- google-api-python-client
- oauth2client

## Creating a service account

Go to https://play.google.com/console (main console, not in any specific app), "Setup" > "API Access" (you need permisions, may need to enable)

Scroll to "Service accounts", and create a new serivce account (opens steps to follow on https://console.developers.google.com)

Create the service account:
- step 2 is displayed as optional, [but must be setup for Play console](https://stackoverflow.com/a/54717925/1016377) ("Basic" > "Editor" was good enough)
- copy the service account email address (`...@....iam.gserviceaccount.com`)
- go to "Keys" tab to create a `P12` key

Go back to Play console, and see if the service account is listed. From table, click "Grant Access".

Grant permissions:
- Needs "App Access" > "View app information..."
- under "Release": "...production..." and/or "...testing tracks..."

## links

- [sample apk publisher](https://github.com/googlesamples/android-play-publisher-api/blob/master/v3/python/upload_apks_rollout.py)
