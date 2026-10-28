from fastapi.testclient import TestClient
from main import app
c=TestClient(app)
def test_health():
    assert c.get('/api/health').status_code == 200
def test_planning():
    r=c.post('/api/planning',json={'area_sqft':1000,'cost_per_sqft_inr':2000,'land_value_inr':1000000,'completion_pct':40,'duration_months':10})
    assert r.status_code==200
    assert r.json()['estimated_total_inr']==2200000
def test_bad_planning():
    assert c.post('/api/planning',json={'area_sqft':-1,'cost_per_sqft_inr':2000,'land_value_inr':0,'completion_pct':40,'duration_months':10}).status_code==422
def test_wrong_file_type():
    r=c.post('/api/analyze/crack', files={'image':('a.txt',b'not image','text/plain')})
    assert r.status_code==415
def test_demo_disclosure():
    r=c.post('/api/analyze/crack',files={'image':('a.png',b'\x89PNG\r\n\x1a\n123','image/png')})
    assert r.status_code==200 and r.json()['mode']=='demo'
def test_weather():
    assert c.post('/api/weather',json={'weather':'heavy_rain'}).status_code==200
