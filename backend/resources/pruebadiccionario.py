import csv
def loadfrecuenciarae(path):
    dicrae={}
    tsvin = open(path, "rt",encoding='utf-8')
    tsvin = csv.reader(tsvin, delimiter=';')
    for row in tsvin:
        numero=row[0]
        print(numero)
        dicrae[row[1].strip()]=numero[:-1].strip()
    return dicrae
        

def main():
    print("hello")
    dicrae=loadfrecuenciarae('frecuenciasrae.csv')
    print(dicrae.get('enfermedad'))
    freq= dicrae.get('enfermedad')
    if freq==None:
        print("es none")
    elif int(freq) < 1500:
        print("menor")
    else:
        print("mayor")

if __name__ == "__main__":
    main()