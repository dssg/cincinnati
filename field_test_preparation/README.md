#Preparing results for a field test [WORK IN PROGRESS]

If the `prepare_field_test` in the configuration file, predictions such test will be saved on `$OUTPUT_FOLDER/field_test_predictions`. Make sure that folder exists.

This folder contains tools to create a list of inspections based on model predictions.

* [postprocess](postprocess/) - Add details (e.g. address) about properties to predictions
* [targeting_priority](targeting_priority/) - Re-rank predictions according to some targeting priority


