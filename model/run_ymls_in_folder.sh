#!/bin/bash
for i in $( ls $1*.yaml); do
    python model.py --pickle --path_to_config_file $i
done
