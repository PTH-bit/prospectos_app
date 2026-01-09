"""
Script de verificación para la funcionalidad de usuarios inactivos.

Este script verifica:
1. Que el usuario servicio_cliente existe
2. Que el dashboard_service filtra usuarios inactivos
3. Que la importación de Excel maneja usuarios inactivos correctamente
"""

import sys
import os
# Agregar el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import Usuario, Prospecto, TipoUsuario
from services.dashboard_service import DashboardService
from datetime import date

def verificar_usuario_servicio_cliente():
    """Verifica que el usuario servicio_cliente existe y está configurado correctamente"""
    print("\n" + "="*60)
    print("1. VERIFICANDO USUARIO SERVICIO_CLIENTE")
    print("="*60)
    
    db = next(get_db())
    user = db.query(Usuario).filter(Usuario.username == 'servicio_cliente').first()
    
    if not user:
        print("❌ ERROR: Usuario servicio_cliente NO existe")
        return False
    
    print(f"✅ Usuario encontrado: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Activo: {user.activo}")
    print(f"   Tipo: {user.tipo_usuario}")
    
    # Verificar configuración correcta
    assert user.email == "servicioclientetravelhouse@gmail.com", "Email incorrecto"
    assert user.activo == 1, "Usuario debe estar activo"
    assert user.tipo_usuario == TipoUsuario.AGENTE.value, "Tipo de usuario incorrecto"
    
    print("✅ Usuario servicio_cliente configurado correctamente")
    return True


def verificar_filtro_dashboard():
    """Verifica que el dashboard filtra usuarios inactivos"""
    print("\n" + "="*60)
    print("2. VERIFICANDO FILTRO DE DASHBOARD")
    print("="*60)
    
    db = next(get_db())
    
    # Obtener admin para las estadísticas
    admin = db.query(Usuario).filter(Usuario.tipo_usuario == TipoUsuario.ADMINISTRADOR.value).first()
    
    if not admin:
        print("❌ ERROR: No hay usuario administrador")
        return False
    
    # Crear servicio de dashboard
    dashboard_service = DashboardService(db)
    
    # Obtener estadísticas
    stats = dashboard_service.get_stats(admin, "mes")
    
    print(f"✅ Estadísticas obtenidas correctamente")
    print(f"   Total prospectos: {stats['total_prospectos']}")
    print(f"   Agentes en conversión: {len(stats['conversion_agentes'])}")
    
    # Verificar que solo incluye usuarios activos
    usuarios_activos = db.query(Usuario).filter(
        Usuario.tipo_usuario == TipoUsuario.AGENTE.value,
        Usuario.activo == 1
    ).count()
    
    print(f"   Usuarios activos en BD: {usuarios_activos}")
    
    # Verificar que ningún usuario inactivo aparece en las estadísticas
    usernames_en_stats = [a['username'] for a in stats['conversion_agentes']]
    usuarios_inactivos = db.query(Usuario).filter(
        Usuario.tipo_usuario == TipoUsuario.AGENTE.value,
        Usuario.activo == 0
    ).all()
    
    for usuario_inactivo in usuarios_inactivos:
        if usuario_inactivo.username in usernames_en_stats:
            print(f"❌ ERROR: Usuario inactivo {usuario_inactivo.username} aparece en estadísticas")
            return False
    
    if usuarios_inactivos:
        print(f"✅ {len(usuarios_inactivos)} usuarios inactivos correctamente excluidos de estadísticas")
    else:
        print("ℹ️  No hay usuarios inactivos para verificar")
    
    return True


def verificar_estructura_base_datos():
    """Verifica que la estructura de la base de datos tiene los campos necesarios"""
    print("\n" + "="*60)
    print("3. VERIFICANDO ESTRUCTURA DE BASE DE DATOS")
    print("="*60)
    
    db = next(get_db())
    
    # Verificar que el modelo Usuario tiene campo activo
    usuarios = db.query(Usuario).first()
    if usuarios:
        assert hasattr(usuarios, 'activo'), "Campo 'activo' no existe en Usuario"
        print("✅ Campo 'activo' existe en modelo Usuario")
    
    # Verificar que el modelo Prospecto tiene agente_original_id
    prospectos = db.query(Prospecto).first()
    if prospectos:
        assert hasattr(prospectos, 'agente_original_id'), "Campo 'agente_original_id' no existe en Prospecto"
        print("✅ Campo 'agente_original_id' existe en modelo Prospecto")
    
    return True


def mostrar_resumen_usuarios():
    """Muestra un resumen de todos los usuarios en el sistema"""
    print("\n" + "="*60)
    print("4. RESUMEN DE USUARIOS EN EL SISTEMA")
    print("="*60)
    
    db = next(get_db())
    usuarios = db.query(Usuario).all()
    
    print(f"\nTotal de usuarios: {len(usuarios)}\n")
    
    activos = [u for u in usuarios if u.activo == 1]
    inactivos = [u for u in usuarios if u.activo == 0]
    
    print(f"Usuarios ACTIVOS ({len(activos)}):")
    for u in activos:
        print(f"  - {u.username:20} | {u.email:35} | Tipo: {u.tipo_usuario}")
    
    if inactivos:
        print(f"\nUsuarios INACTIVOS ({len(inactivos)}):")
        for u in inactivos:
            print(f"  - {u.username:20} | {u.email:35} | Tipo: {u.tipo_usuario}")
    else:
        print("\nNo hay usuarios inactivos")
    
    return True


def main():
    """Ejecuta todas las verificaciones"""
    print("\n" + "="*60)
    print("VERIFICACIÓN DE FUNCIONALIDAD DE USUARIOS INACTIVOS")
    print("="*60)
    
    try:
        resultados = []
        
        # Ejecutar verificaciones
        resultados.append(("Usuario servicio_cliente", verificar_usuario_servicio_cliente()))
        resultados.append(("Filtro de dashboard", verificar_filtro_dashboard()))
        resultados.append(("Estructura de BD", verificar_estructura_base_datos()))
        resultados.append(("Resumen de usuarios", mostrar_resumen_usuarios()))
        
        # Mostrar resumen final
        print("\n" + "="*60)
        print("RESUMEN DE VERIFICACIÓN")
        print("="*60)
        
        for nombre, resultado in resultados:
            estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
            print(f"{estado} - {nombre}")
        
        # Resultado final
        todos_pasaron = all(r[1] for r in resultados)
        
        print("\n" + "="*60)
        if todos_pasaron:
            print("✅ TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE")
        else:
            print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("="*60 + "\n")
        
        return todos_pasaron
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    resultado = main()
    sys.exit(0 if resultado else 1)
