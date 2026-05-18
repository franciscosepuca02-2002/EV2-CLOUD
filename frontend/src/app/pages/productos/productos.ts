import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProductoService } from '../../services/producto';
import { Carrito } from '../../services/carrito';
import { Navbar } from '../../components/navbar/navbar';

@Component({
  selector: 'app-productos',
  standalone: true,
  imports: [CommonModule, Navbar],
  templateUrl: './productos.html',
  styleUrls: ['./productos.css']
})
export class Productos implements OnInit {
  private productoService = inject(ProductoService);
  private carritoSvc = inject(Carrito);
  private cdr = inject(ChangeDetectorRef);

  productos: any[] = [];
  cargando = true;
  error = '';

  ngOnInit() {
    this.productoService.obtenerProductos().subscribe({
      next: (data: any) => {
        this.productos = data;
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.cargando = false;
        this.error = 'No se pudieron cargar los productos';
        console.error(err);
      }
    });
  }

  agregarCarrito(producto: any) {
    this.carritoSvc.agregar({
      id: producto.id,
      nombre: producto.nombre,
      precio: producto.precio
    });
    alert('Producto agregado al carrito');
  }
}
