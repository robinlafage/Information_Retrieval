# How to run the programm

## Steps to install all dependencies :

Firstly, install python version >= python3.8 : 
```
sudo apt install python3.10
```

Then, install python-pip : 
```
sudo apt install python3-pip
```

Then you can download all the packages : 
```
pip install -r requirements.txt
```

## Indexer

To run the indexer, you have to run the following command : 
```
python3 src/main.py index [-h] [-m MINIMUMTOKENLENGTH] [-s STOPWORDSFILE] [-a ALLOWEDCHARACTERSFILE] [--normalizeToLower | --no-normalizeToLower] [--stemming | --no-stemming] inputFile outputDirectory
```

### Arguments
- inputFile : The path to the file containing the corpus to index.
- outputDirectory : The path to the directory where the index files will be written.

### Options
- -h, --help : Show help message and exit.
- -m, --minimumTokenLength MINIMUMTOKENLENGTH : The minimum length of a token to be indexed. Default value is 1.
- -s, --stopWordsFile STOPWORDSFILE : The path to the file containing the stop words. Default value is None (no stop words).
- -a, --allowedCharactersFile ALLOWEDCHARACTERSFILE : The path to the file containing the allowed characters. Default value is None (only letters are allowed).
- --normalizeToLower, --no-normalizeToLower : Normalize or not all tokens to lowercase. Default value is True.
- --stemming, --no-stemming : Stem or not all tokens. Default value is True.

## Searcher

To run the searcher, you have to run the following command : 
```
python3 src/main.py search [-h] [-q QUERYFILE] [-k1 K1] [-b B] [-m MAXIMUMDOCUMENTS] indexDirectory outputFile
```

### Arguments
- indexDirectory : The path to the directory containing the index files.
- outputFile : The path to the file where the search results will be written.

### Options
- -h, --help : Show help message and exit.
- -q, --queryFile QUERYFILE : The path to the file containing the queries. If this option is not provided, the queries will be read from the standard input.
- -k1 K1 : The k1 parameter of the BM25 ranking function. Default value is 1.2.
- -b B : The b parameter of the BM25 ranking function. Default value is 0.75.
- -m MAXIMUMDOCUMENTS : The maximum number of documents to return for each query. Default value is 100.


# Indexer Engine

### SPIMI implementation

### Tokenizer

The tokenizer is using two input files : 
- The stop words file contains all the words considered not worth of tokenizing. This permits to limit the index size by not getting the too common words. This file have to contain all the words in lowercase.
- The allowed characters file represents the characters we will add in the token. When the tokenizer encounter any character that is not in this file, the character is cutted out of the token. In this file, all the characters should be lowercase, as the tokenizer checks if the character of the input flow is equal, in lowercase, to any of the characters in the file.

If the stop words file is missing or unreadable, we assume there is no stop word. If the allowed character file is missing or unreadable, we assume the only allowed characters are the letters. 

When the tokenizer is registering a new token, it checks if it has to be in lowercase via checking a variable set in the command line. After this the tokenizer checks if the token is a stop word, and suppress it if it is one. Another important value to be checked is the token length. If it is smaller than a threshold set in the command line, then the token is suppressed. 

The stemming of the tokens is not handled by the tokenizer in a process of optimization.

### SPIMI algorithm

We implemented a SPIMI (Single Pass In Memory Indexing) algorithm for constructing the inverted index. This algorithm is used to build the inverted index while utilizing a limited amount of memory.  

#### Step 1 

The first step is to build partial indexes. The algorithm for this step is as follows:

1. We start with an empty dictionary that will hold the partial index currently being constructed.
2. Read a document from the corpus file.
3. Tokenize the line into a list of tokens.
4. If the token is not in the dictionary, add it as a key with a list containing the token's position in the document as its value.
5. If the token is already in the dictionary, add the token's position in the document to the list of positions associated with this token.
6. Repeat steps 2 to 5 for the next documents in the corpus.
7. When the dictionary size exceeds a certain threshold, sort the dictionary alphabetically, write the partial index to a file, and clear the dictionary.
8. Repeat steps 2 to 7 until all documents in the corpus have been processed.

#### Step 2

The second step is to merge the partial indexes. To achieve this, we chose to implement a 2-way merge, which means we merge partial indexes two at a time, then merge the resulting indexes two at a time, and so on until only one index remains, as shown in the following diagram:
![2-wayMerge](/img/2way_merge.png)

The algorithm for merging two temporary indexes is as follows:

1. **Initialization**:
Read a block containing the first terms of each temporary index.

2. **Term comparison:**
Compare the first term of each block:
- Case 1: If the two terms are identical:  
Merge their associated position lists.
Write the merged term into the temporary index.
- Case 2: Otherwise:  
Take the smallest term (lexicographically) and write it into the temporary index.

3. **Advancing within blocks:**
If a term has been taken, read the next term from the corresponding index.
If the terms were identical, advance in both blocks.

4. **Switching blocks:**
If a block is fully processed, load the next block from the corresponding index.

5. **Partial writing:**
If the total number of merged terms exceeds a predefined threshold:
- Write the temporary index to a file.
- Clear the temporary index to free up memory.

6. **End of the algorithm:**
Repeat steps 2 to 5 until all terms from both temporary indexes have been processed.

#### Step 3

The third step is to split the index. This step is necessary to optimize the search process. The index is split into multiple files based on the first character of the terms. This way, when searching for a term, we only need to search in the index file corresponding to the first character of the term, which reduces the search time.

#### Step 4

The fourth and last step is to calculate the document length and the total length of each document. This information is used to calculate the BM25 score during the search process. It is stored in a file named `documentLengths.json`. This file is also used to store metadata about the index : stemming or not, minimal token length, normalization to lowercase or not, allowed characters and stop words.

### Index files

The index files are in JSONL format, which allows iterating line by line without loading the entire file into memory, unlike the JSON format.

We can see here the list of indexes : ![alt text](image-1.png)
Here is an exemple of the content of an index file : ![alt text](image-2.png)

### Optimization techniques

The first important optimization is the handling of the stemming. In order to avoid stemming the same token multiple times in the same partial index, the stemming is launched just before writing the partial index in a file. By doing this, all the tokens to stem are unique to this partial index. This optimization permits to save up to **50%** of computation time.

Another optimization is for merging the partial indexes. In order accelerate this part, we make sure to merge partial indexes of approximately the same size if possible. This optimization saves up to **10 minutes**.

### Indexing time

The following times include the calculation of the various documents length and total length, which are used for the searcher and take about 1 minute and 30 seconds, and the split of the index which is about 1 minute.
- With the configuration using the minimal token length of 1 and stemming the total time comes to **TODO minutes**.
- With the configuration using the minimal token length of 1 and no stemming the total time comes to **17 minutes**.
- Without the optimization techniques told earlier, we had came up with times over **45 minutes** for the indexing. This shows the importance of optimizations.

It is important to note that these times may vary depending on the computer launching the indexer.

# Searcher Engine

## Implemented search algorithm

We have implemented a BM25 ranking algorithm for the search engine. 

### Formula BM25

This algorithm is based on the following formula:
$$
\text{Score}(Q, D) = \sum_{i \in Q} \log{\frac{N}{df_i}} \cdot \frac{(k_1 + 1) \cdot tf_{i, D}}{k_1 \cdot ((1 - b) + b \cdot \frac{L_D}{L_{avg}}) + tf_{i, D}}
$$
Where:
- $Q$: The query
- $D$: The document
- $N$: The total number of documents
- $df_i$: The number of documents containing the term $i$
- $tf_{i, D}$: The number of occurrences of term $i$ in document $D$
- $L_D$: The length of document $D$
- $L_{avg}$: The average document length
- $k_1$ and $b$: Algorithm parameters (default values are $k_1 = 1.2$ and $b = 0.75$)

### Implementation

The search algorithm is implemented as follows:
1. Read the first query from the query file (or the query entered by the user in the terminal).
2. Tokenize the query to extract terms according to the same rules used for the indexer.
3. For each term in the query, calculate the BM25 score for every document containing that term.
4. Add the score obtained to the document's total score.
5. Repeat steps 3 and 4 for every term in the query.
6. Sort the documents in descending order by their total score and keep only the n firts, where n in configured by the user (100 by default).
7. Write the results to the output file.
8. Repeat steps 1 to 7 for each query.

## Optimization techniques

In order to reduce the time to search for a token, while not having to load the index in memory, we used some optimization techniques : 

- The first one is splitting the index depending on the first character of the token. Assuming the index is ordered, it's a task that does take only about 1 minute, and permits to gain a lot of time on searching. 

- The second major optimization is done during searching. In order to avoid looking at each line of the index to check if it is the right token, we simply read one line every thousand of line. If the token on this line is greater than our researched token, then we have a slice of 1000 lines in which it is fast enough to check each line until we reach our token. 
By doing this, we reduce the average query processing time by **75%**. 

## Average query processing time

Using the questions.jsonl file given with the subject, we have an average query time of **1 second**.
It is important to note that this time may vary depending on the computer launching the searcher.

# Ranking Metrics

# Additional Information

## General

Here is the Command Line Interface help menus :
```
usage: main.py [-h] {index,search} ...

An Information Retrieval System for the first assignment of the RI course at Universidade de Aveiro

positional arguments:
  {index,search}  Available commands
    index         Build the inverted index
    search        Searcher engine

options:
  -h, --help      show this help message and exit
```

## Indexer

Here is the help menu for the indexer :
```
usage: main.py index [-h] [-m MINIMUMTOKENLENGTH] [-s STOPWORDSFILE] [-a ALLOWEDCHARACTERSFILE]
                     [--normalizeToLower | --no-normalizeToLower] [--stemming | --no-stemming]
                     inputFile outputDirectory

positional arguments:
  inputFile             File to index
  outputDirectory       Directory to save the indexes

options:
  -h, --help            show this help message and exit
  -m MINIMUMTOKENLENGTH, --minimumTokenLength MINIMUMTOKENLENGTH
                        Minimum token length to be indexed
  -s STOPWORDSFILE, --stopwordsFile STOPWORDSFILE
                        File containing stopwords
  -a ALLOWEDCHARACTERSFILE, --allowedCharactersFile ALLOWEDCHARACTERSFILE
                        File containing allowed characters
  --normalizeToLower, --no-normalizeToLower
                        To activate or not the normalization to lower case (default: True)
  --stemming, --no-stemming
                        To activate or not the stemming after tokenization (default: True)
```

## Searcher

Here is the help menu for the searcher :
```
usage: main.py search [-h] [-q QUERYFILE] [-k1 K1] [-b B] [-m MAXIMUMDOCUMENTS] indexDirectory outputFile

positional arguments:
  indexDirectory        Directory containing the index files
  outputFile            File where the results are saved

options:
  -h, --help            show this help message and exit
  -q QUERYFILE, --queryFile QUERYFILE
                        File containing the queries. If this option is not provided, the user can input the queries interactively
  -k1 K1                BM25 k1 parameter
  -b B                  BM25 b parameter
  -m MAXIMUMDOCUMENTS, --maximumDocuments MAXIMUMDOCUMENTS
                        Maximum number of documents to return
```


# Conclusion
