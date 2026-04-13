export class Word {
    word:string
    synonyms:Array<string>
    definition:string
    pictogram:string | null
    source: string

    constructor(){
        this.synonyms = new Array()
    }
}

