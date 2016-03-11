#Running many experments one after another
CORES=8
PATH_TO_MODEL=$ROOT_FOLDER/blight_risk_prediction/model.py
PATH_TO_CLEAN=$ROOT_FOLDER/blight_risk_prediction/experiments/clean_dumps.py
PATH_TO_EXP=$ROOT_FOLDER/blight_risk_prediction/experiments/spring-2016-list

$PATH_TO_MODEL -c $PATH_TO_EXP/all_freq_features_1000m_3months_12_13_all_parcels.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 1';
$PATH_TO_MODEL -c $PATH_TO_EXP/all_freq_features_50m_3months_12_13_all_parcels.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 2';
$PATH_TO_MODEL -c $PATH_TO_EXP/all_freq_features_all_spatiotemporal_params_12_13_all_parcels.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 3';
$PATH_TO_MODEL -c $PATH_TO_EXP/only_agg_and_parcel_features_12_13_all_parcels.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 4';
$PATH_TO_MODEL -c $PATH_TO_EXP/only_agg_and_parcel_features_12_13.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 5';
$PATH_TO_MODEL -c $PATH_TO_EXP/only_freq_features_50m_3months_12_13_all_parcels.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 6';
$PATH_TO_MODEL -c $PATH_TO_EXP/only_freq_features_50m_3months_12_13.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 7';
$PATH_TO_MODEL -c $PATH_TO_EXP/only_parcel_features_12_13_all_parcels.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 8';
$PATH_TO_MODEL -c $PATH_TO_EXP/only_parcel_features_12_13.yaml -n $CORES -p && $PATH_TO_CLEAN && mailme 'exp 9';
