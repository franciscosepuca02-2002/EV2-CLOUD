import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Productos } from './pages/productos/productos';
import { Carrito } from './pages/carrito/carrito';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Productos, Carrito],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
}
