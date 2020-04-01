
# coding: utf-8
import re

f = open('files/en-US~de-De.tsv')
map_dict={}
for line in f:
	x = re.split(r"\t",line)
	map_dict[x[0].strip()] = x[1].strip()

def lang_map(pron):
	phones = pron.split()
	mapped = []
	for phone in phones:
		if phone in map_dict:
			mapped.append(map_dict[phone])
		else:
			mapped.append(phone)
	sep = " "
	mapped_pron = sep.join(mapped)
	return mapped_pron

f = open('files/var_artists_spotify_Top5000_pop.tsv')
artists = []
for artist in f:
	artists.append(artist.strip())

f = open('files/token.tsv', 'r')
token_dict = {}
for line in f:
	a = re.split(r"\t",line)
	word, pron = a[0].strip(),a[1].strip()
	if word in token_dict:
		token_dict[word].append(pron)
	else:
		token_dict[word] = [pron]

f = open('files/string.tsv', 'r')
str_dict = {}
mapped_dict = {}
count = 0
for line in f:
	str_dict[artists[count]] = re.split(r"\t",line.strip())
	for artist in str_dict[artists[count]]:
		if lang_map(artist) not in str_dict[artists[count]]:
			if artists[count] in mapped_dict:
				mapped_dict[artists[count]].append(lang_map(artist))
			else:
				mapped_dict[artists[count]]= [lang_map(artist)]
	count += 1

f = open('output/strings.tsv', 'w')
for x in str_dict:
	print(f'{x}',file=f)
	print(f'{set(str_dict[x])}',file=f)
	print(file=f)

f = open('output/mapped.tsv', 'w')
for x in mapped_dict:
	print(f'{x}',file=f)
	print(f'{set(mapped_dict[x])}',file=f)
	print(file=f)

f = open('output/tokens.tsv', 'w')
for x in token_dict:
	print(f'{x}',file=f)
	print(f'{set(token_dict[x])}',file=f)
	print(file=f)
