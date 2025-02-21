#!/usr/bin/bash

BRANCH_NAME=$1
REPOSITORY_NAME=$2
CURRENT_DIR=$(pwd)

echo "Updating application from branch $BRANCH_NAME in repository $REPOSITORY_NAME..."

cd $REPOSITORY_NAME
git pull origin $BRANCH_NAME

echo "Copying files from $REPOSITORY_NAME to $CURRENT_DIR..."
cp -rvf ./* ../