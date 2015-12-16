#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/ner"
TMP_FOLDER="$LOCAL_DATA_FOLDER/tmp"

#mkdir if tmp folder does not exists
mkdir -p $TMP_FOLDER

#Get Stanford's NER and put it in the tmp folder
#http://nlp.stanford.edu/software/CRF-NER.shtml#Download
NAME="stanford-ner-2015-12-09"
wget --directory-prefix=$TMP_FOLDER "http://nlp.stanford.edu/software/$NAME.zip"
unzip "$TMP_FOLDER/$NAME.zip"

java -mx6000m -cp "$TMP_FOLDER/$NAME/stanford-ner.jar" edu.stanford.nlp.ie.NERServer -port 9191 -loadClassifier \
classifiers/english.all.3class.distsim.crf.ser.gz -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer \
-tokenizerOptions "tokenizeNLs=true" -outputFormat tsv  &