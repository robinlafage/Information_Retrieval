import json
import os

class Merger:
    def __init__(self, outputFile):
        self.outputFile = outputFile
        self.tempDict = {}
        self.jsonList = list()
        self.indexesDir = "../tmpIndexes"


    def merge(self):
        files = self.getFilesFromDirectory(self.indexesDir)
        i = 0
        while len(files) > 2:
            # Prendre les deux premiers fichiers
            file1 = files.pop(0)
            file2 = files.pop(0)
            
            # Définir un fichier temporaire pour la fusion
            mergedFile = f"{self.indexesDir}/mergedPart{i}.jsonl"  # Nom temporaire, à renommer après chaque fusion
            
            # Appel de la fonction de fusion des deux fichiers
            self.merge2Indexes(file1, file2, mergedFile, False)
            
            # Supprimer les deux fichiers fusionnés
            os.remove(file1)
            os.remove(file2)
            
            # Ajouter le fichier fusionné à la liste
            files.insert(0, mergedFile)

            i += 1


        self.merge2Indexes(files[0], files[1], self.outputFile, True)
        os.remove(files[0])
        os.remove(files[1])

        with open(self.outputFile, "a+") as file:
            file.write("}")


    def getFilesFromDirectory(self, directory):
        try:
            all_items = os.listdir(directory)
            
            files = [f"{directory}/{f}" for f in all_items if os.path.isfile(os.path.join(directory, f))]
            
            return files
        except FileNotFoundError:
            print(f"Le répertoire '{directory}' n'existe pas.")
            return []

    def merge2Indexes(self, file1, file2, mergedFile, final):
        nbLines = 100
        maxTerms = 1000

        i1 = -1
        i2 = -1

        with open(file1, "r") as index1, open(file2, "r") as index2:
            stop = 0
            while True:
                if i1 == -1 or i1 == len(index1Lines):
                    index1Lines = [json.loads(line) for line in [index1.readline() for _ in range(nbLines)] if line]
                    i1 = 0
                    if not index1Lines:
                        stop += 1
                if i2 == -1 or i2 == len(index2Lines):
                    index2Lines = [json.loads(line2) for line2 in [index2.readline() for _ in range(nbLines)] if line2]
                    i2 = 0
                    if not index2Lines:
                        stop += 1

                if stop == 2:
                    break

                
                while (i1 < len(index1Lines) and i2 < len(index2Lines)):
                    term1 = list(index1Lines[i1].keys())[0]
                    term2 = list(index2Lines[i2].keys())[0]

                    if term1 < term2:
                        if final:
                            self.tempDict.update(index1Lines[i1])
                        else:
                            self.jsonList.append(index1Lines[i1])
                        i1 += 1
                    elif term2 < term1:
                        if final:
                            self.tempDict.update(index2Lines[i2])
                        else:
                            self.jsonList.append(index2Lines[i2])
                        i2 += 1
                    elif term1 == term2:
                        d = self.merge2Dicts(index1Lines[i1], index2Lines[i2], term1)
                        if final:
                            self.tempDict.update(d)
                        else:
                            self.jsonList.append(d.copy())
                        d.clear()
                        i1 += 1
                        i2 += 1

                if len(self.tempDict) >= maxTerms:
                    self.appendToIndex(self.tempDict, mergedFile)
                    self.tempDict = {}

                if len(self.jsonList) >= maxTerms:
                    self.appendToJsonl(mergedFile)

        if self.tempDict:
            self.appendToIndex(self.tempDict, mergedFile)
            self.tempDict = {}

        if self.jsonList:
            self.appendToJsonl(mergedFile)
                
    
    
    def appendToIndex(self, tmpDict, outputFile):
        with open(outputFile, "a+") as file:
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


    def appendToJsonl(self, outputFile):
        with open(outputFile, "a+") as file:
            for d in self.jsonList:
                file.write(json.dumps(d))
                file.write("\n")
            self.jsonList.clear()


if __name__ == "__main__":
    merger = Merger("out.json")
    merger.merge2Indexes("../tmpIndexes/merged.jsonl", "../tmpIndexes/indexPart2.jsonl", "../tmpIndexes/merged2.jsonl", False)