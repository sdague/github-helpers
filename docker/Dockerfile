# Dockerfile for example whisk docker action
FROM openwhisk/python3action

# add package build dependencies
RUN apk add --no-cache git

RUN pip install pygithub

RUN pip install git+git://github.com/sdague/python-openwhisk.git
