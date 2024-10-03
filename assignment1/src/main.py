import argparse
from indexer import *

def main():
    parser = readCommandLineArgs()

    args = parser.parse_args()
    if args.command == "index":
        print("Building the inverted index")

        indexer = Indexer(args.inputFile, args.outputFile)
        indexer.buildIndex()
        
    elif args.command == "searcher":
        print("Searcher engine")
        print(f"Index file: {args.indexFile}")
    else:
        parser.print_help()
    
    
def readCommandLineArgs():
    parser = argparse.ArgumentParser(description='A Information Retrieval System for the first assignment of the RI course at Universidade de Aveiro')
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    indexer_parser = subparsers.add_parser("index", help="Build the inverted index")
    indexer_parser.add_argument("inputFile", type=str, help="Files to index")
    indexer_parser.add_argument("outputFile", type=str, help="File to save the index")

    searcher_parser = subparsers.add_parser("searcher", help="Searcher engine")
    searcher_parser.add_argument("indexFile", type=str, help="File with the inverted index")

    return parser

if __name__ == '__main__':
    main()

