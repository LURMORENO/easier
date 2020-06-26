import { Component, OnInit, Pipe, PipeTransform, Sanitizer, SecurityContext, AfterViewInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MainService } from 'src/app/services/main.service';
import { DomSanitizer } from '@angular/platform-browser';
import { element } from 'protractor';


@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.scss']
})
export class ResultComponent implements OnInit {

  text: string
  complexWords: Array<any>
  selected: boolean = false
  word:string 
  synonyms: Array<string>
  definition: string
  result: any
  source: string

  constructor(private mainService: MainService, private sanitizer: DomSanitizer) {
    this.complexWords = new Array()
    this.synonyms = new Array()
   }

  ngOnInit() {
    // this.text = history.state.text
    this.text ="En cada barrio de España hay una Sole. Esa mujer que habla con todo el mundo, que conoce hasta al que aún no vive allí. La que siempre está para saludarte. Da igual dónde estés, ahí te encontrarás a la Sole. No muy lejos anda Paco, el vecino que tampoco falta en un distrito. Siempre quejándose, malhumorado….pero muy cotilla pese a que sus ademanes sean educados y discretos. Ambos están haciendo teatro en un taller de interpretación, “la vida misma sobre un escenario” resumen estos dos jóvenes que gesticulan hasta los años con una mueca de felicidad, “¡80 y tantos y subiendo¡”. Sole y Paco no han conocido a Aristóteles pero sí una de sus mejores reflexiones cuando decía que en los teatros griegos se producía una catarsis que purifcaba a los pacientes, depuraba los desarreglos morales y curaba las enfermedades del alma. “Quiero hacer teatro porque me gustaría hacer algo por mí y por los demás, por mejorar y superarme”. Esta es la contestación más habitual cuando uno es preguntando sobre las motivaciones que le llevan a subir a un escenario."
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
      });
    });
  }

  async toggleDictionary(word: string, event) {
    //Obtener definicion y sinonimo
    if(! this.selected){
      this.selected = true
    }
    // Buscar la palabra compleja dentro de la lista
    // Modificar la palabra, sinonimos, definicion y pictograma que se muestra
    word = word.split(' ')[0]
    let complex_word = this.complexWords.find((element => element[4] == word))
    let result = await this.mainService.api.getDefinition(word, complex_word[1])
    this.synonyms = await this.mainService.api.getSynonyms(word, complex_word)
    this.word = word
    this.definition = result['definition']
    this.source = result['source']
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