import os
import sys
import unittest
from datetime import datetime, timedelta

# Append project root to path
sys.path.insert(0, os.path.abspath('.'))

from app import app, db
from models import Client, Loan, Setting, ClientDocument, BiometricRequest

class TestBiometricVaultAudit(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_qr_points_to_biometric_sign_url(self):
        """Auditar si el QR envía a la Firma Digital Biométrica 2026 (/firmar/<token>)"""
        # Create a test client
        test_cli = Client.query.filter_by(name="Auditoría QR Test").first()
        if not test_cli:
            test_cli = Client(name="Auditoría QR Test", whatsapp="3834112233", cuit="20334455669", address="Av. San Martín 100")
            db.session.add(test_cli)
            db.session.commit()

        res = self.client.post('/api/biometric/request/create', json={
            'client_id': test_cli.id,
            'amount': 75000,
            'installments_count': 6,
            'interest_rate': 20
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        
        self.assertTrue(data['success'])
        self.assertIn('/firmar/', data['sign_url'])
        self.assertIn('api.qrserver.com', data['qr_img_url'])
        self.assertIn(data['token'], data['qr_img_url'])

    def test_02_expiry_setting_configuration(self):
        """Auditar configuración de tiempo de emisión de QR en Ajustes"""
        # Set expiry to 45 minutes
        Setting.set_val('qr_biometric_expiry_minutes', '45')
        get_res = self.client.get('/api/settings')
        self.assertEqual(get_res.get_json().get('qr_biometric_expiry_minutes'), '45')

        # Create request and verify remaining seconds
        test_cli = Client.query.first()
        res = self.client.post('/api/biometric/request/create', json={'client_id': test_cli.id, 'amount': 50000})
        token = res.get_json()['token']
        
        bio_req = BiometricRequest.query.filter_by(token=token).first()
        self.assertIsNotNone(bio_req)
        # Should have approximately 45 * 60 = 2700 seconds remaining
        self.assertGreaterEqual(bio_req.remaining_seconds, 2690)
        self.assertLessEqual(bio_req.remaining_seconds, 2700)

        # Restore default 30 mins
        Setting.set_val('qr_biometric_expiry_minutes', '30')

    def test_03_biometric_sign_page_elements_and_facial_scan(self):
        """Auditar vista /firmar/<token> para escaneo facial / selfie y campos requeridos"""
        test_cli = Client.query.first()
        res = self.client.post('/api/biometric/request/create', json={'client_id': test_cli.id, 'amount': 60000})
        token = res.get_json()['token']

        page_res = self.client.get(f'/firmar/{token}')
        self.assertEqual(page_res.status_code, 200)
        html = page_res.get_data(as_text=True)

        # Facial scan & selfie check
        self.assertIn('Selfie / Escaneo Facial Biométrico', html)
        self.assertIn('Cámara en Vivo', html)
        self.assertIn('signatureCanvas', html)

        # DNI Frente y Dorso check
        self.assertIn('dniFrenteInput', html)
        self.assertIn('dniDorsoInput', html)

        # Recibos de Sueldo check
        self.assertIn('reciboSueldo1Input', html)
        self.assertIn('reciboSueldo2Input', html)

        # Factura de servicio (IA) check
        self.assertIn('comprobanteServicioInput', html)
        self.assertIn('Detección IA', html)

        # Garante Solidario check (desmarcado por defecto)
        self.assertIn('tieneGaranteCheck', html)
        self.assertIn('garanteSection', html)
        self.assertIn('hidden p-3 rounded-2xl bg-indigo-950/30', html) # Confirms unchecked/hidden by default

    def test_04_sign_request_saves_all_docs_to_boveda(self):
        """Auditar guardado automático en Bóveda de Documentos & Resguardos"""
        test_cli = Client.query.filter_by(name="Auditoría Vault Test").first()
        if not test_cli:
            test_cli = Client(name="Auditoría Vault Test", whatsapp="3834998877", cuit="20998877665", address="Calle Falsa 123")
            db.session.add(test_cli)
            db.session.commit()

        res = self.client.post('/api/biometric/request/create', json={'client_id': test_cli.id, 'amount': 100000})
        token = res.get_json()['token']

        # Payload simulating signature, selfie, DNI, recibos, servicio IA & Garante
        payload = {
            'signature_data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'selfie_data': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...',
            'dni_frente_data': 'data:image/png;base64,DNI_FRENTE_TEST',
            'dni_dorso_data': 'data:image/png;base64,DNI_DORSO_TEST',
            'recibo_sueldo_1_data': 'data:application/pdf;base64,RECIBO1_TEST',
            'recibo_sueldo_2_data': 'data:application/pdf;base64,RECIBO2_TEST',
            'comprobante_servicio_data': 'data:image/jpeg;base64,SERVICIO_IA_TEST',
            'has_garante': True,
            'garante_name': 'Carlos Garante Test',
            'garante_dni': '20123456789',
            'garante_phone': '3834000111',
            'garante_address': 'Belgrano 300',
            'garante_dni_frente_data': 'data:image/png;base64,GARANTE_DNI_FRENTE',
            'garante_dni_dorso_data': 'data:image/png;base64,GARANTE_DNI_DORSO',
            'garante_recibo_1_data': 'data:application/pdf;base64,GARANTE_RECIBO_1',
            'garante_recibo_2_data': 'data:application/pdf;base64,GARANTE_RECIBO_2'
        }

        sign_res = self.client.post(f'/api/biometric_requests/{token}/sign', json=payload)
        self.assertEqual(sign_res.status_code, 200)
        self.assertTrue(sign_res.get_json()['success'])

        # Verify docs created in ClientDocument (Bóveda)
        docs = ClientDocument.query.filter_by(client_id=test_cli.id).all()
        doc_types = [d.doc_type for d in docs]
        
        self.assertIn('firma_digital', doc_types)
        self.assertIn('selfie_deudor', doc_types)
        self.assertIn('dni_frente', doc_types)
        self.assertIn('dni_dorso', doc_types)
        self.assertIn('recibo_sueldo', doc_types)
        self.assertIn('servicio_impuesto', doc_types)
        self.assertIn('garante_doc', doc_types)

        # Verify Client model updated with Garante info
        db.session.refresh(test_cli)
        self.assertTrue(test_cli.has_guarantor)
        self.assertEqual(test_cli.guarantor_name, 'Carlos Garante Test')
        self.assertEqual(test_cli.guarantor_cuit, '20123456789')

if __name__ == '__main__':
    unittest.main()
