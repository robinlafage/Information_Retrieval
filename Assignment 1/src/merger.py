import json

class Merger:
    def __init__(self, outputFile):
        self.outputFile = outputFile
        self.tempDict = {}


    def merge(self):
        i = 0
        while True:
            try:
                self.merge2Indexes(i, i+1)
                i += 2
            except FileNotFoundError:
                try:
                    with open(f"../tmpIndexes/indexPart{i}.jsonl"):
                        self.appendLastFile(i)
                except FileNotFoundError:
                    pass
                break


        with open(self.outputFile, "a+") as file:
            file.write("}")


    def merge2Indexes(self, a, b):
        nbLines = 100
        maxTerms = 1000

        i1 = -1
        i2 = -1

        with open(f"../tmpIndexes/indexPart{a}.jsonl", "r") as index1, open(f"../tmpIndexes/indexPart{b}.jsonl", "r") as index2:
            while True:
                stop = 0
                if i1 == -1 or i1 == len(index1Lines):
                    index1Lines = [json.loads(line) for line in [index1.readline() for _ in range(nbLines)] if line]
                    i1 = 0
                    if not index1Lines:
                        print("break 1")
                        stop += 1
                if i2 == -1 or i2 == len(index2Lines):
                    index2Lines = [json.loads(line2) for line2 in [index2.readline() for _ in range(nbLines)] if line2]
                    i2 = 0
                    if not index2Lines:
                        print("break 2")
                        stop += 1

                if stop == 2:
                    break

                
                while (i1 < len(index1Lines) and i2 < len(index2Lines)) or (i1 == len(index1Lines) and i2 < len(index2Lines)) or (i1 < len(index1Lines) and i2 == len(index2Lines)):
                    if i1 == len(index1Lines):
                        term1 = None
                    else:
                        term1 = list(index1Lines[i1].keys())[0]

                    if i2 == len(index2Lines):
                        term2 = None
                    else:
                        term2 = list(index2Lines[i2].keys())[0]

                    termToTreat = 0
                    if term1 is not None and term2 is not None:
                        if term1 < term2:
                            termToTreat = 1
                        elif term1 > term2:
                            termToTreat = 2
                        else:
                            termToTreat = 3
                    elif term1 is not None:
                        termToTreat = 1
                    elif term2 is not None:
                        termToTreat = 2

                    if termToTreat == 1:
                        self.tempDict.update(index1Lines[i1])
                        i1 += 1
                    elif termToTreat == 2:
                        self.tempDict.update(index2Lines[i2])
                        i2 += 1
                    elif termToTreat == 3:
                        d = self.merge2Dicts(index1Lines[i1], index2Lines[i2], term1)
                        self.tempDict.update(d)
                        d.clear()
                        i1 += 1
                        i2 += 1

                if len(self.tempDict) >= maxTerms:
                    self.appendToIndex(self.tempDict)
                    self.tempDict = {}

        if self.tempDict:
            self.appendToIndex(self.tempDict)
            self.tempDict = {}
                
    
    
    def appendToIndex(self, tmpDict):
        with open(self.outputFile, "a+") as file:
            if file.tell() == 0:
                file.write("{")
            else:
                file.seek(file.tell() - 1)
                file.write(", ")

            for key, dict2 in tmpDict.items():
                file.write(f"\"{key}\": {{")
                for i, (key2, value) in enumerate(dict2.items()):
                    file.write(f"\"{key2}\": {value}")
                    if i < len(dict2) - 1:
                        file.write(", ")
                file.write("}")
                if list(tmpDict.keys())[-1] != key:
                    file.write(", ")
    


    def merge2Dicts(self, d1, d2, term):
        res = d1.copy()
        res[term].update(d2[term])
        return res
    

    def appendLastFile(self, i):
        dictToAppend = {}

        with open(f"../tmpIndexes/indexPart{i}.jsonl", "r") as file:
            for line in file:
                dictToAppend.update(json.loads(line))

        self.appendToIndex(dictToAppend)
        dictToAppend.clear()



if __name__ == "__main__":
    merger = Merger("out.json")
    merger.merge2Indexes(0, 1)