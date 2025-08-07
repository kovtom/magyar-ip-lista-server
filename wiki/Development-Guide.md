# Fejlesztői Útmutató

> **Teljes útmutató a Magyar IP Lista Server fejlesztéséhez és testreszabásához**

## 🎯 Fejlesztői Környezet

### Rendszerkövetelmények

**Minimális követelmények:**
- **Python**: 3.8+ (ajánlott: 3.11+)
- **Git**: 2.20+
- **IDE**: VS Code, PyCharm, vagy bármilyen Python IDE
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

**Ajánlott eszközök:**
- **Docker**: Konténerizáláshoz
- **Postman/Insomnia**: API teszteléshez
- **MikroTik WinBox**: RouterOS teszteléshez

### Projekt Struktúra

```
hulista/
├── hulista.py              # Fő alkalmazás fájl
├── requirements.txt        # Python függőségek
├── requirements-dev.txt    # Fejlesztői függőségek
├── README.md              # Projekt dokumentáció
├── README_hu.md           # Magyar dokumentáció
├── CHANGELOG.md           # Verzió történet
├── LICENSE                # MIT licenc
├── .gitignore             # Git ignore szabályok
├── .env.example           # Környezeti változók minta
├── tests/                 # Tesztek könyvtára
│   ├── __init__.py
│   ├── test_api.py        # API tesztek
│   ├── test_parser.py     # Parser tesztek
│   └── test_mikrotik.py   # MikroTik integráció tesztek
├── docs/                  # Dokumentáció
│   ├── api.md
│   ├── deployment.md
│   └── architecture.md
├── scripts/               # Segéd scriptek
│   ├── setup.sh           # Telepítő script
│   ├── deploy.sh          # Deployment script
│   └── backup.sh          # Backup script
├── docker/                # Docker konfigurációk
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
└── wiki/                  # GitHub Wiki tartalom
    ├── Home.md
    ├── Installation-Guide.md
    └── ...
```

## 🛠️ Fejlesztői Környezet Beállítása

### 1. Repository Klónozása

```bash
# Projekt klónozása
git clone https://github.com/your-username/hulista.git
cd hulista

# Development branch létrehozása
git checkout -b development
```

### 2. Python Környezet Beállítása

```bash
# Virtual environment létrehozása
python -m venv dev-env

# Aktiválás (Linux/Mac)
source dev-env/bin/activate

# Aktiválás (Windows)
dev-env\Scripts\activate.bat

# Fejlesztői függőségek telepítése
pip install -r requirements-dev.txt
```

### 3. Pre-commit Hooks Beállítása

```bash
# Pre-commit hooks telepítése
pre-commit install

# Manuális futtatás
pre-commit run --all-files
```

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### 4. Környezeti Változók

**.env.example**:
```bash
# Flask beállítások
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# IP lista forrás
IP_SOURCE_URL=https://www.nirsoft.net/countryip/hu.html
IP_SOURCE_BACKUP_URL=https://ipinfo.io/countries/hu

# Kötegelt feldolgozás
BATCH_SIZE=50
DELAY_SECONDS=30

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=hulista.log

# Cache beállítások
CACHE_ENABLED=true
CACHE_TTL=3600

# Monitoring
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=9090
```

**Használat**:
```bash
# .env fájl létrehozása
cp .env.example .env

# Környezeti változók betöltése
pip install python-dotenv
```

```python
# hulista.py-ban
from dotenv import load_dotenv
import os

load_dotenv()

FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 50))
```

## 🏗️ Alkalmazás Architektúra

### Core Komponensek

```python
# app.py - Főalkalmazás
from flask import Flask
from config import Config
from models import IPList
from services import IPDownloader, MikroTikConverter
from api import api_blueprint

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Blueprints regisztrálása
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    
    return app
```

### Modularizált Struktúra

**config.py**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    IP_SOURCE_URL = os.environ.get('IP_SOURCE_URL')
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 50))
    DELAY_SECONDS = int(os.environ.get('DELAY_SECONDS', 30))
    
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
class TestingConfig(Config):
    TESTING = True
    DEBUG = True
```

**models.py**:
```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import ipaddress

@dataclass
class IPRange:
    network: str
    start_ip: str
    end_ip: str
    total_ips: int
    batch_number: Optional[int] = None
    comment: Optional[str] = None
    
    def __post_init__(self):
        # Validáció
        try:
            net = ipaddress.ip_network(self.network)
            self.start_ip = str(net.network_address)
            self.end_ip = str(net.broadcast_address)
            self.total_ips = net.num_addresses
        except ValueError as e:
            raise ValueError(f"Invalid IP network: {self.network}") from e

@dataclass  
class IPList:
    ranges: List[IPRange] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    country_code: str = "HU"
    total_networks: int = 0
    total_ips: int = 0
    
    def add_range(self, network: str, comment: str = None):
        ip_range = IPRange(network=network, comment=comment)
        self.ranges.append(ip_range)
        self.total_networks = len(self.ranges)
        self.total_ips = sum(r.total_ips for r in self.ranges)
    
    def get_batches(self, batch_size: int = 50):
        """Kötegelt feldolgozáshoz gruppok visszaadása"""
        for i in range(0, len(self.ranges), batch_size):
            yield self.ranges[i:i + batch_size]
```

**services.py**:
```python
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
from models import IPList

class IPDownloader:
    def __init__(self, source_url: str, backup_urls: List[str] = None):
        self.source_url = source_url
        self.backup_urls = backup_urls or []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download(self) -> str:
        """IP lista letöltése és HTML visszaadása"""
        urls_to_try = [self.source_url] + self.backup_urls
        
        for url in urls_to_try:
            try:
                logging.info(f"Attempting download from: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logging.warning(f"Failed to download from {url}: {e}")
                continue
        
        raise Exception("All download sources failed")

class IPParser:
    @staticmethod
    def parse_nirsoft_html(html_content: str) -> IPList:
        """Nirsoft.net HTML formátum parser"""
        soup = BeautifulSoup(html_content, 'html.parser')
        ip_list = IPList()
        
        # IP címek keresése táblázatban
        rows = soup.find_all('tr')
        for row in rows[1:]:  # Első sor header
            cells = row.find_all('td')
            if len(cells) >= 3:
                ip_range = cells[0].text.strip()
                if '/' in ip_range:  # CIDR formátum
                    comment = f"HU-IP-{len(ip_list.ranges) + 1}"
                    ip_list.add_range(ip_range, comment)
        
        return ip_list

class MikroTikConverter:
    def __init__(self, batch_size: int = 50, delay_seconds: int = 30):
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
    
    def convert_to_script(self, ip_list: IPList) -> str:
        """IP lista MikroTik script formátumba konvertálása"""
        script_lines = [
            "# Magyar IP Lista - MikroTik RouterOS Script",
            f"# Generálva: {ip_list.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"# IP címek száma: {ip_list.total_networks}",
            "#",
            "# FIGYELEM: Ez a script kötegelt feldolgozást használ!",
            f"# {self.batch_size} IP címenként {self.delay_seconds} másodperc szünetet tart.",
            ""
        ]
        
        batch_number = 1
        total_batches = (len(ip_list.ranges) + self.batch_size - 1) // self.batch_size
        
        for batch in ip_list.get_batches(self.batch_size):
            script_lines.append(f":log info \"Magyar IP lista betöltése - Köteg {batch_number}/{total_batches}\"")
            
            for ip_range in batch:
                command = f"/ip firewall address-list add list=HU_IP address={ip_range.network}"
                if ip_range.comment:
                    command += f" comment=\"{ip_range.comment}\""
                script_lines.append(command)
            
            if batch_number < total_batches:
                script_lines.extend([
                    f":delay {self.delay_seconds}",
                    f":log info \"Köteg {batch_number}/{total_batches} betöltve, {self.delay_seconds} másodperc szünet...\"",
                    ""
                ])
            
            batch_number += 1
        
        script_lines.append(":log info \"Magyar IP lista frissítés befejezve!\"")
        return "\n".join(script_lines)
```

## 🧪 Tesztelési Keretrendszer

### Unit Tesztek

**tests/test_models.py**:
```python
import unittest
from models import IPRange, IPList

class TestIPRange(unittest.TestCase):
    def test_valid_ip_range_creation(self):
        ip_range = IPRange(network="192.168.1.0/24")
        self.assertEqual(ip_range.start_ip, "192.168.1.0")
        self.assertEqual(ip_range.end_ip, "192.168.1.255")
        self.assertEqual(ip_range.total_ips, 256)
    
    def test_invalid_ip_range_raises_error(self):
        with self.assertRaises(ValueError):
            IPRange(network="invalid-network")

class TestIPList(unittest.TestCase):
    def setUp(self):
        self.ip_list = IPList()
    
    def test_add_range_updates_counters(self):
        self.ip_list.add_range("192.168.1.0/24")
        self.assertEqual(self.ip_list.total_networks, 1)
        self.assertEqual(self.ip_list.total_ips, 256)
    
    def test_get_batches_splits_correctly(self):
        # 10 IP range hozzáadása
        for i in range(10):
            self.ip_list.add_range(f"192.168.{i}.0/24")
        
        batches = list(self.ip_list.get_batches(batch_size=3))
        self.assertEqual(len(batches), 4)  # 10/3 = 4 batch (3+3+3+1)
        self.assertEqual(len(batches[0]), 3)
        self.assertEqual(len(batches[-1]), 1)
```

**tests/test_api.py**:
```python
import unittest
import json
from hulista import create_app

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_status_endpoint(self):
        response = self.client.get('/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('version', data)
        self.assertIn('ip_count', data)
    
    def test_mikrotik_script_endpoint(self):
        response = self.client.get('/hu_ip_list.rsc')
        self.assertEqual(response.status_code, 200)
        self.assertIn('MikroTik', response.data.decode())
        self.assertEqual(response.headers['Content-Type'], 'text/plain; charset=utf-8')
    
    def test_json_api_endpoint(self):
        response = self.client.get('/api/v1/ips')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('metadata', data)
        self.assertIn('ip_ranges', data)
        self.assertEqual(data['metadata']['country'], 'HU')
    
    def test_invalid_endpoint_404(self):
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
```

### Integration Tesztek

**tests/test_integration.py**:
```python
import unittest
import requests
import time
import subprocess
import os
from threading import Thread

class IntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Flask szerver indítása teszteléshez"""
        cls.server_process = subprocess.Popen([
            'python', 'hulista.py'
        ], env=dict(os.environ, FLASK_PORT='5001'))
        time.sleep(2)  # Szerver indulásra várás
    
    @classmethod 
    def tearDownClass(cls):
        """Szerver leállítása"""
        cls.server_process.terminate()
        cls.server_process.wait()
    
    def test_full_workflow(self):
        """Teljes workflow tesztelése"""
        base_url = 'http://localhost:5001'
        
        # 1. Szerver állapot ellenőrzése
        response = requests.get(f'{base_url}/status')
        self.assertEqual(response.status_code, 200)
        
        # 2. MikroTik script letöltése
        response = requests.get(f'{base_url}/hu_ip_list.rsc')
        self.assertEqual(response.status_code, 200)
        script_content = response.text
        
        # 3. Script tartalom validálása
        self.assertIn('Magyar IP Lista', script_content)
        self.assertIn(':log info', script_content)
        self.assertIn('/ip firewall address-list add', script_content)
        
        # 4. JSON API tesztelése
        response = requests.get(f'{base_url}/api/v1/ips')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data['metadata']['ip_count'], 0)
```

### Load Testing

**tests/load_test.py**:
```python
import concurrent.futures
import requests
import time
import statistics

def single_request(url):
    start_time = time.time()
    try:
        response = requests.get(url, timeout=10)
        return {
            'success': response.status_code == 200,
            'response_time': time.time() - start_time,
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'success': False,
            'response_time': time.time() - start_time,
            'error': str(e)
        }

def load_test(url, concurrent_users=10, total_requests=100):
    """Load testing egy endpoint-ra"""
    print(f"Load testing: {url}")
    print(f"Concurrent users: {concurrent_users}")
    print(f"Total requests: {total_requests}")
    
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(single_request, url) for _ in range(total_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Eredmények kiértékelése
    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]
    response_times = [r['response_time'] for r in successful_requests]
    
    print(f"\n=== Results ===")
    print(f"Successful requests: {len(successful_requests)}/{total_requests}")
    print(f"Success rate: {len(successful_requests)/total_requests*100:.2f}%")
    print(f"Failed requests: {len(failed_requests)}")
    
    if response_times:
        print(f"Average response time: {statistics.mean(response_times):.3f}s")
        print(f"Median response time: {statistics.median(response_times):.3f}s")
        print(f"95th percentile: {sorted(response_times)[int(len(response_times)*0.95)]:.3f}s")
        print(f"Max response time: {max(response_times):.3f}s")

if __name__ == '__main__':
    # Különböző endpoint-ok tesztelése
    endpoints = [
        'http://localhost:5000/status',
        'http://localhost:5000/hu_ip_list.rsc',
        'http://localhost:5000/api/v1/ips'
    ]
    
    for endpoint in endpoints:
        load_test(endpoint, concurrent_users=5, total_requests=50)
        print("\n" + "="*50 + "\n")
```

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

**.github/workflows/ci.yml**:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, development ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Format check with black
      run: black --check .
    
    - name: Import sort check
      run: isort --check-only .
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=hulista --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run security scan
      run: |
        pip install bandit safety
        bandit -r . -ll
        safety check

  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t hulista:latest .
    
    - name: Run container test
      run: |
        docker run -d -p 5000:5000 --name test-container hulista:latest
        sleep 10
        curl -f http://localhost:5000/status || exit 1
        docker stop test-container

  release:
    needs: [test, security, docker]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Create Release
      if: contains(github.event.head_commit.message, '[release]')
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: v${{ github.run_number }}
        release_name: Release v${{ github.run_number }}
        draft: false
        prerelease: false
```

### Pre-commit Quality Gates

**requirements-dev.txt**:
```
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# Code Quality  
black>=23.1.0
flake8>=6.0.0
isort>=5.12.0
mypy>=1.0.0

# Security
bandit>=1.7.4
safety>=2.3.0

# Development
pre-commit>=3.0.0
python-dotenv>=1.0.0

# Monitoring
prometheus-client>=0.16.0
```

## 📊 Monitoring és Metrics

### Prometheus Metrics

**metrics.py**:
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from functools import wraps
import time

# Metrikák definiálása
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency'
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

IP_LIST_SIZE = Gauge(
    'ip_list_size_total',
    'Total number of IP ranges in the list'
)

def monitor_requests(f):
    """Decorator a request monitoring-hoz"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            status = getattr(result, 'status_code', 200)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=status
            ).inc()
            return result
        finally:
            REQUEST_LATENCY.observe(time.time() - start_time)
    
    return decorated_function

# Flask alkalmazásban használat
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

@app.route('/status')
@monitor_requests
def status():
    # Metrikák frissítése
    IP_LIST_SIZE.set(len(hungarian_ips))
    return jsonify({
        'status': 'running',
        'ip_count': len(hungarian_ips)
    })
```

### Health Checks

**health.py**:
```python
from flask import jsonify
import psutil
import requests
from datetime import datetime

@app.route('/health')
def health_check():
    """Komprehenzív health check"""
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'checks': {}
    }
    
    # Memória ellenőrzés
    memory = psutil.virtual_memory()
    health_status['checks']['memory'] = {
        'status': 'ok' if memory.percent < 90 else 'warning',
        'usage_percent': memory.percent,
        'available_mb': memory.available // 1024 // 1024
    }
    
    # CPU ellenőrzés
    cpu_percent = psutil.cpu_percent(interval=1)
    health_status['checks']['cpu'] = {
        'status': 'ok' if cpu_percent < 80 else 'warning',
        'usage_percent': cpu_percent
    }
    
    # Adatforrás elérhetőség
    try:
        response = requests.get(IP_SOURCE_URL, timeout=5)
        source_status = 'ok' if response.status_code == 200 else 'error'
    except Exception:
        source_status = 'error'
    
    health_status['checks']['data_source'] = {
        'status': source_status,
        'url': IP_SOURCE_URL
    }
    
    # Összesített státusz
    if any(check['status'] == 'error' for check in health_status['checks'].values()):
        health_status['status'] = 'unhealthy'
    elif any(check['status'] == 'warning' for check in health_status['checks'].values()):
        health_status['status'] = 'degraded'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
```

## 🐳 Docker Deployment

### Multi-stage Dockerfile

**Dockerfile**:
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

# Build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user létrehozása
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Jogosultságok beállítása
RUN chown -R appuser:appuser /app
USER appuser

# PATH frissítése
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000
CMD ["python", "hulista.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - redis
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - app-network

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - app-network

volumes:
  redis-data:

networks:
  app-network:
    driver: bridge
```

## 🔒 Security Best Practices

### Input Validation

```python
from flask import request, abort
import re
from functools import wraps

def validate_ip_address(ip_str):
    """IP cím validáció"""
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(ip_pattern, ip_str) is not None

def rate_limit(max_requests=100, per_seconds=3600):
    """Rate limiting decorator"""
    from collections import defaultdict, deque
    import time
    
    requests_log = defaultdict(deque)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            now = time.time()
            
            # Régi kérések törlése
            while (requests_log[client_ip] and 
                   requests_log[client_ip][0] < now - per_seconds):
                requests_log[client_ip].popleft()
            
            # Rate limit ellenőrzése
            if len(requests_log[client_ip]) >= max_requests:
                abort(429)  # Too Many Requests
            
            requests_log[client_ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Használat
@app.route('/api/v1/ips')
@rate_limit(max_requests=10, per_seconds=60)  # 10 kérés/perc
def get_ips_api():
    return jsonify(ip_data)
```

### Security Headers

```python
@app.after_request
def set_security_headers(response):
    """Biztonsági fejlécek beállítása"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

## 📝 Dokumentáció Generálás

### API Dokumentáció Swagger-rel

```python
from flasgger import Swagger, swag_from

app.config['SWAGGER'] = {
    'title': 'Hungarian IP List API',
    'uiversion': 3
}

swagger = Swagger(app)

@app.route('/api/v1/ips')
@swag_from({
    'responses': {
        200: {
            'description': 'Hungarian IP ranges',
            'schema': {
                'type': 'object',
                'properties': {
                    'metadata': {
                        'type': 'object',
                        'properties': {
                            'ip_count': {'type': 'integer'},
                            'generated_at': {'type': 'string'}
                        }
                    },
                    'ip_ranges': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'network': {'type': 'string'},
                                'total_ips': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_ips_api():
    """Get Hungarian IP ranges in JSON format"""
    return jsonify(ip_data)
```

## 🚀 Deployment Stratégiák

### Blue-Green Deployment

**deploy.sh**:
```bash
#!/bin/bash

# Blue-Green deployment script
set -e

BLUE_PORT=5000
GREEN_PORT=5001
HEALTH_CHECK_URL="http://localhost"

echo "Starting Blue-Green deployment..."

# Green környezet indítása
echo "Starting Green environment on port $GREEN_PORT..."
FLASK_PORT=$GREEN_PORT python hulista.py &
GREEN_PID=$!

# Health check
echo "Waiting for Green environment to be ready..."
sleep 10

if curl -f "$HEALTH_CHECK_URL:$GREEN_PORT/health"; then
    echo "Green environment is healthy"
    
    # Nginx konfiguráció váltása
    echo "Switching Nginx to Green environment..."
    sed -i "s/:$BLUE_PORT/:$GREEN_PORT/g" /etc/nginx/sites-available/hulista
    nginx -s reload
    
    # Blue környezet leállítása
    echo "Stopping Blue environment..."
    if [ -f blue.pid ]; then
        kill $(cat blue.pid) || true
    fi
    
    # PID fájl frissítése
    echo $GREEN_PID > blue.pid
    
    echo "Deployment completed successfully!"
else
    echo "Green environment health check failed!"
    kill $GREEN_PID || true
    exit 1
fi
```

### Canary Deployment

```yaml
# kubernetes/canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: hulista-rollout
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {}
      - setWeight: 40
      - pause: {duration: 10}
      - setWeight: 60
      - pause: {duration: 10}
      - setWeight: 80
      - pause: {duration: 10}
  selector:
    matchLabels:
      app: hulista
  template:
    metadata:
      labels:
        app: hulista
    spec:
      containers:
      - name: hulista
        image: hulista:latest
        ports:
        - containerPort: 5000
```

## 🔧 Konfigurációs Minták

### Feature Flags

```python
import json
from typing import Dict, Any

class FeatureFlags:
    def __init__(self, config_file: str = 'features.json'):
        self.config_file = config_file
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'enable_caching': True,
                'enable_metrics': False,
                'enable_rate_limiting': True,
                'batch_size_override': None
            }
    
    def is_enabled(self, flag_name: str) -> bool:
        return self.flags.get(flag_name, False)
    
    def get_value(self, flag_name: str, default=None):
        return self.flags.get(flag_name, default)

# Használat
feature_flags = FeatureFlags()

@app.route('/api/v1/ips')
def get_ips_api():
    if feature_flags.is_enabled('enable_caching'):
        # Cache logika
        pass
    
    if feature_flags.is_enabled('enable_rate_limiting'):
        # Rate limiting
        pass
    
    return jsonify(ip_data)
```

## 📚 Következő Lépések

### Contributing Guidelines

1. **Fork** a repository-t
2. **Branch** létrehozása: `git checkout -b feature/amazing-feature`
3. **Commit** változtatások: `git commit -m 'Add amazing feature'`
4. **Push** a branch-hez: `git push origin feature/amazing-feature`
5. **Pull Request** létrehozása

### Code Review Checklist

- [ ] Kód megfelel a style guide-nak (Black, Flake8)
- [ ] Unit tesztek írva és sikeresek
- [ ] Integration tesztek sikeresek
- [ ] Security scan clean
- [ ] Documentation frissítve
- [ ] CHANGELOG.md frissítve
- [ ] Performance impact értékelve

### Release Process

1. **Version bump** `__version__` változóban
2. **CHANGELOG.md** frissítése
3. **Git tag** létrehozása: `git tag v1.2.3`
4. **GitHub Release** létrehozása
5. **Docker image** push
6. **Documentation** deploy

---

**Fejlesztői útmutató kész! Vissza a [Főoldalra](Home)** 🏠
