import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private http = inject(HttpClient);
  private config: { apiUrl: string } = { apiUrl: 'http://localhost:8000' };

  async load(): Promise<void> {
    try {
      const cfg = await firstValueFrom(
        this.http.get<{ apiUrl: string }>('/assets/config.json')
      );
      if (cfg && cfg.apiUrl) {
        this.config = cfg;
      }
    } catch (e) {
      console.warn('No se pudo cargar config.json, usando default', e);
    }
  }

  get apiUrl(): string {
    return this.config.apiUrl;
  }
}
