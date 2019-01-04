#!/usr/bin/env sh

if [ -z $1 ]
then
    echo "No command passed to script"
    exit 1
elif [ $1 = "test" ]
then
    docker exec -it neopath coverage run /usr/local/bin/nosetests
    docker exec -it neopath coverage report
elif [ $1 = "cover" ]
then
    docker exec -it neopath coverage html -d cover
elif [ $1 = "lint" ]
then
    docker exec -it neopath pylint neopath/ tests/
else
    echo "$1 is not a valid command"
    exit 2
fi
