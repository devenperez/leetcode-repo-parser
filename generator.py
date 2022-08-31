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
    "csv": False,       # Create CSV file of all gathered information
    "json": True,       # Upload generated JSON to GitHub (api-git)
    "debug": False      # Print out validation table 
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
            args["csv"] = strToBool(argsUnparsed[1])
            args["json"] = strToBool(argsUnparsed[2])
            args["debug"] = strToBool(argsUnparsed[3])
        else:
            raise Exception("Invalid arguments (num of args)")

# Pull leetcode from GitHub
if args["leetcode"]:
    # Deletes existing leetcode folder
    if os.path.exists(os.path.join("repos","leetcode")):
        # Pulling from origin (leetcode)
        print("Pulling new commits from leetcode on GitHub")
        leetcodeRepo = git.Repo(os.path.join("repos","leetcode"))
        leetcodeRepo.remotes.origin.pull()
        print("Finished pulling new commits from leetcode on GitHub")
    else:
        # Clone repo from github
        print("Cloning new leetcode folder from GitHub")
        git.Repo.clone_from('https://github.com/devenperez/leetcode.git', os.path.join("repos", "leetcode"))
        print("Finished cloning new leetcode folder from GitHub")
else:
    # If not recloning, check if it exists
    if not os.path.exists(os.path.join("repos","leetcode")):
        raise Exception("\"leetcode\" folder does not exist")
    leetcodeRepo = git.Repo(os.path.join("repos","leetcode"))

print("Starting gathering info from repo")
numFolders = len(os.listdir(os.path.join("repos","leetcode")))
counter = 0
# Gather all necessary info from repo
for problemFolder in os.listdir(os.path.join("repos","leetcode")):
    counter += 1
    if problemFolder in filesToIgnore: continue #Ignores non-problem folders

    print(f"({counter}/{numFolders}) Gathering info for {problemFolder}")
    # Retrieve problem info
    folderSplit = problemFolder.split("-")
    prob = Problem(folderSplit.pop(0), " ".join(folderSplit).title())

    
    # Gather info from folder
    pfPath = os.path.join("repos", "leetcode", problemFolder)
    for file in os.listdir(pfPath):
        if file == "NOTES.md":
            pass
        elif file.startswith("STATS"):
            with open(os.path.join(pfPath, file), "r") as stats:
                wordBreaks = stats.read().split(" ")
            stats = prob.getOrAddStats(file.split("_")[1].split(".")[0])
            stats.addStats(float(wordBreaks[1]), float(wordBreaks[3][1:-3]), float(wordBreaks[5]), float(wordBreaks[7][1:-2]))
        elif file == "README.md":
            with open(os.path.join(pfPath, file), "r") as readme:
                prob.difficulty = readme.read().split("h3")[1][1:-2]
                easyProblemsSolved += 1 if prob.difficulty == "Easy" else 0
                mediumProblemsSolved += 1 if prob.difficulty == "Medium" else 0
                hardProblemsSolved += 1 if prob.difficulty == "Hard" else 0
        else:
            prob.codeFolder = problemFolder + "/" + file
            prob.validate(file.split(".")[-1])
    
    problems.append(prob)
print("Finished gathering info from repo")

print("Sorting problem list")
problems.sort(reverse=True, key=lambda p : p.stats[0].timePercentile + p.stats[0].memoryPercentile)
print("Finished sorting problem list")

if args["debug"]:
    print("-" * 45)
    print("* = Missing code, ' = Missing stats")
    print("-" * 45)
    for p in problems:
        print(p.getDebugRow())
    print("-" * 45)

# Create CSV file
if args["csv"]:
    print("Creating CSV file")
    # Export all info to .csv file
    if os.path.exists("problems_solved.csv"):
        os.remove("problems_solved.csv")

    with open("problems_solved.csv", "x") as csv:
        for problem in problems:
            csv.write(problem.toCSV())
            csv.write("\n")
    print("Finished CSV file")

if args["json"]:
    # Pulling new api-git
    if os.path.exists(os.path.join("repos", "api-git")):
        print("Pulling new commits from api-git on GitHub")
        apiRepo = git.Repo(os.path.join("repos", "api-git"))
        apiRepo.remotes.origin.pull()
        print("Finished pulling new commits from api-git on GitHub")
    else:
        print("Cloning new api-git folder from GitHub")
        git.Repo.clone_from("https://github.com/devenperez/api-git.git", os.path.join("repos", "api-git"))
        apiRepo = git.Repo(os.path.join("repos", "api-git"))
        print("Finished cloning new api-git folder from GitHub")

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
            "location": p.codeFolder,
            "languagesSolved": []
        }
        for pstats in p.stats:
            langSolvedSection = {
                "lang": pstats.language,
                "time": pstats.time,
                "timePercentile": pstats.timePercentile,
                "memory": pstats.memory,
                "memoryPercentile": pstats.memoryPercentile
            }
            individualProblemDict["languagesSolved"].append(langSolvedSection)
        individualProblemDict["languagesSolved"].sort(reverse=True, key=lambda p : p["timePercentile"] + p["memoryPercentile"])

        jsonDictionary["solvedProblems"]["problems"].append(individualProblemDict)

    jsonContents = json.dumps(jsonDictionary, indent=4)

    # Delete existing JSON file
    if os.path.exists(os.path.join("repos", "api-git", "data", "problems_solved.json")):
        os.remove(os.path.join("repos", "api-git", "data", "problems_solved.json"))

    with open(os.path.join("repos", "api-git", "data", "problems_solved.json"), "x") as jsonFile:
        jsonFile.write(jsonContents)
    print("Finished creating JSON file")

    print("Uploading JSON file to GitHub")
    apiRepo.index.add([os.path.join("data", "problems_solved.json")])
    apiRepo.index.commit(f"Updated problem_solved.json ({currentTime})")
    apiRepo.remotes.origin.push()
    print("Finished uploading JSON file to GitHub")