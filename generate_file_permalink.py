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
    
def generate_file_permalink(file, start_line, end_line):
    repo = Repository(file)
    remote_default = next(repo.config.get_multivar("remote.pushdefault"), "origin")
    origin_url = get_git_https_url(repo.remotes[remote_default].url)
    
    head_tree = str(repo.head.target)
    repo_root = get_project_path(file)
        
    repo_info_list = file.split(repo_root)
    permalink_file = ""
    if len(repo_info_list) == 1:
        permalink_file = os.path.basename(repo_info_list[0])
    elif len(repo_info_list) == 2:
        permalink_file = repo_info_list[1].lstrip("/")
    
    if end_line == "":
        return "{}/blob/{}/{}#L{}".format(origin_url, head_tree, permalink_file, start_line)
    else:
        return "{}/blob/{}/{}#L{}-#L{}".format(origin_url, head_tree, permalink_file, start_line, end_line)
    
def get_git_https_url(url: str):
    from giturlparse import parse
    
    if url.startswith("git@") and not url.endswith(".git"):
        url = url + ".git"
        
    https_url = parse(url).url2https
    
    if https_url.endswith(".git"):
        https_url = https_url[:-len(".git")]
        
    return https_url
        
if __name__ == "__main__":
    print(generate_file_permalink(*sys.argv[1:]), end='', flush=True)
