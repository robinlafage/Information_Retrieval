from parser import *

class Indexer:
    def __init__(self, inputFile, outputFile, minimumTokenLength):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.minimumTokenLength = minimumTokenLength

    def buildIndex(self):
        start = 0
        end = 10

        parser = Parser(None)

        with open(self.inputFile, "r") as file:
            for i, line in enumerate(file):
                if i < start:
                    continue 
                if i >= end:
                    break 
                parser.line = line
                parser.parse()
                print(f"DocId: {parser.docId}")
                print(f"Text: {parser.text}")