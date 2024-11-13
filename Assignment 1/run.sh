#!/bin/bash

#Important note
#In order for the searcher to function well, you have to launch this script while in the directory where it is located

cd src

# To run the indexer
python3 main.py index ../MEDLINE_2024_Baseline.jsonl ../indexes/ -s ../stopwords-en.txt -c ../allowedCharacters.txt

# To run the searcher on a question file 
python3 main.py search -q ../questions.jsonl ../indexes/ ../results.jsonl

# To run the searcher in interactive mode
python3 main.py search ../indexes/ ../results.jsonl