import pyphen

class Pyphen:
    dic=pyphen.Pyphen(lang='es')

    def getNSyl(self,word):
        try:
            test = self.dic.inserted(word)
            #print(test)
            count=0
            for i in test:
                if i == '-':
                    count = count + 1
            count += 1
            return count
        except:
            test = self.dic.inserted(str(word))
            #print(test)
            count=0
            for i in test:
                if i == '-':
                    count = count + 1
            count += 1
            return count
