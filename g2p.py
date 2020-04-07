
# coding: utf-8
import subprocess
import re
import sys
from langid import classify

language = {}
transcription = {}
token_list = {}
token_transcription = {}
mapped_dict = {}
g2pde = "/mnt/exchange/ASR Management/G2P/g2p-eand-de-DE-0.119.0/bin/de-DE"
g2pen = "/mnt/exchange/ASR Management/G2P/g2p-eand-de-DE-0.119.0/bin/en-US"
map_file = "/mnt/exchange/ASR Management/spotify_pipeline/3_language mapping/en-US~de-De.tsv"
input_file = str(sys.argv[1])
#"/mnt/exchange/ASR Management/G2P/Spotify_Artists_top1000/sort_lang/sort_lang_popularity/sort_lang_merged/var_artists_spotify_Top5000_pop.tsv"

with open(map_file, 'r', encoding="utf-8") as f:
	map_dict={}
	for line in f:
		x = re.split(r"\t",line)
		map_dict[x[0].strip()] = x[1].strip()

def lang_map(string):
	phones = string.split()
	mapped = []
	for phone in phones:
		if phone in map_dict:
			mapped.append(map_dict[phone])
		else:
			mapped.append(phone)
	sep = " "
	mapped_string = sep.join(mapped)
	return mapped_string


with open(input_file, 'r', encoding="utf-8") as f:
	for entry in f:
		entry = entry.strip()
		# classify language
		language[entry] = classify(entry)[0]

		# run respective g2p for entries and tokens
		byte_entry = entry.encode()
		if language[entry] == 'en':
			g2p = g2pen 
		else:
			g2p = g2pde
		g2p_strings = subprocess.Popen([f'{g2p}/g2p-full', "-u", "-mp", "-pb"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		g2p_tokens = subprocess.Popen([f'{g2p}/g2p-full', "-u", "-mp", "-pb", "-pd"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		strings = g2p_strings.communicate(byte_entry)[0].decode().strip()
		tokens = g2p_tokens.communicate(byte_entry)[0].decode().strip()

		# dict with entry : transcription_list
		transcription[entry] = []
		mapped_dict[entry] = []
		for string in re.split(r'\t',strings):
			transcription[entry].append(string)
			if lang_map(string) not in transcription[entry]:
				if lang_map(string) not in mapped_dict[entry]:
					mapped_dict[entry].append(lang_map(string))

		token_list[entry] = []
		for token in re.split(r'\n',tokens):
			try:
				a = re.split(r"\t",token)
				word,pron=a[0].strip(),a[1].strip()
			except IndexError:
				word = token
				pron = "NA"
			word = re.sub('^#','',word)

			# dict with entry : token_list
			if word not in token_list[entry]:
				token_list[entry].append(word)
				token_transcription[word] = []
			# dict with token : transcription_list
			if pron not in token_transcription[word]:
				token_transcription[word].append(pron)

# output
for unit in transcription:
	# entry , language
	print(unit, language[unit])
	# transcriptions
	print(transcription[unit])
	#transcriptions per token of the entry
	for item in token_list[unit]:
		print(item, token_transcription[item])
	# mapped transcriptions
	print(mapped_dict[unit])
	print()
