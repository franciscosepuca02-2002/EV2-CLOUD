import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class Register {
  private authService = inject(Auth);
  private router = inject(Router);

  nombre = '';
  correo = '';
  password = '';
  error = '';
  exito = '';
  cargando = false;

  onSubmit() {
    this.error = '';
    this.exito = '';
    if (!this.nombre || !this.correo || !this.password) {
      this.error = 'Completa todos los campos';
      return;
    }
    if (this.password.length < 4) {
      this.error = 'Contraseña debe tener al menos 4 caracteres';
      return;
    }
    this.cargando = true;
    this.authService.registro(this.nombre, this.correo, this.password).subscribe({
      next: () => {
        this.cargando = false;
        this.exito = 'Cuenta creada, redirigiendo a login...';
        setTimeout(() => this.router.navigate(['/login']), 1500);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.error?.detail || 'Error registrando usuario';
      }
    });
  }
}
