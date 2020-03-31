
# coding: utf-8

# In[329]:

import json
import zipfile as zp
import pandas as pd
import os
import re


# In[330]:

def import_data():

    # define paths
    basepath = 'B:\\Exchange\\ASR Management\\netflix\\'
    jsonpath = basepath + 'script_folder\\json\\'

    # find latest zip file
    # WARNING: ONLY WORKS FOR 2020 FOR NOW. For multiple year script needs tobe extended
    for file in os.listdir(basepath):
        if file.endswith("_2020.zip"):
            netflix_zipfile = file

    # extract zipfile to json folder
    with zp.ZipFile(basepath + netflix_zipfile, 'r') as f:
        f.extract('de-DE.json', path = jsonpath)

    # rename the file
    
    # take filename from zipfile
    netflix_zipfile_no_ext = re.split('\.', netflix_zipfile)[0]
    
    #remove existing file if it exists
    if os.path.isfile(jsonpath + netflix_zipfile_no_ext + '_de-DE.json'):
        os.remove(jsonpath + netflix_zipfile_no_ext + '_de-DE.json')
    
    os.rename(jsonpath + 'de-DE.json',jsonpath + netflix_zipfile_no_ext + '_de-DE.json')

    # read the file
    json_file = jsonpath + netflix_zipfile_no_ext + '_de-DE.json'

    data = pd.read_json(json_file)
    
    print("data imported")
    
    return data, basepath


# In[331]:

def clean_data(data):
    
    # select data that we need
    data = data.loc[:,['title','type']]

    # make everythings lowercase
    data.loc[:,'title'] = data['title'].str.lower()
    data.loc[:,'type'] = data['type'].str.lower()

    ### execute part of Vijay's script
    # replace all types of hyphens with -
    hyphens_unicode = '[\u002D\u058A\u05BE\u1400\u1806\u2010-\u2015\u2E17\u2E1A\u2E3A\u2E3B\u2E40\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D]'
    data.loc[:,'title'] = data['title'].str.replace(hyphens_unicode, '-')

    # remove lines with not allowed characters (these are fully unusable titles with full chinese characters or cyrillic alphabet)
    not_allowed_chars = '[^A-Za-z0-9äöüÄÖÜßé\’\„\“\«\»\“\”\'\´\"\.\?\!\:\;\,\ \t\n\@\%\&\!\$\€\£\§\°\#\|\>\<\\\/\^\~\(\)\{\}\+\*\=(&amp)\_\–\—\-\—\–\-]'
    data.loc[:,'title'] = data['title'][~data['title'].str.match(not_allowed_chars)]

    # remove the following punctuation characters from titles
    not_allowed_punc = '[\÷\×\°\µ\­\,\:\.\!\?\…\/\~\·\»\(\)\§\©\®\¥\¹\²\þ\Þ\´\¨\¦\¸\‘\’\"\”\¤]'
    data.loc[:,'title'] = data['title'].str.replace(not_allowed_punc, '')

    # remove hyphens which are not directly in between words or before a number(text-to-speech, -10)
    not_allowed_hyphens = '-(?=[\s\-—–])|(?<=[\s\-—–])-(?=[^0-9])|—(?=[\s\-—–])|(?<=[\s\-—–])—(?=[^0-9])|–(?=[\s\-—–])|(?<=[\s\-—–])–(?=[^0-9])'
    data.loc[:,'title'] = data['title'].str.replace(not_allowed_hyphens, '')

    # remove extra spacing
    data.loc[:,'title'] = data['title'].str.replace(' {2,}', ' ')
    data.loc[:,'title'] = data['title'].str.strip()

    # delete empty lines
    data = data[data.loc[:,'title'] != '']
    
    print("data cleaned")
    
    return data


# In[332]:

def export_data(basepath, data):
    
    # export the data temporarily (optional)
    data.to_csv(path_or_buf = basepath + 'script_folder\\output\\titles.txt', index = False, header = False, sep = '\t')
    
    print("data exported to {}".format(basepath + 'script_folder\\output\\titles.txt'))


# In[333]:

if __name__ == "__main__":
    
    # import data
    data, basepath = import_data()
    
    # clean data
    data = clean_data(data)
    
    # optional exporting to textfile
    export_data(basepath, data)


# In[ ]:



