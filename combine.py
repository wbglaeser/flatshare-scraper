#-------------------------------------
# Import Modules
#-------------------------------------
import pandas as pd
import os

def main_func():
    #-------------------------------------
    # Import Files
    #-------------------------------------
    # WOHNUNGEN
    dsets = []
    data_dir = '/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/individual_scrape'
    for dset in os.listdir(data_dir):
        if 'csv' in dset:
            df = pd.read_csv('/'.join([data_dir,dset]), encoding='latin-1')
            dsets.append(df)

    df_full = pd.concat(dsets, ignore_index=True)
    df_full = df_full.drop_duplicates(subset=['ID'], keep='last')
    df_full = df_full.reset_index()

    #IDS
    ids = []
    with open('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/property_ids_full.txt','r') as f:
       for id in f.readlines():
           ids.append(int(id.strip('\n')))

    #-------------------------------------
    # Delete Disappeared Flats
    #-------------------------------------
    to_delete = []
    for index, id in enumerate(df_full['ID']):
        if id not in ids:
            to_delete.append(index)
    df_full = df_full.drop(df_full.index[to_delete])
    df_full = df_full.reset_index()

    # Delete some superfluous columns
    df_full = df_full.drop(['level_0','index'], axis=1)

    #-------------------------------------
    # Save to Excel
    #-------------------------------------
    writer = pd.ExcelWriter('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/properties_full.xlsx')
    df_full.to_excel(writer,'Sheet1', index=False)
    writer.save()

    df_full.to_csv('/home/ubuntu/dataANDtoolbox/scrape-wgs/dataset/properties_full.csv', sep=',')
    print('Files successfully combined and saved')
