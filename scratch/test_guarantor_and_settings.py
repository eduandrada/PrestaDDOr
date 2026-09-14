import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Ensure app imports properly
sys.path.insert(0, os.path.abspath('.'))

from app import app, db
from models import Client, Loan, Setting

def run_tests():
    print("--- INICIANDO TEST COMPLETO DE INTEGRACION ---")
    with app.app_context():
        # Initialize test client
        client = app.test_client()

        # 1. Test Settings GET and POST (Unified Empresa y Aplicacion)
        print("\n1. Verificando endpoint /api/settings...")
        res = client.get('/api/settings')
        assert res.status_code == 200, f"Error getting settings: {res.status_code}"
        initial_settings = res.get_json()
        print(f"Ajustes cargados: {list(initial_settings.keys())}")

        new_settings = {
            "company_name": "Financiera Andrada & Asociados",
            "company_cuit": "20-33889900-4",
            "alias_cbu": "ANDRADA.FINANZAS.MP",
            "company_cbu": "0000003100099988877711",
            "company_bank": "Banco Santander Río",
            "company_titular": "Eduardo Andrada",
            "company_phone": "5493834112233",
            "company_address": "San Martín 450, San Fernando del Valle de Catamarca",
            "default_grace_days": "5",
            "default_late_fee": "1.5",
            "ant_expense_threshold": "3000"
        }
        res_post = client.post('/api/settings', json=new_settings)
        assert res_post.status_code == 200, f"Error posting settings: {res_post.status_code}"
        
        # Verify persistence
        res_get_updated = client.get('/api/settings')
        updated_data = res_get_updated.get_json()
        assert updated_data.get('company_name') == "Financiera Andrada & Asociados"
        assert updated_data.get('alias_cbu') == "ANDRADA.FINANZAS.MP"
        print("✅ Configuración unificada de Empresa y Aplicación persistida con éxito.")

        import time
        t_suffix = str(int(time.time()))[-6:]

        # 2. Test Client Creation without guarantor
        print("\n2. Creando cliente SIN garante...")
        c_no_guarantor = {
            "name": f"Cliente Sin Garante {t_suffix}",
            "dni": f"99{t_suffix}",
            "cuit": f"2099{t_suffix}4",
            "address": "Calle Falsa 123",
            "phone": f"3834{t_suffix}",
            "whatsapp": f"5493834{t_suffix}",
            "has_guarantor": False
        }
        res_c1 = client.post('/api/clients', json=c_no_guarantor)
        assert res_c1.status_code == 201, f"Error creating client without guarantor: {res_c1.data}"
        c1_data = res_c1.get_json()
        assert c1_data['has_guarantor'] is False
        assert c1_data['guarantor_name'] == ''
        print(f"✅ Cliente #{c1_data['id']} creado sin garante correctamente.")

        # 3. Test Client Creation with guarantor validation failure
        print("\n3. Validando requerimiento estricto de campos si has_guarantor es True...")
        invalid_guarantor_client = {
            "name": f"Cliente Fallido Garante {t_suffix}",
            "dni": f"98{t_suffix}",
            "cuit": f"2098{t_suffix}4",
            "address": "Calle Falsa 456",
            "phone": f"3835{t_suffix}",
            "whatsapp": f"5493835{t_suffix}",
            "has_guarantor": True,
            "guarantor_name": "Garante Incompleto",
            # missing cuit, address, phone
        }
        res_inv = client.post('/api/clients', json=invalid_guarantor_client)
        assert res_inv.status_code == 400, f"Expected 400 for incomplete guarantor, got {res_inv.status_code}"
        print(f"✅ Validación exitosa: Rechazó garante incompleto con error: {res_inv.get_json()['error']}")

        # 4. Test Client Creation with valid guarantor
        print("\n4. Creando cliente CON garante completo...")
        valid_guarantor_client = {
            "name": f"Juan Carlos Pérez ({t_suffix})",
            "dni": f"35{t_suffix}",
            "cuit": f"2035{t_suffix}4",
            "address": "Av. Belgrano 780, Catamarca",
            "phone": f"3836{t_suffix}",
            "whatsapp": f"5493836{t_suffix}",
            "email": f"juan_{t_suffix}@example.com",
            "has_guarantor": True,
            "guarantor_name": "Roberto Gómez (Garante)",
            "guarantor_address": "Rivadavia 1234, Catamarca",
            "guarantor_cuit": "20358889994",
            "guarantor_phone": f"5493837{t_suffix}"
        }
        res_c2 = client.post('/api/clients', json=valid_guarantor_client)
        assert res_c2.status_code == 201, f"Error creating client with guarantor: {res_c2.data}"
        c2_data = res_c2.get_json()
        c2_id = c2_data['id']
        assert c2_data['has_guarantor'] is True
        assert c2_data['guarantor_name'] == "Roberto Gómez (Garante)"
        assert c2_data['guarantor_cuit'] == "20358889994"
        assert c2_data['guarantor_phone'] == f"5493837{t_suffix}"
        print(f"✅ Cliente #{c2_id} creado con garante: {c2_data['guarantor_name']}.")

        # 5. Test Ficha PDF Generation
        print(f"\n5. Verificando generación de Ficha y Contrato PDF (/api/clients/{c2_id}/ficha_pdf)...")
        res_ficha = client.get(f'/api/clients/{c2_id}/ficha_pdf')
        assert res_ficha.status_code == 200, f"Error getting ficha pdf: {res_ficha.status_code}"
        ficha_html = res_ficha.data.decode('utf-8')
        assert f"Juan Carlos Pérez ({t_suffix})" in ficha_html
        assert "Roberto Gómez (Garante)" in ficha_html
        assert "20358889994" in ficha_html
        assert "window.print()" in ficha_html
        print("✅ Ficha PDF generada con datos de titular, garante y disparador de impresión.")

        # 6. Test Garante Cobro PDF Generation
        print(f"\n6. Verificando generación de Notificación de Cobro al Garante (/api/clients/{c2_id}/garante_cobro_pdf)...")
        res_cobro = client.get(f'/api/clients/{c2_id}/garante_cobro_pdf')
        assert res_cobro.status_code == 200, f"Error getting garante cobro pdf: {res_cobro.status_code}"
        cobro_html = res_cobro.data.decode('utf-8')
        assert "REQUERIMIENTO FORMAL DE PAGO" in cobro_html or "Intimación Formal de Cobro" in cobro_html
        assert "Roberto Gómez (Garante)" in cobro_html
        assert f"Juan Carlos Pérez ({t_suffix})" in cobro_html
        print("✅ Notificación de cobro al garante en PDF generada con éxito.")

        # 7. Clean up test records
        c1 = Client.query.get(c1_data['id'])
        c2 = Client.query.get(c2_id)
        if c1: db.session.delete(c1)
        if c2: db.session.delete(c2)
        db.session.commit()
        print("\n✅ Limpieza de registros de prueba completada.")

    print("\n🎉 TODOS LOS TESTS COMPLETADOS Y APROBADOS CON ÉXITO.")

if __name__ == '__main__':
    run_tests()
