PATH_TO_MODEL="$ROOT_FOLDER/model"
PATH_TO_EXP="$ROOT_FOLDER/experiments/kdd"
CORES=8

$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_1years_2012.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_2years_2012.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_3years_2012.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/freq_features_4years_2012.yaml
