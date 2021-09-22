# Miguel Reyes,
import os.path
import sys
import pandas as pd
from numpy import nan
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages')

import csvConcatenator #calls for concatenator py script in case that there are more than one csv files that have to be imported

#Getting path to the script, from here all relation to files is created. 
file_name = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]
export_path =  os.path.join(os.path.dirname(os.path.realpath(__file__)),"Asana Export") #Folder where the concatenated file is exported
full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Import to Jira") #Folder where the ready to be imported file is stored

if not os.path.exists(full_path): #creates folder that 
    os.mkdir(full_path)
    if not os.path.exists(os.path.join(full_path, file_name)):
        os.mkdir(os.path.join(full_path, file_name))
file_location = os.path.join(full_path, 'Import_to_Jira.csv')


print ("********************************************")
#We read the export file from Asana
os.chdir(export_path)
df= pd.read_csv("AsanaExport.csv")

df['Notes']=df['Notes'].astype('str') #sets all information in the notes column as string, fixes the error with the multiple columns for this field
df['Epic Link']=df['Parent Task'] #Epic link is the name of the parent task, simply putting in "jira words"

#finding unique epic names for working with them later to create jira csv structure
epicNames=df['Epic Link'].unique()

#Removing the nan values
epicNames=[item for item in epicNames if not(pd.isnull(item)) == True]

df['Issue Type']='Task' #Sets all tasks firsly to the task issue type
#Getting number of elements in the epicNames list

#Iterating using the length of the list in order to mark the issues as Epics when found in the epic list
for i in range(len(epicNames)):
    df.loc[df['Name']==epicNames[i],['Issue Type']]='Epic' #updates the issue type to epic when epic name matches the ecpicName list

df.loc[df['Issue Type']=='Epic',['Epic Name']]=df['Name'] #includes the name of the epic when the task has been flagged as epic

try:#because we don't know if there is an assignee Email field
    df['Assignee Email']=df['Assignee Email'].str.lower() #changes the email address to lower case as normally jira has them in lower case.
    print('Correctly read and adjusted email to Jira format')
except:
    print("No assignee field was found for your tasks, are you sure you have the correct export file?") 
#df=df.sort_values(by=['Issue Type']) #Sorts dataframe to first show epics for stories/subtasks to be created AFTER the epics



#Defining different status as according to the column they are in.
dfStatus=df['Section/Column'].unique()
#defining the array of the possible months in the section/column field
months=['January','February','March','April', 'May','June','July','August','September','October','November','December']

#getting only the current status of the tasks
statusInBoard = [x for x in dfStatus if x not in months]
#Removing the nan values
statusInBoard=[item for item in statusInBoard if not(pd.isnull(item)) == True]

#Adding values for month label and backlog status
columnChoice=1#("Are you using your columns to indicate status (1) or as a tag (2)?")
if columnChoice == 1:
    try:
        df.loc[df['Section/Column'].isin(months),['Month Tag']]=df['Section/Column'] #includes the name of the epic when the task has been flagged as epi
        df.loc[df['Section/Column'].isin(months),['Backlog Status']]='Done' #includes the name of the epic when the task has been flagged as epi
        #Iterating using the length of the list
        for i in range(len(statusInBoard)):
            df.loc[df['Section/Column']==statusInBoard[i],['Backlog Status']]=df['Section/Column'] #updates the issue type to epic when epic name matches the ecpicName list
        print('Correctly read and adjusted status and columns to the different values')
    except:
        print("No Section/Column field was found for your tasks, are you sure you have the correct export file?")
    
else:
    df.loc[df['Completed At'].notnull(),['Backlog Status']]="Done"#marks tasks/epics as done in case that they were completed in Asana    
###############################################################################################################    
###########################################Getting the list of super epics#####################################
epicArray=df[df['Issue Type']=="Epic"] 
superEpicList=epicArray['Epic Link'].unique()
#Removing the nan values
superEpicList=[item for item in superEpicList if not(pd.isnull(item)) == True]
#Getting number of elements in the epicNames list
lengthSuperEpicList = len (superEpicList)
#Iterating using the length of the list
for i in range(len (superEpicList)):
    df.loc[df['Name']==superEpicList[i],['Issue Type']]='Super Epic' #updates the issue type to super epic when epic name matches the ecpicName list
###############################################################################################################
###############################################################################################################


###############################################################################################################    
###########################################Getting the list of super duper epics###############################
superEpicArray=df[df['Issue Type']=="Super Epic"] 
superEpicArray=superEpicArray.sort_values(by=['Name']) #sorts alphabetically for later ennumerating
superDuperEpicList=superEpicArray['Epic Link'].unique()
#Removing the nan values
superDuperEpicList=[item for item in superDuperEpicList if not(pd.isnull(item)) == True]

#Iterating using the length of the list
for i in range(len(superDuperEpicList)):
    df.loc[df['Name']==superDuperEpicList[i],['Issue Type']]='Super Duper Epic' #updates the issue type to super duper epic when epic name matches the ecpicName list
###############################################################################################################
###############################################################################################################

#*******Clearing up for super duper epics*************
df.loc[df['Issue Type']=='Super Epic',['Super Epic Tag']]=df['Epic Link'].str.replace(' ','_') #includes the name of the super epic when the task has been flagged as epic
df.loc[df['Issue Type']=='Super Duper Epic',['Super Epic Tag']]=df['Epic Link'].str.replace(' ','_')+ ' ' + df['Name'].str.replace(' ','_') #includes the name of the epic when the task has been flagged as epic as well as the epic link so that they are linked via the label
df.loc[df['Issue Type']=='Super Duper Epic',['Name']]=df['Name']#includes the name of the epic when the task has been flagged as epic
df.loc[df['Issue Type']=='Super Epic',['Epic Link']]='' #removes epic link for super epic tickets
df.loc[df['Issue Type']=='Super Duper Epic',['Epic Link']]='' #removes epic link for super duper epic tickets

##This is for finding epics that might have had a link to the super duper epic and adds the name of the epic as a tag to the super epic tag field
for i in set(superDuperEpicList):
    df.loc[(df['Epic Link']==i) & (df['Issue Type']=="Epic"),['Super Epic Tag']]=str(i).replace(' ','_')
    df.loc[(df['Epic Link']==i) & (df['Issue Type']=="Epic"),['Epic Link']]=''

###############################################################################################################
###############################################################################################################
###############################################################################################################

print ("********************************************")
##########################superDuperEpicArray check and ennumeration###########################################
superDuperEpicArray=df[df['Issue Type']=="Super Duper Epic"] 
superDuperEpicArray=superDuperEpicArray.sort_values(by=['Name'])
superDuperEpicListUnique=superDuperEpicArray['Name'].unique()
superDuperEpicList=superDuperEpicArray['Name']
print ("Checking list for super duper epics...")
if len(superDuperEpicList) == len(superDuperEpicListUnique):
    print ("You're on the clear, no double registries in the super duper part ;)")
else:
    #for element in superDuperEpicList:
    #    if element not in superDuperEpicListUnique:
    #        superDuperEpicDifference.append(element)
    print ("There is something wrong with your file please change one of the following tasks and reexport")
    print ("You need to rename the following task(s):")
    duplicateSuperDuperEpics=[]
    comparisonList=[]
    for i in superDuperEpicList:
        if i not in comparisonList:
            comparisonList.append(i)
        else:
            duplicateSuperDuperEpics.append(i)    
#try:
#    if duplicateSuperDuperEpics.notempty():
#        for items in duplicateSuperDuperEpics:
#            print(items)    
    

#once that the check has been done we can continue to ennumerate the super duper epics
for i in range(len(superDuperEpicListUnique)):
    df.loc[df['Name']==superDuperEpicListUnique[i],['Issue ID']]=int((i+1))
print("End of checking super duper epic list")
###############################################################################################################

###############################superEpicArray check and ennumeration###########################################
superEpicArray=df[df['Issue Type']=="Super Epic"] 
superEpicArray=superEpicArray.sort_values(by=['Name'])
superEpicListUnique=superEpicArray['Name'].unique()
superEpicList=superEpicArray['Name']
print ("********************************************")
print ("Checking list for super epics...")
if len(superEpicList) == len(superEpicListUnique):
    print ("You're on the clear, no double registries in the super part ;)")
else:
    #for element in superDuperEpicList:
    #    if element not in superDuperEpicListUnique:
    #        superDuperEpicDifference.append(element)
    print ("There is something wrong with your file please change one of the following tasks and reexport")
    print ("You need to rename the following task(s):")
    duplicateSuperEpics=[]
    comparisonList=[]
    for i in superEpicList:
        if i not in comparisonList:
            comparisonList.append(i)
        else:
            duplicateSuperEpics.append(i)
#    for i in duplicateSuperEpics:
#        print (i)
    #exit()****************INCLUDE ONCE THAT THE CODE HAS BEEN TESTED IN JUPYTER
    

#once that the check has been done we can continue to ennumerate the super duper epics
for i in range(len(superEpicListUnique)):
    df.loc[df['Name']==superEpicListUnique[i],['Issue ID']]=int((i+1)*10)    
###############################################################################################################


###############################EpicArray check and ennumeration###########################################
epicArray=df[df['Issue Type']=="Epic"] 
epicArray=epicArray.sort_values(by=['Name'])
epicListUnique=epicArray['Name'].unique()
epicList=epicArray['Name']
print ("********************************************")
print ("Checking list for epics...")
if len(epicList) == len(epicListUnique):
    print ("You're on the clear, no double registries in the normal part ;)")
else:
    #for element in superDuperEpicList:
    #    if element not in superDuperEpicListUnique:
    #        superDuperEpicDifference.append(element)
    print ("There is something wrong with your file please change one of the following tasks and reexport")
    print ("You need to rename the following task(s):")
    duplicateEpics=[]
    comparisonList=[]
    for i in epicList:
        if i not in comparisonList:
            comparisonList.append(i)
        else:
            duplicateEpics.append(i)
            #print(i,end=' ')    
    #exit()****************INCLUDE ONCE THAT THE CODE HAS BEEN TESTED IN JUPYTER
    for i in duplicateEpics:
        print (i)

#once that the check has been done we can continue to ennumerate the super duper epics
for i in range(len(epicListUnique)):
    df.loc[df['Name']==epicListUnique[i],['Issue ID']]=int((i+1)*100)    
#Check is now done, demoting can now happen 
###############################################################################################################


###############################Task ennumeration###########################################
taskArray=df[df['Issue Type']=="Task"].sort_values(by=['Name'])  
########## FOR SWEEPING THROUGH TASKS USING TASK ID AND ENNUMERATING ACCORDINGLY########################
taskIDs=taskArray["Task ID"].tolist()
for i in range(len(taskIDs)):
    df.loc[df['Task ID']==taskIDs[i],['Issue ID']]=int((i+1)+((len(epicListUnique)*100)+100))
########################################################################################################


########## FOR SWEEPING THROUGH TASKS USING TASK NAME AND ENNUMERATING ACCORDINGLY######################
taskList=taskArray["Name"].tolist()
#for i in range(len(taskList)):
#    df.loc[df['Name']==taskList[i],['Issue ID']]=int((i+1)+((len(epicListUnique)*100)+100))
########################################################################################################
print ("********************************************")
#REMOVED SINCE DUPLICATE TASKS ARE A NORMAL THING!!!!
#print ("Checking list for tasks...")
#comparisonList=[]
#duplicateTasks=[]
#for i in taskList:
#    if i not in comparisonList:
#        comparisonList.append(i)
#    else:
#        duplicateTasks.append(i)
#if len(taskList) == len(set(taskList)):
#    print ("You're on the clear, no double registries in the normal part ;)")
#else:
#   print ("There is something wrong with your file please change one of the following tasks and reexport")
#    print ("You need to rename the following task(s):")
#    for i in duplicateTasks:
#        print (i)
###############################################################################################################

###########################Demoting Super Epics to Epics, tasks to subtasks####################################
#using the list of (unique) super epics to assign the values of the
print ("********************************************")
print ("********************************************")
print ("********************************************")
print ("********************************************")
print("Restructuring to Jira format...")
for i in range(len(superEpicListUnique)):
    #print('*******SUPER EPIC********')
    #print(superEpicListUnique[i])
    epicIssueID=str(df.loc[df['Name'] == superEpicListUnique[i], 'Issue ID'].values[0]) # stores the epicIssueID for assigning it to demoted epics
    #print("The value of the epic issue ID is: " +epicIssueID )
    linkedTickets=df[df['Epic Link']==superEpicListUnique[i]] 
    linkedEpicsList=linkedTickets.loc[linkedTickets['Issue Type'] == 'Epic']['Name'].unique()
    #print('*********************EPIC********')
    for j in range(len(linkedEpicsList)):
        #print("Linked (Sub)Epics are " + str(len(linkedEpicsList)) + " in total and are: ")
        #print (linkedEpicsList[j])
        #print("Linked (Sub)Epics are: " + linkedEpicsList)
        taskIssueID=str(df.loc[df['Name'] == linkedEpicsList[j], 'Issue ID'].values[0]) # stores the taskIssueID for assigning it to demoted epics
        #print("The value of the (sub)epic issue ID is: " +taskIssueID )
        ######For demoting tasks to subtasks#######
        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!Linked Tasks are:!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for k in range(len(linkedEpicsList)):
            linkedTasks=df[df['Epic Link']==linkedEpicsList[k]]
            linkedTasksList=linkedTasks["Name"].tolist()
            for l in linkedTasksList:
                #print (l)
                #DONE!! We're browsing through the entire file
                #Going from down to up
                #Changing task  to subtask
                df.loc[df['Name']==(l),['Parent ID']]=taskIssueID #updated parent ID from now subtask with taskIssueID
                df.loc[df['Name']==(l),['Epic Link']]='' #updated epic link to empty
                df.loc[df['Name']==(l),['Issue Type']]='Sub-task' #updated epic link to empty
                #Done with subtask
            #Changing epic to task
            df.loc[df['Name']==(linkedEpicsList[k]),['Epic Link']]=superEpicListUnique[i] #updated epic link from now epic with epic link
            df.loc[df['Name']==(linkedEpicsList[k]),['Epic Name']]='' #updated epic name to empty
            df.loc[df['Name']==(linkedEpicsList[k]),['Issue Type']]='Task' #updated epic link to empty  
            #Done with epic
        #Demoting Super epic to epic
        df.loc[df['Name']==(superEpicListUnique[i]),['Issue Type']]='Epic' #updated epic link to empty  
        

        ###############################################################################################################

#Cleaning up super links to super epics

print("the list of super epics is the following: ")
try:
    for item in superDuperEpicList:
        print(item)
    tasksLinkedToSuperEpics=df[df['Epic Link']==item].sort_values(by=['Name'])
    tasksLinkedToSuperEpics=tasksLinkedToSuperEpics[tasksLinkedToSuperEpics['Issue Type']=="Task"].sort_values(by=['Name'])    
    tasksLinkedToSuperEpics=tasksLinkedToSuperEpics['Name'].tolist()
    print("The tasks linked to super epics are the following:")
    print(tasksLinkedToSuperEpics) 
except:
    print("no super duper epics")
###############################################################################################################
###Epic Confidence Check
epicLinkList=df['Epic Link'].unique().tolist()
#epicLinkList=epicLinkList+(superDuperEpicListUnique.tolist())
#print(epicLinkList)
df=df.sort_values(by=['Name'], ascending = [True])
epicNames=df['Name'].unique().tolist()
#epicNames.sort()


print("******************************************")
print('Reviewing Epic / Task Structure...')    
comparisonList=[]
missingEpics=[]
for i in epicLinkList:
    
    if i not in epicNames:
        missingEpics.append(i)
#        print(i)
#        print("not found")
    else:
        comparisonList.append(i)
        #print("found")
print('Done')
        
if len(missingEpics)> 0:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!ATTENTION!!! The following epics are linked but don't exist!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    for i in missingEpics:
        print(i)
###############################################################################################################
try:#in case there are subtasks
    df=df.sort_values(by=['Epic Name','Epic Link','Parent ID'], ascending = [False, False, False])
except:#in case there are no subtasks
    df=df.sort_values(by=['Epic Name','Epic Link'], ascending = [False, False])
os.chdir(full_path)
df.to_csv (file_location) #Saves sorted database to CSV file with all epics
