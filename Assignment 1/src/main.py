# Group 02

import argparse
from indexer.indexer import *
from searcher.searcher import *
import time

def main():
    argsParser = readCommandLineArgs()

    args = argsParser.parse_args()
    if args.command == "index":
        print("Building the inverted index...")

        tokenizerOptions = {
            "minimumTokenLength": args.minimumTokenLength,
            "normalizeToLower" : args.normalizeToLower,
            "allowedCharactersFile" : args.allowedCharactersFile,
            "stopwordsFile" : args.stopwordsFile,
        }

        stemmerOptions = {
            "stemming" : args.stemming
        }

        indexer = Indexer(args.inputFile, args.outputFile, tokenizerOptions, stemmerOptions)
        indexer.buildIndex()
        
    elif args.command == "search":
        searcherOptions = {
            "queryFile": args.queryFile,
            "k1": args.k1,
            "b": args.b,
            "maximumDocuments": args.maximumDocuments
        }

        searcher = Searcher(args.indexDirectory, args.outputFile, searcherOptions)
        searcher.search()
    else:
        argsParser.print_help()
    
    
def readCommandLineArgs():
    argsParser = argparse.ArgumentParser(description='A Information Retrieval System for the first assignment of the RI course at Universidade de Aveiro')
    subparsers = argsParser.add_subparsers(dest="command", help="Available commands")

    # Indexer parser
    indexer_parser = subparsers.add_parser("index", help="Build the inverted index")
    indexer_parser.add_argument("inputFile", type=str, help="Files to index")
    indexer_parser.add_argument("outputFile", type=str, help="File to save the index")
    indexer_parser.add_argument("-m", "--minimumTokenLength", type=int, default=1, help="Minimum token length to be indexed")
    indexer_parser.add_argument("-w","--stopwordsFile", type=str, default="../stopwords-en.txt", help="File containing stopwords")
    indexer_parser.add_argument("-a", "--allowedCharactersFile", type=str, default="../allowedCharacters.txt", help="File containing characters to cut")
    indexer_parser.add_argument("--normalizeToLower", type=bool, default=True, help="To activate or not the normalization to lower case", action=argparse.BooleanOptionalAction)
    indexer_parser.add_argument("--stemming", type=bool, default=True, help="To activate or not the stemming after tokenization", action=argparse.BooleanOptionalAction)
    
    # Searcher parser
    searcher_parser = subparsers.add_parser("search", help="Searcher engine")
    searcher_parser.add_argument("indexDirectory", type=str, help="Directory containing the index files")
    searcher_parser.add_argument("outputFile", type=str, help="File to save the results")
    searcher_parser.add_argument("-q", "--queryFile", type=str, help="File containing the queries")
    searcher_parser.add_argument("-k1", type=float, default=1.2, help="BM25 k1 parameter")
    searcher_parser.add_argument("-b", type=float, default=0.75, help="BM25 b parameter")
    searcher_parser.add_argument("-m", "--maximumDocuments", type=int, default=100, help="Maximum number of documents to return")

    return argsParser

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(f"Execution time: {end - start} seconds - {(end - start) / 60} minutes")

