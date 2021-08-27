# Miguel Reyes,
import sys
import pandas as pd
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages')

#We read the export file from Asana
df= pd.read_csv("AsanaExport.csv",error_bad_lines=True)

df['Notes']=df['Notes'].astype('str') #sets all information in the notes column as string
df['Epic Link']=df['Parent Task'] #Epic link is the name of the parent task

#finding unique epic names for working with them later to create jira csv structure
epicNames=df['Epic Link'].unique()

df['Issue Type']='Task' #Sets all tasks firsly to the task issue type
#Getting number of elements in the epicNames list
lengthEpicNames = len (epicNames)

#Iterating using the length of the list
for i in range(lengthEpicNames):
    df.loc[df['Name']==epicNames[i],['Issue Type']]='Epic' #updates the issue type to epic when epic name matches the ecpicName list

df['Epic Name']='' #creates the epic name column in the df so that the program is able to add the name in the next command
df.loc[df['Issue Type']=='Epic',['Epic Name']]=df['Name'] #includes the name of the epic when the task has been flagged as epic

try:
    df['Assignee Email']=df['Assignee Email'].str.lower() #changes the email address to lower case as normally jira has them in lower case.
except:
    print("No assignee field was found for your tasks, are you sure you have the correct export file?")
    
sorted=df.sort_values(by=['Issue Type']) #Sorts dataframe to first show epics for stories/subtasks to be created AFTER the epics

sorted.to_csv ('../import_to_jira.csv') #Saves sorted database to CSV file with all epics

