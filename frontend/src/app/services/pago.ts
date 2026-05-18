import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ConfigService } from './config.service';
import { ItemCarrito } from './carrito';

export interface IniciarPagoResponse {
  pedido_id: number;
  url_pago: string;
  external_reference: string;
  total: number;
}

@Injectable({ providedIn: 'root' })
export class Pago {
  private http = inject(HttpClient);
  private config = inject(ConfigService);

  iniciarPago(id_usuario: number, email: string, items: ItemCarrito[]) {
    return this.http.post<IniciarPagoResponse>(
      `${this.config.apiUrl}/pagos/iniciar`,
      { id_usuario, email, items }
    );
  }

  obtenerPedido(pedidoId: number) {
    return this.http.get(`${this.config.apiUrl}/pagos/pedido/${pedidoId}`);
  }
}
