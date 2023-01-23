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


def YesOrNoQuestion(question):
    response = ""
    yesResponses = ["Y", "y", "yes", "Yes", "YES"]
    noResponses = ["N", "n", "no", "No", "NO"]
    validResponses = yesResponses + noResponses
    while not response in validResponses:
        response = input(f"{question} (Y/N) ")

    if response in yesResponses:
        return True
    return False

### Start ###
argsUnparsed = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
args = {
    "auto": False,      # Automatically executes without any further input
    "leetcode": True,   # Pull new leetcode from GitHub
    "csv": False,       # Create CSV file of all gathered information
    "json": True,       # Upload generated JSON to GitHub (api-git)
    "debug": False      # Print out validation table
}
filesToIgnore = [".git", "README.md"]
global problems
problems = []
global easyProblemsSolved
global mediumProblemsSolved
global hardProblemsSolved
easyProblemsSolved = 0
mediumProblemsSolved = 0
hardProblemsSolved = 0
currentTime = int(time.time() * 1000)

def PullFromGithub(shouldFetch):
    if shouldFetch:
        # Deletes existing leetcode folder
        if os.path.exists(os.path.join("repos", "leetcode")):
            # Pulling from origin (leetcode)
            print("Pulling new commits from leetcode on GitHub")
            leetcodeRepo = git.Repo(os.path.join("repos", "leetcode"))
            leetcodeRepo.remotes.origin.pull()
            print("Finished pulling new commits from leetcode on GitHub")
        else:
            # Clone repo from github
            print("Cloning new leetcode folder from GitHub")
            git.Repo.clone_from(
                'https://github.com/devenperez/leetcode.git', os.path.join("repos", "leetcode"))
            print("Finished cloning new leetcode folder from GitHub")
    else:
        # If not recloning, check if it exists
        if not os.path.exists(os.path.join("repos", "leetcode")):
            raise Exception("\"leetcode\" folder does not exist")
        leetcodeRepo = git.Repo(os.path.join("repos", "leetcode"))

def GatherInfo():
    global easyProblemsSolved
    global mediumProblemsSolved
    global hardProblemsSolved
    print("Starting gathering info from repo")
    numFolders = len(os.listdir(os.path.join("repos", "leetcode")))
    counter = 0
    # Gather all necessary info from repo
    for problemFolder in os.listdir(os.path.join("repos", "leetcode")):
        counter += 1
        if problemFolder in filesToIgnore:
            continue  # Ignores non-problem folders

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
                stats.addStats(float(wordBreaks[1]), float(
                    wordBreaks[3][1:-3]), float(wordBreaks[5]), float(wordBreaks[7][1:-2]))
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

def SortProblems():   
    print("Sorting problem list")
    problems.sort(
        reverse=True, key=lambda p: p.stats[0].timePercentile + p.stats[0].memoryPercentile)
    print("Finished sorting problem list")

def PrintDebug(shouldPrint):
    if not shouldPrint:
        return

    print("-" * 45)
    print("* = Missing code, ' = Missing stats")
    print("-" * 45)
    for p in problems:
        print(p.getDebugRow())
    print("-" * 45)

def CreateCSV(shouldCreate):
    # Create CSV file
    if not shouldCreate:
        return

    print("Creating CSV file")
    # Export all info to .csv file
    if os.path.exists("problems_solved.csv"):
        os.remove("problems_solved.csv")

    with open("problems_solved.csv", "x") as csv:
        for problem in problems:
            csv.write(problem.toCSV())
            csv.write("\n")
    print("Finished CSV file")

def CreateJSON(shouldCreate):
    if not shouldCreate:
        return

    # Pulling new api-git
    if os.path.exists(os.path.join("repos", "api-git")):
        print("Pulling new commits from api-git on GitHub")
        apiRepo = git.Repo(os.path.join("repos", "api-git"))
        apiRepo.remotes.origin.pull()
        print("Finished pulling new commits from api-git on GitHub")
    else:
        print("Cloning new api-git folder from GitHub")
        git.Repo.clone_from(
            "https://github.com/devenperez/api-git.git", os.path.join("repos", "api-git"))
        apiRepo = git.Repo(os.path.join("repos", "api-git"))
        print("Finished cloning new api-git folder from GitHub")

    # Writing JSON file
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
        individualProblemDict["languagesSolved"].sort(
            reverse=True, key=lambda p: p["timePercentile"] + p["memoryPercentile"])

        jsonDictionary["solvedProblems"]["problems"].append(
            individualProblemDict)

    jsonContents = json.dumps(jsonDictionary, indent=4)

    # Delete existing JSON file
    if os.path.exists(os.path.join("repos", "api-git", "data", "problems_solved.json")):
        os.remove(os.path.join("repos", "api-git",
                  "data", "problems_solved.json"))

    with open(os.path.join("repos", "api-git", "data", "problems_solved.json"), "x") as jsonFile:
        jsonFile.write(jsonContents)
    print("Finished creating JSON file")

def UploadJSON(shouldUpload):
    if not shouldUpload:
        return

    print("Uploading JSON file to GitHub")
    apiRepo = git.Repo(os.path.join("repos", "api-git"))
    apiRepo.index.add([os.path.join("data", "problems_solved.json")])
    apiRepo.index.commit(f"Updated problem_solved.json ({currentTime})")
    apiRepo.remotes.origin.push()
    print("Finished uploading JSON file to GitHub")


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
            args["auto"] = strToBool(argsUnparsed[0])
            args["leetcode"] = strToBool(argsUnparsed[1])
            args["csv"] = strToBool(argsUnparsed[2])
            args["json"] = strToBool(argsUnparsed[3])
            args["debug"] = strToBool(argsUnparsed[4])
        else:
            raise Exception("Invalid arguments (num of args)")
# Manual interpretation
if not args["auto"]:
    print("""
.__                 __                   .___                 
                              
|  |   ____   _____/  |_  ____  ____   __| _/____   ___________ _______  ______ ___________ 
|  | _/ __ \_/ __ \   __\/ ___\/  _ \ / __ |/ __ \  \____ \__  \\\\_  __ \/  ___// __ \_  __ \\
|  |_\  ___/\  ___/|  | \  \__(  <_> ) /_/ \  ___/  |  |_> > __ \|  | \/\___ \\\\  ___/|  | \/
|____/\___  >\___  >__|  \___  >____/\____ |\___  > |   __(____  /__|  /____  >\___  >__|   
          \/     \/          \/           \/    \/  |__|       \/           \/     \/       
    """)
    print("Welcome to Leetcode parser. This application takes your leetcode github repository and compresses into different file formats.")
    print("Of course, you knew that already because this is a very specified program that only works with your github repo.")
    print("\n"*3)
    PullFromGithub(YesOrNoQuestion(
        "Would you like to pull the newest version of the repo from GitHub?"))
    GatherInfo()
    SortProblems()
    print(f"Problems Solved: {easyProblemsSolved + mediumProblemsSolved + hardProblemsSolved} (E: {easyProblemsSolved}, M: {mediumProblemsSolved}, H:{hardProblemsSolved})")
    print(problems)
    PrintDebug(YesOrNoQuestion(
        "Would you like to print the debug table?"))
    CreateCSV(YesOrNoQuestion(
        "Would you like to create the CSV file?"))
    CreateJSON(YesOrNoQuestion(
        "Would you like to create the JSON file?"))    
    UploadJSON(YesOrNoQuestion(
        "Would you like to upload this JSON file?"))
    exit()

#### AUTO VERSION #####
PullFromGithub(args["leetcode"])
GatherInfo()
SortProblems()
PrintDebug(args["debug"])
CreateCSV(args["csv"])
CreateJSON(args["json"])
UploadJSON(args["json"])