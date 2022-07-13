import git
import os
import time
import shutil
from problem import Problem

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

# Retrives website embed
def get_embed_from_url(url):
    target = url.replace("/", "%2F")
    return f"<script src=\"https://emgithub.com/embed.js?target=https%3A%2F%2Fgithub.com%2Fdevenperez%2Fleetcode%2Fblob%2Fmain%2F{target}&style=github&showBorder=on&showLineNumbers=on\"></script>"

### Start ###

filesToIgnore = [".git", "README.md"]
problems = []

# Deletes existing leetcode folder
if os.path.exists("leetcode"):
    rmdirAll("leetcode")

# Clone repo from github
git.Repo.clone_from('https://github.com/devenperez/leetcode', "leetcode")


for problemFolder in os.listdir("leetcode"):
    if problemFolder in filesToIgnore: continue #Ignores non-problem folders

    # Retrieve problem info
    folderSplit = problemFolder.split("-")
    prob = Problem(folderSplit.pop(0), " ".join(folderSplit).title())

    
    # Gather info from folder
    pfPath = os.path.join("leetcode", problemFolder)
    for file in os.listdir(pfPath):
        if file == "NOTES.md":
            pass
        elif file.startswith("STATS"):
            stats = open(os.path.join(pfPath, file), "r")
            wordBreaks = stats.read().split(" ")
            stats.close()
            prob.time = float(wordBreaks[1])
            prob.timePercentile = float(wordBreaks[3][1:-3])
            prob.memory = float(wordBreaks[5])
            prob.memoryPercentile = float(wordBreaks[7][1:-2])
        elif file == "README.md":
            readme = open(os.path.join(pfPath, file), "r")
            prob.difficulty = readme.read().split("h3")[1][1:-2]
            readme.close()
        else:
            codeFolder = problemFolder + "/" + file
            prob.embedCode = get_embed_from_url(codeFolder)
            prob.language = file.split(".")[-1]
    
    problems.append(prob)

# Export all info to .csv file
if os.path.exists("problems_solved.csv"):
    os.remove("problems_solved.csv")

csv = open("problems_solved.csv", "x")
for problem in problems:
    csv.write(problem.toCSV())
    csv.write("\n")
csv.close()