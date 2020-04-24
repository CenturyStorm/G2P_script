#!/bin/sh
# bash script for running g2p docker image 

docker run -it \
	--mount src="/mnt/exchange",target="/mnt/exchange",type=bind \
	lars_g2p "$1" "$2"

#	--mount src="$(pwd)",target="/home/asr-g2p",type=bind \