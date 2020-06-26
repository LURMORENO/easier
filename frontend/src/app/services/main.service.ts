import { Injectable } from '@angular/core';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class MainService {

  public api: ApiService

  constructor(api: ApiService) {
    this.api = api
   }
}
