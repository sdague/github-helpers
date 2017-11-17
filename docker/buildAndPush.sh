#!/bin/bash
#
# This script will build the docker image and push it to dockerhub.
#
# Usage: buildAndPush.sh imageName
#
# Dockerhub image names look like "username/appname" and must be all lower case.
# For example, "janesmith/calculator"

set -e

IMAGE_NAME=$1

function usage {
    cat <<EOF

buildAndPush.sh <imagename>

EOF
    exit 1
}

if [[ -z "$IMAGE_NAME" ]]; then
    usage
fi

echo "Using $IMAGE_NAME as the image name"

# Make the docker image
docker build --no-cache -t $IMAGE_NAME .
if [ $? -ne 0 ]; then
    echo "Docker build failed"
    exit
fi
docker push $IMAGE_NAME
if [ $? -ne 0 ]; then
    echo "Docker push failed"
    exit
fi
