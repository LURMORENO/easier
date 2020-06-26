from fasttext import load_model

class FastText:
    f = load_model("../backend/resources/fasttxt/cc.es.300.bin")

    def __init__(self):
        self.data = []

    def wordvector(self, word):
       try:
            wordvector = self.f.get_word_vector(word)
            return wordvector
       except:
            wordvector = [0] * 300
            return wordvector