import git
import os
import time
import shutil

# Recursive delete folder
def rmdirAll(path):
    for file in os.listdir(path):
        fullpath = os.path.join(path, file)
        if os.path.isdir(fullpath):
            rmdirAll(fullpath)
        else:
            os.chmod(fullpath, 0o777)
            os.remove(fullpath)
    os.rmdir(path)


filesToIgnore = [".git", "README.md"]

"""
if os.path.exists("leetcode"):
    rmdirAll("leetcode")
    
git.Repo.clone_from('https://github.com/devenperez/leetcode', "leetcode")
"""

for problemFolder in os.listdir("leetcode"):
    if problemFolder in filesToIgnore: continue #Ignores non-problem folders
    print(problemFolder)