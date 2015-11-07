#!/bin/bash

run_service() {
	SERVICE_NAME=$1
	WAIT_FOR=$2
	WAIT_PORT=$3

    if [ ! -z $WAIT_FOR ]; then
        if [ -z $WAIT_PORT ]; then
            echo "Please also provide a port"
            exit 1
        fi

        COUNT=0
        TIMEOUT=10

        echo -n "Waiting for '$WAIT_FOR' on $WAIT_PORT "
        while ! (nc -z $WAIT_FOR $WAIT_PORT)
        do
            sleep 1
            if [[ "$COUNT" -ge "$TIMEOUT" ]]
            then
                echo "$WAIT_FOR:$WAIT_PORT not available, aborting..."
                exit -1
           fi
           let COUNT++
           echo -n "."
        done
        echo "."
        echo "'$WAIT_FOR' available on $WAIT_PORT."
    fi

    echo "Starting service $SERVICE_NAME"
    python3 /harpc/start_$SERVICE_NAME.py
}

run_service $*
