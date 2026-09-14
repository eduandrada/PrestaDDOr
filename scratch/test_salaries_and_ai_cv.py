import unittest
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000"

class TestSalariesAndAiCv(unittest.TestCase):

    def test_01_dynamic_family_salaries(self):
        extra_salaries = [
            {"id": 1, "name": "💼 Freelance IT", "amount": 180000},
            {"id": 2, "name": "🏠 Renta Local", "amount": 120000}
        ]
        payload = json.dumps({
            "salary_name_1": "👨‍💻 Eduardo",
            "user_salary_eduardo": "600000",
            "salary_name_2": "👩‍💼 Maira",
            "user_salary_maira": "500000",
            "extra_salaries_json": json.dumps(extra_salaries)
        }).encode('utf-8')

        req = urllib.request.Request(f"{BASE_URL}/api/settings", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)

        get_req = urllib.request.Request(f"{BASE_URL}/api/settings")
        with urllib.request.urlopen(get_req) as get_resp:
            settings = json.loads(get_resp.read().decode('utf-8'))
            self.assertIn("extra_salaries_json", settings)
            parsed = json.loads(settings["extra_salaries_json"])
            self.assertEqual(len(parsed), 2)
            self.assertEqual(parsed[0]["name"], "💼 Freelance IT")

    def test_02_ai_cv_enhance_endpoint(self):
        payload = json.dumps({
            "action": "profile",
            "puesto": "Analista Senior",
            "text": "Experiencia en finanzas y desarrollo web."
        }).encode('utf-8')

        req = urllib.request.Request(f"{BASE_URL}/api/cv/ai_enhance", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode('utf-8'))
            self.assertTrue(data.get('success'))
            self.assertIn("Perfil Profesional en Analista Senior", data.get('result', ''))

    def test_03_generar_cv_2026_pro_all_templates(self):
        fake_base64_photo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        templates = ['minimalista', 'ejecutivo', 'creativa', 'tecnologica', 'adobe_express', 'microsoft_word']
        for tmpl in templates:
            payload = json.dumps({
                "nombre": "Eduardo Andrada 2026",
                "puesto": "Senior Solutions Architect",
                "email": "eduardo@example.com",
                "telefono": "+54 9 383 4112233",
                "ubicacion": "Catamarca, Argentina",
                "foto_url": fake_base64_photo,
                "linkedin": "linkedin.com/in/eduardoandrada",
                "github": "github.com/eduandrada",
                "web": "eduardoandrada.dev",
                "sobre_mi": "Resumen profesional impulsado por Inteligencia Artificial.",
                "experiencia": "• Lead Architect (2020 - 2026): Liderazgo de proyectos corporativos.",
                "educacion": "• Licenciatura en Sistemas (2015 - 2020)",
                "certificaciones": "• AWS Certified Solutions Architect 2026",
                "habilidades": "Python, Flask, SQL, Arquitectura Cloud, Liderazgo",
                "idiomas": "Español (Nativo), Inglés (Avanzado C1)",
                "proyectos": "• Sistema de Gestión P2P & Finanzas",
                "referencias": "• Referencias disponibles a solicitud.",
                "plantilla": tmpl,
                "accent_color": "#0284c7"
            }).encode('utf-8')

            req = urllib.request.Request(f"{BASE_URL}/generar-cv", data=payload, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                html = resp.read().decode('utf-8')
                self.assertIn("Eduardo Andrada 2026", html)
                self.assertIn("AWS Certified Solutions Architect 2026", html)
                self.assertIn(fake_base64_photo, html)

    def test_04_raffle_flyer_new_themes(self):
        new_styles = ['edit_org_gold', 'adobe_express_raffle', 'postermywall_fiesta', 'pinterest_retro']
        for st in new_styles:
            req = urllib.request.Request(f"{BASE_URL}/api/generar-flyer?title=Gran+Sorteo+Pro&motive=Prueba+IA&style={st}")
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                self.assertEqual(resp.headers.get('Content-Type'), 'image/png')

if __name__ == '__main__':
    unittest.main()
