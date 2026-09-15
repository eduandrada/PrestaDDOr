import sys
sys.path.insert(0, r'c:\Users\Usuario\app Prestamos')
import unittest
import json
import time
from app import app, db
from models import Client, ClientRegistrationRequest, Setting

class TestClientExpressQrAudit(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_client_express_qr_lifecycle(self):
        # 1. Create client registration QR request
        res = self.app.post('/api/client_registration_requests')
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('token', data)
        token = data['token']

        # 2. Render registration page GET
        res_get = self.app.get(f'/registrar_cliente/{token}')
        self.assertEqual(res_get.status_code, 200)
        self.assertIn('Registro Express de Cliente', res_get.get_data(as_text=True))

        # 3. Submit registration POST
        suffix = str(int(time.time()))
        payload = {
            'name': f'Cliente Express {suffix}',
            'whatsapp': f'54911{suffix[-6:]}',
            'cuit': f'20{suffix[-7:]}88',
            'address': 'Calle Falsa 742',
            'email': f'express_{suffix}@test.com',
            'bank_alias': 'ALIAS.EXPRESS.MP',
            'notes': 'Cliente registrado desde QR remoto'
        }
        res_post = self.app.post(f'/registrar_cliente/{token}', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res_post.status_code, 200)
        data_post = res_post.get_json()
        self.assertTrue(data_post['success'])

        # 4. Render registration page again -> blocked/expired
        res_get_expired = self.app.get(f'/registrar_cliente/{token}')
        self.assertEqual(res_get_expired.status_code, 200)
        self.assertIn('Registro Completado', res_get_expired.get_data(as_text=True))

        # 5. Fetch client registration requests list
        res_list = self.app.get('/api/client_registration_requests')
        self.assertEqual(res_list.status_code, 200)
        reqs = res_list.get_json()
        target_req = next((r for r in reqs if r['token'] == token), None)
        self.assertIsNotNone(target_req)
        self.assertEqual(target_req['status'], 'registrado')
        self.assertEqual(target_req['bank_alias'], 'ALIAS.EXPRESS.MP')

        # 6. Approve request
        res_appr = self.app.post(f'/api/client_registration_requests/{token}/approve')
        self.assertEqual(res_appr.status_code, 200)
        data_appr = res_appr.get_json()
        self.assertTrue(data_appr['success'])
        created_client = data_appr['client']
        self.assertTrue('Cliente' in created_client['name'])
        self.assertIn('ALIAS', created_client['bank_alias'])

if __name__ == '__main__':
    unittest.main()
