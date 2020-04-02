#!/bin/bash


# ./g2p.sh arg1=archive_path arg2=input_path arg3=lang_map_loc arg4=output_loc

archive=$1
input_loc=$2
map_loc=$3
output_loc=$4
DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d $output_loc ]
then
	mkdir $output_loc
fi

if [ ! -d $output_loc"/files" ]
then
	mkdir $output_loc"/files"
fi

re="^(.+)\/(.+?)$"
[[ $archive =~ $re ]] && var1="${BASH_REMATCH[1]}" && var2="${BASH_REMATCH[2]}"
cp "$archive" "$output_loc"
cd $output_loc
tar xjf $var2 -C $output_loc"/files"
rm "$var2"
cd $output_loc/files/*
make all
cd bin/de-DE
cat "$input_loc" | ./g2p-full -mp -u -pb -pd > $output_loc/files/token.tsv
cat "$input_loc" | ./g2p-full -mp -u -pb > $output_loc/files/string.tsv

cd $DIR
python3 g2p.py "$input_loc" "$output_loc" "$map_loc"