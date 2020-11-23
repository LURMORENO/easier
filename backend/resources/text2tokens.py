import os
import spacy
import math
from resources.clasificador import clasificador
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer(language='spanish')
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
            if (token.pos_=='NOUN' or token.pos_=='VERB'):
                listapalabras.append((["P" + str(j), oracion.text, token.idx, token.idx+len(token.orth_), token.orth_, 10, 10, 0, 1,1,0.05]))
            if (token.orth_=='vulnerables' or token.orth_=='crónicos'):
                listapalabras.append((["P" + str(j), oracion.text, token.idx, token.idx+len(token.orth_), token.orth_, 10, 10, 0, 1,1,0.05]))
        
        return listapalabras

    def sentence2tokenseasier(self,sentence):
        listapalabras=list()
        oracion=self.nlp(sentence)
        for j,token in enumerate(oracion):
            if (token.pos_=='NOUN' or token.pos_=='VERB'or token.pos_=='ADJ'):
                listapalabras.append((["P" + str(j), oracion.text, token.idx, token.idx+len(token.orth_), token.orth_, 10, 10, 0, 1,1,0.05]))
        
        return listapalabras

    def lematizar(self, word):
        palabra = self.nlp(word)

        return palabra[0].lemma_

    def getroot(self,word):
        lenword=len(word)/2
        newword=word[:math.ceil(lenword)]
        newword2=word[:math.floor(lenword)]
        return newword,newword2

    def eliminarstem(self,dic,word):
        dic2={}
        raiz1,raiz2=self.getroot(word)
        for element in dic:
            if stemmer.stem(word) not in element.lower() and raiz1 not in element.lower() and element!='':
                dic2[element]=None     
        if len(dic2)==0:
            dic2[word]=None
        return dic2

    def removestemrae(self,dicp):
        newdic={}
        for item,value in dicp.items():
            if self.removestemraeword(stemmer.stem(item))==True:
                newdic[item]=value
        return newdic

    def removestemraeword(self,word):
        for element in clasificadorobj.diccionariorae:
            if word in element:
                return True

    def cleanspecificdic(self,dicp):
        newdic={}
        #print("entró a función")
        for key,value in dicp.items():
            if key.lower()!="incapacidad" and key.lower()!="incapacidades" and key.lower()!="impedidos" and key.lower()!="manos" and key.lower()!="poder":
                newdic[key]=value        
        #print(newdic)
        return newdic
                
        
