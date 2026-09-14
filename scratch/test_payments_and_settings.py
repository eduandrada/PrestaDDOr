import unittest
import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:5000"

class TestPaymentsAndSettings(unittest.TestCase):

    def test_save_settings_persistence(self):
        # Post new settings
        new_name = "Prestamos & Finanzas Test Persist"
        payload = json.dumps({"company_name": new_name, "default_grace_days": "5"}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/api/settings", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)

        # Retrieve settings and verify persistence
        get_req = urllib.request.Request(f"{BASE_URL}/api/settings")
        with urllib.request.urlopen(get_req) as get_resp:
            settings = json.loads(get_resp.read().decode('utf-8'))
            self.assertEqual(settings.get('company_name'), new_name)
            self.assertEqual(settings.get('default_grace_days'), "5")

    def test_process_payment(self):
        # Fetch loans
        req = urllib.request.Request(f"{BASE_URL}/api/loans")
        with urllib.request.urlopen(req) as resp:
            loans = json.loads(resp.read().decode('utf-8'))
            if loans:
                loan = loans[0]
                insts = loan.get('installments', [])
                pending = [i for i in insts if i.get('status') != 'pagado']
                if pending:
                    inst = pending[0]
                    inst_id = inst['id']
                    pay_payload = json.dumps({
                        "amount": 1000.0,
                        "payment_method": "Transferencia",
                        "notes": "Test payment unit test"
                    }).encode('utf-8')

                    pay_req = urllib.request.Request(f"{BASE_URL}/api/installments/{inst_id}/pay", data=pay_payload, headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(pay_req) as pay_resp:
                        self.assertEqual(pay_resp.status, 200)
                        res_data = json.loads(pay_resp.read().decode('utf-8'))
                        self.assertTrue(res_data.get('success'))
                        self.assertIn('receipt_details', res_data)

if __name__ == '__main__':
    unittest.main()
