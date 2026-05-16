import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Productos } from '../productos/productos';

@Component({
  selector: 'app-inicio',
  imports: [CommonModule, Productos],
  templateUrl: './inicio.html',
  styleUrl: './inicio.css',
})
export class Inicio {}
