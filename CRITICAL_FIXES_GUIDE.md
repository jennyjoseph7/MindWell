# 🛠️ CRITICAL FIXES IMPLEMENTATION
## Immediate Actions Required (Complete Today)

---

## 🔥 PRIORITY 1: Security Fixes (2-3 hours)

### 1. Fix Hardcoded API Key (30 minutes)

**Current Problem:**
```python
# src/mental_health_tracker/config.py:27
GEMINI_API_KEY = "AIzaSyDaUJr7_CYqGC-nD-M8oVVS4Ey_BgXyBKE"  # EXPOSED!
```

**Step 1: Rotate the API Key**
1. Go to Google Cloud Console: https://console.cloud.google.com/apis/credentials
2. Find API key ending in "...BgXyBKE"
3. Click "DELETE" or "REGENERATE"
4. Create new key with restrictions:
   - API restrictions: Only Gemini API
   - HTTP referrers: Only your domains

**Step 2: Update Configuration**
```python
# src/mental_health_tracker/config.py

# REMOVE THIS LINE:
# GEMINI_API_KEY = "AIzaSyDaUJr7_CYqGC-nD-M8oVVS4Ey_BgXyBKE"

# REPLACE WITH:
import os
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError(
            "GEMINI_API_KEY environment variable is required. "
            "Get your key from https://ai.google.dev/ and add to .env file"
        )
    else:
        logger.warning("GEMINI_API_KEY not set. Some features will not work.")
```

**Step 3: Update .env file**
```bash
# Create .env file (if not exists)
echo "GEMINI_API_KEY=your_new_api_key_here" > .env
echo "SECRET_KEY=your_32_char_secret_key" >> .env
echo "DATABASE_URL=postgresql://user:pass@localhost/mindwell" >> .env
```

**Step 4: Verify .gitignore**
```bash
# Ensure .env is ignored
grep ".env" .gitignore
# Should show: .env
```

### 2. Enable CSRF Protection (1 hour)

**Current Problem:**
```python
# config.py:37-38
WTF_CSRF_ENABLED = False
WTF_CSRF_CHECK_DEFAULT = False
```

**Step 1: Enable CSRF in Config**
```python
# src/mental_health_tracker/config.py

# CHANGE FROM:
WTF_CSRF_ENABLED = False
WTF_CSRF_CHECK_DEFAULT = False

# CHANGE TO:
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

    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Make CSRF token available in all templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf())

    return app
```

**Step 3: Add CSRF Tokens to Forms**
Find all HTML templates with forms and add:
```html
<!-- In every form template (templates/auth/login.html, etc.) -->
<form method="POST">
    {{ csrf_token() }}  <!-- ADD THIS LINE -->
    <!-- rest of form fields -->
</form>
```

**Step 4: Update AJAX Requests**
```javascript
// In templates with AJAX (enhanced_chat.html, etc.)
function getCsrfToken() {
    return document.querySelector('input[name="csrf_token"]').value;
}

// Update all fetch requests:
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()  // ADD THIS
    },
    body: JSON.stringify(data)
});
```

### 3. Generate Strong SECRET_KEY (15 minutes)

**Current Problem:**
```python
# __init__.py:183
SECRET_KEY='dev'  # Anyone can forge sessions!
```

**Step 1: Generate Strong Key**
```python
import secrets
print(secrets.token_hex(32))
# Example output: a8f5f167f44f4964e6c998dee827110c47e5d75f6a19b3f1d2e5e5f5f5f5f5f5
```

**Step 2: Update Configuration**
```python
# config.py
import secrets
import os

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError("SECRET_KEY must be set in production")
    else:
        SECRET_KEY = secrets.token_hex(32)
```

**Step 3: Update .env file**
```bash
echo "SECRET_KEY=a8f5f167f44f4964e6c998dee827110c47e5d75f6a19b3f1d2e5e5f5f5f5f5f5" >> .env
```

### 4. Add Input Validation (1 hour)

**Current Problem:**
```python
# No validation on user input
content = request.form.get('content')  # Can contain XSS/SQL injection
```

**Step 1: Install Validation Libraries**
```bash
pip install bleach python-magic
```

**Step 2: Create Validation Utilities**
```python
# src/mental_health_tracker/utils/validation.py

import bleach
from wtforms.validators import ValidationError

ALLOWED_HTML_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

def sanitize_html(content: str) -> str:
    """Sanitize HTML to prevent XSS attacks"""
    return bleach.clean(
        content,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def validate_content_length(min_len: int = 10, max_len: int = 10000):
    """Validate content length"""
    def validator(form, field):
        if len(field.data) < min_len:
            raise ValidationError(f'Content must be at least {min_len} characters')
        if len(field.data) > max_len:
            raise ValidationError(f'Content must be less than {max_len} characters')
    return validator

def validate_no_malicious_content(form, field):
    """Prevent SQL injection and other attacks"""
    malicious_patterns = ['<script', 'javascript:', 'DROP TABLE', 'DELETE FROM', 'INSERT INTO']
    content_lower = field.data.lower()
    for pattern in malicious_patterns:
        if pattern in content_lower:
            raise ValidationError('Invalid content detected')
```

**Step 3: Update Forms**
```python
# src/mental_health_tracker/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Email
from .utils.validation import sanitize_html, validate_content_length, validate_no_malicious_content

class JournalEntryForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=200),
        validate_no_malicious_content
    ])

    content = TextAreaField('Content', validators=[
        DataRequired(),
        validate_content_length(min_len=10, max_len=10000),
        validate_no_malicious_content
    ])

    def validate_content(self, field):
        field.data = sanitize_html(field.data)

class MoodEntryForm(FlaskForm):
    mood_score = SelectField('Mood',
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        coerce=int,
        validators=[DataRequired()]
    )

    mood_note = TextAreaField('Notes', validators=[
        Length(max=1000),
        validate_no_malicious_content
    ])

    def validate_mood_note(self, field):
        field.data = sanitize_html(field.data)
```

---

## 🏗️ PRIORITY 2: Architecture Fixes (4-6 hours)

### 1. Break Up Monolithic __init__.py (3 hours)

**Current Problem:** 1,758 lines in single file = unmaintainable

**Step 1: Create Blueprint Structure**
```python
# src/mental_health_tracker/blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from ..models import User, db
from ..forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Login logic here
    pass

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Registration logic here
    pass
```

**Step 2: Extract Business Logic**
```python
# src/mental_health_tracker/services/crisis_service.py
class CrisisService:
    @staticmethod
    def detect_crisis_in_text(text: str) -> Dict[str, Any]:
        # Crisis detection logic
        pass

    @staticmethod
    def book_therapy_session(user_id: str, crisis_level: str) -> Dict[str, Any]:
        # Therapy booking logic
        pass
```

**Step 3: Update Main Application**
```python
# src/mental_health_tracker/__init__.py (simplified)

def create_app():
    app = Flask(__name__)

    # Register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.journal import journal_bp
    from .blueprints.mood import mood_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(journal_bp, url_prefix='/journal')
    app.register_blueprint(mood_bp, url_prefix='/mood')

    # Only configuration and app setup here
    return app
```

### 2. Fix Database Issues (2 hours)

**Step 1: Add Missing Indexes**
```python
# src/mental_health_tracker/models/models.py

class MoodEntry(db.Model):
    __tablename__ = 'mood_entries'
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'date_created'),
        db.Index('idx_mood_score', 'mood_score'),
    )

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'date_created'),
        db.Index('idx_sentiment', 'sentiment_score'),
    )
```

**Step 2: Add Connection Pooling**
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'echo': False  # Set to True for SQL debugging
}
```

---

## 📦 PRIORITY 3: Infrastructure Setup (1-2 days)

### 1. Docker Configuration (4 hours)

**Step 1: Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc postgresql-client curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env.example ./.env.example

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "src.mental_health_tracker:create_app()"]
```

**Step 2: Create docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports: ["5000:5000"]
    environment:
      - DATABASE_URL=postgresql://mindwell:password@postgres:5432/mindwell
      - REDIS_URL=redis://redis:6379/0
      - FLASK_ENV=production
    depends_on: [postgres, redis]

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mindwell
      POSTGRES_USER: mindwell
      POSTGRES_PASSWORD: secure_password_here
    volumes: [postgres_data:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    volumes: [redis_data:/data]

volumes:
  postgres_data:
  redis_data:
```

### 2. Basic Testing Setup (4 hours)

**Step 1: Create Test Structure**
```bash
mkdir -p tests/unit tests/integration tests/e2e
```

**Step 2: Install Test Dependencies**
```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

**Step 3: Create Basic Tests**
```python
# tests/unit/test_crisis_detection.py
import pytest
from src.mental_health_tracker.utils.robust_enhanced_chatbot import RobustEnhancedChatbot

def test_crisis_detection():
    chatbot = RobustEnhancedChatbot()

    # Test suicidal keywords
    result = chatbot._assess_crisis_level("i feel sucidal", {}, {})
    assert result == 'critical'

    # Test normal message
    result = chatbot._assess_crisis_level("I'm happy today", {}, {})
    assert result == 'none'
```

---

## 🚀 DEPLOYMENT COMMANDS

### Quick Security Test
```bash
# 1. Test CSRF protection
curl -X POST http://localhost:5000/journal/new \
  -d "title=Test&content=Test" \
  -H "Content-Type: application/x-www-form-urlencoded"
# Should return 400 (CSRF error)

# 2. Test input validation
curl -X POST http://localhost:5000/journal/new \
  -d "title=Test&content=<script>alert('XSS')</script>&csrf_token=valid_token" \
  -H "Content-Type: application/x-www-form-urlencoded"
# Should sanitize the script tag

# 3. Test rate limiting (after implementing)
for i in {1..10}; do
  curl -X POST http://localhost:5000/login \
    -d "username=test&password=test" \
    -H "Content-Type: application/x-www-form-urlencoded"
  echo "Request $i: $?"
done
# Should see 429 errors after limit exceeded
```

### Start Development Server
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your keys

# 2. Run database migrations
python -c "from src.mental_health_tracker import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"

# 3. Start development server
python -c "from src.mental_health_tracker import create_app; app = create_app(); app.run(debug=True, host='0.0.0.0', port=5000)"
```

---

## ✅ SUCCESS CRITERIA

### Security ✅
- [ ] CSRF protection enabled and tested
- [ ] API key removed from source code
- [ ] Strong SECRET_KEY generated
- [ ] Input validation implemented
- [ ] Security scan passes (bandit, safety)

### Architecture ✅
- [ ] Monolithic code split into blueprints
- [ ] Business logic extracted to services
- [ ] Database indexes added
- [ ] Connection pooling configured

### Testing ✅
- [ ] pytest runs successfully
- [ ] Basic unit tests pass
- [ ] Integration tests work
- [ ] Code coverage > 50%

**Total Time Estimate:** 8-12 hours  
**Team Required:** 1-2 senior engineers  
**Risk Level:** Low (all fixes are standard practices)

---

## 🎯 NEXT STEPS

1. **Complete security fixes** (Priority 1)
2. **Setup Docker environment** (Priority 2)
3. **Write comprehensive tests** (Priority 3)
4. **Implement production monitoring** (Priority 4)

**Ready for production deployment after these fixes!** 🚀
