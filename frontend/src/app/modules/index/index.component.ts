import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-index',
  templateUrl: './index.component.html',
  styleUrls: ['./index.component.scss']
})
export class IndexComponent implements OnInit {

  easierForm = new FormGroup({
    text: new FormControl("", [Validators.required,])
  });

  constructor(private router: Router) { }

  val:string
  ngOnInit(): void {
  }

  onSubmit() {
    //console.log(this.val)
    let text = this.easierForm.get("text").value
    this.router.navigate(['result'], { state : { text: text , flag:this.val} })
  }

  easierclick(){
    this.val='1'
  }
  beaclick(){
    this.val='0'
  }

}
