import os

#Retrieve the corresponding local data folder given a file
def for_file(path):
    #Root folder for the project is
    root_folder = os.environ['ROOT_FOLDER']
    #Data input/output is expected in
    data_folder = os.environ['DATA_FOLDER']
    script_dir = os.path.abspath(os.path.dirname(path))
    rel_to_root = os.path.relpath(script_dir, root_folder)
    rel_to_data = os.path.join(data_folder, rel_to_root)
    return rel_to_data