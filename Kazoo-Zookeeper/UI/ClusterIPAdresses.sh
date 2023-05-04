#!/bin/bash

# Create an empty array to store the container information
containers=()

# Loop through all containers with names starting with "worker_svc-"
for container_name in $(sudo docker ps --format '{{.Names}}' | grep 'worker-'); do
    # Get the container IP address
    container_ip=$(sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container_name")

    # Add the container information to the array
    containers+=("{\"name\":\"$container_name\",\"ip\":\"$container_ip\"}")
done

# Convert the array to JSON format and save to a file
echo "{\"containers\":[$(printf '%s\n' "${containers[@]}" | paste -sd ',' -)]}" > IPAddresses.json