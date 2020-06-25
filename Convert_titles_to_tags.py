# coding: utf-8
#######################
#
# This script uses the file generated from Netflix_import_clean.py to create tags
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


def import_data_tsv(source_path):

	# read in data
	data = pd.read_csv(source_path, sep = '\t')

	print("data imported")

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

	print("tags created")

	return data


def export_data(output_path, data):

	# add de-DE at top of file
	data_de = pd.DataFrame(['de-DE'])
	data_de.to_csv(path_or_buf = output_path, index = False, header = None)

	# export data to already existing g2p_output_path file
	data.to_csv(path_or_buf = output_path, mode = 'a', index = False, sep = '\t', header = None)

	print("data exported to {}".format(output_path))


if __name__ == "__main__":
    
    #define paths
    sourcepath = 'script_folder/output/netflix_titles_g2p.tsv'
    outputpath = 'script_folder/output/netflix_titles_g2p_tags.tsv'

    data = import_data_tsv(sourcepath)

    data = modify_data(data)

    export_data(outputpath, data)