#Read variables from config file
echo 'Reading db connection details from '$ROOT_FOLDER'/config.yaml'
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#create schemas
echo 'Creating schemas...'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA shape_files;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA features;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA inspections;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA inspections_raw;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA inspections_views;"

echo 'Creating address table...'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/address.sql"  

echo 'Remember to install PostGIS in the database...'

echo 'Done!'