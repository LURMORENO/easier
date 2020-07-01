import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

// Angular Material
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner'; 

// Request
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ResultComponent } from './modules/result/result.component';
import { IndexComponent } from './modules/index/index.component';
import { HeaderComponent } from './modules/header/header.component';
import { FooterComponent } from './modules/footer/footer.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ProjectComponent } from './modules/project/project.component';
import { ContactComponent } from './modules/contact/contact.component';
import { AccessibilityComponent } from './modules/accessibility/accessibility.component';


@NgModule({
  declarations: [
    AppComponent,
    ResultComponent,
    IndexComponent,
    HeaderComponent,
    FooterComponent,
    ProjectComponent,
    ContactComponent,
    AccessibilityComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    MatProgressSpinnerModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
