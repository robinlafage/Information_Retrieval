from tokenizer import Tokenizer
from CNNInteractionBasedModel import CNNInteractionBasedModel

def main():
    question = "Which name is also used to describe the Amazon rainforest in English?"
    document = "The Amazon rainforest, also known in English as Amazonia or the Amazon Jungle"

    question2 = "Which name is also used to describe the Amazon rainforest in English?"
    document2 = "The Amazon rainforest, also known in English as Amazonia or the Amazon Jungle forever and ever and ever"

    tokenizer = Tokenizer()
    tokenizer.fit(question, document)
    tokenizer.fit(question2, document2)
    model = CNNInteractionBasedModel(tokenizer.vocab_size)
    query_ids = tokenizer(question)
    document_ids = tokenizer(document)

    model(query_ids, document_ids)

    query_ids2 = tokenizer(question2)
    document_ids2 = tokenizer(document2)

    model(query_ids2, document_ids2)

if __name__ == "__main__":
    main()