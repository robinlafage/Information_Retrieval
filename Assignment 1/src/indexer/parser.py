import json

class Parser:
    def __init__(self, line):
        self.line = line
        self.docId = None
        self.text = None

    def parse(self):
        jsonLine = json.loads(self.line)
        self.docId = jsonLine["doc_id"]
        self.text = jsonLine["text"]