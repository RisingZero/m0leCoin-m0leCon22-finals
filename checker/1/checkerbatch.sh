#!/bin/bash

for i in 1 2 3 4 5 6
do
	ACTION=CHECK_SLA TEAM_ID=$1 ROUND=$i ./checker.py
	ACTION=PUT_FLAG FLAG=FLAG TEAM_ID=$1 ROUND=$i ./checker.py
	ACTION=GET_FLAG FLAG=FLAG TEAM_ID=$1 ROUND=$i ./checker.py
done

