import subprocess
import re
import sys
from langid import classify
import pandas as pd

print("python version = " + sys.version)

transcriptions = []
g2pde = "/g2p-eand-de-DE-0.119.0/bin/de-DE"
g2pen = "/g2p-eand-de-DE-0.119.0/bin/en-US"
map_file = "/home/en-US~de-De.tsv"
output_file = str(sys.argv[2])
input_file = str(sys.argv[1])

data = pd.read_csv(input_file, sep = '\t')
for index, row in data.iterrows():
	
	lang = row['language_id']
	title = row['title'].strip().encode()

	if lang == 'en':
		g2p = g2pen
	else:
		g2p = g2pde

	g2p_strings = subprocess.Popen(['.' + g2p + '/g2p-full', "-u", "-mp", "-pb"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	strings = g2p_strings.communicate(title)[0].decode().strip()
	transcriptions.append(strings)

data_transcriptions = pd.DataFrame(transcriptions, columns = ['transcriptions'])
data_transcriptions.to_csv(path_or_buf = output_file, index = False, sep = '\t')


################################################################################################################ LEGACY CODE

#token_list = {}
#token_transcription = {}
#mapped_dict = {}

#"/mnt/exchange/ASR Management/G2P/Spotify_Artists_top1000/sort_lang/sort_lang_popularity/sort_lang_merged/var_artists_spotify_Top5000_pop.tsv"

#with open(map_file, 'r', encoding="utf-8") as f:
#	map_dict={}
#	for line in f:
#		x = re.split(r"\t",line)
#		map_dict[x[0].strip()] = x[1].strip()

#def lang_map(string):
#	phones = string.split()
#	mapped = []
#	for phone in phones:
#		if phone in map_dict:
#			mapped.append(map_dict[phone])
#		else:
#			mapped.append(phone)
#	sep = " "
#	mapped_string = sep.join(mapped)
#	return mapped_string





#with open(input_file, 'r', encoding="utf-8") as f:
#	for entry in f:
#		#print(entry)
#		#entry = entry.strip()
#		# classify language
#		language[entry] = classify(entry)[0]#

#		# run respective g2p for entries and tokens
#		byte_entry = entry.encode()
#		if language[entry] == 'en':
#			g2p = g2pen 
#		else:
#			g2p = g2pde#

#		g2p_strings = subprocess.Popen(['.' + g2p + '/g2p-full', "-u", "-mp", "-pb"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#		#g2p_tokens = subprocess.Popen(['.' + g2p + '/g2p-full', "-u", "-mp", "-pb", "-pd"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#		strings = g2p_strings.communicate(byte_entry)[0].decode().strip()
#		#tokens = g2p_tokens.communicate(byte_entry)[0].decode().strip()#

#		# dict with entry : transcription_list
#		#transcription[entry] = []
#		#mapped_dict[entry] = []
#		#for string in re.split(r'\t',strings):
#		transcriptions.append(strings)
#			#if lang_map(string) not in transcription[entry]:
#			#	if lang_map(string) not in mapped_dict[entry]:
#			#		mapped_dict[entry].append(lang_map(string))#

##		token_list[entry] = []
##		for token in re.split(r'\n',tokens):
##			try:
##				a = re.split(r"\t",token)
##				word,pron=a[0].strip(),a[1].strip()
##			except IndexError:
##				word = token
##				pron = "NA"
##			word = re.sub('^#','',word)#

##			# dict with entry : token_list
##			if word not in token_list[entry]:
##				token_list[entry].append(word)
##				token_transcription[word] = []
##			# dict with token : transcription_list
##			if pron not in token_transcription[word]:
##				token_transcription[word].append(pron)
##		print(transcription)#

##print(transcription, len(transcription))

# output
#with open(output_file, 'w', encoding="utf-8") as f:
	#for transcription in transcriptions:
		# entry , language
		#print(unit, language[unit])
		# transcriptions
		#print(transcription[unit])
		#transcriptions per token of the entry
		#for item in token_list[unit]:
		#	print(item, token_transcription[item])
		# mapped transcriptions
		#print(mapped_dict[unit])

		# limit the number of g2p entries per title to n max
		#n_max = 10

		# write to file
		#if len(mapped_dict[unit]) == 0:
#		if len(transcription) == 1:
		#f.write(transcription + '\n')
#		else:
#			f.write('\t'.join(transcription[unit][:n_max]) + '\n' )
		#else:
	#		f.write(mapped_dict[unit][0] + '\n')
