class Problem:
    def __init__(self, number, name) -> None:
        self.number = number
        self.name = name
        self.difficulty = ""
        self.codeFolder = ""

        self.stats = []


    def __repr__(self) -> str:
        return f"{self.number}. {self.name} {self.language} ({self.difficulty}) {self.time} ({self.timePercentile}) {self.memory} ({self.memoryPercentile}) "

    def toCSV(self) -> str:
        return f"{self.number},{self.name},{self.difficulty},{self.language},{self.time},{self.timePercentile}%,{self.memory},{self.memoryPercentile}%,{self.codeFolder}"

    def getOrAddStats(self, lang):
        match = [ps for ps in self.stats if ps.language == lang]
        if len(match) == 0:
            self.stats.append(ProbStats(lang))
            return self.stats[-1]
        else:
            return match[0]

    def validate(self, lang):
        self.getOrAddStats(lang).codeAdded = True

class ProbStats:
    def __init__(self, language) -> None:
        self.time = 0.0
        self.timePercentile = 0.0
        self.memory = 0.0
        self.memoryPercentile = 0.0

        self.language = language
        self.codeAdded = False
    
    def addStats(self, time = -1, timePercentile = -1, memory = -1, memoryPercentile = -1):
        self.time = time if time > 0 else self.time
        self.timePercentile = timePercentile if timePercentile > 0 else self.timePercentile
        self.memory = memory if memory > 0 else self.memory
        self.memoryPercentile = memoryPercentile if memoryPercentile > 0 else self.memoryPercentile