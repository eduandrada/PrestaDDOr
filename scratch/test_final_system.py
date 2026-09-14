import unittest
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000"

class TestFinalSystem(unittest.TestCase):

    def test_01_formulario_cv_page(self):
        req = urllib.request.Request(f"{BASE_URL}/formulario-cv")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            html = resp.read().decode('utf-8')
            self.assertIn("Generador de CV Premium", html)
            self.assertIn("Minimalista", html)

    def test_02_generar_cv_post(self):
        templates = ['minimalista', 'ejecutivo', 'creativa', 'tecnologica']
        for tmpl in templates:
            data = urllib.parse.urlencode({
                'nombre': 'Juan Carlos Perez',
                'puesto': 'Desarrollador Senior',
                'email': 'juan.perez@example.com',
                'telefono': '+54 383 4123456',
                'linkedin': 'linkedin.com/in/juanperez',
                'sobre_mi': 'Profesional con más de 10 años de experiencia.',
                'experiencia': 'Empresa A (2020-2026): Desarrollador Lead\nEmpresa B (2015-2020): Analista',
                'educacion': 'Universidad Nacional de Catamarca - Lic. en Sistemas (2010-2015)',
                'habilidades': 'Python, JavaScript, SQL, HTML/CSS',
                'plantilla': tmpl
            }).encode('utf-8')

            req = urllib.request.Request(f"{BASE_URL}/generar-cv", data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                cv_html = resp.read().decode('utf-8')
                self.assertIn("Juan Carlos Perez", cv_html)
                self.assertIn("Desarrollador Senior", cv_html)

    def test_03_documents_api(self):
        req = urllib.request.Request(f"{BASE_URL}/api/documents/all")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode('utf-8'))
            self.assertIn('documents', data)
            self.assertIsInstance(data['documents'], list)

    def test_04_client_custom_score(self):
        # Fetch clients
        req = urllib.request.Request(f"{BASE_URL}/api/clients")
        with urllib.request.urlopen(req) as resp:
            clients = json.loads(resp.read().decode('utf-8'))
            if clients:
                client = clients[0]
                cid = client['id']
                # Update custom score
                payload = json.dumps({'custom_score': 85}).encode('utf-8')
                put_req = urllib.request.Request(f"{BASE_URL}/api/clients/{cid}", data=payload, headers={'Content-Type': 'application/json'}, method='PUT')
                with urllib.request.urlopen(put_req) as put_resp:
                    updated = json.loads(put_resp.read().decode('utf-8'))
                    self.assertEqual(updated['metrics']['score_points'], 85)
                    self.assertEqual(updated['custom_score'], 85)

if __name__ == '__main__':
    unittest.main()
