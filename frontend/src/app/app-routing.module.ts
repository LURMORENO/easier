import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { IndexComponent } from './modules/index/index.component';
import { ResultComponent } from './modules/result/result.component';


const routes: Routes = [
  { path: '', component: IndexComponent },
  { path: 'result', component: ResultComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
