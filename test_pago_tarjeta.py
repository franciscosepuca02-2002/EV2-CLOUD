#!/usr/bin/env python3
"""
Script de prueba para procesar pagos con tarjetas de prueba de MercadoPago
Prueba diferentes escenarios de pago según las tarjetas de prueba oficiales
"""

import requests
import json
import time
from typing import Dict, Any

# Configuración del servicio
BASE_URL = "http://localhost:8002"

# Tarjetas de prueba de MercadoPago
TARJETAS_PRUEBA = {
    "mastercard_credito": {
        "numero": "5416752602582580",
        "cvv": "123",
        "mes": 11,
        "anio": 2030,
        "tipo": "Mastercard Crédito"
    },
    "visa_credito": {
        "numero": "4168818844447115",
        "cvv": "123",
        "mes": 11,
        "anio": 2030,
        "tipo": "Visa Crédito"
    },
    "amex_credito": {
        "numero": "375778174461804",
        "cvv": "1234",
        "mes": 11,
        "anio": 2030,
        "tipo": "American Express"
    },
    "mastercard_debito": {
        "numero": "5241019826646950",
        "cvv": "123",
        "mes": 11,
        "anio": 2030,
        "tipo": "Mastercard Débito"
    },
    "visa_debito": {
        "numero": "4023653523914373",
        "cvv": "123",
        "mes": 11,
        "anio": 2030,
        "tipo": "Visa Débito"
    }
}

# Escenarios de prueba según titular de la tarjeta
ESCENARIOS_PRUEBA = {
    "APRO": {
        "nombre": "APRO",
        "documento": "123456789",
        "resultado_esperado": "PAGADO",
        "descripcion": "Pago aprobado"
    },
    "OTHE": {
        "nombre": "OTHE",
        "documento": "123456789",
        "resultado_esperado": "RECHAZADO",
        "descripcion": "Rechazado por error general"
    },
    "CONT": {
        "nombre": "CONT",
        "documento": "123456789",
        "resultado_esperado": "PENDIENTE",
        "descripcion": "Pendiente de pago"
    },
    "CALL": {
        "nombre": "CALL",
        "documento": "123456789",
        "resultado_esperado": "RECHAZADO",
        "descripcion": "Rechazado con validación para autorizar"
    },
    "FUND": {
        "nombre": "FUND",
        "documento": "123456789",
        "resultado_esperado": "RECHAZADO",
        "descripcion": "Rechazado por importe insuficiente"
    },
    "SECU": {
        "nombre": "SECU",
        "documento": "123456789",
        "resultado_esperado": "RECHAZADO",
        "descripcion": "Rechazado por código de seguridad inválido"
    },
    "EXPI": {
        "nombre": "EXPI",
        "documento": "123456789",
        "resultado_esperado": "RECHAZADO",
        "descripcion": "Rechazado por fecha de vencimiento"
    }
}


def verificar_servicio() -> bool:
    """Verifica que el servicio esté disponible"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servicio disponible: {data}")
            return data.get("status") == "healthy"
        else:
            print(f"❌ Servicio no saludable: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servicio: {e}")
        return False


def procesar_pago(
    tarjeta: Dict[str, Any],
    escenario: Dict[str, Any],
    id_usuario: int = 1,
    monto: float = 1000.0
) -> Dict[str, Any]:
    """Procesa un pago con los datos proporcionados"""
    
    payload = {
        "id_usuario": id_usuario,
        "numero_tarjeta": tarjeta["numero"],
        "mes_vencimiento": tarjeta["mes"],
        "anio_vencimiento": tarjeta["anio"],
        "cvv": tarjeta["cvv"],
        "nombre_titular": escenario["nombre"],
        "email": "test@example.com",
        "descripcion": f"Prueba {escenario['descripcion']}",
        "monto": monto
    }
    
    print(f"\n{'='*80}")
    print(f"🔄 Procesando pago...")
    print(f"   Tarjeta: {tarjeta['tipo']}")
    print(f"   Escenario: {escenario['descripcion']}")
    print(f"   Titular: {escenario['nombre']}")
    print(f"   Monto: ${monto}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/pagos/directo/procesar",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            
            if data.get('data'):
                pago_data = data['data']
                print(f"\n💳 Detalles del pago:")
                print(f"   ID Pago: {pago_data.get('id_pago')}")
                print(f"   Estado: {pago_data.get('estado')}")
                print(f"   MP Payment ID: {pago_data.get('mp_payment_id')}")
                print(f"   External Reference: {pago_data.get('external_reference')}")
                
                # Verificar si el resultado es el esperado
                estado_obtenido = pago_data.get('estado')
                estado_esperado = escenario['resultado_esperado']
                
                if estado_obtenido == estado_esperado:
                    print(f"\n✅ ÉXITO: Estado obtenido '{estado_obtenido}' coincide con esperado '{estado_esperado}'")
                else:
                    print(f"\n⚠️  ADVERTENCIA: Estado obtenido '{estado_obtenido}' difiere de esperado '{estado_esperado}'")
                
                return {
                    "success": True,
                    "id_pago": pago_data.get('id_pago'),
                    "estado": estado_obtenido,
                    "mp_payment_id": pago_data.get('mp_payment_id')
                }
            
            return {"success": True, "data": data}
        else:
            error_data = response.json() if response.text else {}
            print(f"   Error: {error_data}")
            print(f"\n❌ FALLO: {response.status_code} - {error_data.get('detail', 'Error desconocido')}")
            return {"success": False, "error": error_data}
            
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {str(e)}")
        return {"success": False, "error": str(e)}


def consultar_estado_pago(id_pago: int) -> Dict[str, Any]:
    """Consulta el estado de un pago"""
    try:
        response = requests.get(f"{BASE_URL}/pagos/{id_pago}/estado", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Estado del pago {id_pago}: {data.get('estado')}")
            return data
        else:
            print(f"❌ Error consultando estado: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}


def main():
    """Función principal de pruebas"""
    print("\n" + "="*80)
    print("🚀 INICIANDO PRUEBAS DE PAGOS CON MERCADOPAGO")
    print("="*80)
    
    # Verificar que el servicio esté disponible
    if not verificar_servicio():
        print("\n❌ El servicio no está disponible. Asegúrate de que esté corriendo.")
        print("   Ejecuta: docker-compose up -d")
        return
    
    print("\n✅ Servicio verificado y funcionando correctamente")
    
    # Prueba 1: Pago aprobado con Visa
    print("\n" + "="*80)
    print("📝 PRUEBA 1: Pago APROBADO con Visa Crédito")
    print("="*80)
    resultado1 = procesar_pago(
        tarjeta=TARJETAS_PRUEBA["visa_credito"],
        escenario=ESCENARIOS_PRUEBA["APRO"],
        monto=5000.0
    )
    
    if resultado1.get("success") and resultado1.get("id_pago"):
        time.sleep(2)
        consultar_estado_pago(resultado1["id_pago"])
    
    time.sleep(3)
    
    # Prueba 2: Pago rechazado por fondos insuficientes
    print("\n" + "="*80)
    print("📝 PRUEBA 2: Pago RECHAZADO por fondos insuficientes")
    print("="*80)
    resultado2 = procesar_pago(
        tarjeta=TARJETAS_PRUEBA["mastercard_credito"],
        escenario=ESCENARIOS_PRUEBA["FUND"],
        monto=2500.0
    )
    
    if resultado2.get("success") and resultado2.get("id_pago"):
        time.sleep(2)
        consultar_estado_pago(resultado2["id_pago"])
    
    time.sleep(3)
    
    # Prueba 3: Pago pendiente
    print("\n" + "="*80)
    print("📝 PRUEBA 3: Pago PENDIENTE")
    print("="*80)
    resultado3 = procesar_pago(
        tarjeta=TARJETAS_PRUEBA["visa_debito"],
        escenario=ESCENARIOS_PRUEBA["CONT"],
        monto=1500.0
    )
    
    if resultado3.get("success") and resultado3.get("id_pago"):
        time.sleep(2)
        consultar_estado_pago(resultado3["id_pago"])
    
    time.sleep(3)
    
    # Prueba 4: Pago rechazado por error general
    print("\n" + "="*80)
    print("📝 PRUEBA 4: Pago RECHAZADO por error general")
    print("="*80)
    resultado4 = procesar_pago(
        tarjeta=TARJETAS_PRUEBA["mastercard_debito"],
        escenario=ESCENARIOS_PRUEBA["OTHE"],
        monto=3000.0
    )
    
    if resultado4.get("success") and resultado4.get("id_pago"):
        time.sleep(2)
        consultar_estado_pago(resultado4["id_pago"])
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE PRUEBAS COMPLETADAS")
    print("="*80)
    print("✅ Todas las pruebas han sido ejecutadas")
    print("   Revisa los logs anteriores para ver los resultados detallados")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
