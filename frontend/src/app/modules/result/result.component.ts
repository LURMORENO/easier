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
  complexWords: Array<any>
  selected: boolean = false
  word: Word
  loading: boolean = true
  showResultText: boolean = true

  constructor(private mainService: MainService, private sanitizer: DomSanitizer) {
    this.complexWords = new Array()
    this.word = new Word()
   }

  ngOnInit() {
    // this.text = history.state.text
    this.text ="En cada barrio de España hay una Sole. Esa mujer que habla con todo el mundo, que conoce hasta al que aún no vive allí. La que siempre está para saludarte."
    this.getComplexWords(this.text)
  }

  async getComplexWords(text: string){
    this.complexWords = await this.mainService.api.getComplexWords(text)
    for(let word of this.complexWords){
      let synonym = await this.mainService.api.getSynonyms(word[4], word)
      //Identificar la palabra compleja y añadir su mejor sinonimo
      this.replaceComplexWords(word[4], synonym[0])
      this.addListener()
    }
  }

  replaceComplexWords(word: string, synonym?: string){
    let text = document.querySelector("#text");
    let regex = new RegExp(`\\b${word}\\b`, 'gi');
    text.innerHTML = text.innerHTML.replace(regex, `<span class=word>${word} <span class=wordtext>${synonym}</span></span>`)
    // this.sanitizer.bypassSecurityTrustHtml(text)    
  }

  addListener(){
    let words = document.querySelectorAll(".word");
    words.forEach(word => {
      word.addEventListener("click", () => {
        this.toggleDictionary(word.textContent, event);
        if(this.isMobile()){
          this.showResultText = false
          console.log(this.showResultText)
        }
      });
    });
  }

  async toggleDictionary(word: string, event) {
    //Obtener definicion y sinonimo
    if(! this.selected){
      this.selected = true
    }
    this.loading = true
    // Buscar la palabra compleja dentro de la lista
    // Modificar la palabra, sinonimos, definicion y pictograma que se muestra
    word = word.split(' ')[0]
    let complex_word = this.complexWords.find((element => element[4] == word))
    let result = await this.mainService.api.getDefinition(word, complex_word[1])
    this.word.synonyms = await this.mainService.api.getSynonyms(word, complex_word)
    this.word.pictogram = await this.mainService.api.getPictogram(word)
    if(! this.word.pictogram){
      this.word.pictogram = null
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