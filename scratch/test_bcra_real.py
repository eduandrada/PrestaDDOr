import sys
sys.path.insert(0, '.')
from app import app, query_bcra_api

with app.app_context():
    client = app.test_client()
    
    # 1. Test query_bcra_api for Banco Nación CUIT (30500010912)
    print("Testing direct BCRA official API query for 30500010912...")
    res_direct = query_bcra_api('30500010912')
    print(f"Direct Query Result: Denominacion='{res_direct.get('denominacion')}', MaxSit={res_direct.get('max_situacion')}, EntitiesCount={len(res_direct.get('entidades', []))}")
    assert res_direct.get('denominacion') == 'BANCO DE LA NACION ARGENTINA'
    assert len(res_direct.get('entidades', [])) > 0
    print("Direct Query PASSED!\n")
    
    # 2. Test Flask endpoint GET /api/bcra/check/30500010912
    print("Testing Flask endpoint GET /api/bcra/check/30500010912...")
    r = client.get('/api/bcra/check/30500010912')
    data = r.get_json()
    print(f"Endpoint Status: {r.status_code}")
    print(f"Endpoint Result: Denominacion='{data.get('denominacion')}', TotalDeudaPesos={data.get('total_deuda_pesos')}")
    assert r.status_code == 200
    assert data.get('denominacion') == 'BANCO DE LA NACION ARGENTINA'
    print("Endpoint Test PASSED!\n")
    
    print("ALL BCRA REAL DATA TESTS PASSED SUCCESSFULLY!")
