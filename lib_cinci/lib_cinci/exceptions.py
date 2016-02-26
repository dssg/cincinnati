class SchemaMissing():
    def __init__(self, schema_name):
        self.schema_name = schema_name

    def __str__(self):
        return "Schema {} does not exist".format(self.schema_name)

class MaxDateError(Exception):
    pass

class NoFeaturesSelected(Exception):
    pass

class ConfigError(Exception):
    pass