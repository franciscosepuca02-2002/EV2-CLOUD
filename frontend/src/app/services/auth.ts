import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConfigService } from './config.service';
import { tap } from 'rxjs/operators';

export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
}

@Injectable({ providedIn: 'root' })
export class Auth {
  private http = inject(HttpClient);
  private config = inject(ConfigService);

  registro(nombre: string, correo: string, password: string) {
    return this.http.post<{ message: string; usuario: Usuario }>(
      `${this.config.apiUrl}/registro`,
      { nombre, correo, password }
    );
  }

  login(correo: string, password: string) {
    return this.http.post<{ message: string; usuario: Usuario }>(
      `${this.config.apiUrl}/login`,
      { correo, password }
    ).pipe(
      tap(res => {
        if (res.usuario) {
          localStorage.setItem('usuario', JSON.stringify(res.usuario));
        }
      })
    );
  }

  logout() {
    localStorage.removeItem('usuario');
  }

  getUsuario(): Usuario | null {
    const data = localStorage.getItem('usuario');
    return data ? JSON.parse(data) : null;
  }

  estaAutenticado(): boolean {
    return this.getUsuario() !== null;
  }
}
