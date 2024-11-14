import json
import math
import os
import time

class Merger:
    def __init__(self, inputFile, outputDirectory, tokenizerOptions, stemmerOptions, temporaryIndexesDirectory):
        self.inputFile = inputFile
        self.outputDirectory = outputDirectory
        self.tempDict = {}
        self.jsonList = list()
        self.temporaryIndexesDirectory = temporaryIndexesDirectory
        self.tokenizerOptions = tokenizerOptions
        self.stemmerOptions = stemmerOptions
        self.outputFile = 'output.jsonl'

    def merge(self):
        """
        Given the temporary indexes directory, this function merges all the partial indexes.
        When all the partial indexes are merged, the file outputFile is created.
        """
        files = self.getFilesFromDirectory(self.temporaryIndexesDirectory)
        i = 0
        if not os.path.exists(self.outputDirectory):
            os.mkdir(self.outputDirectory)
        
        if os.path.exists(self.outputFile):
            os.remove(self.outputFile)
            
        #Cleaning the output directory
        filesInOutputDir = self.getFilesFromDirectory(self.outputDirectory)
        if len(filesInOutputDir) > 0 :
            for file in filesInOutputDir :
                os.remove(f"{self.outputDirectory}/{file}")

        #If we only have 1 file, then we create an empty one in order to merge it with the first one.
        #This is made to make sure we enter in the while loop without letting any file unmerged.
        if len(files) == 1 :
            with open("empty_file.jsonl", "w") as file :
                files.append("empty_file.jsonl")
            file.close()
        while len(files) > 1:
            # Take first two files
            file1 = files.pop(0)
            file2 = files.pop(0)
            
            # Define a temporary file hosting the merge
            mergedFile = f"{self.temporaryIndexesDirectory}/mergedPart{i}.jsonl"  
        
            # Call the merging function
            if len(files) == 0:
                self.merge2Indexes(file1, file2, self.outputFile, False)
            else :
                self.merge2Indexes(file1, file2, mergedFile, False)
            
            # Delete merged files
            os.remove(file1)
            os.remove(file2)
            
            # Add merged file to the list
            if not len(files) == 0 :
                files.append(mergedFile)
            i += 1
    
        #On end, we split the index
        self.cutIndexDependingOnLetters()
        os.rmdir(self.temporaryIndexesDirectory)
        os.remove(self.outputFile)


    def getFilesFromDirectory(self, directory):
        """
        Given a directory, this function return a list of the files of the directory

        Args:
            directory (string): directory path (absolute or relative)

        Returns:
            [string]: list of the files of the directory
        """
        try:
            all_items = os.listdir(directory)
            
            files = [f"{directory}/{f}" for f in all_items if os.path.isfile(os.path.join(directory, f))]
            
            return files
        except FileNotFoundError:
            print(f"Directory '{directory}' doesn't exist.")
            return []

    def merge2Indexes(self, file1, file2, mergedFile, final):
        """
        Merge two indexes into one.

        Args:
            file1: the first index file.
            file2: the second index file
            mergedFile: the output file
            final: whether this is the final merge or not : if it is, the output will be a json file, otherwise it will be a jsonl file (not used anymore).
        """

        nbLines = 10000
        maxTerms = 1000

        i1 = -1
        i2 = -1

        with open(file1, "r") as index1, open(file2, "r") as index2:
            stop1 = False
            stop2 = False
            while True:
                if i1 == -1 or i1 == len(index1Lines):
                    index1Lines = [json.loads(line) for line in [index1.readline() for _ in range(nbLines)] if line]
                    i1 = 0
                    if not index1Lines:
                        stop1 = True
                if i2 == -1 or i2 == len(index2Lines):
                    index2Lines = [json.loads(line2) for line2 in [index2.readline() for _ in range(nbLines)] if line2]
                    i2 = 0
                    if not index2Lines:
                        stop2 = True

                if stop1 == True and stop2 == True:
                    break
                
                elif stop1 == True : 
                    while (i2 < len(index2Lines)):
                        if final:
                            self.tempDict.update(index2Lines[i2])
                        else:
                            self.jsonList.append(index2Lines[i2])
                        i2 += 1
                elif stop2 == True :
                    while (i1 < len(index1Lines)):
                        if final:
                            self.tempDict.update(index1Lines[i1])
                        else:
                            self.jsonList.append(index1Lines[i1])
                        i1 += 1
                
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

                if len(self.jsonList) >= maxTerms:
                    self.appendToJsonl(mergedFile)

        if self.jsonList:
            self.appendToJsonl(mergedFile)


    def merge2Dicts(self, d1, d2, term):
        """Given 2 dictionaries and a key, this function merge their values for this key.

        Args:
            d1 (dict): First dictionary
            d2 (dict): Second dictionary
            term (string): Key to merge 

        Returns:
            dict: Result of the merge
        """
        res = d1.copy()
        res[term].update(d2[term])
        return res


    def appendToJsonl(self, outputFile):
        """This function append a json list into a jsonl file

        Args:
            outputFile (string): Path of the file in which the jsonl will be written
        """
        with open(outputFile, "a+") as file:
            for d in self.jsonList:
                file.write(json.dumps(d))
                file.write("\n")
            self.jsonList.clear()

    
    def cutIndexDependingOnLetters(self):
        """
        This function has for objective to split the index depending on the first letter of each token.
        This permits to fasten the searcher.
        """
        characterToPut = ''
        nbLines = 10000
        i = 0
        with open(self.outputFile, 'r') as indexFile:
            line = indexFile.readline()
            while line != '' :
                #If we arrived at the maximum number of lines in memory, then we write out in the file
                if i==nbLines :
                    self.appendToJsonl(f"{self.outputDirectory}/index_by_character_{characterToPut}.jsonl")
                    i = 0
                linejson = json.loads(line)
                token = list(linejson.keys())[0]
                if characterToPut == '' :
                    characterToPut = token[0].lower()
                #If the first letter of the token is the same as the character to put, then we add the json line into the list to write
                if token[0].lower() == characterToPut :
                    self.jsonList.append(linejson)
                    i+=1
                #If the first letter of the token is not the same as the character to put, it means we are going to the next index.
                #This is possible because the index is sorted.
                else :
                    self.appendToJsonl(f"{self.outputDirectory}/index_by_character_{characterToPut}.jsonl")
                    i = 0
                    characterToPut = token[0].lower()
                    self.jsonList.append(linejson)   
                    i+=1   
                line = indexFile.readline()
            #At the end of the loop, if the list isn't empty we write it in the appropriate file before ending the function
            if self.jsonList != [] :
                self.appendToJsonl(f"{self.outputDirectory}/index_by_character_{characterToPut}.jsonl")
