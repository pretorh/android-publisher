FROM alpine

RUN apk add --update python3 py3-pip py3-openssl && \
    pip3 install --upgrade google-api-python-client oauth2client

COPY *.py /opt/android-publisher/
