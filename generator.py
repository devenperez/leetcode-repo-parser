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

def get_embed_from_url(url):
    target = url.replace(" ", "%20")
    target = url.replace(":", "%3A")
    target = url.replace("/", "%2F")
    return "<script src=\"https://emgithub.com/embed.js?target=" + target + "&style=github&showBorder=on&showLineNumbers=on\"></script>"

filesToIgnore = [".git", "README.md"]

"""
if os.path.exists("leetcode"):
    rmdirAll("leetcode")
    
git.Repo.clone_from('https://github.com/devenperez/leetcode', "leetcode")
"""

for problemFolder in os.listdir("leetcode"):
    if problemFolder in filesToIgnore: continue #Ignores non-problem folders
    embedCode = ""
    codeFolder = ""
    difficulty = ""
    
    # Retrieve problem info
    folderSplit = problemFolder.split("-")
    number = folderSplit.pop(0)
    name = " ".join(folderSplit).title()
    
    print(number)
    print(name)
    
    # 
    pfPath = os.path.join("leetcode", problemFolder)
    for file in os.listdir(pfPath):
        if file == "NOTES.md": 
            continue #Notes can be ignored for this
        elif file == "README.md":
            readme = open(os.path.join(pfPath, file), "r")
            print(readme.read())
        else:
            codeFolder = problemFolder + "/" + file
            
    print(codeFolder)
    print("\n")
        