#!/bin/bash

scp eth-deploy/envs/$1.env root@10.60.$1.1:/root/s1-m0leCoin/.env

ssh root@10.60.$1.1 <<EOF
cd /root/s1-m0leCoin
docker-compose down
rm -rf m0lecoin-backend/data/*
docker-compose up -d --build
EOF
