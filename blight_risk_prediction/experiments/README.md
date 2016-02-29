This file contains confguration files for some of the experiments we tried.

Using the `--pickle` option in `model.py` will pickle imputer, scaler and model objects, those files will be stores in your `$OUTPUT_FOLDER`. As you train models, that folder will increase in size a lot. Run `clean_dumps.py` if you want to clean such folders and only keep the top 20 models, imputers and scalers for each experiment. The script will also do the same in the `$OUTPUT_FOLDER/predictions` folder and the MongoDB database.

Depending on how many fiels there are, this may take a while to run.