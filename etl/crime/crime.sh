echo "Loading data from $CRIME_CPD_FOLDER"

#Step 1 - Convert raw data files to csv and store results in tmp folder
xlsx2csv -d x09 -s 1 "$CRIME_CPD_FOLDER/CRIME 2004-2006.xlsx" > "$TMP_FOLDER/crime_2004.csv"
xlsx2csv -d x09 -s 2 "$CRIME_CPD_FOLDER/CRIME 2004-2006.xlsx" > "$TMP_FOLDER/crime_2005.csv"

#Put all files in a single CSV file
cat $TMP_FOLDER/crime_*.csv > "$TMP_FOLDER/2004-2014.csv"
  
#Perform cleaning on the  CSV file
python "$PROJECT_FOLDER/etl/crime/clean.py" "$TMP_FOLDER/2004-2014.csv" > "$TMP_FOLDER/2004-2014_cleaned.csv"

#Use csvsql to create a SQL script with the CREATE TABLE statement
csvsql -i postgresql --tables crime --db-schema public -d ';' "$TMP_FOLDER/2004-2014_cleaned.csv" > "$TMP_FOLDER/crime.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS crime;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/crime.sql"  

#Import the data into the new create table
cat "$TMP_FOLDER/2004-2014_cleaned.csv" | psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\COPY public.crime FROM STDIN  WITH CSV HEADER DELIMITER ';';"