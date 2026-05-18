import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Navbar } from '../../components/navbar/navbar';
import { Carrito as CarritoSvc, ItemCarrito } from '../../services/carrito';

@Component({
  selector: 'app-carrito',
  standalone: true,
  imports: [CommonModule, RouterModule, Navbar],
  templateUrl: './carrito.html',
  styleUrl: './carrito.css'
})
export class Carrito implements OnInit {
  private carritoSvc = inject(CarritoSvc);

  items: ItemCarrito[] = [];
  total = 0;

  ngOnInit() {
    this.refrescar();
  }

  refrescar() {
    this.items = this.carritoSvc.obtener();
    this.total = this.carritoSvc.total();
  }

  eliminar(index: number) {
    this.carritoSvc.eliminar(index);
    this.refrescar();
  }

  vaciar() {
    this.carritoSvc.vaciar();
    this.refrescar();
  }
}
