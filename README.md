# Information Retrieval project - Universidade de Aveiro

This repository contains the code and documentation for the Information Retrieval project developed as part of the course at Universidade de Aveiro.  
The main objective of this project is to identify and retrieve the most relevant documents from a given corpus in response to a user's query.  

## Project Structure
The project is organized into the following directories:
- `Assignment1/`: Contains the code and resources for the Indexer and the BM25 searcher.
- `Assignment2/`: Contains the code and resources for the Neural Reranker.  

## Overview
1. **Indexer**: The indexer processes the document corpus and creates an inverted index that maps terms to their corresponding documents. This index is essential for efficient search and retrieval operations.
2. **BM25 Searcher**: The BM25 searcher utilizes the BM25 ranking algorithm to retrieve documents that are most relevant to the user's query based on the indexed data.
3. **Neural Reranker**: The Neural Reranker takes the initial set of documents retrieved by the BM25 searcher and re-ranks them using a neural network model to improve the relevance of the results.