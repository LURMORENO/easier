import { Component, OnInit } from '@angular/core';
import { MainService } from 'src/app/services/main.service';
import { DomSanitizer } from '@angular/platform-browser';
import { Word } from 'src/app/data/word';


@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.scss']
})
export class ResultComponent implements OnInit {

  text: string
  flag:string
  complexWords: Array<any>
  selected: boolean = false
  word: Word
  loading: boolean = true
  showResultText: boolean = true

  complexWordsString: Array<string>

  constructor(private mainService: MainService, private sanitizer: DomSanitizer) {
    this.complexWords = new Array()
    this.word = new Word()
    this.complexWordsString = new Array()
  }

  ngOnInit() {
    this.text = history.state.text
    this.flag = history.state.flag
    this.getComplexWords(this.text,this.flag)
  }

  async getComplexWords(text: string,flag:string){
    this.complexWords = await this.mainService.api.getComplexWords(text,flag)
    for(let word of this.complexWords){
      // Comprobar que la palabra compleja no se sustituye dos veces
      if(! this.complexWordsString.includes(word[4])){
        this.complexWordsString.push(word[4])
        let synonym = await this.mainService.api.getSynonyms(word[4], word)
        //Identificar la palabra compleja y añadir su mejor sinonimo
        this.replaceComplexWords(word[4], synonym[1],synonym[0])
        this.addListener()
      }
    }
  }

  // Esta función no reemplaza nada realmente. Lo que hace es, en caso de haber un sinónimo,
  // añade un div para que, al hacer hover, este se renderice con el sinónimo en cuestión. Si
  // no hay un sinónimo, inserta la misma palabra en el contenedor.
  replaceComplexWords(word: string, synonym?: string,synonym2?: boolean){
    let text = document.querySelector("#text");
    let regex = new RegExp(`\\b${word}\\b`, 'gi');
    if (synonym2==true){
      //console.log("TRUE!")
      text.innerHTML = text.innerHTML.replace(regex, `<div class=word>${word}<span class=wordtext>${synonym}</span></div>`)
    }
    else{
      //console.log("FALSE!")
      text.innerHTML = text.innerHTML.replace(regex, `<div class=word>${word}<span class=wordtext>${word}</span></div>`)
    }
    
    // this.sanitizer.bypassSecurityTrustHtml(text)    
  }

  addListener(){
    let words = document.querySelectorAll(".word");
    words.forEach(word => {
      word.addEventListener("click", () => {
        this.toggleDictionary(word.firstChild.textContent);
        if(this.isMobile()){
          this.showResultText = false
        }
      });
    });
  }

  // getSynonyms se ejecuta dos veces. Una para obtener un único sinónimo, y otra para poder
  // renderizar los tres sinónimos que deben de aparecer en el lateral tras clickear en la palabra
  async toggleDictionary(word: string) {
    //Obtener definicion y sinonimo
    if(! this.selected){
      this.selected = true
    }
    this.loading = true
    // Buscar la palabra compleja dentro de la lista
    // Modificar la palabra, sinonimos, definicion y pictograma que se muestra
    let complex_word = this.complexWords.find((element => element[4] == word))
    let result = await this.mainService.api.getDefinition(word, complex_word[1])
    this.word.synonyms = await this.mainService.api.getSynonyms(word, complex_word)

    // para comprobar si un pictograma tiene sentido o no, se lanza una petición. Si las keywords
    // o tags devuelven algo más a parte de la propia palabra, se devuelve un pictograma nulo (solo)
    // si ningún sinónimo se corresponde tampoco
    let picto_result = await this.mainService.api.getPictogram(word)
    if(! picto_result){
      for (let i = 0; i < this.word.synonyms.length; i++) {
          let picto_result = await this.mainService.api.getPictogram(this.word.synonyms[i]);
          if (picto_result){
            this.word.pictogram = picto_result;
          } else {
            this.word.pictogram = null;
          }
      }
    }
    
    this.word.word = word
    this.word.definition = result['definition']
    this.word.source = result['source']
    this.loading = false
  }

  goBack(){
    //Ocultar la información de la palabra y mostar el texto de nuevo
    this.showResultText = true
  }

  isMobile() {
    return !window.matchMedia("(min-width: 768px)").matches;
  }

  isHidden(elem) {
    var style = window.getComputedStyle(elem);
    return ((style.display === 'none') || (style.visibility === 'hidden'))
  }

  hideElement(elem) {
    elem.style.display = "none";
  }

  showElement(elem, type = "block") {
    elem.style.display = type;
  }

}