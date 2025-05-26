import json
from urllib.request import urlopen

class worddictionary:

    def SSinonimos(self, word):
        json2 = ''
        url = ''
        sameword = list()
        word = str(word)
        key = open("/app/resources/thesaurus_key.txt", "r").read()

        try:
            url = "http://thesaurus.altervista.org/thesaurus/v1?word="+word+"&language=es_ES&key="+key+"&output=json"
            response = urlopen(url).read().decode('utf-8')
            json2=json.loads(response)
            synonymslist=list()
            for var in json2['response']:
                synonyms=var["list"]['synonyms'].split('|')
                for syn in synonyms:
                    synonymslist.append(syn)
            return synonymslist
        except:
            sameword.append(word)
            return sameword
