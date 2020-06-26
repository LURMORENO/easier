import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

// Angular Material
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

// Request
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ResultComponent } from './modules/result/result.component';
import { IndexComponent } from './modules/index/index.component';
import { HeaderComponent } from './modules/header/header.component';
import { FooterComponent } from './modules/footer/footer.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';


@NgModule({
  declarations: [
    AppComponent,
    ResultComponent,
    IndexComponent,
    HeaderComponent,
    FooterComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
