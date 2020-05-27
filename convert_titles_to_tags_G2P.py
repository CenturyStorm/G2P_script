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

# define paths globally


def import_data(exchange_path):

	# define import path
	basepath = os.path.join(exchange_path, 'ASR Management/netflix/')
	titles_path = os.path.join(basepath, "script_folder/output/titles.tsv")

	# read in data
	data = pd.read_csv(titles_path, sep = '\t')

	return data


def modify_data(data):

	# select only the first g2p entry
	data = data[['title', 'type', 'language_id', 'g2p_1']]

	# remove entries with de language
	data = data[data['language_id'] != 'de']


	data.loc[:,'title'] = data['title'].str.replace(' ',';')
	data.loc[:,'language_id'] = data['language_id'].str.replace('en','enUS')

	# update the type tag with all uppercase and replace show and movie with TVSHOWS
	data.loc[:,'type'] = data['type'].str.upper()
	data.loc[:,'type'] = data['type'].str.replace('SHOW','TVSHOWS')
	data.loc[:,'type'] = data['type'].str.replace('MOVIE','TVSHOWS')


	# construct the tags from 
	tags = data['title'] + '_' + data['language_id'] + '_' + data['type']

	data['g2p_tag'] = tags

	data = data[['g2p_tag', 'g2p_1']]

	return data



def export_data(exchange_path, data):

	# define output path
	basepath = os.path.join(exchange_path, 'ASR Management/netflix/')
	
	g2p_output_path = os.path.join(basepath, "script_folder/output/g2p_output.tsv")

	# add de-DE at top of file
	data_de = pd.DataFrame(['de-DE'])
	data_de.to_csv(path_or_buf = g2p_output_path, index = False, header = None)

	# export data to already existing g2p_output_path file
	data.to_csv(path_or_buf = g2p_output_path, mode = 'a', index = False, sep = '\t', header = None)



if __name__ == "__main__":
    
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('--exchange', '-e', required=False, default='/mnt/exchange/', help='Path to exchange.Default: /mnt/exchange/')
    args = parser.parse_args()

    data = import_data(args.exchange)

    data = modify_data(data)

    export_data(args.exchange, data)