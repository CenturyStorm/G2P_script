#!/bin/sh
# bash script for running g2p docker image 
# Usage: ./run.sh -e /mnt/exchange -t titles.tsv -g g2p.tsv

# Parse arguments
while getopts ":e:t:g:" option; do
    case "${option}" in
        e)
            EXCHANGE=${OPTARG}
            ;;
        t)
            TITLES=${OPTARG}
            ;;
		g)
            G2P=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

docker run -it \
	--mount src="$EXCHANGE",target="/mnt/exchange",type=bind \
	lars_g2p "$TITLES" "$G2P"

#	--mount src="$(pwd)",target="/home/asr-g2p",type=bind \