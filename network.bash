#!/bin/bash

# Docker network name
NETWORK_NAME="your_network_name"

# Container name filters
NAME_FILTERS=("ui-" "monitoring-")

# Get container IDs
container_ids=$(docker ps -q)

# Iterate over container IDs
for container_id in $container_ids; do
  # Get container name
  container_name=$(docker inspect --format='{{.Name}}' "$container_id" | sed 's/^\///')

  # Check if container name matches the filters
  for name_filter in "${NAME_FILTERS[@]}"; do
    if [[ $container_name == *"$name_filter"* ]]; then
      # Get container IP
      container_ip=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$container_id")
      echo "Container Name: $container_name, IP: $container_ip"
    fi
  done
done