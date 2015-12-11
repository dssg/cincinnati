#!/usr/bin/env bash

#Get the location of the tmp folder for taxes etl
TMP_FOLDER="$DATA_FOLDER/etl/taxes/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Use csvsql to create a SQL script with the CREATE TABLE statement
#2007
csvsql -i postgresql --tables taxes_2007 --db-schema public -d ',' "$TMP_FOLDER/taxes_2007.csv" > "$TMP_FOLDER/taxes_2007.sql"
#2008
csvsql -i postgresql --tables taxes_2008 --db-schema public -d ',' "$TMP_FOLDER/taxes_2008.csv" > "$TMP_FOLDER/taxes_2008.sql"
#2009
csvsql -i postgresql --tables taxes_2009 --db-schema public -d ',' "$TMP_FOLDER/taxes_2009.csv" > "$TMP_FOLDER/taxes_2009.sql"
#2010
csvsql -i postgresql --tables taxes_2010 --db-schema public -d ',' "$TMP_FOLDER/taxes_2010.csv" > "$TMP_FOLDER/taxes_2010.sql"
#2011
csvsql -i postgresql --tables taxes_2011 --db-schema public -d ',' "$TMP_FOLDER/taxes_2011.csv" > "$TMP_FOLDER/taxes_2011.sql"
#2012
csvsql -i postgresql --tables taxes_2012 --db-schema public -d ',' "$TMP_FOLDER/taxes_2012.csv" > "$TMP_FOLDER/taxes_2012.sql"
#2013
csvsql -i postgresql --tables taxes_2013 --db-schema public -d ',' "$TMP_FOLDER/taxes_2013.csv" > "$TMP_FOLDER/taxes_2013.sql"
#2014
csvsql -i postgresql --tables taxes_2014 --db-schema public -d ',' "$TMP_FOLDER/taxes_2014.csv" > "$TMP_FOLDER/taxes_2014.sql"
#2015
csvsql -i postgresql --tables taxes_2015 --db-schema public -d ',' "$TMP_FOLDER/taxes_2015.csv" > "$TMP_FOLDER/taxes_2015.sql"

#Drop tables if they already exist
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2007;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2008;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2009;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2010;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2011;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2012;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2013;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2014;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2015;"

#Run the CREATE TABLE statements on the database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2007.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2008.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2009.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2010.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2011.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2012.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2013.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2014.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/taxes_2015.sql"

#Import the data into the tables
cat "$TMP_FOLDER/taxes_2007.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2007 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2007 table!'

cat "$TMP_FOLDER/taxes_2008.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2008 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2008 table!'

cat "$TMP_FOLDER/taxes_2009.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2009 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2009 table!'

cat "$TMP_FOLDER/taxes_2010.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2010 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2010 table!'

cat "$TMP_FOLDER/taxes_2011.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2011 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2011 table!'

cat "$TMP_FOLDER/taxes_2012.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2012 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2012 table!'

cat "$TMP_FOLDER/taxes_2013.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2013 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2013 table!'

cat "$TMP_FOLDER/taxes_2014.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2014 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2014 table!'

cat "$TMP_FOLDER/taxes_2015.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.taxes_2015 FROM STDIN  WITH CSV HEADER DELIMITER ',';"
echo 'Done creating taxes_2015 table!'
