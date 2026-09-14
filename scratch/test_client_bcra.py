import unittest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import Client

class ClientBcraTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_create_client_validation(self):
        # Missing WhatsApp and Address
        res = self.app.post('/api/clients', json={'name': 'Test Incomplete'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('whatsapp', res.get_json()['error'].lower())

        # Successful creation
        import time
        t = str(int(time.time()))
        unique_cuit = f"20{t[:9]}"
        payload = {
            'name': f'Carlos Perez Test {t}',
            'whatsapp': f'54938344{t[-5:]}',
            'address': 'Calle Falsa 123',
            'cuit': unique_cuit,
            'email': 'carlos@test.com',
            'notes': 'Cliente de prueba auditoria'
        }
        res_ok = self.app.post('/api/clients', json=payload)
        self.assertEqual(res_ok.status_code, 201, msg=res_ok.get_json())
        data = res_ok.get_json()
        self.assertEqual(data['name'], f'Carlos Perez Test {t}')
        self.assertEqual(data['cuit'], unique_cuit)

        # Duplicate creation test
        res_dup = self.app.post('/api/clients', json=payload)
        self.assertEqual(res_dup.status_code, 400)
        self.assertIn('ya existe', res_dup.get_json()['error'].lower())

    def test_02_bcra_endpoint(self):
        res = self.app.get('/api/bcra/check/20334455669')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('underwriting', data)
        self.assertIn('status', data['underwriting'])
        self.assertIn('cuit', data)

    def test_03_create_loan_validation(self):
        first_client = Client.query.first()
        client_id = first_client.id if first_client else 1

        # Invalid client_id
        res_no_client = self.app.post('/api/loans', json={'client_id': 999999, 'amount': 50000})
        self.assertEqual(res_no_client.status_code, 400)
        self.assertIn('el cliente seleccionado no existe', res_no_client.get_json()['error'].lower())

        # Invalid amount
        res_no_amount = self.app.post('/api/loans', json={'client_id': client_id, 'amount': 0})
        self.assertEqual(res_no_amount.status_code, 400)
        self.assertIn('monto', res_no_amount.get_json()['error'].lower())

        # Successful loan creation for existing client
        res_ok = self.app.post('/api/loans', json={
            'client_id': client_id,
            'amount': 75000,
            'interest_rate': 15,
            'rate_type': 'mensual',
            'modality': 'mensual',
            'installments_count': 3,
            'grace_days': 3,
            'late_fee_type': 'porcentaje',
            'late_fee_value': 1.0
        })
        self.assertEqual(res_ok.status_code, 201, msg=res_ok.get_json())
        data = res_ok.get_json()
        self.assertEqual(data['amount'], 75000)

if __name__ == '__main__':
    unittest.main()
