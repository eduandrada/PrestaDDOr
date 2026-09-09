import sys
import os
import json
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import app, db
from models import Client, Loan, PersonalBill, Expense, Raffle, ShoppingItem, NoticeBoardItem, HomeCalendarItem, BiometricRequest

def run_audit():
    print("==================================================================")
    print("      INICIANDO AUDITORÍA COMPLETA DEL SISTEMA PRESTAMOS 2026     ")
    print("==================================================================")
    
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    passed_tests = 0
    total_tests = 0

    def check(name, condition, error_msg=""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"  [PASS] {name}")
        else:
            print(f"  [FAIL] {name}: {error_msg}")


    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # 1. Main Page Index Render
            print("\n--- 1. INDEX & DASHBOARD RENDER ---")
            res = client.get('/')
            check("GET / (Index HTML)", res.status_code == 200 and b'<!DOCTYPE html>' in res.data)

            res = client.get('/api/dashboard/stats')
            check("GET /api/dashboard/stats", res.status_code == 200 and 'capital_en_calle' in res.get_json())

            res = client.get('/api/dolar-rates')
            check("GET /api/dolar-rates", res.status_code == 200)

            res = client.get('/api/settings')
            check("GET /api/settings", res.status_code == 200)

            res = client.post('/api/settings', data=json.dumps({'company_name': 'Prestamos Familia Andrada'}), content_type='application/json')
            check("POST /api/settings", res.status_code == 200)

            # 2. Clients CRUD & Documents Vault
            print("\n--- 2. CLIENTES & BÓVEDA DIGITAL ---")
            res = client.get('/api/clients')
            check("GET /api/clients", res.status_code == 200)

            res = client.post('/api/clients', data=json.dumps({
                'name': 'Juan Carlos Test',
                'whatsapp': '5491199887766',
                'email': 'juancarlos@test.com',
                'address': 'Calle Falsa 123',
                'notes': 'Cliente de auditoría'
            }), content_type='application/json')
            check("POST /api/clients (Crear)", res.status_code == 201)
            c_json = res.get_json()
            client_id = c_json.get('client', {}).get('id') if isinstance(c_json, dict) and 'client' in c_json else c_json.get('id')

            res = client.put(f'/api/clients/{client_id}', data=json.dumps({
                'name': 'Juan Carlos Test Actualizado',
                'whatsapp': '5491199887766'
            }), content_type='application/json')
            check("PUT /api/clients/<id> (Editar)", res.status_code == 200)

            res = client.get(f'/api/clients/{client_id}/history')
            check("GET /api/clients/<id>/history", res.status_code == 200)

            res = client.get(f'/api/clients/{client_id}/vcard')
            check("GET /api/clients/<id>/vcard", res.status_code == 200 and 'BEGIN:VCARD' in res.data.decode())

            sample_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            res = client.post(f'/api/clients/{client_id}/documents', data=json.dumps({
                'doc_type': 'dni_frente',
                'title': 'DNI Frente',
                'image_data': sample_img
            }), content_type='application/json')
            check("POST /api/clients/<id>/documents", res.status_code == 201)
            doc_id = res.get_json()['id']

            res = client.delete(f'/api/documents/{doc_id}')
            check("DELETE /api/documents/<id>", res.status_code == 200)

            # 3. Loans CRUD, Amortization, Payments, Pagaré PDF
            print("\n--- 3. PRÉSTAMOS, AMORTIZACIÓN & PAGARÉ ---")
            res = client.get('/api/loans')
            check("GET /api/loans", res.status_code == 200)

            res = client.post('/api/loans', data=json.dumps({
                'client_id': client_id,
                'amount': 100000,
                'interest_rate': 20,
                'rate_type': 'mensual',
                'modality': 'mensual',
                'installments_count': 4,
                'start_date': '2026-09-01',
                'grace_days': 3,
                'late_fee_type': 'porcentaje',
                'late_fee_value': 1.0
            }), content_type='application/json')
            check("POST /api/loans (Crear Préstamo)", res.status_code == 201)
            l_json = res.get_json()
            loan_id = l_json.get('loan', {}).get('id') if isinstance(l_json, dict) and 'loan' in l_json else l_json.get('id')


            res = client.get(f'/api/loans/{loan_id}')
            check("GET /api/loans/<id>", res.status_code == 200)
            loan_data = res.get_json()
            inst_id = loan_data['installments'][0]['id']

            res = client.put(f'/api/loans/{loan_id}', data=json.dumps({
                'notes': 'Notas editadas auditoría',
                'grace_days': 5
            }), content_type='application/json')
            check("PUT /api/loans/<id>", res.status_code == 200)

            res = client.post(f'/api/installments/{inst_id}/pay', data=json.dumps({
                'amount': 30000,
                'payment_method': 'Transferencia',
                'notes': 'Pago parcial auditoría'
            }), content_type='application/json')
            check("POST /api/installments/<id>/pay", res.status_code == 200 and res.get_json()['success'] is True)

            res = client.get(f'/api/loans/{loan_id}/pagare_pdf')
            check("GET /api/loans/<id>/pagare_pdf", res.status_code == 200 and res.mimetype == 'application/pdf')

            # 4. Personal Accounts, Salaries & AI Financial Advisor
            print("\n--- 4. CUENTAS PERSONALES, SUELDOS & ASESOR IA ---")
            res = client.get('/api/personal_accounts')
            check("GET /api/personal_accounts", res.status_code == 200)

            res = client.post('/api/personal_accounts', data=json.dumps({
                'name': 'Internet Fibra Óptica',
                'category': 'servicio',
                'owner': 'Compartido',
                'amount': 18500,
                'due_day': 15,
                'status': 'pendiente',
                'month': 9,
                'year': 2026
            }), content_type='application/json')
            check("POST /api/personal_accounts", res.status_code == 201)
            bill_id = res.get_json()['bill']['id']

            res = client.post(f'/api/personal_accounts/{bill_id}/toggle_paid')
            check("POST /api/personal_accounts/<id>/toggle_paid", res.status_code == 200)

            res = client.post('/api/personal_accounts/salaries', data=json.dumps({
                'salary_eduardo': 600000,
                'salary_maira': 500000
            }), content_type='application/json')
            check("POST /api/personal_accounts/salaries", res.status_code == 200)

            res = client.get('/api/personal_accounts/ai_analysis')
            check("GET /api/personal_accounts/ai_analysis", res.status_code == 200)

            res = client.get('/api/ai_financial_advisor')
            check("GET /api/ai_financial_advisor", res.status_code == 200)

            res = client.post('/api/personal_accounts/ai_advisor_chat', data=json.dumps({
                'question': '¿Qué dinero puedo retirar este mes?'
            }), content_type='application/json')
            check("POST /api/personal_accounts/ai_advisor_chat", res.status_code == 200 and 'response' in res.get_json())

            # 5. Expenses Module
            print("\n--- 5. MÓDULO DE GASTOS & FUGA HORMIGA ---")
            res = client.get('/api/expenses')
            check("GET /api/expenses", res.status_code == 200)

            res = client.post('/api/expenses', data=json.dumps({
                'category': 'Variable',
                'description': 'Café y Snacks',
                'amount': 3500,
                'date': '2026-09-09',
                'is_ant_expense': True
            }), content_type='application/json')
            check("POST /api/expenses", res.status_code == 201)
            exp_id = res.get_json()['expense']['id']

            res = client.delete(f'/api/expenses/{exp_id}')
            check("DELETE /api/expenses/<id>", res.status_code == 200)

            # 6. Sorteos, Bingo, Lotería & Flyers
            print("\n--- 6. SORTEOS, BINGO, LOTERÍA & FLYERS ---")
            res = client.get('/api/sorteos')
            check("GET /api/sorteos", res.status_code == 200)

            res = client.post('/api/sorteos', data=json.dumps({
                'title': 'Rifa Auditoría Pro 2026',
                'description': 'Sorteo con cartones de bingo',
                'mode': 'bingo',
                'ticket_price': 2000,
                'prizes': [{'rank': 1, 'title': 'Combo Canasta Familiar'}]
            }), content_type='application/json')
            check("POST /api/sorteos", res.status_code == 201)
            raffle_id = res.get_json()['raffle']['id']

            res = client.post(f'/api/raffles/{raffle_id}/draw')
            check("POST /api/raffles/<id>/draw", res.status_code == 200 and res.get_json()['status'] == 'success')

            res = client.get(f'/api/generar-flyer?id={raffle_id}')
            check("GET /api/generar-flyer", res.status_code == 200 and res.mimetype == 'image/png')

            res = client.get(f'/api/generar-cartones-bingo?id={raffle_id}')
            check("GET /api/generar-cartones-bingo", res.status_code == 200)

            # 7. Compras & Hogar, Calculador Multievento y PDF
            print("\n--- 7. COMPRAS & HOGAR + CALCULADOR DE COMIDAS ---")
            res = client.get('/api/shopping')
            check("GET /api/shopping", res.status_code == 200)

            res = client.post('/api/shopping', data=json.dumps({
                'category': 'Supermercado',
                'name': 'Aceite de Oliva 1L',
                'quantity': '2'
            }), content_type='application/json')
            check("POST /api/shopping", res.status_code == 201)
            shop_id = res.get_json()['item']['id']

            res = client.post(f'/api/shopping/{shop_id}/toggle')
            check("POST /api/shopping/<id>/toggle", res.status_code == 200)

            res = client.delete(f'/api/shopping/{shop_id}')
            check("DELETE /api/shopping/<id>", res.status_code == 200)

            res = client.get('/api/noticeboard')
            check("GET /api/noticeboard", res.status_code == 200)

            res = client.post('/api/noticeboard', data=json.dumps({
                'title': 'Aviso Auditoría',
                'content': 'Recordatorio de pago de servicios',
                'color': 'yellow'
            }), content_type='application/json')
            check("POST /api/noticeboard", res.status_code == 201)
            notice_id = res.get_json()['item']['id']

            res = client.delete(f'/api/noticeboard/{notice_id}')
            check("DELETE /api/noticeboard/<id>", res.status_code == 200)

            res = client.get('/api/home-calendar')
            check("GET /api/home-calendar", res.status_code == 200)

            res = client.post('/api/home-calendar', data=json.dumps({
                'event_date': '2026-09-15',
                'title': 'Cierre de Tarjeta Santander',
                'category': 'tarjetas'
            }), content_type='application/json')
            check("POST /api/home-calendar", res.status_code == 201)
            cal_id = res.get_json()['item']['id']

            res = client.delete(f'/api/home-calendar/{cal_id}')
            check("DELETE /api/home-calendar/<id>", res.status_code == 200)

            res = client.post('/api/hogar/parse-audio', data=json.dumps({
                'audio_text': 'Comprar 3 kilos de asado y pagar el gas'
            }), content_type='application/json')
            check("POST /api/hogar/parse-audio", res.status_code == 200)

            res = client.post('/api/comidas/calculate', data=json.dumps({
                'menu_type': 'asado',
                'people': 10,
                'bought_items': [
                    {'name': 'Tira de Asado', 'price': 25000, 'category': 'alimentos'},
                    {'name': 'Vino y Gaseosas', 'price': 10000, 'category': 'bebidas'},
                    {'name': 'Helado 1kg', 'price': 5000, 'category': 'postres'},
                    {'name': 'Carbón y Hielo', 'price': 3000, 'category': 'varios'}
                ]
            }), content_type='application/json')
            check("POST /api/comidas/calculate", res.status_code == 200)
            comidas_res = res.get_json()['data']

            res = client.post('/api/comidas/pdf', data=json.dumps(comidas_res), content_type='application/json')
            check("POST /api/comidas/pdf", res.status_code == 200 and res.mimetype in ['application/pdf', 'image/png'])

            # 8. Convertidor Universal (RAM BytesIO)
            print("\n--- 8. CONVERTIDOR UNIVERSAL MULTIMEDIA (RAM) ---")
            res = client.post('/api/convert/doc', data={
                'file': (BytesIO(b"Documento de Auditoria RAM"), "auditoria.txt"),
                'target_format': 'docx'
            }, content_type='multipart/form-data')
            check("POST /api/convert/doc (TXT -> DOCX)", res.status_code == 200)

            res = client.post('/api/convert/spreadsheet', data={
                'file': (BytesIO(b"Item,Costo\nAsado,25000\nBebidas,10000"), "gastos.csv"),
                'target_format': 'xlsx'
            }, content_type='multipart/form-data')
            check("POST /api/convert/spreadsheet (CSV -> XLSX)", res.status_code == 200)

            from PIL import Image
            img_io = BytesIO()
            Image.new('RGB', (100, 100), color='blue').save(img_io, 'PNG')
            img_io.seek(0)
            res = client.post('/api/convert/image', data={
                'file': (img_io, "foto.png"),
                'target_format': 'pdf'
            }, content_type='multipart/form-data')
            check("POST /api/convert/image (PNG -> PDF)", res.status_code == 200)

            res = client.post('/api/convert/audio', data={
                'file': (BytesIO(b"WAVE_DUMMY_AUDIO"), "nota_voz.wav"),
                'target_format': 'txt'
            }, content_type='multipart/form-data')
            check("POST /api/convert/audio (WAV -> TXT)", res.status_code == 200)

            res = client.post('/api/convert/archive', data={
                'file': (BytesIO(b"PK\x03\x04...DUMMY_ZIP"), "paquete.zip"),
                'target_format': 'txt'
            }, content_type='multipart/form-data')
            check("POST /api/convert/archive (ZIP -> TXT)", res.status_code == 200)

            # 9. Quotes, Biometric Pagaré, Reports & Utilities
            print("\n--- 9. PRESUPUESTOS, FIRMA BIOMÉTRICA & UTILIDADES ---")
            res = client.get('/api/quote/pdf?client_name=Cliente%20Auditoria&amount=50000&installments=4&interest_rate=15')
            check("GET /api/quote/pdf", res.status_code == 200 and res.mimetype == 'application/pdf')

            res = client.post('/api/biometric_requests', data=json.dumps({
                'client_name': 'Cliente Biométrico Test',
                'amount': 80000,
                'installments_count': 6
            }), content_type='application/json')
            check("POST /api/biometric_requests", res.status_code == 201)
            bio_token = res.get_json()['request']['token']

            res = client.get(f'/firmar/{bio_token}')
            check("GET /firmar/<token>", res.status_code == 200 and b'Firma' in res.data)

            res = client.post(f'/api/biometric_requests/{bio_token}/sign', data=json.dumps({
                'signature_data': sample_img,
                'face_photo_data': sample_img
            }), content_type='application/json')
            check("POST /api/biometric_requests/<token>/sign", res.status_code == 200)

            res = client.get('/api/cajas/detail/1')
            check("GET /api/cajas/detail/1", res.status_code == 200)

            res = client.get('/api/cajas/pdf/1')
            check("GET /api/cajas/pdf/1", res.status_code == 200)

            res = client.get('/api/cashflow/detail')
            check("GET /api/cashflow/detail", res.status_code == 200)

            res = client.get('/api/history/general')
            check("GET /api/history/general", res.status_code == 200)

            res = client.get('/api/reports/csv')
            check("GET /api/reports/csv", res.status_code == 200)

            res = client.get('/api/calendar/ics')
            check("GET /api/calendar/ics", res.status_code == 200)

            res = client.get('/api/backup/download')
            check("GET /api/backup/download", res.status_code == 200)

            print("\n==================================================================")
            print(f"   AUDITORÍA FINALIZADA: {passed_tests} DE {total_tests} PRUEBAS EXITOSAS!")
            print("==================================================================")

if __name__ == '__main__':
    run_audit()
