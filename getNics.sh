#!/bin/sh -ex

url="http://localhost:8080/ovirt-engine/api"
user="admin@internal"
password="engine"


function req()
{
request=$1
cmd=$2
curl \
--user "${user}:${password}" \
--request $request \
--header "Version: 4" \
--header "Accept: application/xml" \
"${url}/${cmd}"
#--verbose \
}

function get()
{
	req GET $1
}

function del()
{
	req DELETE $1
}

get hosts/2127de9d-317b-4829-a10b-0a4c68093bdb/nics

