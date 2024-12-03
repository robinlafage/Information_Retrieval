import re

class Tokenizer:
    def __init__(self):
        self.token_to_id = {"<PAD>":0, "<UNK>":1}
        self.vocab_size = len(self.token_to_id)
        self.index=2
        self.padding_size = 0

    def __call__(self, text):
        # converts the text to a sequence of token ids
        tokenIds = []
        terms =  re.split('[?.,!:;/\n ]', text)
        terms = list(filter(None, terms))
        for i in range(self.padding_size):
          if i < len(terms):
            tokenIds.append(self.token_to_id[terms[i].lower()])
          else :
            tokenIds.append(self.token_to_id['<PAD>'])
        return tokenIds

    def fit(self, question, document):
      text = question+document
      terms =  re.split('[?.,!:;/\n ]', text)
      terms = list(filter(None, terms))
      for token in terms:
        token = token.lower()
        if token not in self.token_to_id:
          self.token_to_id[token] = self.index
          self.index+=1
      self.vocab_size = len(self.token_to_id)
      self.padding_size = max(len(question.split()), len(document.split()))

