import os
import sys
from giturlparse import parse
from pygit2 import Repository

def get_command_result(command_string, cwd):
    import subprocess
    process = subprocess.Popen(command_string, cwd=cwd, shell=True, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = process.wait()
    return "".join((process.stdout if ret == 0 else process.stderr).readlines()).strip()

def get_project_path(filepath):
    import os
    dir_path = os.path.dirname(filepath)
    if get_command_result("git rev-parse --is-inside-work-tree", dir_path) == "true":
        return get_command_result("git rev-parse --show-toplevel", dir_path)
    else:
        return filepath
    
def generate_file_permalink(file, line):
    repo = Repository(file)
    remote_default = next(repo.config.get_multivar("remote.pushdefault"), "origin")
    
    origin_url = parse(repo.remotes[remote_default].url).url2https
    if origin_url.endswith(".git"):
        origin_url = origin_url[:-len(".git")]
    
    head_tree = str(repo.head.target)
    repo_root = get_project_path(file)
        
    return "{}/blob/{}/{}#L{}".format(origin_url, head_tree, file.split(repo_root)[1].lstrip('/'), line)

if __name__ == "__main__":
    print(generate_file_permalink(*sys.argv[1:]), end='', flush=True)
