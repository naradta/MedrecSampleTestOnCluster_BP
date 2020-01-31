#!/bin/sh
CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $CURR_DIR/../config/db_config.properties

export ORACLE_HOME

LD_LIBRARY_PATH=$ORACLE_HOME:$ORACLE_HOME/lib
SQLPLUS=$ORACLE_HOME/sqlplus

export LD_LIBRARY_PATH

CONNRCTION_STRING="(DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=${DB_HOSTNAME})(PORT=${DB_PORT}))(CONNECT_DATA=(SERVICE_NAME=${DB_SID})))"


PATH=$ORACLE_HOME:$PATH
export PATH

echo "$ORACLE_HOME"
echo "$LD_LIBRARY_PATH"
echo "$PATH"

db_statuscheck() {
   COUNT=0
   while :
   do
	echo "`date` :Checking DB connectivity...";
	echo "`date` :Trying to connect "${DB_USERNAME}"/"${DB_PASSWORD}"@"${CONNRCTION_STRING}" ..."

	echo "exit" | ${SQLPLUS} -L ${DB_USERNAME}"/"${DB_PASSWORD}@${CONNRCTION_STRING} | grep Connected > /dev/null
	if [ $? -eq 0 ]
	then
		DB_STATUS="UP"
		export DB_STATUS
		echo "`date` :Status: ${DB_STATUS}. Able to Connect..."
		echo "`date` :Status: ${DB_STATUS}. Populate data..."
		#echo "@sqlScripts.sql" | ${SQLPLUS} -L ${DB_USERNAME}"/"${CONNRCTION_STRING} 
		#echo "@sqlScripts.sql" | ${SQLPLUS} -L${DB_USERNAME}"/"${DB_PASSWORD}@${CONNRCTION_STRING}
                echo "exit" | ${SQLPLUS} -s ${DB_USERNAME}"/"${DB_PASSWORD}@${CONNRCTION_STRING} @$CURR_DIR/sqlScripts.sql               
		break
	else
		DB_STATUS="DOWN"
		export DB_STATUS
		echo "`date` :Status: DOWN . Not able to Connect."
		echo "`date` :Not able to connect to database with Username: "${DB_USERNAME}" Password: "${DB_PASSWORD}" DB HostName: "${DB_HOSTNAME}" DB Port: "${DB_PORT}" SID: "${DB_SID}"."
		sleep 30
		COUNT=$((COUNT + 1))
                if [ $COUNT -gt 30 ]
                then
			echo "`date` :Status: DOWN . Please check if DB is healthy, unable to connect to DB for long time."
			exit 1
		fi
	fi
   done
}

db_statuscheck



