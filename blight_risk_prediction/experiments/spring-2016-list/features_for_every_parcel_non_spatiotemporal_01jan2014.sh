PATH_TO_BOT="$ROOT_FOLDER/blight_risk_prediction/features"

#non-spatiotemporal features
$PATH_TO_BOT/featurebot.py -d 01jan2014 -f tax,crime_agg,named_entities,house_type,parc_area,parc_year,census_2010