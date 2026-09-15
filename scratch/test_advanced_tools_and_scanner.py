import unittest
import urllib.request
import urllib.parse
import json
import sys
import io
from PIL import Image

sys.path.insert(0, '.')
import app as flask_app
from image_filters import apply_document_clean_filter, apply_color_enhance_filter, compress_pdf_in_ram

class TestAdvancedToolsAndScanner(unittest.TestCase):

    def setUp(self):
        self.client = flask_app.app.test_client()

    def test_01_image_filters(self):
        img = Image.new('RGB', (200, 200), color='gray')
        
        clean = apply_document_clean_filter(img)
        self.assertIsNotNone(clean)
        self.assertEqual(clean.size, (200, 200))
        
        color_enh = apply_color_enhance_filter(img)
        self.assertIsNotNone(color_enh)
        self.assertEqual(color_enh.size, (200, 200))

    def test_02_pdf_compression_in_ram(self):
        from utils.notification import create_pdf
        import tempfile, os
        
        html_dummy = "<html><body><h1>Prueba Compresion PDF en RAM</h1><p>" + ("Texto extenso de pagaré o contrato. " * 50) + "</p></body></html>"
        fd, path = tempfile.mkstemp(suffix='.pdf'); os.close(fd)
        create_pdf(html_dummy, path)
        with open(path, 'rb') as f:
            pdf_bytes = f.read()
        os.unlink(path)

        comp_bytes, orig_sz, comp_sz = compress_pdf_in_ram(pdf_bytes, target_max_bytes=500000)
        self.assertTrue(len(comp_bytes) > 0)
        self.assertGreater(orig_sz, 0)

        # Test endpoint
        res = self.client.post('/api/pdf/compress', data={
            'file': (io.BytesIO(pdf_bytes), "pagare_contrato.pdf"),
            'target_max_kb': '1000'
        }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)

    def test_03_camscanner_ocr_endpoint(self):
        img_io = io.BytesIO()
        Image.new('RGB', (150, 150), color='white').save(img_io, 'JPEG')
        img_io.seek(0)

        res = self.client.post('/api/camscanner/ocr', data={
            'file': (img_io, "recibo_pagare.jpg"),
            'filter_mode': 'aclarado',
            'target_format': 'docx'
        }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        self.assertIn('wordprocessingml', res.mimetype)

    def test_04_webp_to_jpg_png_conversion(self):
        webp_io = io.BytesIO()
        Image.new('RGB', (100, 100), color='green').save(webp_io, 'WEBP')
        webp_bytes = webp_io.getvalue()

        # Convert WebP to JPG with filter
        res1 = self.client.post('/api/convert/image', data={
            'file': (io.BytesIO(webp_bytes), "foto_whatsapp.webp"),
            'target_format': 'jpg',
            'filter_mode': 'aclarado'
        }, content_type='multipart/form-data')
        self.assertEqual(res1.status_code, 200)
        self.assertIn('image/jpeg', res1.mimetype)

        # Convert WebP to PNG
        res2 = self.client.post('/api/convert/image', data={
            'file': (io.BytesIO(webp_bytes), "foto_whatsapp.webp"),
            'target_format': 'png'
        }, content_type='multipart/form-data')
        self.assertEqual(res2.status_code, 200)
        self.assertIn('image/png', res2.mimetype)

    def test_05_csv_excel_to_json_and_html(self):
        csv_data = b"Cliente,Monto,Estado\nJuan Perez,150000,Activo\nMaria Gomez,80000,Pagado\n"

        # CSV to JSON
        res_json = self.client.post('/api/convert/spreadsheet', data={
            'file': (io.BytesIO(csv_data), "cartera_clientes.csv"),
            'target_format': 'json'
        }, content_type='multipart/form-data')
        self.assertEqual(res_json.status_code, 200)
        json_parsed = json.loads(res_json.data.decode('utf-8'))
        self.assertEqual(len(json_parsed), 2)
        self.assertEqual(json_parsed[0]['Cliente'], 'Juan Perez')

        # CSV to HTML Table
        res_html = self.client.post('/api/convert/spreadsheet', data={
            'file': (io.BytesIO(csv_data), "cartera_clientes.csv"),
            'target_format': 'html'
        }, content_type='multipart/form-data')
        self.assertEqual(res_html.status_code, 200)
        html_text = res_html.data.decode('utf-8')
        self.assertIn("cartera_clientes", html_text)
        self.assertIn("Juan Perez", html_text)
        self.assertIn("<table", html_text)

        # CSV to XLSX using openpyxl
        res_xlsx = self.client.post('/api/convert/spreadsheet', data={
            'file': (io.BytesIO(csv_data), "cartera_clientes.csv"),
            'target_format': 'xlsx'
        }, content_type='multipart/form-data')
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertIn('spreadsheetml', res_xlsx.mimetype)

if __name__ == '__main__':
    unittest.main()
