from java.io import FileInputStream
import java.lang
import os
import string

import sys
import java.sql.SQLException
from oracle.jdbc.pool import OracleDataSource

propdir=sys.argv[6]
propfile= propdir+"/resource_config.properties"
propInputStream = FileInputStream(propfile)

configProps = Properties()
configProps.load(propInputStream)

#Read Properties
##############################

### - Connecting details - read from system arguments
username=sys.argv[3]
password=sys.argv[4]
adminHost = sys.argv[1]
adminPort = sys.argv[2]

serverUrl="t3://"+adminHost+":"+adminPort
clusterName=sys.argv[5]
 
#migratableTargetName = configProps.get("migratabletarget.name")
## changes this value dynamically
migratableTargetName= 'MS-2'+' (migratable)'
#machineName = configProps.get("machine.name")

### - JMSServer details
jmsServerName = configProps.get("jms.server.name")
jdbcstoreName = configProps.get("jdbcstore.name")
 
storeName = configProps.get("store.name")
#storePath = configProps.get("store.path")

### - SystemModule Details
systemModuleName = configProps.get("system.module.name")
 
### - ConnectionFactory Details
connectionFactoryName = configProps.get("connection.factory.name")
ConnectionFactoryJNDIName = configProps.get("connection.factory.jndi.name")
 
### - SubDeployment, Queue 
SubDeploymentName = configProps.get("sub.deployment.name")
queueName = configProps.get("queue.name")
queueJNDIName = configProps.get("queue.jndi.name")

domainname = sys.argv[7]
storePath = sys.argv[8]

### -Admin User details for medrec
medrec_admin_userid=configProps.get("medrec.admin.username")
medrec_admin_password=configProps.get("medrec.admin.password")
medrec_admin_userdesc=configProps.get("medrec.admin.userdesc")

#Connection to the Server
print 'connection to Weblogic Admin Server'
connect(username,password,serverUrl)
runningServer = ''
candidateServerList = []
################New changes###################

# Stop the cluster
def shutdownCluster(clusterName):
	try:
		shutdown(clusterName,'Cluster')
	except Exception, e:
		print 'Error while shutting down cluster' ,e
		dumpStack()


# Start the cluster
def startCluster(clusterName):
	try:
		start(clusterName,'Cluster',block='true')
	except Exception, e:
		print 'Error while starting cluster' ,e
		dumpStack()

def startClusterServers(clusterName):
    try:
       serverConfig()
       clusters = cmo.getClusters()   
       if clusters !=None:
           for cluster in clusters:
               if cluster.getName() == clusterName:
                   servers = cluster.getServers()
                   if servers !=None:
                       print('Number of servers in '+clusterName+' cluster is '+str(len(servers)))
                   for server in servers:
                       statevalMap = state(server.getName(),'Server',returnMap="true")
                       #print('stateval of server'+server.getName() +'is'+str(statevalMap))
                       stateval = str(statevalMap.get(server.getName()))
                       if stateval != 'RUNNING':
                           start(server.getName(),'Server',block='true')
                                  
    except Exception, e: 
       print 'Error while starting servers ',e 
       dumpStack() 


def setRequriedParamsOfCluster(clusterName):
    global runningServer
    global migratableTargetName
    global candidateServerList
    try:
       serverConfig()
       clusters = cmo.getClusters()   
       if clusters !=None:
           for cluster in clusters:
               if cluster.getName() == clusterName:
                   servers = cluster.getServers()
                   if servers !=None:
                       print('Number of servers in '+clusterName+' cluster are: '+str(len(servers)))

                   print('Checking Cluster '+clusterName+' Managed Servers State')

                   for server in servers:
                       statevalMap = state(server.getName(),'Server',returnMap="true")
                       #print('stateval of server'+server.getName() +'is'+str(statevalMap))
                       stateval = str(statevalMap.get(server.getName()))
                       if stateval == 'RUNNING':
                           runningServer = server.getName()                           
                           migratableTargetName= runningServer+' (migratable)'
                           break;
						  

                   for server in servers:
                       statevalMap = state(server.getName(),'Server',returnMap="true")
                       print('stateval of server'+server.getName() +'is'+str(statevalMap))
                       #stateval = str(statevalMap.get(server.getName()))
                       if stateval == 'RUNNING' and runningServer != server.getName() :
                           migratableTargetName = server.getName()+' (migratable)'	                           
                           break;

                   for server in servers:
                       statevalMap = state(server.getName(),'Server',returnMap="true")
                       #print('stateval of server'+server.getName() +'is'+str(statevalMap))
                       stateval = str(statevalMap.get(server.getName()))
                       if stateval == 'RUNNING':
                           candidateServerList.append(ObjectName('com.bea:Name='+server.getName()+',Type=Server'))


    except Exception, e: 
       print 'Error while checking server states ',e 
       dumpStack() 

startClusterServers(clusterName)
setRequriedParamsOfCluster(clusterName)

domainConfig()

edit()
startEdit()

print 'Setting Consensus Leasing Migration Basis for Cluster '+clusterName
cd('/Clusters/'+clusterName)
cmo.setMigrationBasis('consensus')
save()
activate()

print '###### Completed configuration of Consensus Leasing Migration Basis for Cluster ##############'

print 'Restarting Cluster to ensure changes are reflected....'
shutdown(clusterName,'Cluster')
start(clusterName,'Cluster')
print 'Cluster Restarted succesfully.'


print 'RunningServer name is '+runningServer
print 'MigratableTargetName name is '+migratableTargetName


cd('/')
startEdit()
ref = getMBean('/MigratableTargets/' + migratableTargetName)
if(ref != None):
        print '########## Migratable Target already exists with name '+ migratableTargetName
else:
        cmo.createMigratableTarget(migratableTargetName)

cd('/MigratableTargets/'+migratableTargetName)
cmo.setCluster(getMBean('/Clusters/'+clusterName))
cmo.setUserPreferredServer(getMBean('/Servers/'+runningServer))
cmo.setMigrationPolicy('exactly-once')
set('ConstrainedCandidateServers',jarray.array(candidateServerList, ObjectName))
cmo.setNumberOfRestartAttempts(6)
cmo.setNonLocalPostAllowed(false)
cmo.setRestartOnFailure(false)
cmo.setPostScriptFailureFatal(true)
cmo.setSecondsBetweenRestarts(30)
save()
activate()


print '###### Completed configuration of Migratable targets##############'


##############################################




#Creating Authentication user
###########################
serverConfig()
print 'Creating Admin User....'
cd('/SecurityConfiguration/'+domainname+'/Realms/myrealm/AuthenticationProviders/DefaultAuthenticator')
if (cmo.userExists(medrec_admin_userid)):
	print '########## User already exists with username '+medrec_admin_userid
else:
	cmo.createUser(medrec_admin_userid,medrec_admin_password,medrec_admin_userdesc)

domainConfig()

#creating FileStore
############################

print 'Creating JMS FileStore....'
#domainConfig()
edit()
startEdit()

cd('/')
ref = getMBean('/FileStores/' + storeName)

if(ref != None):
	print '########## File Store already exists with name '+ storeName
else:
	cmo.createFileStore(storeName)
	print '===> Created FileStore - ' + storeName
	Thread.sleep(10)
	cd('/FileStores/'+storeName)
	cmo.setDirectory(storePath)
	print 'Running Server '+runningServer
	#set('Targets',jarray.array([ObjectName('com.bea:Name='+runningServer+' (migratable),Type=MigratableTarget')], ObjectName))
	set('Targets',jarray.array([ObjectName('com.bea:Name='+migratableTargetName+',Type=MigratableTarget')], ObjectName))

save()
activate()


#Creating JMS Server
############################

print 'Creating JMS Server....'
startEdit()
cd('/')
ref = getMBean('/JMSServers/' + jmsServerName)

if(ref != None):
	print '########## JMS Server already exists with name '+ jmsServerName
else:
	cmo.createJMSServer(jmsServerName)
	print '===> Created JMS Server - ' + jmsServerName
	Thread.sleep(10)
	cd('/JMSServers/'+jmsServerName)
	#cmo.setPersistentStore(getMBean('/JDBCStores/'+jdbcstoreName))
	cmo.setPersistentStore(getMBean('/FileStores/'+storeName))
	set('Targets',jarray.array([ObjectName('com.bea:Name='+migratableTargetName+',Type=MigratableTarget')], ObjectName))

save()
activate()

#Creating JMS Module
#########################

print 'Creating JMS Module....in cluster: '+clusterName

startEdit()
cd('/')

ref = getMBean('/JMSSystemResources/' + systemModuleName)

if(ref != None):
	print '########## JMS System Module Already exists with name '+ systemModuleName
else:
	cmo.createJMSSystemResource(systemModuleName)
	print '===> Created JMS System Module - ' + systemModuleName
	cd('/JMSSystemResources/'+systemModuleName)
	set('Targets',jarray.array([ObjectName('com.bea:Name='+clusterName+',Type=Cluster')], ObjectName))

save()
activate()


#Creating JMS SubDeployment
############################

print 'Creating JMS SubDeployment....'

startEdit()

ref = getMBean('/JMSSystemResources/'+systemModuleName+'/SubDeployments/'+SubDeploymentName)
if(ref != None):
	print '########## JMS SubDeployment Already exists with name '+ SubDeploymentName + 'in module '+systemModuleName
else:
	cmo.createSubDeployment(SubDeploymentName)
	print '===> Created JMS SubDeployment - ' + systemModuleName
	cd('/JMSSystemResources/'+systemModuleName+'/SubDeployments/'+SubDeploymentName)
	set('Targets',jarray.array([ObjectName('com.bea:Name='+jmsServerName+',Type=JMSServer')], ObjectName))

save()
activate()

#Creating JMS Connection Factory
###############################

print 'Creating JMS Connection Factory....'
startEdit()

ref = getMBean('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/ConnectionFactories/'+connectionFactoryName)

if(ref != None):
	print '########## JMS Connection Factory Already exists with name '+ connectionFactoryName + 'in module '+systemModuleName
else:
	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName)
	cmo.createConnectionFactory(connectionFactoryName)
	print '===> Created Connection Factory - ' + connectionFactoryName
	
	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/ConnectionFactories/'+connectionFactoryName)
	cmo.setJNDIName(ConnectionFactoryJNDIName)

	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/ConnectionFactories/'+connectionFactoryName+'/SecurityParams/'+connectionFactoryName)
	cmo.setAttachJMSXUserId(false)

	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/ConnectionFactories/'+connectionFactoryName+'/ClientParams/'+connectionFactoryName)
	cmo.setClientIdPolicy('Restricted')
	cmo.setSubscriptionSharingPolicy('Exclusive')
	cmo.setMessagesMaximum(10)

	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/ConnectionFactories/'+connectionFactoryName+'/TransactionParams/'+connectionFactoryName)
	cmo.setXAConnectionFactoryEnabled(true)

	cd('/JMSSystemResources/'+systemModuleName+'/SubDeployments/'+SubDeploymentName)
	set('Targets',jarray.array([ObjectName('com.bea:Name='+jmsServerName+',Type=JMSServer')], ObjectName))

	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/ConnectionFactories/'+connectionFactoryName)
	cmo.setSubDeploymentName(''+SubDeploymentName)

save()
activate()


#Creating JMS Queue
##################################

print 'Creating JMS Queue....'

startEdit()

ref = getMBean('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/Queues/'+queueName)

if(ref != None):
	print '########## JMS Queue Already exists with name '+ queueName + 'in module '+systemModuleName
else:
	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName)
	cmo.createQueue(queueName)
	print '===> Created Queue - ' + queueName

	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/Queues/'+queueName)
	cmo.setJNDIName(queueJNDIName)
	
	cd('/JMSSystemResources/'+systemModuleName+'/SubDeployments/'+SubDeploymentName)
	set('Targets',jarray.array([ObjectName('com.bea:Name='+jmsServerName+',Type=JMSServer')], ObjectName))

	cd('/JMSSystemResources/'+systemModuleName+'/JMSResource/'+systemModuleName+'/Queues/'+queueName)
	cmo.setSubDeploymentName(''+SubDeploymentName)

save()
activate()
print '###### Completed configuration of all required JMS Objects ##############'


#Creating Mail Session
##################################
print 'Creating Mail Session....'

#8 -Mail Session Details
ms_name=configProps.get("mailsession.name")
ms_username=configProps.get("mailsession.username")
ms_password=configProps.get("mailsession.password")
ms_mail_user=configProps.get("mailsession.mail.user")
ms_mail_host=configProps.get("mailsession.mail.host")
ms_jndiname=configProps.get("mailsession.jndiname")

startEdit()

ref = getMBean('/MailSessions/mail/'+ms_name)

if(ref != None):
	print '########## MailSession Already exists with name '+ms_name
else:
	cd('/')
	cmo.createMailSession('mail/'+ms_name)
	cd('/MailSessions/mail/'+ms_name)
	cmo.setSessionUsername(ms_username)
	cmo.setSessionPassword(ms_password)
	#setEncrypted('SessionPassword', 'SessionPassword_1580205200887', '/scratch/app/mw/wls_domains/wls_12_2_1_3_d2/Script1580205057775Config', '/scratch/app/mw/wls_domains/wls_12_2_1_3_d2/Script1580205057775Secret')
	prop = Properties()
	prop.setProperty('mail.user', ms_mail_user)
	prop.setProperty('mail.host', ms_mail_host)
	cmo.setProperties(prop)
	cmo.setJNDIName(ms_jndiname)
	set('Targets',jarray.array([ObjectName('com.bea:Name='+clusterName+',Type=Cluster')], ObjectName))

save()
activate()

#Creating WLDF Resources
##################################
print 'Creating WLDF....'

startEdit()

ref = getMBean('/WLDFSystemResources/MedRecWLDF')

if(ref != None):
	print '########## WLDF Already exists with name MedRecWLDF'
else:
	cd('/WLDFSystemResources')
	cmo.createWLDFSystemResource('MedRecWLDF')
	cd('/WLDFSystemResources/MedRecWLDF')
	cmo.setDescription('')
	set('Targets',jarray.array([ObjectName('com.bea:Name='+clusterName+',Type=Cluster')], ObjectName))
	cd('/WLDFSystemResources/MedRecWLDF/WLDFResource/MedRecWLDF/Harvester/MedRecWLDF')
	cmo.createHarvestedType('com.oracle.medrec.admin.AdminReport')
	cd('/WLDFSystemResources/MedRecWLDF/WLDFResource/MedRecWLDF/Harvester/MedRecWLDF/HarvestedTypes/com.oracle.medrec.admin.AdminReport')
	set('HarvestedAttributes',jarray.array([String('NewUserCount')], String))
	cmo.setHarvestedInstances(None)
	cmo.setNamespace('ServerRuntime')
	cd('/WLDFSystemResources/MedRecWLDF/WLDFResource/MedRecWLDF/Instrumentation/MedRecWLDF')
	cmo.setEnabled(true)
	cmo.createWLDFInstrumentationMonitor('DyeInjection')
	cd('/WLDFSystemResources/MedRecWLDF/WLDFResource/MedRecWLDF/Instrumentation/MedRecWLDF/WLDFInstrumentationMonitors/DyeInjection')
	cmo.setDescription('Dye Injection monitor')
	cmo.setProperties('ADDR1=127.0.0.1 USER1=volley@ball.com')
	set('Actions',jarray.array([], String))
	cmo.setDyeMask(None)


save()
activate()


disconnect()
exit()
