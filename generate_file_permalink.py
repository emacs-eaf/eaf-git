import os
import sys
from giturlparse import parse
from pygit2 import Repository

def generate_file_permalink(file, line):
    repo = Repository(file)
    
    origin_url = parse(repo.remotes["origin"].url).url2https
    if origin_url.endswith(".git"):
        origin_url = origin_url[:-len(".git")]
    
    head_tree = str(repo.head.target)
    
    repo_root = repo.path
    if repo_root.endswith(".git/"):
        repo_root = repo_root[:-len(".git/")]
    
    return "{}/blob/{}/{}#L{}".format(origin_url, head_tree, file.split(repo_root)[1], line)

if __name__ == "__main__":
    print(generate_file_permalink(*sys.argv[1:]), end='', flush=True)
