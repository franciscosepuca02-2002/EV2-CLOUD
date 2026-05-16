import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProductoService } from '../../services/producto';
import { ChangeDetectorRef } from '@angular/core';
import { Navbar } from '../../components/navbar/navbar';

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule, Navbar],
  templateUrl: './productos.html',
  styleUrls: ['./productos.css']
})
export class Productos implements OnInit {

  productos:any[] = [];

  constructor(
  private productoService: ProductoService,
  private cdr: ChangeDetectorRef
){}

  ngOnInit(){

  this.productoService.obtenerProductos()
  .subscribe((data:any)=>{

    console.log(data);

    this.productos = data;

    this.cdr.detectChanges();
  });
}

  agregarCarrito(producto:any){

    let carrito = JSON.parse(localStorage.getItem('carrito') || '[]');

    carrito.push(producto);

    localStorage.setItem('carrito', JSON.stringify(carrito));

    alert('Producto agregado');
  }
}