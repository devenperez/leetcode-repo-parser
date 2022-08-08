class Problem:
    def __init__(self, number, name) -> None:
        self.number = number
        self.name = name

        self.time = 0.0
        self.timePercentile = 0.0
        self.memory = 0.0
        self.memoryPercentile = 0.0

        self.difficulty = ""
        self.codeFolder = ""
        self.language = ""

    def __repr__(self) -> str:
        return f"{self.number}. {self.name} {self.language} ({self.difficulty}) {self.time} ({self.timePercentile}) {self.memory} ({self.memoryPercentile}) "

    def toCSV(self) -> str:
        return f"{self.number},{self.name},{self.difficulty},{self.language},{self.time},{self.timePercentile}%,{self.memory},{self.memoryPercentile}%,{self.codeFolder}"
