#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#install postgis

#create schemas
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA shape_files;"  