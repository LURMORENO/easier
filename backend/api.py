import torch

from flask import Flask, request, Response
from flask_cors import CORS
from flask import jsonify
from markupsafe import escape

import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from urllib.request import Request, urlopen
from urllib.parse import quote

from resources.text2tokens import text2tokens
from models.models import Config
config = Config()

from multiprocessing import Pool

from transformers import BertForMaskedLM, BertTokenizer

from inflector import Inflector,Spanish
import spacy

nlp = spacy.load('es_core_news_md')
inflector = Inflector(Spanish)

text2tokens = text2tokens(nlp)

# pool=Pool()

with torch.no_grad():
    tokenizer = BertTokenizer.from_pretrained("resources/pytorch/", do_lower_case=False)
    model = BertForMaskedLM.from_pretrained("resources/pytorch/")
    model.eval()

app = Flask(__name__)
CORS(app)

# Reuse Gunicorn handlers so logs are visible in `docker logs`.
gunicorn_logger = logging.getLogger("gunicorn.error")
if gunicorn_logger.handlers:
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

def _get_word_pos(word):
    if not word:
        return None
    doc = nlp(str(word))
    if len(doc) == 0:
        return None
    return doc[0].pos_


def _is_pos_compatible(target_pos, candidate_pos):
    if not target_pos or not candidate_pos:
        return True

    if target_pos == 'NOUN':
        return candidate_pos in {'NOUN', 'PROPN'}
    if target_pos == 'PROPN':
        return candidate_pos in {'PROPN', 'NOUN'}
    if target_pos == 'VERB':
        return candidate_pos == 'VERB'
    if target_pos == 'ADJ':
        return candidate_pos == 'ADJ'
    if target_pos == 'ADV':
        return candidate_pos == 'ADV'

    return candidate_pos == target_pos

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", 
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

@app.route('/api/complex-words', methods=['GET'])
def get_complex_words():
    if request.method == 'GET':
        text = request.args.get('text')
        flag = request.args.get('flag')

        to_remove_words = text.split()
        to_remove_words = [
            word for word in to_remove_words
            if word.lower().strip(".,;:!?¡¿") not in DAYS
            and word.lower().strip(".,;:!?¡¿") not in MONTHS
        ]

        text = " ".join(to_remove_words)

        words = list()
        complex_words = list()
        
        sentencelist =  text2tokens.text2sentences(text)
        if flag=='1':
            words = [text2tokens.sentence2tokenseasier(sentence) for sentence in sentencelist]
        elif flag=='0':
            words = [text2tokens.sentence2tokens(sentence) for sentence in sentencelist]
        predictedtags = list()

        if words and words[0]:
            words = [item for item in words if item]
            
            matrix_deploy = [
                        config.clasificadorobj.getMatrix_Deploy(sentencetags, config.trigrams,config.totalTris, 
                        config.bigrams, config.unigrams, config.totalBis,
                        config.totalUnis, config.uniE2R) for sentencetags in words]
            if flag=='1':
                predictedtags = [config.clasificadorobj.SVMPredict(rowdeploy) for rowdeploy in matrix_deploy]
                print("entro en easier")
            elif flag=='0': # ??
                predictedtags = [config.clasificadorobj.SVMPredict2(rowdeploy) for rowdeploy in matrix_deploy]
                print("entro en easier")
                # TODO: wtf is the bea flag??
        if flag=='1':
            for j in range(0, len(words)):
                sentencetags = words[j]
                for i in range(0, len(sentencetags)):
                    if predictedtags[j][i] == 1:
                        print("compleja"+" "+sentencetags[i][4])
                        complex_words.append(sentencetags[i])
                    elif predictedtags[j][i] == 0:
                        print("simple"+" "+sentencetags[i][4])
                        numsil= config.clasificadorobj.Pyphenobj.getNSyl(sentencetags[i][4])
                        if  numsil >4:
                            complex_words.append(sentencetags[i])
                            print(numsil)
        elif flag=='0': # TODO: again bea??
            for j in range(0, len(words)):
                sentencetags = words[j]
                for i in range(0, len(sentencetags)):
                    if sentencetags[i][4]=='crónicos' or sentencetags[i][4]=='vulnerables':
                        print("add compleja"+" "+sentencetags[i][4])
                        complex_words.append(sentencetags[i])
                    if predictedtags[j][i] == 1:
                        if config.clasificadorobj.getfreqRAE(sentencetags[i][4])==None:
                            print("none compleja"+" "+sentencetags[i][4])
                            complex_words.append(sentencetags[i])
                        elif int(config.clasificadorobj.getfreqRAE(sentencetags[i][4]))>1500:
                            print("compleja pero mayor a 1500 en diccionario rae"+" "+sentencetags[i][4])
                            complex_words.append(sentencetags[i])
                        else:
                            print("compleja pero menor a 1500 en diccionario rae"+" "+sentencetags[i][4])    

        return jsonify(result=complex_words)


@app.route('/api/disambiguate', methods=['GET'])
def get_disambiguate():
    if request.method == 'GET':
        word = request.args.get('word')
        phrase = request.args.get('phrase')
        definition_list = request.args.get('definition_list')
        definition_list = json.loads(definition_list)

        phrase = phrase.replace(word, "[MASK]")
        # CLS and SEP are specials tokens used in BERT Models
        # CLS stands for Classification Token: the model does a vectorial representation and uses it
        # as a summary of the entire phrase. SEP stands for separator: used for separating sequences
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
        
        #other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "tagger"]
        #nlp.disable_pipes(*other_pipes)
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

@app.route('/api/definition-easy', methods=['GET'])
def get_definition_easy():
    if request.method == 'GET':
        word = escape(request.args.get('word'))

        definition_list = list()
        page = requests.get(url= 'http://diccionariofacil.org/diccionario/' + word)
        soup = BeautifulSoup(page.text, 'html.parser')
        error_content = soup.find("div", {"id": "infoBoxArrowError3contendor"})
        if page.status_code == 200 and not error_content:
            definitions_content = soup.findAll(True, {"class":["field-definicion"]})
            for definition_content in definitions_content:
                definition_list.append(definition_content.text.replace("\n", ""))
            return jsonify(definition_list=definition_list)
        else:
            return jsonify(definition_list=definition_list)


@app.route('/api/definition-rae', methods=['GET'])
def get_definition_rae():
    if request.method == 'GET':
        word = escape(request.args.get('word'))
        api_url = f"https://rae-api.com/api/words/{word}"
        response = requests.get(api_url)

        definition_list = []

        if response.status_code == 200:
            data = response.json()
            meanings = data.get("data", {}).get("meanings", [])
            if meanings:
                senses = meanings[0].get("senses", [])
                if senses:
                    # Coger la primera definición
                    first_definition = senses[0].get("raw", "").strip()
                    if first_definition:
                        definition_list.append(first_definition)
        return jsonify(definition_list=definition_list)


@app.route('/api/pictogram', methods=['GET'])
def get_pictogram():
    if request.method == 'GET':
        word = request.args.get('word')
        if not word:
            return jsonify(result='')

        # Hardcoded cases previously handled in frontend.
        pictogram_ids = {
            'pandemia': 30987,
            'plataforma': 12333,
            'mascarillas': 9169,
            'insta': 34697,
            'facilitar': 19522,
            'incorporación': 8026,
            'garantiza': 16021,
            'garantice': 16021,
            'contraer': 6457,
            'crónicos': 28742,
            'vulnerables': 4620,
            'concentración': 38796,
        }

        if word in pictogram_ids:
            url = f"https://api.arasaac.org/api/pictograms/{pictogram_ids[word]}?download=false"
            return jsonify(result=url)

        try:
            search_url = f"https://api.arasaac.org/api/pictograms/es/search/{quote(word)}"
            response = requests.get(search_url, timeout=8)
            if response.status_code != 200:
                return jsonify(result='')

            candidates = response.json()
            if not isinstance(candidates, list) or len(candidates) == 0:
                return jsonify(result='')

            word_id = candidates[0].get('_id')
            if not word_id:
                return jsonify(result='')

            url = f"https://api.arasaac.org/api/pictograms/{word_id}?download=false"
            return jsonify(result=url)
        except Exception:
            return jsonify(result='')


@app.route('/api/lemmatize', methods=['GET'])
def get_lemma():
    if request.method == 'GET':
        word = request.args.get('word')
        lemma = text2tokens.lematizar(word)
        print("hay lemma")

        return jsonify(result=lemma)


@app.route('/api/synonyms', methods=['GET'])
def get_synonyms():
    if request.method == 'GET':
        word = request.args.get('word')
        sentencetags = request.args.get('sentencetags')
        sentencetags = json.loads(sentencetags)

        # metodo que obtiene los sinonimos de una palabra
        dicsim={}
        synonims_final = list()
        if word == "plataforma":
            dicsim["organización"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "pandemia":
            dicsim["epidemia"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "mascarillas":
            dicsim["mascarillas"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "insta":
            dicsim["pide"]=None
            dicsim["solicita"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "facilitar":
            dicsim["ayudar"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "incorporación":
            dicsim["introducción"]=None
            dicsim["inscripción"]=None 
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "garantiza":
            dicsim["asegurar"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "garantice":
            dicsim["asegurar"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "contraer":
            dicsim["adquirir"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "crónicos":
            dicsim["grave"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "vulnerables":
            dicsim["débil"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            synonims_final=list(dicsim)
            return jsonify(result=synonims_final)
        if word== "discapacidad":
            dicsim["discapacidad"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        if word== "vacuna" or word== "vacunas":
            dicsim["inyecciones"]=None
            dicsim["inmunización"]=None
            synonims_final=list(dicsim)
            synonims_final.insert(0,True)
            return jsonify(result=synonims_final)
        else:
            dis2 = 0
            synonims_final = list()
            dicsim={}
            dicsim2={}
            synonims = list()
            synonimsc=list()
            synonimsb=list()
            stem = config.lematizador.lemmatize(word)
            synonimsb = config.diccionario_babel.babelsearch(word)
            synonimsb+= config.diccionario_babel.babelsearch(stem)


            if word.lower() in config.diccionarioparafrases:
                synonimsc=config.diccionarioparafrases[word.lower()]
            else:
                synonimsc.append(word)

            if len(config.dictionario_palabras.SSinonimos(word)):
                synonims = config.dictionario_palabras.SSinonimos(stem)

            if not synonims:
                synonims = config.dictionario_palabras.SSinonimos(word)
                stem = word
        
            synonims_total = list(synonims + synonimsb+synonimsc)
            dic_synonims = dict.fromkeys(synonims_total)

            dic_synonims=text2tokens.eliminarstem(dic_synonims,word.lower())

            # if word is NOUN, only NOUN synonyms and so...
            target_pos = _get_word_pos(word)
            for candidate in dic_synonims.keys():
                candidate_pos = _get_word_pos(candidate)
                if not _is_pos_compatible(target_pos, candidate_pos):
                    continue

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

                #candidatematrix = config.clasificadorobj.getMatrix_Deploy(listcandidatesentencetags, config.trigrams, config.totalTris, config.bigrams, config.unigrams, config.totalBis, config.totalUnis, config.uniE2R)
                #candidatepredictedtag = config.clasificadorobj.SVMPredict(candidatematrix)
        
                # Buscar el sinonimo optimo
                dis1 = config.clasificadorobj.word2vector.similarity(candidate, word)
                window = config.clasificadorobj.getWindowlexical(word, sentencetags[1], sentencetags[2])
                diswindow1 = config.clasificadorobj.word2vector.similarity(window[1], candidate)
                diswindow2 = config.clasificadorobj.word2vector.similarity(window[2], candidate)
                dis3 = dis1 + diswindow1 + diswindow2

                #if dis2 < dis3 and word != candidate.lower() and candidatepredictedtag[0] != 1:
                if word != candidate.lower() and candidate.lower()!='':
                    dicsim[candidate]=dis3


            if word.lower() == 'alcance':
                dicsim2={k: v for k, v in sorted(dicsim.items(), key=lambda item: item[1])}
                dicsim2=text2tokens.cleanspecificdic(dicsim2)
            else:
                dicsim=text2tokens.removestemrae(dicsim)
                dicsim2={k: v for k, v in sorted(dicsim.items(), key=lambda item: item[1])}

            # Si se ha encontrado al menos un sinonimo se devuelven los 3 mas significativos            
            if len(dicsim2) > 0:
                synonims_final=list(dicsim2)[-3:]
                if config.clasificadorobj.getfreqRAE(synonims_final[0])==None:
                    synonims_final.insert(0,False)
                    return jsonify(result=synonims_final)
                else:
                    synonims_final.insert(0,True)
                    return jsonify(result=synonims_final)
            # Si no se ha encontrado ningun sinonimo se devuelve una lista con
            # la palabra original
            else:
                synonims_final.append(word)
                return jsonify(result=synonims_final)