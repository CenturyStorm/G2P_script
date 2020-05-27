# coding: utf-8

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

def import_data(exchange_path):

    # define paths
    basepath = os.path.join(exchange_path, 'ASR Management/netflix/')
    jsonpath = os.path.join(basepath, 'script_folder/json/')
    
    # find latest zip file
    # WARNING: ONLY WORKS FOR 2020 FOR NOW. For multiple year script needs to be extended
    # try to unzip latest file, if that doesn't work look for folder of the same name and copy the de-DE file
    try:
        for file in os.listdir(basepath):
            if file.endswith("_2020.zip"):
                netflix_zipfile = file

        # extract zipfile to json folder
        with zp.ZipFile(basepath + netflix_zipfile, 'r') as f:
            f.extract('de-DE.json', path = jsonpath)
    except:
        netflix_folder= netflix_zipfile.replace(".zip","/")
        copyfile(basepath + netflix_folder + 'de-DE.json', jsonpath + 'de-DE.json')
    
    # take filename from zipfile
    netflix_zipfile_no_ext = re.split('\.', netflix_zipfile)[0]
    
    #remove existing named file if it exists
    if os.path.isfile(jsonpath + netflix_zipfile_no_ext + '_de-DE.json'):
        os.remove(jsonpath + netflix_zipfile_no_ext + '_de-DE.json')
    
    # rename file from de-DE.json to Netflix EU-KR Data_MM_DD_YYYY_de-DE.json
    os.rename(jsonpath + 'de-DE.json',jsonpath + netflix_zipfile_no_ext + '_de-DE.json')

    # read the file
    json_file = jsonpath + netflix_zipfile_no_ext + '_de-DE.json'

    data = pd.read_json(json_file)
    
    print("data imported")
    
    return data, basepath


def clean_data(data):
    
    # select data that we need
    data = data.loc[:,['title','type']]

    # make everythings lowercase. DISABLED
    #data.loc[:,'title'] = data['title'].str.lower()
    #data.loc[:,'type'] = data['type'].str.lower()

    # set both columns to type string
    data = data.astype("string")

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

    # remove double title entries
    data.loc[:,'title'] = data['title'].drop_duplicates()

    # delete empty lines and reindex
    data = data[data.loc[:,'title'] != '']
    data.index = range(0, len(data))

    # limit data to n_limit entries
    #if N_MIN and N_MAX != None:
    data = data[N_MIN:N_MAX]
    data.index = range(0, len(data))

    print("data cleaned")
    
    return data


def language_id(data):
    langids = []

    for title in data['title']:
        langid = classify(title)[0]
        if langid != 'de':
            langid = 'en'
        langids.append(langid)

    data['language_id'] = langids

    print("language identified")

    return data


def sideloading_data(basepath, data):

    # load side data
    rep_path = basepath + 'script_folder/sideload/replace.tsv'
    del_path = basepath + 'script_folder/sideload/delete.tsv'

    rep_data = pd.read_csv(rep_path, sep = '\t', header = None, skiprows = 1, names = data.columns)
    del_data = pd.read_csv(del_path, sep = '\t', header = None, skiprows = 1)

    # overwrite entries if matched on the same title
    data = data.append(rep_data)
    data = data.drop_duplicates(subset = 'title', keep = 'last')
    data.index = range(0, len(data))

    # delete entries read from del_data
    del_data_array = list(del_data.values.squeeze().tolist())
    data = data[~data['title'].isin(del_data_array)]
    data.index = range(0, len(data))

    print("sideloaded data")

    return data


def tempdump_data(basepath, data):
    
    # export the data temporarily (optional)
    titles_path = os.path.join(basepath, "script_folder/output/titles.tsv")
    data.to_csv(path_or_buf = titles_path, index = False, sep = '\t')
    
    print("data exported to {}".format(titles_path))


def read_g2p(exchange_path, data, basepath):

    titles_path = os.path.join(basepath, "script_folder/output/titles.tsv")
    g2p_path = os.path.join(basepath, "script_folder/output/g2p.tsv")

    subprocess.call("./build.sh")

    print("starting g2p generation")

    runsh = ["./run.sh", "-e", exchange_path, "-t", titles_path, "-g", g2p_path]
    subprocess.call(runsh)

    print("g2p succesfully generated")

    # read in g2p data and split into separate columns, named g2p_1 until g2p_{MAX_G2P + 1}
    g2p_data = pd.read_csv(g2p_path)
    g2p_data = g2p_data['transcriptions'].str.split('\t', expand=True)
    g2p_data.columns = ['g2p_{}'.format(i) for i in range(1, g2p_data.shape[1] + 1)]

    # cut off dataframe after max number of g2p transcriptions
    g2p_data = g2p_data.iloc[:,:MAX_G2P]

    # merge g2p data together with original data
    data = pd.concat([data, g2p_data], axis = 1)

    print("g2p read in and appended to original dataframe")

    return data


def map_language(data):

    mapfile = 'en-US~de-De.tsv'
    
    mapfile_data = pd.read_csv(mapfile, sep = '\t', header = None, names = ['en-US','de-DE'])

    # remove lines that are the same
    mapfile_data = mapfile_data[mapfile_data['en-US'] != mapfile_data['de-DE']]

    # add extra whitespaces/tabs/beginning/end for regex replacement
    mapfile_data['en-US'] = '(^|\t| )' + mapfile_data['en-US'] + '( |\t|$)'
    mapfile_data['de-DE'] = '\\1' + mapfile_data['de-DE'] + '\\2'

    print(mapfile_data['en-US'].tolist(), len(mapfile_data['en-US'].tolist()))
    print(mapfile_data['de-DE'].tolist(), len(mapfile_data['de-DE'].tolist()))

    # map language in g2p output
    data.loc[:,'g2p_1':] = data.loc[:,'g2p_1':].replace(mapfile_data['en-US'].tolist(),
                                                        mapfile_data['de-DE'].tolist(), 
                                                        regex = True)

    # map language in g2p output
    #data.loc[:,'g2p_1':] = data.loc[:,'g2p_1':].replace(['ao', 'dh'],
    #                                                    ['oo', 'd'], 
    #                                                    regex = True)

    return data


def export_data(data):
    titles_path = os.path.join(basepath, "script_folder/output/titles.tsv")
    data.to_csv(path_or_buf = titles_path, index = False, sep = '\t')
    
    print("data exported to {}".format(titles_path))


if __name__ == "__main__":
    
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('--exchange', '-e', required=False, default='/mnt/exchange/', help='Path to exchange.Default: /mnt/exchange/')
    args = parser.parse_args()
    
    # import data
    data, basepath = import_data(args.exchange)
    
    # clean data
    data = clean_data(data)

    # determine language of title
    data = language_id(data)

    # add or remove entries
    data = sideloading_data(basepath, data)

    # optional exporting to textfile
    tempdump_data(basepath, data)

    # run g2p
    data = read_g2p(args.exchange, data, basepath)

    # map g2p from en-US to de-DE
    data = map_language(data)

    export_data(data)