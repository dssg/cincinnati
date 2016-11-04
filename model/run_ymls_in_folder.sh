#!/bin/bash
for i in $( ls $1*.yaml); do
    python $ROOT_FOLDER/model/model.py --pickle --path_to_config_file $i
done
