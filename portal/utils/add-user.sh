#! /bin/bash
##
# @file add-user.sh
# @brief: Authorize specified Github user for PACE
# @author Sarat Sreepathi
# @version 1.0
# @date 2019-08-26

USAGE="Usage: add-user.sh <github_username>"

# Check arguments
if [ $# -eq 0 ] ; then
    echo $USAGE
    exit 1;
fi

myid=$1

# mysql -u sarat -p pace --batch -N -e "select id from authusers where user = '$1' ; "
#  Error code check for existing user doesn't seem to work
# echo $?
mysql -u sarat -p pace -e "insert into authusers (user) VALUES ('$1');"
# mysql -u sarat -p pace -e "select * from authusers where user = '$1' ; "
# mysql -u sarat -p pace -e "select * from authusers where user = \"$1\" ; "


