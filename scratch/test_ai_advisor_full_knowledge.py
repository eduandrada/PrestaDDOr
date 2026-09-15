import sys
sys.path.insert(0, r'c:\Users\Usuario\app Prestamos')
import unittest
from app import app
from gemini_services import _generar_respuesta_local_asesor, chat_ia_asesor_contador

class TestAiAdvisorFullKnowledge(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_local_advisor_how_to_queries(self):
        # 1. Test BCRA query explanation
        res_bcra = _generar_respuesta_local_asesor("¿Cómo uso la Evaluación BCRA?")
        self.assertIn("Evaluación Crediticia & Central de Deudores BCRA", res_bcra)
        self.assertIn("Consultar BCRA", res_bcra)

        # 2. Test Pagare QR query explanation
        res_qr = _generar_respuesta_local_asesor("¿Cómo funciona el Pagaré Express QR?")
        self.assertIn("Pagaré Express QR & Firma Biométrica", res_qr)

        # 3. Test Cobranzas query explanation
        res_cobro = _generar_respuesta_local_asesor("¿Cómo registro un cobro de cuota y mando recibo por WhatsApp?")
        self.assertIn("Gestión de Cobranzas", res_cobro)

        # 4. Test Arqueo de caja query explanation
        res_caja = _generar_respuesta_local_asesor("¿Qué es el capital en calle y cómo controlo los gastos hormiga?")
        self.assertIn("Arqueo de Caja", res_caja)

    def test_api_ai_financial_advisor_chat_endpoint(self):
        # Test endpoint /api/ai_financial_advisor/chat with feature question
        res = self.app.post('/api/ai_financial_advisor/chat', json={
            "query": "¿Cómo funciona la Evaluación Crediticia BCRA y el envío de notificaciones WhatsApp?"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("BCRA", data.get("reply"))

if __name__ == '__main__':
    unittest.main()
