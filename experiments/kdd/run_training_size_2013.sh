PATH_TO_MODEL="$ROOT_FOLDER/blight_risk_prediction"
PATH_TO_EXP="$ROOT_FOLDER/experiments/kdd"
CORES=8

$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_1years_2013.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_2years_2013.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_3years_2013.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_4years_2013.yaml