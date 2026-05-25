#!/bin/bash


# This will start local for all the dependencies, including the database and the API server.
ACTION=$1
if [ "$ACTION" = "start" ]; then
    echo "Starting Docker servers..."
    sudo docker start Tryora-postgres
    sudo docker start Tryora-redis
elif [ "$ACTION" = "stop" ]; then
    echo "Stopping Docker servers..."
    sudo docker stop Tryora-postgres
    sudo docker stop Tryora-redis
else
    echo "Usage: $0 {start|stop}"
    echo "$ACTION is not a valid action."
fi

# . ./scripts/local.sh start
# TODO: Add more services to start/stop, such as the API server, if needed.