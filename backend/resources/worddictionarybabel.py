from babelnetpy.babelnet import BabelNet

class worddictionarybabel:
    bn = BabelNet(open("/app/resources/llavebabel.txt", "r").read())

    def babelsearch(self, palabra):
        listasyn = list()
        sameword = list()
        try:
            Ids = self.bn.getSynset_Ids(palabra, "ES")
            for i in range(0, len(Ids)):
                synsets = self.bn.getSynsets(Ids[i].id)
                # synsets = self.bn.getSynsets("ES", Ids[i].id)
                for j in range(0, len(synsets)):
                    for x in range(0, len(synsets[j].senses)):
                        syn = synsets[j].senses[x]['properties']['fullLemma']
                        language = synsets[j].senses[x]['properties']['language']
                        if (language == "ES" and len(syn.split(" ")) and len(syn.split("_")) == 1):
                            listasyn.append(syn)
            if (len(listasyn)==0):
                sameword.append(palabra)
                return sameword
            else:
                return listasyn
        except:
            sameword.append(palabra)
            return listasyn