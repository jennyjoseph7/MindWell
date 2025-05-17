# 🚨 IMMEDIATE SECURITY FIXES - ACTION REQUIRED
## MindWell Platform - Priority P0 Issues

**Status:** ⛔ CRITICAL - MUST FIX BEFORE ANY DEPLOYMENT  
**Timeline:** Complete within 24-48 hours  
**Team:** Assign 2 senior engineers

---

## 🔥 CRITICAL FIX #1: Rotate Exposed API Key

**IMMEDIATE ACTION REQUIRED - DO THIS FIRST**

### The Problem
Your Google Gemini API key is hardcoded in `config.py` and committed to Git:
```python
GEMINI_API_KEY = "AIzaSyDaUJr7_CYqGC-nD-M8oVVS4Ey_BgXyBKE"
```

### Why This is Critical
- ✅ This key is visible in your Git history
- ✅ Anyone with repo access can steal it
- ✅ Attackers can consume your API quota
- ✅ Potential data breach via API abuse

### Immediate Steps (Next 30 Minutes)

1. **Go to Google Cloud Console NOW**
   - Navigate to https://console.cloud.google.com/apis/credentials
   - Find the API key ending in "...BgXyBKE"
   - Click "DELETE" or "REGENERATE"

2. **Generate New Key**
   - Create a new API key
   - Add restrictions:
     - HTTP referrers: Only your domains
     - API restrictions: Only Gemini API
   - Copy the new key to a secure location

3. **Update Your Application**
   ```bash
   # Edit .env file (NEVER commit this file)
   echo "GEMINI_API_KEY=your_new_key_here" >> .env
   ```

4. **Remove Hardcoded Key**
   ```python
   # src/mental_health_tracker/config.py
   
   # DELETE THIS LINE:
   # GEMINI_API_KEY = "AIzaSyDaUJr7_CYqGC-nD-M8oVVS4Ey_BgXyBKE"
   
   # REPLACE WITH:
   GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
   if not GEMINI_API_KEY:
       raise ValueError(
           "GEMINI_API_KEY environment variable is required. "
           "Get your key from https://ai.google.dev/ and add to .env file"
       )
   ```

5. **Verify .gitignore**
   ```bash
   # Ensure .env is ignored
   cat .gitignore | grep ".env"
   # Should show: .env
   ```

6. **Test Application**
   ```bash
   python -c "from src.mental_health_tracker import create_app; app = create_app(); print('✓ Config loaded')"
   ```

---

## 🔥 CRITICAL FIX #2: Enable CSRF Protection

### The Problem
CSRF protection is completely disabled in `config.py`:
```python
WTF_CSRF_ENABLED = False  # DANGEROUS!
WTF_CSRF_CHECK_DEFAULT = False
```

### Impact
Attackers can perform actions on behalf of authenticated users:
- Create/delete journal entries
- Modify mood entries  
- Delete user account
- Change settings

### Fix Implementation (2 Hours)

**Step 1: Enable CSRF in Config**
```python
# src/mental_health_tracker/config.py

# Change from:
WTF_CSRF_ENABLED = False
WTF_CSRF_CHECK_DEFAULT = False

# To:
WTF_CSRF_ENABLED = True
WTF_CSRF_CHECK_DEFAULT = True
WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
WTF_CSRF_SSL_STRICT = True if os.getenv('FLASK_ENV') == 'production' else False
```

**Step 2: Update Application Factory**
```python
# src/mental_health_tracker/__init__.py

from flask_wtf.csrf import CSRFProtect, generate_csrf

def create_app():
    app = Flask(__name__)
    
    # Enable CSRF protection
    csrf = CSRFProtect(app)
    
    # Make CSRF token available in all templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())
    
    return app
```

**Step 3: Add CSRF Tokens to All Forms**

Find all HTML forms and add:
```html
<!-- In every form template -->
<form method="POST">
    {{ csrf_token() }}  <!-- ADD THIS LINE -->
    <!-- rest of form -->
</form>
```

**Step 4: Update AJAX Requests**
```javascript
// In templates with AJAX
function getCsrfToken() {
    return document.querySelector('input[name="csrf_token"]').value;
}

// For all fetch requests:
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()  // ADD THIS
    },
    body: JSON.stringify(data)
});
```

**Step 5: Exempt Specific Endpoints (If Needed)**
```python
# For public APIs that need to bypass CSRF
from flask_wtf.csrf import csrf

@app.route('/api/public/endpoint', methods=['POST'])
@csrf.exempt  # Only for truly public APIs
def public_endpoint():
    pass
```

**Step 6: Test CSRF Protection**
```python
# Test that forms fail without CSRF token
import requests

# This should FAIL with 400 Bad Request
response = requests.post('http://localhost:5000/journal/new', data={
    'title': 'Test',
    'content': 'Test'
})
assert response.status_code == 400

# This should SUCCEED
session = requests.Session()
response = session.get('http://localhost:5000/journal/new')
csrf_token = extract_csrf_token(response.text)
response = session.post('http://localhost:5000/journal/new', data={
    'title': 'Test',
    'content': 'Test',
    'csrf_token': csrf_token
})
assert response.status_code == 302  # Redirect on success
```

---

## 🔥 CRITICAL FIX #3: Replace Weak SECRET_KEY

### The Problem
```python
SECRET_KEY='dev'  # Anyone can forge session cookies!
```

### Why This Matters
- Session cookies can be forged by attackers
- Users can be impersonated
- All authentication bypassed

### Fix Implementation (15 Minutes)

**Step 1: Generate Strong Key**
```python
import secrets
print(secrets.token_hex(32))
# Example output: 'a8f5f167f44f4964e6c998dee827110c47e5d75f6a19b3f1d2e5e5f5f5f5f5f5'
```

**Step 2: Add to .env File**
```bash
# .env
SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47e5d75f6a19b3f1d2e5e5f5f5f5f5f5
```

**Step 3: Update Config**
```python
# src/mental_health_tracker/config.py

SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError("SECRET_KEY must be set in production")
    else:
        # Only for development
        logger.warning("Using development SECRET_KEY - NOT SECURE!")
        SECRET_KEY = secrets.token_hex(32)
```

**Step 4: Update Application**
```python
# src/mental_health_tracker/__init__.py

# DELETE THIS:
# app.config['SECRET_KEY'] = 'dev'

# REPLACE WITH:
from .config import SECRET_KEY
app.config['SECRET_KEY'] = SECRET_KEY
```

**Step 5: Force Session Regeneration**

After deploying this fix, all existing sessions will be invalid. Add this notice:
```python
@app.before_request
def check_session_version():
    if 'session_version' not in session:
        session.clear()
        session['session_version'] = 2  # Increment when you rotate keys
```

---

## 🔥 CRITICAL FIX #4: Add Rate Limiting

### The Problem
No rate limiting allows:
- Brute force password attacks
- API abuse
- DOS attacks

### Fix Implementation (3 Hours)

**Step 1: Install Dependencies**
```bash
pip install Flask-Limiter redis
```

**Step 2: Setup Redis**
```bash
# Install Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt install redis-server
# Mac: brew install redis

# Start Redis
redis-server
```

**Step 3: Add Rate Limiter**
```python
# src/mental_health_tracker/extensions.py (new file)

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379",
    strategy="fixed-window"
)
```

**Step 4: Initialize in App**
```python
# src/mental_health_tracker/__init__.py

from .extensions import limiter

def create_app():
    app = Flask(__name__)
    limiter.init_app(app)
    return app
```

**Step 5: Apply to Sensitive Routes**
```python
# Authentication routes - strict limits
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    pass

@app.route('/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    pass

# API routes - moderate limits
@app.route('/api/mood/new', methods=['POST'])
@limiter.limit("10 per minute")
def create_mood():
    pass

# Chat endpoint - generous but limited
@app.route('/enhanced-ai-chat/send', methods=['POST'])
@limiter.limit("20 per minute")
def chat():
    pass
```

**Step 6: Add Error Handler**
```python
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'retry_after': e.description
    }), 429
```

**Step 7: Test Rate Limiting**
```python
# Test script
import requests
import time

for i in range(10):
    response = requests.post('http://localhost:5000/login', data={
        'username': 'test',
        'password': 'test'
    })
    print(f"Request {i+1}: {response.status_code}")
    if response.status_code == 429:
        print("✓ Rate limiting working!")
        break
    time.sleep(1)
```

---

## 🔥 CRITICAL FIX #5: Input Validation & Sanitization

### The Problem
User input accepted without validation:
```python
# DANGEROUS:
content = request.form.get('content')  # No validation!
db.session.add(JournalEntry(content=content))
```

### Fix Implementation (4 Hours)

**Step 1: Install Validation Libraries**
```bash
pip install bleach python-magic
```

**Step 2: Create Validation Utilities**
```python
# src/mental_health_tracker/utils/validation.py

import bleach
from wtforms.validators import ValidationError
import re

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS"""
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def validate_length(min_len: int = 0, max_len: int = 10000):
    """Validate string length"""
    def validator(form, field):
        if len(field.data) < min_len:
            raise ValidationError(f'Must be at least {min_len} characters')
        if len(field.data) > max_len:
            raise ValidationError(f'Must be less than {max_len} characters')
    return validator

def validate_no_sql_keywords(form, field):
    """Prevent SQL injection attempts"""
    sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC', 'UNION', 'SELECT']
    content_upper = field.data.upper()
    for keyword in sql_keywords:
        if keyword in content_upper:
            raise ValidationError('Invalid content detected')
```

**Step 3: Update Forms**
```python
# src/mental_health_tracker/forms.py

from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp
from .utils.validation import validate_length, validate_no_sql_keywords, sanitize_html

class JournalEntryForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be 1-200 characters'),
        validate_no_sql_keywords
    ])
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required'),
        validate_length(min_len=10, max_len=10000),
        validate_no_sql_keywords
    ])
    
    def validate_content(self, field):
        # Sanitize HTML
        field.data = sanitize_html(field.data)

class MoodEntryForm(FlaskForm):
    mood_score = SelectField('Mood', 
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        coerce=int,
        validators=[DataRequired()]
    )
    
    mood_note = TextAreaField('Notes', validators=[
        Length(max=1000, message='Notes must be less than 1000 characters'),
        validate_no_sql_keywords
    ])
```

**Step 4: Update Routes to Use Forms**
```python
# Instead of:
content = request.form.get('content')

# Use:
form = JournalEntryForm()
if form.validate_on_submit():
    content = form.content.data  # Already validated and sanitized
    # ... save to database
else:
    # Show errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')
```

---

## 📋 DEPLOYMENT CHECKLIST

Before ANY deployment, verify:

```
Security Fixes:
☐ API keys rotated and stored in environment variables
☐ CSRF protection enabled and tested
☐ Strong SECRET_KEY generated and set
☐ Rate limiting configured and working
☐ Input validation implemented on all forms
☐ SQL injection prevention verified
☐ XSS prevention verified

Configuration:
☐ .env file created with all secrets
☐ .env file NOT in Git (check .gitignore)
☐ Config validates required environment variables
☐ Debug mode disabled in production

Testing:
☐ Manual security testing completed
☐ Automated security scan run (bandit, safety)
☐ All critical routes tested with invalid input
☐ Rate limits tested and working

Documentation:
☐ Security fixes documented
☐ Deployment guide updated
☐ Incident response plan created
```

---

## 🚦 TESTING YOUR FIXES

**Security Test Suite**
```python
# tests/security/test_security_fixes.py

import pytest
from src.mental_health_tracker import create_app

def test_csrf_protection_enabled():
    app = create_app()
    assert app.config['WTF_CSRF_ENABLED'] == True

def test_strong_secret_key():
    app = create_app()
    secret = app.config['SECRET_KEY']
    assert len(secret) >= 32
    assert secret != 'dev'

def test_api_key_from_environment():
    app = create_app()
    # Should not find hardcoded key in source
    import src.mental_health_tracker.config as config_module
    source = inspect.getsource(config_module)
    assert 'AIzaSyDaUJr' not in source

def test_rate_limiting_works():
    client = app.test_client()
    for i in range(10):
        response = client.post('/login', data={'username': 'test', 'password': 'test'})
        if response.status_code == 429:
            return  # Rate limit working!
    pytest.fail("Rate limiting not working")

def test_xss_prevention():
    client = app.test_client()
    # Login first
    # ...
    
    # Try XSS attack
    response = client.post('/journal/new', data={
        'title': 'Test',
        'content': '<script>alert("XSS")</script>',
        'csrf_token': get_csrf_token(client)
    })
    
    # Verify script was sanitized
    entry = JournalEntry.query.first()
    assert '<script>' not in entry.content

def test_sql_injection_prevention():
    client = app.test_client()
    # Try SQL injection
    response = client.post('/journal/new', data={
        'title': "'; DROP TABLE users; --",
        'content': 'Test',
        'csrf_token': get_csrf_token(client)
    })
    
    # Verify form rejected
    assert response.status_code == 400
    # Verify tables still exist
    assert User.query.count() > 0
```

**Run Tests**
```bash
pytest tests/security/test_security_fixes.py -v
```

---

## 📞 EMERGENCY CONTACTS

If you discover a security breach:

1. **Immediately rotate all keys**
2. **Force logout all users** (invalidate all sessions)
3. **Review audit logs** for suspicious activity
4. **Notify affected users** if data exposed
5. **Document incident** for post-mortem

---

## 🎯 SUCCESS CRITERIA

These fixes are complete when:

✅ All 5 critical vulnerabilities fixed  
✅ Security test suite passes 100%  
✅ Automated security scan shows no critical issues  
✅ Manual penetration testing attempted and failed  
✅ Code review completed by security expert  
✅ Documentation updated

**Estimated Time:** 8-12 hours of focused work  
**Required Skills:** Python, Flask, Web Security, Testing  
**Priority:** ⛔ P0 - Block all other work until complete
