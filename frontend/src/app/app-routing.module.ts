import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { IndexComponent } from './modules/index/index.component';
import { ResultComponent } from './modules/result/result.component';
import { ProjectComponent } from './modules/project/project.component';
import { ContactComponent } from './modules/contact/contact.component';
import { AccessibilityComponent } from './modules/accessibility/accessibility.component';
import { DownloadComponent } from './modules/download/download.component';


const routes: Routes = [
  { path: '', component: IndexComponent },
  { path: 'result', component: ResultComponent },
  { path: 'project', component: ProjectComponent},
  { path: 'contact', component: ContactComponent},
  { path: 'accessibility', component: AccessibilityComponent},
  { path: 'download', component: DownloadComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {useHash:true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
