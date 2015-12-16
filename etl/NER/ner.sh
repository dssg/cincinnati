#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/ner"
LOCAL_CODE_FOLDER="$ROOT_FOLDER/etl/ner"
TMP_FOLDER="$LOCAL_DATA_FOLDER/tmp"

#mkdir if tmp folder does not exists
mkdir -p $TMP_FOLDER

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Get Stanford's NER and put it in the tmp folder
#http://nlp.stanford.edu/software/CRF-NER.shtml#Download
#This NER system requires Java 1.8 or later. Make sure you have Java 8.
NAME="stanford-ner-2015-12-09"
wget --directory-prefix=$TMP_FOLDER "http://nlp.stanford.edu/software/$NAME.zip"
unzip "$TMP_FOLDER/$NAME.zip"

java -mx6000m -cp "$TMP_FOLDER/$NAME/stanford-ner.jar" edu.stanford.nlp.ie.NERServer -port 9191 -loadClassifier \
classifiers/english.all.3class.distsim.crf.ser.gz -tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer \
-tokenizerOptions "tokenizeNLs=true" -outputFormat tsv  &

#Perform NER for all tax data from 2007 to 2015. One CSV is written per year. Must use python3 for this step!
python "$LOCAL_CODE_FOLDER/get_tax_owners.py"

#Combine all those CSVs into one CSV
python "$LOCAL_CODE_FOLDER/merge.py"

#Create new table in the database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_CODE_FOLDER/taxes_owners.sql"  

#Upload the data to the database
cat owners_2007-2015.csv | psql -h $DB_HOST -U $DB_USER \
-d $DB_NAME -c "\COPY public.taxes_owners FROM STDIN  WITH CSV HEADER DELIMITER ',';"