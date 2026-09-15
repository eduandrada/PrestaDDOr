import sys
sys.path.insert(0, r'c:\Users\Usuario\app Prestamos')
import unittest
import time
from app import app, db

class TestBcraPdfAndWhatsapp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_bcra_pdf_report_route_html(self):
        # Test CUIT Banco Nación 30500010912
        res = self.app.get('/api/bcra/report_pdf/30500010912')
        self.assertEqual(res.status_code, 200)
        html_text = res.get_data(as_text=True)
        self.assertIn('INFORME OFICIAL', html_text.upper())
        self.assertIn('BANCO DE LA NACION ARGENTINA', html_text)
        self.assertIn('Central de Deudores BCRA', html_text)
        self.assertIn('Enviar Resolución por WhatsApp', html_text)

    def test_bcra_pdf_report_route_download(self):
        # Test CUIT Banco Nación 30500010912 with ?download=1
        res = self.app.get('/api/bcra/report_pdf/30500010912?download=1')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'application/pdf')
        pdf_bytes = res.get_data()
        self.assertTrue(pdf_bytes.startswith(b'%PDF-'))

if __name__ == '__main__':
    unittest.main()
