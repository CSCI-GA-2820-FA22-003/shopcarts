#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
docker cp ~/.bluemix/apikey.json nyu:/home/devops 
docker exec nyu sudo chown devops:devops /home/devops/apikey.json
echo "Complete"
