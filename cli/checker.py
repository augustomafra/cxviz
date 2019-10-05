import os

def readable_path(path):
    if not os.access(path, os.R_OK):
        raise Exception('No read access on path: {}'.format(path))
    return path

def maybe_dir(maybe_dir):
    if not os.path.isdir(maybe_dir):
        os.mkdir(maybe_dir)

    just_dir = maybe_dir
    if not os.access(just_dir, os.W_OK):
        raise Exception('No write access on directory: {}'.format(just_dir))
    if not os.access(just_dir, os.R_OK):
        raise Exception('No read access on directory: {}'.format(just_dir))

    return just_dir

