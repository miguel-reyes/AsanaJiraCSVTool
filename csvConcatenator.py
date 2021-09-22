import os
import glob
import pandas as pd
import sys
from numpy import nan
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages')

file_name = os.path.splitext(os.path.basename(os.path.realpath(__file__)))[0]

export_path =  os.path.join(os.path.dirname(os.path.realpath(__file__)),"Asana Export")

mid_path =  os.path.join(os.path.dirname(os.path.realpath(__file__)),"Place your CSV Files Here")


full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Import to Jira")

if not os.path.exists(full_path):
    os.mkdir(full_path)

    if not os.path.exists(os.path.join(full_path, file_name)):
        os.mkdir(full_path)

file_location = os.path.join(full_path, file_name, 'import_to_jira.csv')


#print(mid_path)

if not os.path.exists(mid_path):
    os.mkdir(mid_path)
    print("No CSV folder was found")
else:
    os.chdir(mid_path)
    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

if len(all_filenames)>1:
    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
    #export to csv
    if not os.path.exists(export_path):
        os.mkdir(export_path)
        os.chdir(export_path)
        combined_csv.to_csv( "AsanaExport.csv", index=False, encoding='utf-8-sig')
    else:
        os.chdir(export_path)
        combined_csv.to_csv( "AsanaExport.csv", index=False, encoding='utf-8-sig')
else:
    print("There are no files in the folder, please try again.")
