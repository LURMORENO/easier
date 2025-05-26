from gensim.models import KeyedVectors

class word2vec:
    model = KeyedVectors.load_word2vec_format("/app/resources/sbw_vectors.bin",binary=True)

    def __init__(self):
        self.data = []

    def similarity(self, word, wordcompare):
        if word in self.model.wv.vocab and wordcompare in self.model.wv.vocab:
            dis1 = self.model.wv.similarity(word, wordcompare)
            return dis1
        else:
            return 0

    def wordvector(self, word):
        if word in self.model.wv.vocab:
            wordvector = self.model.wv[word]
        else:
            wordvector = [0] * 300
        return wordvector