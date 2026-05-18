import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Navbar } from '../../components/navbar/navbar';
import { Carrito, ItemCarrito } from '../../services/carrito';
import { Auth } from '../../services/auth';
import { Pago as PagoService } from '../../services/pago';

@Component({
  selector: 'app-pago',
  standalone: true,
  imports: [CommonModule, FormsModule, Navbar],
  templateUrl: './pago.html',
  styleUrl: './pago.css',
})
export class Pago implements OnInit {
  private carritoSvc = inject(Carrito);
  private authSvc = inject(Auth);
  private pagoSvc = inject(PagoService);
  private router = inject(Router);

  items: ItemCarrito[] = [];
  total = 0;
  cargando = false;
  error = '';
  metodoPago: 'credito' | 'debito' = 'credito';

  ngOnInit() {
    this.items = this.carritoSvc.obtener();
    this.total = this.carritoSvc.total();

    if (this.items.length === 0) {
      this.router.navigate(['/carrito']);
    }
  }

  pagar() {
    this.error = '';
    const usuario = this.authSvc.getUsuario();

    if (!usuario) {
      this.error = 'Debes iniciar sesión para pagar';
      setTimeout(() => this.router.navigate(['/login']), 1500);
      return;
    }

    this.cargando = true;
    this.pagoSvc.iniciarPago(usuario.id, usuario.correo, this.items).subscribe({
      next: (res) => {
        this.cargando = false;
        // limpiar carrito local antes de redirigir a Mercado Pago
        this.carritoSvc.vaciar();
        if (res.url_pago) {
          window.location.href = res.url_pago;
        } else {
          this.error = 'No se recibió URL de pago';
        }
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.error?.detail || 'Error iniciando el pago';
      }
    });
  }
}
