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
pip install nltk  
pip install scikit-learn  
pip install regex (à vérifier)
```

# Indexer Engine

### SPIMI implementation

### Tokenizer

The tokenizer is using two input files : 
- The stop words file contains all the words considered not worth of tokenizing. This permits to limit the index size by not getting the too common words. This file have to contain all the words in lowercase.
- The allowed characters file represents the characters we will add in the token. When the tokenizer encounter any character that is not in this file, the character is cutted out of the token. In this file, all the characters should be lowercase, as the tokenizer checks if the character of the input flow is equal, in lowercase, to any of the characters in the file.

If the stop words file is missing or unreadable, we assume there is no stop word. If the allowed character file is missing or unreadable, we assume the only allowed characters are the letters. 

When the tokenizer is registering a new token, it checks if it has to be in lowercase via checking a variable set in the command line. After this the tokenizer checks if the token is a stop word, and suppress it if it is one. Another important value to be checked is the token length. If it is smaller than a threshold set in the command line, then the token is suppressed. 

The stemming of the tokens is not handled by the tokenizer in a process of optimization.

### Index files

The index file is firstly written in a big jsonl file. It permits to iterate over each line without having to load the full index in memory. Using this process, we then split the index in smaller indexes depending on the first letter of each token. With this process, we have an index for each character of the allowed character file. It permits to access each token more easily in the searcher. 

We can see here the list of indexes : ![alt text](image-1.png)
Here is an exemple of the content of an index file : ![alt text](image-2.png)

### Optimization techniques

The first important optimization is the handling of the stemming. In order to avoid stemming the same token multiple times in the same partial index, the stemming is launched just before writing the partial index in a file. By doing this, all the tokens to stem are unique to this partial index. This optimization permits to save up to **50%** of computation time.

Another optimization is for merging the partial indexes. In order accelerate this part, we make sure to merge partial indexes of approximately the same size if possible. This optimization saves up to **10 minutes**.

### Indexing time

The following times include the calculation of the various documents length and total length, which are used for the searcher and take about 1 minute and 30 seconds, and the split of the index which is about 1 minute.
- With the configuration using the minimal token length of 1 and stemming the total time comes to ** minutes**.
- With the configuration using the minimal token length of 1 and no stemming the total time comes to **17 minutes**.
- Without the optimization techniques told earlier, we had came up with times over **45 minutes** for the indexing. This shows the importance of optimizations.

It is important to note that these times may vary depending on the computer launching the indexer.

# Searcher Engine

### Implemented search algorithm

### Optimization techniques

In order to reduce the time to search for a token, while not having to load the index in memory, we used some optimization techniques : 

- The first one is splitting the index depending on the first character of the token. Assuming the index is ordered, it's a task that does take only about 1 minute, and permits to gain a lot of time on searching. 

- The second major optimization is done during searching. In order to avoid looking at each line of the index to check if it is the right token, we simply read one line every thousand of line. If the token on this line is greater than our researched token, then we have a slice of 1000 lines in which it is fast enough to check each line until we reach our token. 
By doing this, we reduce the average query processing time by **75%**. 

### Average query processing time

Using the questions.jsonl file given with the subject, we have an average query time of **1 second**.
It is important to note that this time may vary depending on the computer launching the searcher.

# Ranking Metrics

# Additional Information

Here is the Command Line Interface help menus :

# Conclusion
