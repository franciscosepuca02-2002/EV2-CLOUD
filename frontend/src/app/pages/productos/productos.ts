import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './productos.html',
  styleUrl: './productos.css'
})
export class Productos {

  productos = [
    {
      id: 1,
      nombre: 'Notebook Gamer',
      precio: 850000
    },
    {
      id: 2,
      nombre: 'Mouse Logitech',
      precio: 25000
    }
  ];

  agregarCarrito(producto:any){

    let carrito = JSON.parse(localStorage.getItem('carrito') || '[]');

    carrito.push(producto);

    localStorage.setItem('carrito', JSON.stringify(carrito));

    alert('Producto agregado');
    localStorage.setItem('carrito', '');
  }
}