#!/bin/bash

# List of container names and IP addresses
container_names=("worker1" "worker2" "worker3" "worker4")
ip_addresses=("172.25.0.10" "172.25.0.11" "172.25.0.12" "172.25.0.13")

# Create an empty array for the workers
workers=()

# Loop over each container name and IP address and ping the IP
for (( i=0; i<${#container_names[@]}; i++ ))
do
  name=${container_names[$i]}
  ip=${ip_addresses[$i]}
  if ping -c 1 -W 1 $ip > /dev/null 2>&1
  then
    # If the container is alive, add an object to the workers array with the container name, IP address, and status of 1
    workers+=('{"name": "'$name'", "ip": "'$ip'", "status": "1"}')
  else
    # If the container is not responding, add an object to the workers array with the container name, IP address, and status of 0
    workers+=('{"name": "'$name'", "ip": "'$ip'", "status": "0"}')
  fi
done

# Create the final JSON object with the workers array
json='{"workers":['$(IFS=,; echo "${workers[*]}")']}'

# Write the JSON object to a file
echo $json > WorkerStatus.json