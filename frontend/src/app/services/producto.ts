import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConfigService } from './config.service';

@Injectable({ providedIn: 'root' })
export class ProductoService {
  private http = inject(HttpClient);
  private config = inject(ConfigService);

  obtenerProductos() {
    return this.http.get<any[]>(`${this.config.apiUrl}/productos`);
  }
}
