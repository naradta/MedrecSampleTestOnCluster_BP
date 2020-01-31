#!/bin/sh

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $CURR_DIR/../config/wls_config.properties

PROPERTIES_DIR=$CURR_DIR/../config

config_resources(){
${WLS_ORACLE_HOME}/oracle_common/common/bin/wlst.sh $CURR_DIR/configDataSource.py "${WLS_ADMINHOST}" "${WLS_ADMINPORT}" "${WLS_USERNAME}" "${WLS_PASSWORD}" "${WLS_CLUSTERNAME}" "${PROPERTIES_DIR}" "${WLS_DOMAIN_NAME}" "${FILE_STORE_PATH}"

${WLS_ORACLE_HOME}/oracle_common/common/bin/wlst.sh $CURR_DIR/configResources.py "${WLS_ADMINHOST}" "${WLS_ADMINPORT}" "${WLS_USERNAME}" "${WLS_PASSWORD}" "${WLS_CLUSTERNAME}" "${PROPERTIES_DIR}" "${WLS_DOMAIN_NAME}" "${FILE_STORE_PATH}"
}

config_resources
