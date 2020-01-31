from java.io import FileInputStream
import java.lang
import os
import string

import sys
import java.sql.SQLException
from oracle.jdbc.pool import OracleDataSource

propdir=sys.argv[6]
propfile= propdir+"/db_config.properties"
propInputStream = FileInputStream(propfile)

configProps = Properties()
configProps.load(propInputStream)


# 1 - Connecting details - read from system arguments
username=sys.argv[3]
password=sys.argv[4]
adminHost = sys.argv[1]
adminPort = sys.argv[2]

serverUrl="t3://"+adminHost+":"+adminPort
clusterName=sys.argv[5]

#6 - Data Source Details
dsname = configProps.get("DS_NAME")
dsdbname= configProps.get("DB_NAME")
dsjndiname=configProps.get("DS_JNDI")
dsdriver = configProps.get("DS_DRIVER_CLASS")
dsurl = configProps.get("DB_URL")
dsusername = configProps.get("DB_USERNAME")
dspassword = configProps.get("DB_PASSWORD")
dsmaxcapacity =configProps.get("DS_MAX_CAPACITY")
dbHostName= configProps.get("DB_HOSTNAME")
dbPort= configProps.get("DB_PORT")
dbsid= configProps.get("DB_SID")
dsurl='jdbc:oracle:thin:@'+dbHostName+':'+dbPort+':'+dbsid


#Connection to the Server
print 'connection to Weblogic Admin Server'
connect(username,password,serverUrl)

#Create data source
############################

print 'Creating Data Source....'
edit()
startEdit()

# Create data source.
cd('/')
ref = getMBean('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname)

if(ref != None):
	print '########## JDBCSystemResources already exists with name '+ dsname

else:
	cmo.createJDBCSystemResource(dsname)
	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname)
	cmo.setName(dsname)

	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname + '/JDBCDataSourceParams/' + dsname)
	set('JNDINames',jarray.array([String(dsjndiname)], String))

	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname + '/JDBCDriverParams/' + dsname)
	cmo.setUrl(dsurl)
	cmo.setDriverName(dsdriver)
	set('Password', dspassword)

	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname + '/JDBCConnectionPoolParams/' + dsname)
	cmo.setTestTableName('SQL SELECT 1 FROM DUAL')

	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname + '/JDBCDriverParams/' + dsname + '/Properties/' + dsname)
	cmo.createProperty('user')
	cmo.createProperty('databaseName')

	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname + '/JDBCDriverParams/' + dsname + '/Properties/' + dsname + '/Properties/user')
	cmo.setValue(dsusername)

	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname + '/JDBCDriverParams/' + dsname + '/Properties/' + dsname + '/Properties/databaseName')
	cmo.setValue(dsdbname)


	cd('/JDBCSystemResources/' + dsname + '/JDBCResource/' + dsname + '/JDBCDataSourceParams/' + dsname)
	cmo.setGlobalTransactionsProtocol('TwoPhaseCommit')

	cd('/SystemResources/' + dsname)
	set('Targets',jarray.array([ObjectName('com.bea:Name=' + clusterName + ',Type=Cluster')], ObjectName))

save()
activate()

disconnect()
exit()
