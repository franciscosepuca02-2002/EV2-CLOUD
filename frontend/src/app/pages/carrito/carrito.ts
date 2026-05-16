import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Navbar } from '../../components/navbar/navbar';

@Component({
  selector: 'app-carrito',
  standalone: true,
  imports: [CommonModule, RouterModule, Navbar],
  templateUrl: './carrito.html',
  styleUrl: './carrito.css'
})
export class Carrito {

  carrito:any[] = [];

  total = 0;

  ngOnInit(){

    this.carrito = JSON.parse(localStorage.getItem('carrito') || '[]');

    this.calcularTotal();
  }

  calcularTotal(){

    this.total = this.carrito.reduce(
      (acc, item) => acc + item.precio,
      0
    );
  }
}