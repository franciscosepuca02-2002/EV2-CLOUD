import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  private authService = inject(Auth);
  private router = inject(Router);

  correo = '';
  password = '';
  error = '';
  cargando = false;

  onSubmit() {
    this.error = '';
    if (!this.correo || !this.password) {
      this.error = 'Completa todos los campos';
      return;
    }
    this.cargando = true;
    this.authService.login(this.correo, this.password).subscribe({
      next: () => {
        this.cargando = false;
        this.router.navigate(['/productos']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.error?.detail || 'Error iniciando sesión';
      }
    });
  }
}
