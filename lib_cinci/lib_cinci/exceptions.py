class SchemaMissing():
    def __init__(self, schema_name):
        self.schema_name = schema_name

    def __str__(self):
        return "Schema {} does not exist".format(self.schema_name)


class ExperimentExists():
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name

    def __str__(self):
        return "Experiment {} already exists in the MongoDB database".format(self.experiment_name)


class MaxDateError(Exception):
    pass


class NoFeaturesSelected(Exception):
    pass


class ConfigError(Exception):
    pass
