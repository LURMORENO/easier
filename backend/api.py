import torch

from flask import Flask, request, Response
from flask_cors import CORS
from flask import jsonify
from markupsafe import escape

import requests
from bs4 import BeautifulSoup
import re
import json

from resources.text2tokens import text2tokens
from models.models import Config
config = Config()

from multiprocessing import Pool

from transformers import BertForMaskedLM, BertTokenizer

from inflector import Inflector,Spanish
import spacy

nlp = spacy.load('es_core_news_md')
inflector = Inflector(Spanish)

text2tokens = text2tokens()

# pool=Pool()

tokenizer = BertTokenizer.from_pretrained("resources/pytorch/", do_lower_case=False)
model = BertForMaskedLM.from_pretrained("resources/pytorch/")
model.eval()

app = Flask(__name__)
CORS(app)

@app.route('/api/complex-words', methods=['GET'])
def get_complex_words():
    if request.method == 'GET':
        text = request.args.get('text')

        words = list()
        complex_words = list()
        sentencelist = text2tokens.text2sentences(text)
        words = [text2tokens.sentence2tokens(sentence) for sentence in sentencelist]
        predictedtags = list()

        if words and words[0]:
            words = [item for item in words if item]
            
            matrix_deploy = [
                        config.clasificadorobj.getMatrix_Deploy(sentencetags, config.trigrams,config.totalTris, 
                        config.bigrams, config.unigrams, config.totalBis,
                        config.totalUnis, config.uniE2R) for sentencetags in words]
                        
            predictedtags = [config.clasificadorobj.SVMPredict(rowdeploy) for rowdeploy in matrix_deploy]

        for j in range(0, len(words)):
                sentencetags = words[j]
                for i in range(0, len(sentencetags)):
                    if predictedtags[j][i] == 1:
                        complex_words.append(sentencetags[i])

        return jsonify(result=complex_words)

@app.route('/api/disambiguate', methods=['GET'])
def get_disambiguate():
    if request.method == 'GET':
        word = request.args.get('word')
        phrase = request.args.get('phrase')
        definition_list = request.args.get('definition_list')
        definition_list = json.loads(definition_list)

        phrase = phrase.replace(word, "[MASK]")
        phrase = "[CLS] " + phrase + " [SEP]"

        tokens = tokenizer.tokenize(phrase)
        indexed_tokens = tokenizer.convert_tokens_to_ids(tokens)
        tokens_tensor = torch.tensor([indexed_tokens])
        predictions = model(tokens_tensor)[0]
        midx = tokens.index("[MASK]")
        idxs = torch.argsort(predictions[0,midx], descending=True)
        predicted_token = tokenizer.convert_ids_to_tokens(idxs[:5])

        newpredicted_token=list()
        tokensmlist=list()

        if word in predicted_token:
            predicted_token.remove(word)
        
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "tagger"]
        nlp.disable_pipes(*other_pipes)
        for doc in nlp.pipe(predicted_token):
            if len(doc) > 0:
                if doc[0].pos_=='PROPN' or doc[0].pos_=='NOUN':
                    nword=inflector.pluralize(doc[0].text)
                    newpredicted_token.append(nword)
            newpredicted_token.append(doc)
        doc = nlp(phrase)
        for token in doc:
            if token.pos_ == "NOUN" and token.text!=word:
                nword=inflector.pluralize(token.text)
                newpredicted_token.append(nword)
                newpredicted_token.append(token.text)
            elif token.pos_=="VERB" or token.pos_ == "ADV" or token.pos_ == "PROPN" and token.text!=word:
                newpredicted_token.append(token.text)
        
        final = ""
        temp = ""
        for meaning in definition_list:
            tokensmlist.append(tokenizer.tokenize(meaning))
            cont=0
            temp=0
            for i in tokensmlist:
                cont=0
                for j in newpredicted_token:
                    if j in i:
                        cont=cont+1
                if cont>temp:
                    final=i
                    temp=cont
        
        if final == "":
            final = definition_list[0]
        else:
            final = " ".join(final)
            final = final.replace(' ##', '').replace(" .", ".").replace(" ,", ",")

        return jsonify(definition=final)

@app.route('/api/synonyms', methods=['GET'])
def get_synonyms():
    if request.method == 'GET':
        word = request.args.get('word')
        sentencetags = request.args.get('sentencetags')
        sentencetags = json.loads(sentencetags)

        # metodo que obtiene los sinonimos de una palabra
        dis2 = 0
        synonims = list()
        synonimsb = config.diccionario_babel.babelsearch(word)
        synonims_final = list()

        if len(config.dictionario_palabras.SSinonimos(word)):
            if str(word[len(word) - 5:]) == 'mente':
                stem = word.replace("mente", "")
                synonims = config.dictionario_palabras.SSinonimos(stem)
            else:
                stem = config.lematizador.lemmatize(word)
                synonims = config.dictionario_palabras.SSinonimos(stem)

        if not synonims:
            synonims = config.dictionario_palabras.SSinonimos(word)
            stem = word
    
        synonims_total = list(synonims + synonimsb)
        dic_synonims = dict.fromkeys(synonims_total)

        for candidate in dic_synonims.keys():
            candidatesentencetags = list(sentencetags)
            candidatesentencetags[4] = str(candidate)
            candidatelen = len(candidate)
            wordlen = len(word)
            candidatesentencetags[3] = candidatesentencetags[2] + candidatelen
            candidatesentencetags[1] = str(candidatesentencetags[1])[
                :candidatesentencetags[2]] + str(candidate) + \
                candidatesentencetags[1][
                candidatesentencetags[2] + wordlen:]

            listcandidatesentencetags = list()
            listcandidatesentencetags.append(candidatesentencetags)
    
            # Buscar el sinonimo optimo
            dis1 = config.clasificadorobj.word2vector.similarity(candidate, word)
            window = config.clasificadorobj.getWindow(word, sentencetags[1], sentencetags[2])
            diswindow1 = config.clasificadorobj.word2vector.similarity(window[1], candidate)
            diswindow2 = config.clasificadorobj.word2vector.similarity(window[2], candidate)
            dis3 = dis1 + diswindow1 + diswindow2

            if dis2 < dis3 and word != candidate.lower():
                dis2 = dis3
                wordreplace = candidatesentencetags[4]
                if wordreplace:
                    synonims_final.append(wordreplace)

        # Si se ha encontrado al menos un sinonimo se devuelven los 3 mas significativos            
        if len(synonims_final) > 0:
            return jsonify(result=synonims_final[:3])
        # Si no se ha encontrado ningun sinonimo se devuelve una lista con
        # la palabra original
        else:
            synonims_final.append(word)
            return jsonify(result=synonims_final)

@app.route('/api/definition-easy', methods=['GET'])
def get_definition_easy():
    if request.method == 'GET':
        word = escape(request.args.get('word'))

        definition_list = list()
        page = requests.get(url= 'http://diccionariofacil.org/diccionario/' + word + '.html')
        soup = BeautifulSoup(page.text, 'html.parser')
        error_content = soup.find("div", {"id": "infoBoxArrowError3contendor"})
        if page.status_code == 200 and not error_content:
            definitions_content = soup.findAll(True, {"class":["definicionContent font600", "definicionContent"]})
            for definition_content in definitions_content:
                definition_list.append(definition_content.text.replace("\n", "")[2:])
            return jsonify(definition_list=definition_list)
        else:
            return jsonify(definition_list=definition_list)

@app.route('/api/definition-rae', methods=['GET'])
def get_definition_rae():
    if request.method == 'GET':
        word = escape(request.args.get('word'))
        definition_list = list()
        page = requests.get(url= 'https://dle.rae.es/' + word)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            # Coger la primera definición
            definitions_content = soup.findAll('p', attrs={'class' : ['j', 'j2', 'm']})
            if definitions_content:
                for definition_content in definitions_content:
                    definition_content = re.findall('.*?[.]', definition_content.text)
                    definition = ""
                    for i in definition_content:
                        if(len(i) > 8):
                            definition += i
                    definition = definition.strip()
                    definition_list.append(definition)  
                return jsonify(definition_list=definition_list)  
            else:
                return jsonify(definition_list=definition_list)
        else:
            return jsonify(definition_list=definition_list)


@app.route('/api/pictogram', methods=['GET'])
def get_pictogram():
    if request.method == 'GET':
        word = request.args.get('word')
        # Metodo que obtiene un pictograma de arasaac
        params = {
            's': word,
            'idiomasearch':0,
            'Buscar': 'Buscar',
            'buscar_por': 1,
            'pictogramas_color': 1,
            'pictogramas_byn': 1,
            'fotografia': 1,
            'lse_color': 1
        }

        page = requests.get(url='http://www.arasaac.org/buscar.php', params=params)
        if page.status_code == 200:
            try:
                soup = BeautifulSoup(page.text, 'html.parser')
                # Comprobar que la palabra conincice exactamente con la imagen recupeada
                li_list = soup.find(id="ultimas_imagenes").find_all('li')
                if li_list is not None:
                    for li in li_list:
                        index = re.search(r'\d', li.text)
                        text = li.text[:index.start()].strip()
                        if word == text:
                            href = li.find('a')['href']
                            page = requests.get(url = 'http://www.arasaac.org/' + href)
                            soup = BeautifulSoup(page.text, 'html.parser')
                            url = soup.find(id="principal").find(class_='image')['src']
                            url = 'www/arasaac.org/' + url
                            return jsonify(result=url)
                    return jsonify(result='')
            except:
                return jsonify(result='')

        else:
            return jsonify(result='')

@app.route('/api/lemmatize', methods=['GET'])
def get_lemma():
    if request.method == 'GET':
        word = request.args.get('word')
        lemma = text2tokens.lematizar(word)

        return jsonify(result=lemma)