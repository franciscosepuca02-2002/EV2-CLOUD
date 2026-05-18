import { Injectable } from '@angular/core';

export interface ItemCarrito {
  id: number;
  nombre: string;
  precio: number;
}

@Injectable({ providedIn: 'root' })
export class Carrito {
  private key = 'carrito';

  obtener(): ItemCarrito[] {
    return JSON.parse(localStorage.getItem(this.key) || '[]');
  }

  agregar(item: ItemCarrito) {
    const items = this.obtener();
    items.push(item);
    localStorage.setItem(this.key, JSON.stringify(items));
  }

  eliminar(index: number) {
    const items = this.obtener();
    items.splice(index, 1);
    localStorage.setItem(this.key, JSON.stringify(items));
  }

  vaciar() {
    localStorage.removeItem(this.key);
  }

  total(): number {
    return this.obtener().reduce((acc, item) => acc + item.precio, 0);
  }

  cantidad(): number {
    return this.obtener().length;
  }
}
