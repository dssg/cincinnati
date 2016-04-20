PATH_TO_MODEL="$ROOT_FOLDER/model"
PATH_TO_EXP="$ROOT_FOLDER/experiments/kdd"
CORES=8

$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/all_freq_features_50m_3months.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/all_freq_features_50m_6months.yaml
$PATH_TO_MODEL/model.py -n $CORES -c $PATH_TO_EXP/all_freq_features_50m_9months.yaml