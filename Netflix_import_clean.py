# coding: utf-8
#######################
#
# This script creates phonetic transcriptions from titles in english and german
#
# (c) Lars Tijssen
#
########################

import json
import zipfile as zp
import pandas as pd
import os
import re
import subprocess
from langid import classify
from shutil import copyfile
from argparse import ArgumentParser


# limit number of output lines to curb computation time
N_MIN, N_MAX = None,None

#  constant defining the maximum number of g2p transcriptions per title
MAX_G2P = 10

def import_data_tsv(source_path):

    df = pd.read_csv(sourcepath, sep = '\t')

    if df.shape[1] == 1:
        df.columns = ['title']
    elif df.shape[1] == 2:
        df.columns = ['title', 'type']
    else:
        print('Unsupported df size. Please make sure the dimensions are correct (should be 1 or 2 columns)')
    
    print("data imported")
    
    return df

def clean_data(df):

    # if type does not exist create placeholder
    if 'type' not in df:
        df['type'] = ['SHOW']*len(df)
    
    # select df that we need
    df = df.loc[:,['title','type']]

    # make everythings lowercase. DISABLED
    #df.loc[:,'title'] = df['title'].str.lower()
    #df.loc[:,'type'] = df['type'].str.lower()

    # set both columns to type string
    df = df.astype("string")

    ### execute part of Vijay's script
    # replace all types of hyphens with -
    hyphens_unicode = '[\u002D\u058A\u05BE\u1400\u1806\u2010-\u2015\u2E17\u2E1A\u2E3A\u2E3B\u2E40\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D]'
    df.loc[:,'title'] = df['title'].str.replace(hyphens_unicode, '-')

    # remove lines with not allowed characters (these are fully unusable titles with full chinese characters or cyrillic alphabet)
    not_allowed_chars = '[^A-Za-z0-9äöüÄÖÜßé\’\„\“\«\»\“\”\'\´\"\.\?\!\:\;\,\ \t\n\@\%\&\!\$\€\£\§\°\#\|\>\<\\\/\^\~\(\)\{\}\+\*\=(&amp)\_\–\—\-\—\–\-]'
    df.loc[:,'title'] = df['title'][~df['title'].str.match(not_allowed_chars)]

    # remove the following punctuation characters from titles
    not_allowed_punc = '[\÷\×\°\µ\­\,\:\.\!\?\…\/\~\·\»\(\)\§\©\®\¥\¹\²\þ\Þ\´\¨\¦\¸\‘\’\"\”\¤]'
    df.loc[:,'title'] = df['title'].str.replace(not_allowed_punc, '')

    # remove hyphens which are not directly in between words or before a number(text-to-speech, -10)
    not_allowed_hyphens = '-(?=[\s\-—–])|(?<=[\s\-—–])-(?=[^0-9])|—(?=[\s\-—–])|(?<=[\s\-—–])—(?=[^0-9])|–(?=[\s\-—–])|(?<=[\s\-—–])–(?=[^0-9])'
    df.loc[:,'title'] = df['title'].str.replace(not_allowed_hyphens, '')

    # remove extra spacing
    df.loc[:,'title'] = df['title'].str.replace(' {2,}', ' ')
    df.loc[:,'title'] = df['title'].str.strip()

    # remove double title entries
    df.loc[:,'title'] = df['title'].drop_duplicates()

    # delete empty lines and reindex
    df = df[df.loc[:,'title'] != '']
    df.index = range(0, len(df))

    # limit df to n_limit entries
    #if N_MIN and N_MAX != None:
    df = df[N_MIN:N_MAX]
    df.index = range(0, len(df))

    print("data cleaned")
    
    return df


def language_id(df):
    langids = []

    for title in df['title']:
        langid = classify(title)[0]
        if langid != 'de':
            langid = 'en'
        langids.append(langid)

    df['language_id'] = langids

    print("language identified")

    return df


def sideloading_data(replace_path, delete_path, df):

    rep_df = pd.read_csv(replace_path, sep = '\t', header = None, skiprows = 1, names = df.columns)
    del_df = pd.read_csv(delete_path, sep = '\t', header = None, skiprows = 1)

    # overwrite entries if matched on the same title
    df = df.append(rep_df)
    df = df.drop_duplicates(subset = 'title', keep = 'last')
    df.index = range(0, len(df))

    # delete entries read from del_df
    del_df_array = list(del_df.values.squeeze().tolist())
    df = df[~df['title'].isin(del_df_array)]
    df.index = range(0, len(df))

    print("sideloaded data")

    return df


def tempdump_data(titles_path, df):
    
    # export the df temporarily (optional)
    df.to_csv(path_or_buf = titles_path, index = False, sep = '\t')
    
    print("data exported to {}".format(titles_path))


def read_g2p(g2p_path, df):

    subprocess.call("./build.sh")

    print("starting g2p generation")

    #runsh = ["./run.sh", "-e", exchange_path, "-t", titles_path, "-g", g2p_path]
    runsh = ["./run.sh", "-t", "/output/netflix_titles_g2p.tsv", "-g", "/output/g2p.tsv"]
    subprocess.call(runsh)

    print("g2p succesfully generated")

    # read in g2p df and split into separate columns, named g2p_1 until g2p_{MAX_G2P + 1}
    g2p_df = pd.read_csv(g2p_path)
    g2p_df = g2p_df['transcriptions'].str.split('\t', expand=True)
    g2p_df.columns = ['g2p_{}'.format(i) for i in range(1, g2p_df.shape[1] + 1)]

    # cut off dfframe after max number of g2p transcriptions
    g2p_df = g2p_df.iloc[:,:MAX_G2P]

    # merge g2p df together with original df
    df = pd.concat([df, g2p_df], axis = 1)

    print("g2p read in and appended to original dataframe")

    return df


def map_language(df):

    mapfile = 'en-US~de-De.tsv'
    
    mapfile_df = pd.read_csv(mapfile, sep = '\t', header = None, names = ['en-US','de-DE'])

    # remove lines that are the same
    mapfile_df = mapfile_df[mapfile_df['en-US'] != mapfile_df['de-DE']]

    # add extra whitespaces/tabs/beginning/end for regex replacement
    mapfile_df['en-US'] = '(^|\t| )' + mapfile_df['en-US'] + '( |\t|$)'
    mapfile_df['de-DE'] = '\\1' + mapfile_df['de-DE'] + '\\2'

    # map language in g2p output
    df.loc[:,'g2p_1':] = df.loc[:,'g2p_1':].replace(mapfile_df['en-US'].tolist(),
                                                        mapfile_df['de-DE'].tolist(), 
                                                        regex = True)

    return df


def export_data(titles_path, df):

    df.to_csv(path_or_buf = titles_path, index = False, sep = '\t')
    
    print("data exported to {}".format(titles_path))


if __name__ == "__main__":
    
    # define paths
    sourcepath = 'source_files/output/netflix_titles.tsv'
    titlespath = 'source_files/output/netflix_titles_g2p.tsv'
    g2ppath = 'source_files/output/g2p.tsv'

    replacepath = 'source_files/sideload/replace.tsv'
    deletepath = 'source_files/sideload/delete.tsv'

    # import data
    data = import_data_tsv(sourcepath)
    
    # clean data
    data = clean_data(data)

    # determine language of title
    data = language_id(data)

    # add or remove entries
    data = sideloading_data(replacepath, deletepath, data)

    # optional exporting to textfile
    tempdump_data(titlespath, data)

    # run g2p
    data = read_g2p(g2ppath, data)

    # map g2p from en-US to de-DE
    data = map_language(data)

    export_data(titlespath, data)





    ##################################################################################### LEGACY CODE BELOW

    #def import_data_json(exchange_path):#

#    # define paths
#    basepath = os.path.join(exchange_path, 'ASR Management/netflix/')
#    jsonpath = os.path.join(basepath, 'source_files/json/')
#    
#    # find latest zip file
#    # WARNING: ONLY WORKS FOR 2020 FOR NOW. For multiple year script needs to be extended
#    # try to unzip latest file, if that doesn't work look for folder of the same name and copy the de-DE file
#    try:
#        for file in os.listdir(basepath):
#            if file.endswith("_2020.zip"):
#                netflix_zipfile = file#

#        # extract zipfile to json folder
#        with zp.ZipFile(basepath + netflix_zipfile, 'r') as f:
#            f.extract('de-DE.json', path = jsonpath)
#    except:
#        netflix_folder= netflix_zipfile.replace(".zip","/")
#        copyfile(basepath + netflix_folder + 'de-DE.json', jsonpath + 'de-DE.json')
#    
#    # take filename from zipfile
#    netflix_zipfile_no_ext = re.split('\.', netflix_zipfile)[0]
#    
#    #remove existing named file if it exists
#    if os.path.isfile(jsonpath + netflix_zipfile_no_ext + '_de-DE.json'):
#        os.remove(jsonpath + netflix_zipfile_no_ext + '_de-DE.json')
#    
#    # rename file from de-DE.json to Netflix EU-KR Data_MM_DD_YYYY_de-DE.json
#    os.rename(jsonpath + 'de-DE.json',jsonpath + netflix_zipfile_no_ext + '_de-DE.json')#

#    # read the file
#    json_file = jsonpath + netflix_zipfile_no_ext + '_de-DE.json'#

#    data = pd.read_json(json_file)
#    
#    print("data imported")
#    
#    return data, basepath