import json
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app, db
from models import Client, Loan
from utils.notification import generate_loan_summary_html, send_whatsapp

def test_settings_validation_and_persistence(tmp_path):
    with app.test_client() as c:
        r=c.post('/settings', json={'cuit_cuil':'20-12345678-9','alias':'TEST.ALIAS','notify_pdf':True})
        assert r.status_code==200
        assert c.get('/settings').get_json()['alias']=='TEST.ALIAS'

def test_settings_reject_invalid_cuit():
    with app.test_client() as c:
        assert c.post('/settings', json={'cuit_cuil':'123'}).status_code==400

def test_whatsapp_missing_credentials():
    with patch.dict('os.environ', {}, clear=True):
        try: send_whatsapp('hola','5493830000000')
        except RuntimeError as e: assert 'Twilio' in str(e)
        else: raise AssertionError('Expected missing credential error')

def test_pdf_html_generation():
    html=generate_loan_summary_html({'id':1,'amount':1000,'total_loan_amount':1200,'remaining_balance':1200,'installments_count':1,'installments':[{'number':1,'due_date':'2026-10-01','amount':1200,'status':'pendiente'}],'client':{'name':'Test'}})
    assert '<html' in html and 'Test' in html
