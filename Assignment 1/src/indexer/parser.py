import json

class Parser:
    def __init__(self, line):
        self.line = line
        self.docId = None
        self.text = None

    def parse(self):
        """
        Given a string representing a document of the corpus, 
        this function separate the doc ID and the text of a document.
        """
        jsonLine = json.loads(self.line)
        self.docId = jsonLine["doc_id"]
        self.text = jsonLine["text"]