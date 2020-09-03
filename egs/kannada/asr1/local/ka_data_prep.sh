#!/bin/bash

# Copyright 2013   (Authors: Bagher BabaAli, Daniel Povey, Arnab Ghoshal)
#           2014   Brno University of Technology (Author: Karel Vesely)
#           2019   IIIT-Bangalore (Shreekantha Nadig)
# Apache 2.0.
if [ $# -le 0 ]; then
    echo "Argument should be the Timit directory, see ../run.sh for example."
    exit 1;
fi

dir=`pwd`/data/local/data
lmdir=`pwd`/data/local/nist_lm
mkdir -p $dir $lmdir
local=`pwd`/local
utils=`pwd`/utils
conf=`pwd`/conf

if [ $2 ]; then
    if [[ $2 = "char" || $2 = "phn" ]]; then
        trans_type=$2
    else
        echo "Transcript type must be one of [phn, char]"
        echo $2
    fi
else
    trans_type=phn
fi

. ./path.sh # Needed for KALDI_ROOT
export PATH=$PATH:$KALDI_ROOT/tools/irstlm/bin
sph2pipe=$KALDI_ROOT/tools/sph2pipe_v2.5/sph2pipe
if [ ! -x $sph2pipe ]; then
    echo "Could not find (or execute) the sph2pipe program at $sph2pipe";
    exit 1;
fi


tmpdir=$(mktemp -d /tmp/kaldi.XXXX);
trap 'rm -rf "$tmpdir"' EXIT

cd $dir
for x in train dev test; do
    # Prepare STM file for sclite:
    wav-to-duration --read-entire-file=true scp:${x}_wav.scp ark,t:${x}_dur.ark || exit 1
    awk -v dur=${x}_dur.ark \
    'BEGIN{
     while(getline < dur) { durH[$1]=$2; }
     print ";; LABEL \"O\" \"Overall\" \"Overall\"";
     print ";; LABEL \"F\" \"Female\" \"Female speakers\"";
     print ";; LABEL \"M\" \"Male\" \"Male speakers\"";
   }
   { wav=$1; spk=wav; sub(/_.*/,"",spk); $1=""; ref=$0;
     gender=(substr(spk,0,1) == "f" ? "F" : "M");
     printf("%s 1 %s 0.0 %f <O,%s> %s\n", wav, spk, durH[wav], gender, ref);
   }
    ' ${x}.text >${x}.stm || exit 1
    
    # Create dummy GLM file for sclite:
    echo ';; empty.glm
  [FAKE]     =>  %HESITATION     / [ ] __ [ ] ;; hesitation token
    ' > ${x}.glm
done

echo "Data preparation succeeded"
