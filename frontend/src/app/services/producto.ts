import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ProductoService {

  http = inject(HttpClient);

  api = 'http://127.0.0.1:8000';

  obtenerProductos(){

    return this.http.get(`${this.api}/productos`);
  }
}
