#!/bin/sh

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $CURR_DIR/../config/wls_config.properties

SERVER_URL="t3://${WLS_ADMINHOST}:${WLS_ADMINPORT}"
deployApplication(){
     echo "`date` :Deploying Application...";
     cd ${WLS_ORACLE_HOME}/oracle_common/common/bin
     . ./setWlstEnv.sh

java weblogic.Deployer -adminurl $SERVER_URL -username "${WLS_USERNAME}" -password "${WLS_PASSWORD}" -targets "${WLS_CLUSTERNAME}" -deploy "${CURR_DIR}"/../dist/medrec.ear

java weblogic.Deployer -adminurl $SERVER_URL -username "${WLS_USERNAME}" -password "${WLS_PASSWORD}" -targets "${WLS_CLUSTERNAME}" -deploy "${CURR_DIR}"/../dist/browser-starter.war

java weblogic.Deployer -adminurl $SERVER_URL -username "${WLS_USERNAME}" -password "${WLS_PASSWORD}" -targets "${WLS_CLUSTERNAME}" -deploy "${CURR_DIR}"/../dist/chat.war

java weblogic.Deployer -adminurl $SERVER_URL -username "${WLS_USERNAME}" -password "${WLS_PASSWORD}" -targets "${WLS_CLUSTERNAME}" -deploy "${CURR_DIR}"/../dist/physician.ear

}

deployApplication


