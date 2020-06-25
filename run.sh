#!/bin/sh
# bash script for running g2p docker image 
# Parse arguments

while getopts ":t:g:" option; do
    case "${option}" in
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
    --mount src="$(pwd)"/source_files/output,target=/output,type=bind \
    lars_g2p "$TITLES" "$G2P"
    


