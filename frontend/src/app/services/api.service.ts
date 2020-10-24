import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  url = "http://163.117.129.208:5000/api"
  //url = "http://127.0.0.1:5000/api"

  constructor(private http: HttpClient) { }

  getComplexWords(text: string,flag:string): Promise<any>{
    return new Promise<any> ((resolve, reject) => {
      try {
        this.http.get(this.url+'/complex-words', {
          params: {
            text:text,
            flag:flag
          }
        }).subscribe((data) => {
          resolve(data['result']);
        })
      } catch (error) {
        reject(error)
      }
    })
  }

  getSynonyms(word: string, sentencetags): Promise<any>{
    return new Promise<any>((resolve, reject) => {
      try {
        this.http.get(this.url+'/synonyms-v2', {
          params: {
            word: word,
            sentencetags: JSON.stringify(sentencetags)
          }
        }).subscribe((data) => {
          resolve(data['result'])
        })
      } catch (error) {
        reject(error)
      }
    })
  }

  getDefinitionEasy(word: string):Promise<string[]>{
    return new Promise<string[]>((resolve, reject) => {
      try {
        this.http.get(this.url+'/definition-easy', {
          params: {
            word: word
          }
        }).subscribe((result) => {
          resolve(result['definition_list'])
        })
      } catch (error) {
        reject(error)
      }
    })
  }

  getDefinitionRae(word: string):Promise<string[]>{
    return new Promise<string[]>((resolve, reject) => {
      try {
        this.http.get(this.url+'/definition-rae', {
          params: {
            word: word
          }
        }).subscribe((result) => {
          resolve(result['definition_list'])
        })
      } catch (error) {
        reject(error)
      }
    })
  }

  getDefinition(word: string, phrase: string): Promise<any>{
    return new Promise<any>(async (resolve, reject) => {
      try {
        let definition_list: string[]
        let definition: string
        let source: string
    
        definition_list = await this.getDefinitionEasy(word)
        source = 'facil'
        // Si no se encuentran resultados se obtiene la palabra raiz y se vuelve a consultar
        if(definition_list.length == 0){
          let lemma = await this.getLemma(word)
          definition_list = await this.getDefinitionEasy(lemma)
          // Si la palabra raiz tampoco da resultados se consulta el diccionario rae
          if(definition_list.length == 0){
            definition_list = await this.getDefinitionRae(word)
            source = 'rae'
            // Si no se obtienen resultados se prueba otra vez con la palabra raiz
            if(definition_list.length == 0){
              definition_list = await this.getDefinitionRae(lemma)
              // Si no se encuentra nada se devuelve la palabra original
              if(definition_list.length == 0){
                definition_list.push(word)
                source = 'No encontrado'
                resolve({definition_list, source})
              }
            }
          }
        }
        let result = await this.http.get(this.url+'/disambiguate', {
          params: {
            word: word,
            phrase: phrase,
            definition_list: JSON.stringify(definition_list)
          }
        }).toPromise()

        definition = result['definition']

        resolve({definition, source})
        
      } catch (error) {
        reject(error)
      }
    })
  }

  getPictogram(word: string):Promise<string>{
    return new Promise<string>((resolve, reject) => {
      try {
        this.http.get(`https://api.arasaac.org/api/pictograms/es/bestsearch/${word}`)
        .subscribe((result => {
          let word_id = result[0]['_id']
          let url = `https://api.arasaac.org/api/pictograms/${word_id}?download=false`
          resolve(url)
          
        }),
        (error => {
          resolve('')
        }))
      } catch (error) {
        reject(error)
      }
    })
  }

  // getPictogram(word: string):Promise<string>{
  //   return new Promise<string>((resolve, reject) => {
  //     try {
  //       this.http.get(this.url+'/pictogram', {
  //         params: {
  //           word: word
  //         }
  //       }).subscribe((result => {
  //         resolve(result['result'])
  //       }))
  //     } catch (error) {
  //       reject(error)
  //     }
  //   })
  // }

  getLemma(word: string):Promise<string>{
    return new Promise<string>((resolve, reject) => {
      try {
        this.http.get(this.url+'/lemmatize', {
          params: {
            word: word
          }
        }).subscribe((result) => {
          resolve(result['result'])
        })
      } catch (error) {
        reject(error)
      }
    })
  }

}
