#!/usr/bin/bash

BRANCH_NAME=$1
REPOSITORY_NAME=$2

echo "Pulling latest changes from branch $BRANCH_NAME in repository $REPOSITORY_NAME..."

cd $REPOSITORY_NAME
git pull origin $BRANCH_NAME
cp -r ./* ../