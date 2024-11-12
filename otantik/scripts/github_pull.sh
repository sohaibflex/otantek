#!/bin/bash
# Checking the Service Status
service="odoo"
service_status=""

x=1
while [ $x -le 5 ]
do
	if [ -z "$service" ]; then
		echo "usage: $0 <service-name>"
		service_status="start"
		break
	fi
	echo "Checking $service status"
	STATUS="$(systemctl is-active $service)"
	RUNNING="$(systemctl show -p SubState $service | cut -d'=' -f2)"
	if [ "${STATUS}" = "active" ]; then
		echo "$service Service is Active"
	if [ "${RUNNING}" = "running" ]; then
		echo "$service Service is Running"
		service_status="start"
		systemctl stop odoo
	else
		echo "$service Service Not Running"
		service_status="stop"
		break
	fi
	else
		echo "$service Service not Active "
		service_status="stop"
		break
	fi
	x=$(( $x + 1 ))
	sleep 5
done



if [ "$service_status" = "stop" ]; then
	eval `ssh-agent -s`
	ssh-add  /root/.ssh/otantik-github-key
	cd /odoo/addons/otantik
	git pull git@github.com:otantik-amazonserver/otantik.git 


fi

