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

  ngOnInit(): void {
  }

  onSubmit() {
    let text = this.easierForm.get("text").value
    this.router.navigate(['result'], { state : { text: text } })
  }

}
