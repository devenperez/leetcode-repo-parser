import git
import os
import time
import sys
from problem import Problem
import json

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

def strToBool(s):
    if s.lower() == "true":
        return True
    elif s.lower() == "false":
        return False
    else:
        raise Exception("Invalid arguments (bool)")

### Start ###
argsUnparsed = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
args = {
    "leetcode": True,   # Pull new leetcode from GitHub
    "json": True,       # Upload generated JSON to GitHub (api-git)
}
filesToIgnore = [".git", "README.md"]
problems = []
easyProblemsSolved = 0
mediumProblemsSolved = 0
hardProblemsSolved = 0
currentTime = int(time.time() * 1000)

# Parse arguments
if len(argsUnparsed) > 0:
    if argsUnparsed[0].__contains__("="):
        # Manual argument assignment
        for a in argsUnparsed:
            keyValPair = a.split("=")
            if len(keyValPair) != 2:
                raise Exception("Invalid arguments (missing equal sign)")

            if keyValPair[0].lower() in args.keys():
                args[keyValPair[0].lower()] = strToBool(keyValPair[1])
            else:
                raise Exception("Invalid arguments (key)")
    else:
        # Sequential argument assignment
        if len(argsUnparsed) == len(args):
            args["leetcode"] = strToBool(argsUnparsed[0])
            args["json"] = strToBool(argsUnparsed[1])
        else:
            raise Exception("Invalid arguments (num of args)")

# Pull leetcode from GitHub
if args["leetcode"]:
    # Deletes existing leetcode folder
    if os.path.exists("leetcode"):
        print("Deleting current leetcode folder")
        rmdirAll("leetcode")
else:
    # If not recloning, check if it exists
    if not os.path.exists("leetcode"):
        raise Exception("\"leetcode\" folder does not exist")

    # Clone repo from github
    print("Cloning new leetcode folder from github")
    git.Repo.clone_from('https://github.com/devenperez/leetcode', "leetcode")


if os.path.exists("api-git"):
        print("Deleting current api-git folder")
        rmdirAll("api-git")

git.Repo.clone_from("https://github.com/devenperez/api-git.git", "api-git")
apiRepo = git.Repo("api-git")

print("Starting gathering info from repo")
numFolders = len(os.listdir("leetcode"))
counter = 0
# Gather all necessary info from repo
for problemFolder in os.listdir("leetcode"):
    counter += 1
    if problemFolder in filesToIgnore: continue #Ignores non-problem folders

    print(f"({counter}/{numFolders}) Gathering info for {problemFolder}")
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
            easyProblemsSolved += 1 if prob.difficulty == "Easy" else 0
            mediumProblemsSolved += 1 if prob.difficulty == "Medium" else 0
            hardProblemsSolved += 1 if prob.difficulty == "Hard" else 0
            readme.close()
        else:
            prob.codeFolder = problemFolder + "/" + file
            prob.language = file.split(".")[-1]
    
    problems.append(prob)
print("Finished gathering info from repo")

print("Sorting problem list")
problems.sort(reverse=True, key=lambda p : p.timePercentile + p.memoryPercentile)
print("Finished sorting problem list")

print("Creating CSV file")
# Export all info to .csv file
if os.path.exists("problems_solved.csv"):
    os.remove("problems_solved.csv")

csv = open("problems_solved.csv", "x")
for problem in problems:
    csv.write(problem.toCSV())
    csv.write("\n")
csv.close()
print("Finished CSV file")

## Writing JSON file
print("Creating JSON file")
jsonDictionary = {
    "timeGathered": currentTime,
    "solvedProblems": {
        "solvedTotals": {
            "all": easyProblemsSolved + mediumProblemsSolved + hardProblemsSolved,
            "easy": easyProblemsSolved,
            "medium": mediumProblemsSolved,
            "hard": hardProblemsSolved
        },
        "problems": []
    }
}

for p in problems:
    individualProblemDict = {
        "number": p.number,
        "name": p.name,
        "difficulty": p.difficulty,
        "lang": p.language,
        "location": p.codeFolder,
        "scores": 
        {
            "time": p.time,
            "timePercentile": p.timePercentile,
            "memory": p.memory,
            "memoryPercentile": p.memoryPercentile
        }   
    }

    jsonDictionary["solvedProblems"]["problems"].append(individualProblemDict)

jsonContents = json.dumps(jsonDictionary, indent=4)

# Delete existing JSON file
if os.path.exists(os.path.join("api-git", "data", "problems_solved.json")):
    os.remove(os.path.join("api-git", "data", "problems_solved.json"))

jsonFile = open(os.path.join("api-git", "data", "problems_solved.json"), "x")
jsonFile.write(jsonContents)
jsonFile.close()
print("Finished creating JSON file")

print("Uploading JSON file to GitHub")
apiRepo.index.add([os.path.join("data", "problems_solved.json")])
apiRepo.index.commit(f"Updated problem_solved.json ({currentTime})")
apiOrigin = apiRepo.remote()
apiOrigin.push()
print("Finished uploading JSON file to GitHub")