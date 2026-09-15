import sys
sys.path.insert(0, '.')
import app as flask_app
import json

client = flask_app.app.test_client()

print("Testing GET /formulario-cv...")
res1 = client.get('/formulario-cv')
print("Status:", res1.status_code)

print("Testing POST /generar-cv (json)...")
res2 = client.post('/generar-cv', json={
    "nombre": "Eduardo Andrada 2026",
    "puesto": "Senior Solutions Architect",
    "email": "eduardo@example.com",
    "plantilla": "minimalista"
})
print("Status 2:", res2.status_code)
if res2.status_code != 200:
    print("Response 2:", res2.data.decode('utf-8'))

print("Testing POST /generar-cv (form)...")
res3 = client.post('/generar-cv', data={
    "nombre": "Juan Carlos Perez",
    "puesto": "Desarrollador Senior",
    "plantilla": "minimalista"
})
print("Status 3:", res3.status_code)
if res3.status_code != 200:
    print("Response 3:", res3.data.decode('utf-8'))
