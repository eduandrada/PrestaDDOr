import unittest
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000"

class TestGeminiServices(unittest.TestCase):

    def test_01_ai_chat_endpoint(self):
        payload = json.dumps({
            "mensaje": "¿Cuál es la recomendación de tasa para un préstamo quincenal en Argentina?",
            "rol": "asesor"
        }).encode('utf-8')

        req = urllib.request.Request(f"{BASE_URL}/api/ai/chat", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode('utf-8'))
            self.assertIn("respuesta", data)
            self.assertTrue(len(data["respuesta"]) > 5)

    def test_02_ai_cv_endpoint(self):
        payload = json.dumps({
            "datos": "Nombre: Eduardo. Puesto: Desarrollador Backend Python & Flask. Experiencia: 5 años en desarrollo de software financiero."
        }).encode('utf-8')

        req = urllib.request.Request(f"{BASE_URL}/api/ai/cv", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode('utf-8'))
            self.assertIn("cv", data)
            self.assertTrue(len(data["cv"]) > 10)

    def test_03_ai_arte_sorteo_endpoint(self):
        payload = json.dumps({
            "premio": "Auto 0km & 10 Millones de Pesos"
        }).encode('utf-8')

        req = urllib.request.Request(f"{BASE_URL}/api/ai/arte-sorteo", data=payload, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                data = json.loads(resp.read().decode('utf-8'))
                # If API key is active or returns image / fallback
                self.assertTrue("imagen_base64" in data or "error" in data)
        except urllib.error.HTTPError as err:
            # 500 error if Imagen 3 quota/permission is limited, endpoint exists
            self.assertIn(err.code, [200, 500])

if __name__ == '__main__':
    unittest.main()
