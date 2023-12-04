#!/bin/bash
set -e

echo "Updating deployment image and run jobs"
echo

export COMMIT_HASH=$(git rev-parse HEAD)

cd `dirname "$0"`

cat configmap.yaml \
    | sed "s/<COMMIT_HASH>/\"$COMMIT_HASH\"/" \
    | kubectl apply -f -

for manifest in django.yaml clearsessions.yaml
do
    cat $manifest | sed "s/<COMMIT_HASH>/$COMMIT_HASH/" | kubectl apply -f -
done

for manifest in migrate.yaml collectstatic.yaml
do
    cat $manifest | sed "s/<COMMIT_HASH>/$COMMIT_HASH/" | kubectl create -f -
done

echo
echo "Project deployed successfully"
echo "Commit hash of deployed version: $COMMIT_HASH"
