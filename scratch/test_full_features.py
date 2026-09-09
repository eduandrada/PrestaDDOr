import sys
import os
import json
from io import BytesIO

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import app, db

def test_features():
    print("=== STARTING FULL FEATURE INTEGRATION TESTS ===")
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # 1. Test Sorteo creation (Bingo & Lotería modes)
            print("\n1. Testing Sorteo Creation (Bingo & Lotería)...")
            res = client.post('/api/sorteos', data=json.dumps({
                'title': 'Sorteo Bingo Aniversario IA',
                'description': 'Bingo familiar 75 bolillas con cartones PDF',
                'mode': 'bingo',
                'ticket_price': 1500,
                'range_min': 1,
                'range_max': 75,
                'prizes': [
                    {'rank': 1, 'title': 'Lechón + Caja de Vino'},
                    {'rank': 2, 'title': 'Torta Helada'}
                ]
            }), content_type='application/json')
            assert res.status_code == 201, f"Failed creation: {res.data}"
            sorteo_data = res.get_json()
            raffle_id = sorteo_data['raffle']['id']
            print(f"   [PASS] Created Bingo Raffle ID: {raffle_id}")

            # 2. Test Flyer Generator with AI Art background
            print("\n2. Testing /api/generar-flyer with AI art...")
            res_flyer = client.get(f'/api/generar-flyer?id={raffle_id}&use_ai=1')
            assert res_flyer.status_code == 200, f"Failed flyer: {res_flyer.status_code}"
            assert res_flyer.mimetype == 'image/png', f"Wrong mimetype: {res_flyer.mimetype}"
            print(f"   [PASS] Flyer PNG generated ({len(res_flyer.data)} bytes)")

            # 3. Test Bingo Cards PDF Generator
            print("\n3. Testing /api/generar-cartones-bingo PDF...")
            res_bingo = client.get(f'/api/generar-cartones-bingo?id={raffle_id}&type=75')
            assert res_bingo.status_code == 200, f"Failed bingo PDF: {res_bingo.status_code}"
            assert res_bingo.mimetype in ['application/pdf', 'image/png'], f"Wrong mimetype: {res_bingo.mimetype}"
            print(f"   [PASS] Bingo 75 PDF generated ({len(res_bingo.data)} bytes)")

            # 4. Test Multi-Menu Food Calculator
            print("\n4. Testing /api/comidas/calculate (Pizza menu with itemized ingredients)...")
            res_comidas = client.post('/api/comidas/calculate', data=json.dumps({
                'menu_type': 'pizza',
                'people': 12,
                'bought_items': [
                    {'name': 'Muzzarella 3kg', 'price': 15000, 'category': 'alimentos'},
                    {'name': 'Cerveza + Gaseosas', 'price': 6000, 'category': 'bebidas'},
                    {'name': 'Helado 1kg', 'price': 4000, 'category': 'postres'},
                    {'name': 'Hielo 2 bolsas', 'price': 2000, 'category': 'varios'}
                ]
            }), content_type='application/json')
            assert res_comidas.status_code == 200, f"Failed comidas calculation: {res_comidas.data}"
            comidas_json = res_comidas.get_json()
            assert comidas_json['success'] is True
            res_dict = comidas_json.get('data') or comidas_json.get('calculation') or {}
            assert res_dict['people'] == 12
            assert res_dict['total_cost'] > 0
            assert res_dict['per_person_cost'] > 0
            print(f"   [PASS] Pizza Calculation: Total=${res_dict['total_cost']}, PerPerson=${res_dict['per_person_cost']}")
            print(f"   IA Message Preview: {res_dict['wa_share_string'][:80].encode('ascii', 'ignore').decode()}...")

            # 5. Test Food Receipt PDF Generator (with uploaded ticket photo)
            print("\n5. Testing /api/comidas/pdf report generation with ticket photos...")
            sample_b64_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            res_pdf = client.post('/api/comidas/pdf', data=json.dumps({
                'menu_name': res_dict['menu_name'],
                'people': res_dict['people'],
                'total_cost': res_dict['total_cost'],
                'per_person_cost': res_dict['per_person_cost'],
                'bought_items': res_dict['bought_items'],
                'ticket_images': [sample_b64_img]
            }), content_type='application/json')
            assert res_pdf.status_code == 200, f"Failed food PDF: {res_pdf.status_code}"
            assert res_pdf.mimetype in ['application/pdf', 'image/png'], f"Wrong mimetype: {res_pdf.mimetype}"
            print(f"   [PASS] Comidas PDF Report with Ticket Photos generated ({len(res_pdf.data)} bytes)")

            # 6. Test Universal Converter Endpoints (RAM BytesIO processing)
            print("\n6. Testing Universal Converter endpoints...")
            
            # Document Conversion: TXT -> DOCX
            res_doc = client.post('/api/convert/doc', data={
                'file': (BytesIO(b"Documento de Prueba 2026\nConvertidor Universal en RAM"), "test.txt"),
                'target_format': 'docx'
            }, content_type='multipart/form-data')
            assert res_doc.status_code == 200, f"Failed doc conversion: {res_doc.status_code}"
            print(f"   [PASS] Doc Conversion (TXT -> DOCX): {len(res_doc.data)} bytes")

            # Spreadsheet Conversion: CSV -> XLSX
            res_sheet = client.post('/api/convert/spreadsheet', data={
                'file': (BytesIO(b"Nombre,Monto,Estado\nEduardo,50000,Activo\nMaira,45000,Activo"), "datos.csv"),
                'target_format': 'xlsx'
            }, content_type='multipart/form-data')
            assert res_sheet.status_code == 200, f"Failed spreadsheet conversion: {res_sheet.status_code}"
            print(f"   [PASS] Spreadsheet Conversion (CSV -> XLSX): {len(res_sheet.data)} bytes")

            # Image Conversion: Image -> PDF
            from PIL import Image
            test_img_io = BytesIO()
            Image.new('RGB', (200, 200), color='red').save(test_img_io, 'PNG')
            test_img_io.seek(0)

            res_img = client.post('/api/convert/image', data={
                'file': (test_img_io, "foto.png"),
                'target_format': 'pdf'
            }, content_type='multipart/form-data')
            assert res_img.status_code == 200, f"Failed image conversion: {res_img.status_code}"
            print(f"   [PASS] Image Conversion (PNG -> PDF): {len(res_img.data)} bytes")

            # Audio Conversion: Audio -> TXT
            res_audio = client.post('/api/convert/audio', data={
                'file': (BytesIO(b"RIFF....WAVEfmt ...data..."), "dictado.wav"),
                'target_format': 'txt'
            }, content_type='multipart/form-data')
            assert res_audio.status_code == 200, f"Failed audio conversion: {res_audio.status_code}"
            print(f"   [PASS] Audio Conversion (WAV -> TXT): {len(res_audio.data)} bytes")

            print("\n=============================================")
            print(">>> ALL 6 INTEGRATION TESTS PASSED SUCCESSFULLY! <<<")
            print("=============================================")

if __name__ == '__main__':
    test_features()

