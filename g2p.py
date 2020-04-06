
# coding: utf-8
import re
import sys

# saving phone mapping to map_dict
map_file = str(sys.argv[3])
with open(map_file, 'r', encoding="utf-8") as f:
	map_dict={}
	for line in f:
		x = re.split(r"\t",line)
		map_dict[x[0].strip()] = x[1].strip()

# replacing phones due to map_dict
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

# reading input file
input_file = str(sys.argv[1])
with open(input_file, 'r', encoding="utf-8") as f:
	artists = []
	for artist in f:
		artists.append(artist.strip())

# reading g2p for tokens
token_file = str(sys.argv[2]) + "/files/token.tsv"
with open(token_file, 'r', encoding="utf-8") as f:
	token_dict = {}
	for line in f:
		a = re.split(r"\t",line)
		word, pron = a[0].strip(),a[1].strip()
		if word in token_dict:
			token_dict[word].append(pron)
		else:
			token_dict[word] = [pron]

# reading g2p for strings
string_file = str(sys.argv[2]) + "/files/string.tsv"
with open(string_file, 'r', encoding="utf-8") as f:
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

# printing
write_file = str(sys.argv[2]) + "/strings.tsv"
with open(write_file, 'w', encoding="utf-8") as f:
	for x in str_dict:
		new_x = x.replace(" ",";")
		for y in set(str_dict[x]):
			print(f'{new_x}_langTag_domTag\t{y}',file=f)

write_file = str(sys.argv[2]) + "/mapped.tsv"
with open(write_file, 'w', encoding="utf-8") as f:
	for x in mapped_dict:
		new_x = x.replace(" ",";")
		for y in set(mapped_dict[x]):
			print(f'{new_x}_langTag_domTag\t{y}',file=f)

write_file = str(sys.argv[2]) + "/tokens.tsv"
with open(write_file, 'w', encoding="utf-8") as f:
	for x in token_dict:
		new_x=x.replace("#","")
		for y in set(token_dict[x]):
			print(f'{new_x}_langTag_domTag\t{y}',file=f)
