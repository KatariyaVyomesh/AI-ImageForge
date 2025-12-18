# AI Image Generator

## 📋 Overview
A Django-based web application for AI-powered image generation with user authentication. The app uses multiple AI models (Gemini for prompt generation and Hugging Face/FAL for image generation) to create custom images based on user input.

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd <project-folder>

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

#### Environment Variables
Create a `.env` file in the project root:
```env
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Django Settings (optional)
SECRET_KEY=your_django_secret_key
DEBUG=True
```

**Get API Keys:**
- **Gemini API**: Google AI Studio
- **Hugging Face Token**: Hugging Face → Settings → Access Tokens

---

### 3. Database Setup
```bash
python manage.py makemigrations generator
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

---

### 4. Run Development Server
```bash
python manage.py runserver
```
Visit: **http://127.0.0.1:8000/**

---

## 🔧 Project Structure
```
project/
├── generator/
│   ├── templates/generator/
│   │   ├── home.html
│   │   ├── index.html
│   │   ├── direct_generate.html
│   │   ├── result.html
│   │   ├── dashboard.html
│   │   ├── signup.html
│   │   └── login.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── manage.py
├── requirements.txt
└── .env
```

---

## 📖 Features

### 🔐 User Authentication
- Public homepage access
- User registration with validation
- Secure login & logout
- Protected image generation routes

---

### 🖼️ Image Generation Modes

#### 1. Automatic Generation
- **Input**: Topic + Title
- **Flow**: Gemini AI → Enhanced Prompt → Image Generation
- **Output**: AI-generated image

#### 2. Direct Generation
- **Input**: Custom prompt
- **Flow**: Prompt → Image Generation
- **Output**: Image based on user input

---

## 🛠️ Image Generation Backends

### Primary
- **API**: Hugging Face Inference API
- **Provider**: FAL-AI
- **Default Model**: `Tongyi-MAI/Z-Image-Turbo`

**Supported Models:**
- `black-forest-labs/FLUX.1-dev`
- `stabilityai/stable-diffusion-xl-base-1.0`
- `runwayml/stable-diffusion-v1-5`

### Fallback
- **Pollinations API**
- Automatic failover if primary model fails

---

## 🗄️ Database Features
- User-specific image storage
- Metadata tracking:
  - Creation timestamp
  - Generation type (automatic / direct)
  - Original prompt & enhanced prompt
  - Base64 image data

---

## 🌐 URL Endpoints
| URL | View | Description | Auth |
|---|---|---|---|
| `/` | home | Public homepage | ❌ |
| `/signup/` | signup_view | User registration | ❌ |
| `/login/` | login_view | User login | ❌ |
| `/logout/` | logout_view | Logout | ✅ |
| `/generate/` | index | Automatic generation | ✅ |
| `/generate/direct/` | direct_generate | Direct prompt generation | ✅ |
| `/generate/result/<id>/` | result | View generated image | ✅ |
| `/dashboard/` | user_dashboard | User gallery | ✅ |

---

## 🧪 Usage Examples

### Automatic Generation
- Topic: **Fantasy Landscape**
- Title: **Dragon's Peak at Sunset**

### Direct Generation
```
A cyberpunk cityscape at night with neon lights and flying cars, digital art style
```

---

## ⚙️ Technical Details

### Dependencies
```
Django>=4.2
google-generativeai>=0.3.0
requests>=2.31.0
python-dotenv>=1.0.0
huggingface-hub>=0.20.0
Pillow>=10.0.0
```

### Image Storage
- Base64 encoded images
- Content type preserved
- User-linked & timestamped

### Security
- Password hashing
- CSRF protection
- Session-based authentication
- User data isolation

---

## 🐛 Troubleshooting

### API Key Errors
- Ensure `.env` exists
- Restart server after changes

### Hugging Face Errors
- Verify token permissions
- Automatic fallback enabled

### Database Issues
```bash
python manage.py migrate
```

### Test API Connectivity
```python
import os
from dotenv import load_dotenv
load_dotenv()

print("Gemini Key:", bool(os.getenv('GEMINI_API_KEY')))
print("HF Token:", bool(os.getenv('HUGGINGFACE_TOKEN')))
```

---

## 🔄 Future Enhancements
- Image download
- Social sharing
- Batch generation
- Prompt templates
- Model selector
- Image editing
- Community gallery

---

## 📄 License
Specify your license here.

---

## 👥 Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Open a Pull Request

---

## 📧 Support
- Review troubleshooting section
- Verify API keys
- Check Django logs & documentation

