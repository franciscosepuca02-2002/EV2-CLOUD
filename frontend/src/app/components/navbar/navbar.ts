import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { Auth, Usuario } from '../../services/auth';
import { Carrito } from '../../services/carrito';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
})
export class Navbar implements OnInit {
  private authSvc = inject(Auth);
  private carritoSvc = inject(Carrito);
  private router = inject(Router);

  usuario: Usuario | null = null;

  ngOnInit() {
    this.usuario = this.authSvc.getUsuario();
  }

  get cantidadCarrito(): number {
    return this.carritoSvc.cantidad();
  }

  cerrarSesion() {
    this.authSvc.logout();
    this.usuario = null;
    this.router.navigate(['/login']);
  }
}
