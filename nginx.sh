#!/bin/bash

nginx_containers=$(docker ps --filter "name=nginx" --format "{{.ID}}")
for container_id in $nginx_containers; do
    docker exec "$container_id" nginx -s reload
done