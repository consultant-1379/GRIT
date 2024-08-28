#!/bin/bash
echo Loading Data in DB
echo "Enter DB Name :"
read dbname 
echo "Enter Port Number :"
read port 
echo "Enter DB userid :"
read user 
echo "Enter DB password :"
read pwd
cmd="dbisql -nogui -c \"eng="$dbname";links=tcpip{host=localhost;port="$port"};uid="$user";pwd="$pwd"\""
while IFS='' read -r line || [[ -n "$line" ]]; do
    TableName="$(echo "$line" grep |cut -d '.' -f2 |cut -d " " -f1 |cut -d "'" -f1)"
    echo "Current Table :"$TableName
     $cmd $line
    echo Successfully Loaded
done < "$1"

