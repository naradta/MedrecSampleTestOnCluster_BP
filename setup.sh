#!/bin/sh
CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

function printMsg()
{
  msg=$1
  echo -e "\n=================== $msg ===================\n"
}

printMsg  "Oracle DB Scripts "
$CURR_DIR/scripts/importDBScripts.sh
printMsg  "End of Oracle DB Scripts"

printMsg  "Config WLS Resources "
$CURR_DIR/scripts/setupWLSResources.sh
printMsg  "End of Config WLS Resources "


printMsg  "Deploy Applications"
$CURR_DIR/scripts/deployApplications.sh
printMsg  "End of Deploy Applications"

