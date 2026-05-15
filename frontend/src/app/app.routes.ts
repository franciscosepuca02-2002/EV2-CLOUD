import { Routes } from '@angular/router';

import {Productos} from './pages/productos/productos';
import { Carrito } from './pages/carrito/carrito';
import { Pago } from './pages/pago/pago';
import { Login } from './pages/login/login';
import { Register } from './pages/register/register';

export const routes: Routes = [
    { path: '', component: Productos },
    { path: 'carrito', component: Carrito },
    { path: 'pago', component: Pago },
    { path: 'login', component: Login },
    { path: 'register', component: Register }
];