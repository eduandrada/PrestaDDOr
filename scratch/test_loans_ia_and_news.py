import os
import sys
import json
import unittest

# Ensure app can be imported
sys.path.insert(0, os.path.abspath('.'))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from app import app, db
from models import Client, Loan, Installment, Setting

def run_tests():
    with app.app_context():
        client = app.test_client()
        
        print("=== TEST 1: GET /api/news ===")
        res = client.get('/api/news')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        news_data = res.get_json()
        assert isinstance(news_data, list), "Expected list in /api/news response"
        print(f"-> OK: Found {len(news_data)} news items.")
        if news_data:
            print(f"   Sample headline: {news_data[0]['title']} ({news_data[0]['source']})")
        
        print("\n=== TEST 2: GET and POST /api/settings ===")
        res = client.get('/api/settings')
        assert res.status_code == 200
        settings = res.get_json()
        assert "marquee_enabled" in settings, "Missing marquee_enabled"
        assert "marquee_speed" in settings, "Missing marquee_speed"
        assert "news_source_esquiu" in settings, "Missing news_source_esquiu"
        print("-> OK: Current settings retrieved correctly.")
        
        update_data = {
            "marquee_enabled": "1",
            "marquee_speed": "rapida",
            "custom_marquee_text": "Aviso de prueba: Cobranzas activas hasta 18hs",
            "news_source_esquiu": "1",
            "news_source_ancasti": "1",
            "news_source_catamarca_actual": "1",
            "news_source_la_union": "1",
            "marquee_show_news": "1"
        }
        res = client.post('/api/settings', json=update_data)
        assert res.status_code == 200
        print("-> OK: Settings updated successfully.")
        
        # Verify custom text appears in news
        res = client.get('/api/news')
        news_data = res.get_json()
        has_custom = any("Cobranzas activas" in item["title"] for item in news_data)
        assert has_custom, "Custom announcement text was not prepended to news list"
        print("-> OK: Custom marquee text dynamically included in news feed.")

        print("\n=== TEST 3: CLIENT WITH GUARANTOR & LOAN WITH AI PDF ===")
        # Check existing or create test client with guarantor
        c = Client.query.filter_by(name="Cliente Test Con Garante").first()
        if not c:
            c = Client(
                name="Cliente Test Con Garante",
                cuit="20-33444555-4",
                whatsapp="3834112233",
                email="cliente.test@example.com",
                address="Calle República 450, San Fernando del Valle de Catamarca",
                has_guarantor=True,
                guarantor_name="Juan Garante Solidario",
                guarantor_cuit="20-28999888-3",
                guarantor_phone="3834998877",
                guarantor_address="Av. Ocampo 1200, Catamarca"
            )
            db.session.add(c)
            db.session.commit()
            print(f"-> Created test client with guarantor (ID: {c.id})")
        else:
            print(f"-> Using existing test client with guarantor (ID: {c.id})")
            
        c_dict = c.to_dict()
        assert c_dict.get("has_guarantor") is True
        assert c_dict.get("guarantor_name") == "Juan Garante Solidario"
        print("-> OK: Client to_dict includes guarantor fields correctly.")

        # Create a loan for this client
        loan_payload = {
            "client_id": c.id,
            "amount": 100000,
            "interest_rate": 20,
            "installments_count": 4,
            "modality": "mensual",
            "start_date": "2026-09-15"
        }
        res = client.post('/api/loans', json=loan_payload)
        assert res.status_code == 201, f"Loan creation failed: {res.data}"
        loan_data = res.get_json()
        loan_id = loan_data["id"]
        print(f"-> OK: Loan created with ID {loan_id}, total to pay: ${loan_data['total_loan_amount']}")

        # Test AI PDF route
        print(f"\n=== TEST 4: GET /api/loans/{loan_id}/resumen_ia_pdf ===")
        res = client.get(f'/api/loans/{loan_id}/resumen_ia_pdf')
        assert res.status_code == 200
        html_content = res.get_data(as_text=True)
        assert "RESUMEN FINANCIERO INTELIGENTE" in html_content
        assert "DETALLE CRONOGRAMA" in html_content
        assert "FIRMA CLIENTE" in html_content
        assert "FIRMA GARANTE" in html_content
        assert "Juan Garante Solidario" in html_content
        print("-> OK: AI PDF generated valid HTML containing loan breakdown, guarantor, schedule, and signature blocks.")

        print("\n==================================================")
        print("TODOS LOS TESTS PASARON EXITOSAMENTE (100% OK)")
        print("==================================================")

if __name__ == '__main__':
    run_tests()
