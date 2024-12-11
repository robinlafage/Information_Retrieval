import re
import torch

class Tokenizer:
    def __init__(self):
        self.token_to_id = {"<PAD>": 0, "<UNK>": 1}
        self.vocab_size = len(self.token_to_id)
        self.index = 2
        self.padding_size = 0

    def __call__(self, text):
        """
        Convertit le texte en une séquence d'identifiants de tokens.

        Args:
            text (str): Le texte à tokenizer.

        Returns:
            List[int]: Liste des identifiants des tokens avec padding.
        """
        token_ids = []
        terms = re.split(r'[?.,!:;/\n ]', text)  # Découpe le texte
        terms = list(filter(None, terms))  # Filtre les chaînes vides

        for i in range(self.padding_size):
            if i < len(terms):
                if terms[i].lower() in self.token_to_id:
                    token_ids.append(self.token_to_id[terms[i].lower()])
                else:
                    token_ids.append(self.token_to_id["<UNK>"])
            else:
                token_ids.append(self.token_to_id['<PAD>'])

        return token_ids

    def fit(self, document):
        """
        Crée le vocabulaire en s'adaptant aux données.

        Args:
            question (str): Texte des questions.
            document (str): Texte des documents.
        """
        text = document
        terms = re.split(r'[?.,!:;/\n ]', text)
        terms = list(filter(None, terms))

        for token in terms:
            token = token.lower()
            if token not in self.token_to_id:
                self.token_to_id[token] = self.index
                self.index += 1

        self.vocab_size = len(self.token_to_id)
        if self.padding_size < len(document.split()):
          self.padding_size =len(document.split())

    def to_tensor(self, text, device=None):
        """
        Convertit le texte en un tenseur PyTorch d'identifiants de tokens.

        Args:
            text (str): Le texte à tokenizer.
            device (torch.device, optional): L'appareil sur lequel placer le tenseur.

        Returns:
            torch.Tensor: Tenseur des identifiants des tokens.
        """
        token_ids = self(text)
        tensor = torch.tensor(token_ids, dtype=torch.long)
        if device:
            tensor = tensor.to(device)
        return tensor
