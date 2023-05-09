#!/bin/bash

# Look up IP addresses of containers named "worker"
WORKER_IPS=$(dig "worker" +short)

# Convert the IP addresses to a JSON array
JSON=$(printf '{"ips": %s}' "$(echo "${WORKER_IPS}" | jq -R . | jq -s .)")

# Save the JSON array to a file
echo $JSON > WorkerIPs.json