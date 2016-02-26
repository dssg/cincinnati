#Generate spatiotemporal features for features_field_test_31dec2014 table
#with the following spatiotemporal parameters:
#50m, 400m, 700, 1000m
#3months, 6months, 9months
PATH_TO_BOT="$ROOT_FOLDER/blight_risk_prediction/features"

#non-spatiotemporal features
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f tax,crime_agg,named_entities,house_type,parc_area,parc_year,census_2010 -s field_test

#50m
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 3 -md 50 -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 6 -md 50 -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 9 -md 50 -s field_test

#400m
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 3 -md 400 -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 6 -md 400 -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 9 -md 400 -s field_test

#700m
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 3 -md 700m -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 6 -md 700m -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 9 -md 700m -s field_test

#1000m
#400m
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 3 -md 1000 -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 6 -md 1000 -s field_test
$PATH_TO_BOT/featurebot.py -d 31dec2014 -f three11,permits,crime,fire,sales -m 9 -md 1000 -s field_test