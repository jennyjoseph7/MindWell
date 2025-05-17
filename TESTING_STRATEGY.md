# 🧪 COMPREHENSIVE TESTING STRATEGY
## MindWell Platform - Testing Implementation Guide

**Status:** Critical Gap - 2% Coverage (UNACCEPTABLE)  
**Target:** 80%+ Coverage in 2 weeks  
**Priority:** P0 - Block production deployment

---

## 📊 CURRENT TESTING STATUS

### Existing Tests (2% Coverage)
- ✅ `test_crisis_detection.py` - Manual crisis pattern testing
- ✅ `test_emotion_detection.py` - Emotion analysis validation
- ✅ `test_sentiment.py` - Basic sentiment analysis
- ❌ **No unit tests** for core business logic
- ❌ **No integration tests** for database operations
- ❌ **No E2E tests** for user journeys
- ❌ **No security tests** for vulnerabilities

### Testing Debt Analysis

| Component | Lines of Code | Tests Needed | Current Coverage |
|-----------|---------------|--------------|------------------|
| **Authentication** | 150 lines | 20 tests | 0% |
| **Crisis Detection** | 512 lines | 50 tests | 5% |
| **Journal System** | 300 lines | 30 tests | 0% |
| **Mood Tracker** | 200 lines | 25 tests | 0% |
| **AI Chatbot** | 259 lines | 40 tests | 0% |
| **Database Models** | 176 lines | 15 tests | 0% |
| **API Endpoints** | 200 lines | 35 tests | 0% |
| **Total** | **1,797 lines** | **215 tests** | **2%** |

---

## 🎯 TESTING ROADMAP

### Week 1: Foundation (50 tests, 40% coverage)

#### **Day 1-2: Setup Testing Infrastructure**
```bash
# Install testing dependencies
pip install pytest pytest-cov pytest-asyncio pytest-mock
pip install selenium playwright locust
pip install bandit safety flake8 black

# Create test directory structure
mkdir -p tests/{unit,integration,e2e,load,security}
mkdir -p tests/fixtures
mkdir -p tests/data
```

#### **Day 3-4: Core Unit Tests**
```python
# tests/unit/test_auth.py
import pytest
from src.mental_health_tracker import create_app
from src.mental_health_tracker.models import User, db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_user_registration(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'confirm_password': 'SecurePass123!'
    })
    assert response.status_code == 302  # Redirect on success
    assert User.query.filter_by(username='testuser').first() is not None

def test_invalid_login(client):
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_password_hashing():
    user = User(username='test', email='test@example.com')
    user.set_password('password123')
    assert user.check_password('password123') == True
    assert user.check_password('wrongpassword') == False
    assert user.password_hash != 'password123'  # Not plain text
```

#### **Day 5: Crisis Detection Tests**
```python
# tests/unit/test_crisis_detection.py
import pytest
from src.mental_health_tracker.utils.robust_enhanced_chatbot import RobustEnhancedChatbot

class TestCrisisDetection:
    @pytest.fixture
    def chatbot(self):
        return RobustEnhancedChatbot()

    def test_detects_critical_crisis(self, chatbot):
        """Test detection of suicidal ideation"""
        result = chatbot._assess_crisis_level(
            "I want to kill myself",
            {'sentiment': 'negative'},
            {'crisis_mentions': 0}
        )
        assert result == 'critical'

    def test_handles_misspellings(self, chatbot):
        """Test detection of common misspellings"""
        test_cases = [
            "i feel sucidal",
            "i feel suicidal",
            "I want to end my life",
            "I'm thinking about ending it all"
        ]

        for message in test_cases:
            result = chatbot._assess_crisis_level(message, {}, {})
            assert result in ['critical', 'high'], f"Failed for: {message}"

    def test_no_false_positives(self, chatbot):
        """Test that normal messages don't trigger crisis"""
        normal_messages = [
            "I'm feeling happy today",
            "Just having a normal day",
            "Work is going well",
            "Looking forward to the weekend"
        ]

        for message in normal_messages:
            result = chatbot._assess_crisis_level(message, {}, {})
            assert result == 'none', f"False positive for: {message}"

    def test_emotion_detection_accuracy(self, chatbot):
        """Test emotion detection accuracy"""
        # Crisis message
        emotions = chatbot._extect_emotions_simple("I feel hopeless and suicidal")
        assert 'despair' in emotions
        assert emotions['despair'] > 0.6  # High confidence

        # Happy message
        emotions = chatbot._extect_emotions_simple("I'm so happy and excited!")
        assert 'joy' in emotions
        assert emotions['joy'] > 0.4
```

#### **Day 6: Database Integration Tests**
```python
# tests/integration/test_database.py
import pytest
from src.mental_health_tracker import create_app, db
from src.mental_health_tracker.models import User, MoodEntry, JournalEntry

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

class TestDatabaseOperations:
    def test_mood_entry_crud(self, app, client):
        """Test complete mood entry lifecycle"""
        with app.app_context():
            # Create user
            user = User(username='test', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            # Login
            client.post('/login', data={
                'username': 'test',
                'password': 'password'
            })

            # Create mood entry
            response = client.post('/mood/new', data={
                'mood_score': '3',
                'mood_note': 'Feeling okay today',
                'csrf_token': 'valid_token'
            })
            assert response.status_code == 302

            # Verify in database
            entry = MoodEntry.query.filter_by(user_id=user.id).first()
            assert entry is not None
            assert entry.mood_score == 3
            assert entry.notes == 'Feeling okay today'

    def test_journal_crisis_detection(self, app, client):
        """Test crisis detection in journal entries"""
        with app.app_context():
            # Create user
            user = User(username='test', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

            # Login
            client.post('/login', data={
                'username': 'test',
                'password': 'password'
            })

            # Create journal with crisis keywords
            response = client.post('/journal/new', data={
                'title': 'Dark thoughts',
                'content': 'I feel sucidal and alone',
                'csrf_token': 'valid_token'
            })

            # Should redirect and create crisis incident
            assert response.status_code == 302

            # Verify crisis was detected and logged
            crisis_incident = db.session.query(CrisisIncident).filter_by(
                user_id=user.id
            ).first()
            assert crisis_incident is not None
            assert crisis_incident.crisis_level == 'critical'
```

#### **Day 7: API Integration Tests**
```python
# tests/integration/test_api.py
import pytest
import json
from src.mental_health_tracker import create_app

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

class TestAPIEndpoints:
    def test_chat_api_security(self, client):
        """Test chat API security"""
        # Test without authentication
        response = client.post('/api/chat', json={
            'message': 'Hello'
        })
        assert response.status_code == 401

        # Test with invalid data
        # (would need authenticated client for full test)

    def test_journal_api_validation(self, client):
        """Test journal API input validation"""
        # Test XSS attempt
        response = client.post('/journal/new', data={
            'title': 'Test',
            'content': '<script>alert("XSS")</script>',
            'csrf_token': 'valid_token'
        })
        # Should either reject or sanitize
        assert response.status_code in [400, 302]

    def test_mood_api_constraints(self, client):
        """Test mood API data constraints"""
        # Test invalid mood score
        response = client.post('/mood/new', data={
            'mood_score': '999',  # Invalid score
            'mood_note': 'Test',
            'csrf_token': 'valid_token'
        })
        assert response.status_code == 400
```

### Week 2: Advanced Testing (80% coverage target)

#### **Day 8-10: E2E Testing with Playwright**
```bash
# Install Playwright
pip install playwright
playwright install chromium

# tests/e2e/test_user_journey.py
import pytest
from playwright.sync_api import sync_playwright

class TestUserJourney:
    def test_complete_user_registration(self):
        """Test complete user registration flow"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Navigate to registration
            page.goto('http://localhost:5000/register')

            # Fill registration form
            page.fill('input[name="username"]', 'e2e_test_user')
            page.fill('input[name="email"]', 'e2e@test.com')
            page.fill('input[name="password"]', 'TestPass123!')
            page.fill('input[name="confirm_password"]', 'TestPass123!')
            page.click('button[type="submit"]')

            # Should redirect to dashboard
            page.wait_for_url('**/dashboard')
            assert 'Welcome' in page.content()

            browser.close()

    def test_crisis_detection_e2e(self):
        """Test crisis detection in real user flow"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Login
            page.goto('http://localhost:5000/login')
            page.fill('input[name="username"]', 'test_user')
            page.fill('input[name="password"]', 'password')
            page.click('button[type="submit"]')

            # Navigate to journal
            page.goto('http://localhost:5000/journal/new')

            # Enter crisis content
            page.fill('input[name="title"]', 'Feeling down')
            page.fill('textarea[name="content"]', 'I feel sucidal and hopeless')
            page.click('button[type="submit"]')

            # Should show crisis warning
            page.wait_for_selector('.alert-danger')
            assert 'KIRAN' in page.content() or 'crisis' in page.content().lower()

            browser.close()
```

#### **Day 11-12: Load Testing with Locust**
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between, events
import json

class MindWellUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login when user starts"""
        response = self.client.post('/login', data={
            'username': 'loadtest_user',
            'password': 'LoadTest123!',
            'csrf_token': self.get_csrf_token()
        })
        if response.status_code != 302:
            print("Failed to login")

    def get_csrf_token(self):
        """Extract CSRF token from page"""
        # Implementation for CSRF token extraction
        return 'test_token'

    @task(3)
    def view_dashboard(self):
        """Most common user action"""
        self.client.get('/dashboard')

    @task(2)
    def create_mood_entry(self):
        """Mood tracking"""
        self.client.post('/mood/new', data={
            'mood_score': '3',
            'mood_note': 'Feeling okay',
            'csrf_token': self.get_csrf_token()
        })

    @task(1)
    def chat_with_ai(self):
        """AI interaction"""
        self.client.post('/enhanced-ai-chat/send', json={
            'message': 'How are you?',
            'session_id': 'load_test_session'
        })

    @task(1)
    def create_journal_entry(self):
        """Journal writing"""
        self.client.post('/journal/new', data={
            'title': 'Daily reflection',
            'content': 'Today was a good day overall',
            'csrf_token': self.get_csrf_token()
        })

# Custom events for monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Starting load test with {environment.runner.user_count} users")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test completed")
```

#### **Day 13-14: Security Testing**
```python
# tests/security/test_security.py
import pytest
from src.mental_health_tracker import create_app

class TestSecurity:
    def test_csrf_protection(self, client):
        """Test CSRF protection is enabled"""
        app = create_app()

        # CSRF should be enabled in production
        assert app.config['WTF_CSRF_ENABLED'] == True

        # Test without CSRF token (should fail)
        response = client.post('/journal/new', data={
            'title': 'Test',
            'content': 'Test'
        })
        assert response.status_code == 400  # CSRF error

    def test_xss_prevention(self, client):
        """Test XSS prevention"""
        # This would require authenticated client
        # Test that script tags are sanitized

    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention"""
        # Test malicious input is rejected
        malicious_input = "'; DROP TABLE users; --"
        response = client.post('/journal/new', data={
            'title': malicious_input,
            'content': 'Test',
            'csrf_token': 'valid_token'
        })
        # Should reject or sanitize
        assert response.status_code in [400, 302]

    def test_rate_limiting(self, client):
        """Test rate limiting is working"""
        # Make multiple rapid requests
        for i in range(10):
            response = client.post('/login', data={
                'username': 'test',
                'password': 'wrong'
            })

            if response.status_code == 429:
                return  # Rate limiting working

        pytest.fail("Rate limiting not working")

    def test_input_validation(self, client):
        """Test input validation"""
        # Test oversized input
        huge_content = 'x' * 100000  # 100KB content
        response = client.post('/journal/new', data={
            'title': 'Test',
            'content': huge_content,
            'csrf_token': 'valid_token'
        })
        assert response.status_code == 400  # Should reject

    def test_session_security(self, client):
        """Test session security"""
        app = create_app()

        # Session should be secure
        assert app.config['SESSION_COOKIE_SECURE'] == True
        assert app.config['SESSION_COOKIE_HTTPONLY'] == True

        # SECRET_KEY should be strong
        secret = app.config['SECRET_KEY']
        assert len(secret) >= 32
        assert secret != 'dev'
```

---

## 🚀 CI/CD PIPELINE SETUP

### 1. GitHub Actions Configuration

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio bandit safety flake8 black

    - name: Run tests
      run: |
        pytest tests/unit/ tests/integration/ --cov=src --cov-report=xml --cov-report=html --cov-fail-under=80
      env:
        DATABASE_URL: postgresql://postgres:test_password@localhost/test_db
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test_secret_key_for_ci
        GEMINI_API_KEY: test_key_for_ci

    - name: Security scan
      run: |
        bandit -r src/ -f json -o bandit-report.json
        safety check --json > safety-report.json
        # Fail if critical vulnerabilities found
        python -c "
        import json
        with open('bandit-report.json') as f:
            bandit = json.load(f)
        if any(issue['issue_severity'] == 'HIGH' for issue in bandit['results']):
            print('CRITICAL: High severity security issues found!')
            exit(1)
        "

    - name: Code quality
      run: |
        flake8 src/ --max-line-length=120 --exclude=__pycache__ --count --statistics
        black --check --diff src/

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t mindwell:${{ github.sha }} .

    - name: Test Docker image
      run: |
        docker run -d --name test-container -p 5000:5000 mindwell:${{ github.sha }}
        sleep 10
        curl -f http://localhost:5000/health || exit 1
        curl -f http://localhost:5000/ || exit 1
        docker stop test-container
        docker rm test-container

    - name: Push to registry (if needed)
      if: success()
      run: |
        echo "Ready for deployment"
        # docker push to registry
```

---

## 📊 TEST COVERAGE TARGETS

### Coverage Goals by Component

| Component | Current | Target | Priority | Tests Needed |
|-----------|---------|--------|----------|--------------|
| **Authentication** | 0% | 90% | P0 | Login, register, logout, password reset |
| **Crisis Detection** | 5% | 95% | P0 | Pattern matching, escalation, notifications |
| **Journal System** | 0% | 85% | P1 | CRUD operations, crisis integration |
| **Mood Tracker** | 0% | 85% | P1 | Entry creation, analytics, trends |
| **AI Chatbot** | 0% | 80% | P1 | Response generation, context management |
| **Database Models** | 0% | 90% | P1 | Relationships, constraints, migrations |
| **API Endpoints** | 0% | 85% | P2 | Status codes, validation, error handling |
| **Security** | 0% | 90% | P0 | CSRF, XSS, SQL injection prevention |

### Test Categories and Metrics

```python
# pytest configuration
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    security: Security tests
    slow: Slow running tests
```

---

## 🛠️ TESTING TOOLS & FRAMEWORKS

### 1. Unit Testing
```python
# Core testing stack
pytest                    # Test framework
pytest-cov               # Coverage reporting
pytest-asyncio           # Async test support
pytest-mock              # Mocking utilities
pytest-xdist             # Parallel test execution
pytest-html              # HTML test reports
```

### 2. Integration Testing
```python
# Database testing
pytest-postgresql        # PostgreSQL test database
pytest-redis             # Redis test instance
factory-boy              # Test data factories
faker                    # Fake data generation
```

### 3. E2E Testing
```python
# Browser automation
playwright               # Modern browser automation
selenium                 # Alternative browser testing
pytest-playwright        # Playwright integration
```

### 4. Load Testing
```python
# Performance testing
locust                   # Load testing framework
pytest-benchmark         # Performance benchmarking
memory-profiler          # Memory usage analysis
```

### 5. Security Testing
```python
# Security scanning
bandit                   # Python security linting
safety                   # Dependency vulnerability scanning
pip-audit                # Package vulnerability checking
```

### 6. Code Quality
```python
# Code analysis
flake8                   # Style and error checking
black                    # Code formatting
mypy                     # Type checking
isort                    # Import sorting
pre-commit               # Pre-commit hooks
```

---

## 🎯 IMPLEMENTATION TIMELINE

### Week 1: Foundation (50 tests, 40% coverage)

| Day | Focus | Tests | Target Coverage |
|-----|-------|-------|-----------------|
| **Day 1** | Setup infrastructure | 0 | 2% |
| **Day 2** | Authentication tests | 15 | 15% |
| **Day 3** | Crisis detection tests | 20 | 30% |
| **Day 4** | Database integration | 10 | 35% |
| **Day 5** | API endpoint tests | 5 | 40% |
| **Day 6** | CI pipeline setup | 0 | 40% |
| **Day 7** | Review and optimization | 0 | 40% |

### Week 2: Advanced Testing (80% coverage)

| Day | Focus | Tests | Target Coverage |
|-----|-------|-------|-----------------|
| **Day 8** | E2E test framework | 5 | 45% |
| **Day 9** | User journey tests | 10 | 55% |
| **Day 10** | Load testing setup | 5 | 60% |
| **Day 11** | Security tests | 15 | 70% |
| **Day 12** | Performance tests | 10 | 75% |
| **Day 13** | Coverage gaps | 15 | 85% |
| **Day 14** | Final optimization | 5 | 80% |

---

## 📈 SUCCESS METRICS

### Coverage Goals
- **Unit Tests:** 90%+ coverage of business logic
- **Integration Tests:** 85%+ coverage of API endpoints
- **E2E Tests:** 80%+ coverage of user journeys
- **Security Tests:** 95%+ coverage of attack vectors

### Quality Gates
```yaml
# .github/workflows/quality-gates.yml
- Coverage must be > 80%
- No critical security vulnerabilities (bandit)
- No unsafe dependencies (safety)
- All tests must pass
- Code must follow style guidelines (flake8)
- No new technical debt without justification
```

### Performance Benchmarks
- **Unit tests:** < 5 seconds
- **Integration tests:** < 30 seconds
- **E2E tests:** < 2 minutes
- **Load tests:** Support 100 concurrent users with < 2s response time

---

## 🚨 TESTING CHECKLIST

### Pre-Deployment Testing ✅
- [ ] All security tests pass
- [ ] Crisis detection works in all contexts (journal, mood, chat)
- [ ] Authentication flows work correctly
- [ ] Database operations are properly tested
- [ ] API endpoints return correct status codes
- [ ] Error handling works as expected

### Performance Testing ✅
- [ ] Load testing completed (100 concurrent users)
- [ ] Database query optimization verified
- [ ] AI response times acceptable (< 2 seconds)
- [ ] Memory usage monitored and acceptable

### Security Testing ✅
- [ ] CSRF protection tested and working
- [ ] XSS prevention verified
- [ ] SQL injection attempts blocked
- [ ] Rate limiting tested and effective
- [ ] Input validation working correctly

**Ready for production after comprehensive testing!** 🧪✅
