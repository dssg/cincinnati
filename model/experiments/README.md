# Experiment Configurations

Model configurations are defined by YAML files.
An example is the [`default.yaml`](https://github.com/dssg/cincinnati/blob/master/default.yaml).

We found it useful to generate such YAML files for various temporal splits and feature selections programmatically;
there are two (hacky) modules, `generate_templates.py` (which generates templates, i.e., YAMLs that 
explore various feature combinations, but are not yet tied to a temporal split) and `generate_configs.py`
(which takes templates and generates the full YAML files for various temporal splits).

This folder contains the [templates](templates/) we generated for the iteration of the project 
that used the data update from September 2016, and the fully-specified YAML files in the folder
[splits](splits/).
