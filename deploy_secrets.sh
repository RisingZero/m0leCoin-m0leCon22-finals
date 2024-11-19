#!/bin/bash

for (( i=0; i < $1; i++ ))
do
	scp eth-deploy/envs/$i.env root@138.201.93.240:/root/certs/certs/team$i/m0lecoin.envs/$i.env
done

