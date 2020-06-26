import os
import spacy
from resources.clasificador import clasificador
clasificadorobj=clasificador()

class text2tokens:
    nlp = spacy.load('es_core_news_md')

    def text2sentences(self,text):
        lista_oraciones = list()
        document = self.nlp(text)
        for s in document.sents:
            lista_oraciones.append(s.text)
        
        return lista_oraciones

    def sentence2tokens(self,sentence):
        listapalabras=list()
        oracion=self.nlp(sentence)
        for j,token in enumerate(oracion):
            if (token.pos_=='ADJ' or token.pos_=='ADV' or token.pos_=='NOUN' or token.pos_=='VERB'):
                listapalabras.append((["P" + str(j), (oracion.text), token.idx, token.idx+len(token.orth_), token.orth_, 10, 10, 0, 1,1,0.05]))
        
        return listapalabras

    def lematizar(self, word):
        palabra = self.nlp(word)

        return palabra[0].lemma_