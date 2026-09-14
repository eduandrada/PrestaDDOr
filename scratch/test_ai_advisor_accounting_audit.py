import sys
sys.path.insert(0, r'c:\Users\Usuario\app Prestamos')
import unittest
import json
import time
from app import app, db
from models import Client, Loan, Installment, HomeCalendarItem, Setting

class TestAiAdvisorAccountingAudit(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_ai_advisor_complete_flow(self):
        # 1. Create test client & loan with created_by
        suffix = str(int(time.time()))
        res = self.app.post('/api/clients', data=json.dumps({
            'name': f'Cliente Auditoria {suffix}',
            'whatsapp': f'54911{suffix[-6:]}',
            'cuit': f'20{suffix[-7:]}99',
            'address': 'Av. San Martín 100',
            'bank_alias': 'ALIAS.AUDITORIA.MP'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        client_id = res.get_json()['id'] if 'id' in res.get_json() else res.get_json()['client']['id']

        res_loan = self.app.post('/api/loans', data=json.dumps({
            'client_id': client_id,
            'amount': 200000,
            'installments_count': 4,
            'interest_rate': 15,
            'status': 'activo',
            'created_by': 'Asesor Carlos'
        }), content_type='application/json')
        self.assertEqual(res_loan.status_code, 201)
        loan_id = res_loan.get_json()['id']

        # 2. Add calendar item inside app context
        with app.app_context():
            item = HomeCalendarItem(
                title=f'Pago de Servicio Luz {suffix}',
                category='servicio',
                due_date='2026-09-20',
                due_time='10:00'
            )
            db.session.add(item)
            db.session.commit()

        # 3. Test GET /api/ai_financial_advisor
        res_get = self.app.get('/api/ai_financial_advisor')
        self.assertEqual(res_get.status_code, 200)
        data = res_get.get_json()
        self.assertIn('capital_en_calle', data)
        self.assertIn('calendar_summary', data)
        self.assertIn('clients_summary', data)

        # 4. Test POST /api/ai_financial_advisor/chat for client
        res_chat_c = self.app.post('/api/ai_financial_advisor/chat', data=json.dumps({
            'client_id': client_id
        }), content_type='application/json')
        self.assertEqual(res_chat_c.status_code, 200)
        data_chat_c = res_chat_c.get_json()
        self.assertTrue(data_chat_c['success'])
        self.assertIn('Asesor Carlos', data_chat_c['reply'])
        self.assertIn('ALIAS.AUDITORIA.MP', data_chat_c['reply'])

        # 5. Test POST /api/ai_financial_advisor/chat for calendar
        res_chat_cal = self.app.post('/api/ai_financial_advisor/chat', data=json.dumps({
            'query': '¿Qué vencimientos hay en el calendario?'
        }), content_type='application/json')
        self.assertEqual(res_chat_cal.status_code, 200)
        data_chat_cal = res_chat_cal.get_json()
        self.assertTrue(data_chat_cal['success'])
        self.assertIn('Pago de Servicio Luz', data_chat_cal['reply'])

        # 6. Test POST /api/ai_financial_advisor/export_pdf
        res_pdf = self.app.post('/api/ai_financial_advisor/export_pdf', data=json.dumps({
            'title': 'Informe Auditoría Contable Test',
            'text_body': 'Reporte detallado de prueba del Contador IA.'
        }), content_type='application/json')
        self.assertEqual(res_pdf.status_code, 200)
        self.assertTrue(res_pdf.get_data().startswith(b'%PDF-'))

if __name__ == '__main__':
    unittest.main()
