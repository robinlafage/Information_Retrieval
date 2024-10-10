# Group 02

import argparse
from indexer import *
import time

def main():
    argsParser = readCommandLineArgs()

    args = argsParser.parse_args()
    if args.command == "index":
        print("Building the inverted index")

        tokenizerOptions = {
            "minimumTokenLength": args.minimumTokenLength,
            "normalizeToLower" : args.normalizeToLower,
            "cuttingCharactersFile" : args.cuttingCharactersFile,
            "stopWordsFile" : args.stopWordsFile,
            "useStemming" : args.useStemming
        }
        indexer = Indexer(args.inputFile, args.outputFile, tokenizerOptions)
        indexer.buildIndex()
        
    elif args.command == "search":
        print("Searcher engine")
        print(f"Index file: {args.indexFile}")
    else:
        argsParser.print_help()
    
    
def readCommandLineArgs():
    argsParser = argparse.ArgumentParser(description='A Information Retrieval System for the first assignment of the RI course at Universidade de Aveiro')
    subparsers = argsParser.add_subparsers(dest="command", help="Available commands")

    indexer_parser = subparsers.add_parser("index", help="Build the inverted index")
    indexer_parser.add_argument("inputFile", type=str, help="Files to index")
    indexer_parser.add_argument("outputFile", type=str, help="File to save the index")
    indexer_parser.add_argument("-m", "--minimumTokenLength", type=int, default=1, help="Minimum token length to be indexed")
    indexer_parser.add_argument("-w","--stopwordsFile", type=str, default="../stopwords-en.txt", help="File containing stopwords")
    indexer_parser.add_argument("-c", "--cuttingCharactersFile", type=str, default="../cuttingCharacters.txt", help="File containing characters to cut")
    indexer_parser.add_argument("-n", "--normalizeToLower", type=bool, default=True, help="To activate or not the normalization to lower case")
    indexer_parser.add_argument("-s", "--useStemming", type=bool, default=True, help="To activate or not the stemming after tokenization")

    searcher_parser = subparsers.add_parser("search", help="Searcher engine")
    searcher_parser.add_argument("indexFile", type=str, help="File with the inverted index")

    return argsParser

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(f"Execution time: {end - start} seconds - {(end - start) / 60} minutes")

