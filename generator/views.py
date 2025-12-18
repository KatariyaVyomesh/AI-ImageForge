# Add these imports at the top of views.py
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
import os
import google.generativeai as genai
import requests
import base64
from django.conf import settings
from .models import ImageGenerationTask
from dotenv import load_dotenv
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from huggingface_hub import InferenceClient  # NEW IMPORT
from io import BytesIO
from PIL import Image
load_dotenv()

# HOME PAGE VIEW
def home(request):
    """Home page - accessible to everyone"""
    if request.user.is_authenticated:
        # Show recent images for logged in user only
        recent_images = ImageGenerationTask.objects.filter(
            user=request.user
        ).order_by('-created_at')[:3]
        context = {
            'recent_images': recent_images,
            'user': request.user
        }
    else:
        context = {}
    return render(request, 'generator/home.html', context)
# SIGNUP VIEW
def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'generator/signup.html', {'form': form})

# LOGIN VIEW
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'generator/login.html', {'form': form})

# LOGOUT VIEW
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# ImageGenerator class remains the same
class ImageGenerator:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')  # NEW: Get HF token
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    def generate_prompt(self, topic, title):
        """Generate a detailed image generation prompt based on topic and title"""
        if not self.gemini_api_key:
            return "Error: Gemini API key not configured"
        
        try:
            system_prompt = f"""
                You are an expert AI image prompt engineer.

                Generate a highly detailed, vivid, and cinematic image-generation prompt based strictly on:
                Topic: {topic}
                Title: {title}

                Guidelines:
                Focus ONLY on visual elements (no explanations or storytelling)
                Describe environment, subjects, composition, colors, lighting, textures, and mood
                Specify artistic style (e.g., photorealistic, digital art, cinematic, 3D render, illustration)
                Include camera perspective or framing when relevant
                Ensure the prompt is suitable for modern AI image generation models
                Limit the output to 2–3 well-crafted sentences

                Output rules:
                Return ONLY the final image prompt text
                Do NOT include labels, bullet points, or extra commentary
            """
            
            response = self.model.generate_content(system_prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating prompt: {str(e)}"
    
    def generate_image(self, prompt):
        """Generate image using Hugging Face Inference API with fal-ai provider"""
        try:
            if not self.hf_token:
                return {"error": "Hugging Face token not configured"}
            
            # Initialize Hugging Face InferenceClient with fal-ai provider
            client = InferenceClient(
                provider="fal-ai",
                api_key=self.hf_token,
            )
            
            # Generate image using the Tongyi-MAI/Z-Image-Turbo model
            # You can also try other models like:
            # - "black-forest-labs/FLUX.1-dev" 
            # - "stabilityai/stable-diffusion-xl-base-1.0"
            # - "runwayml/stable-diffusion-v1-5"
            image = client.text_to_image(
                prompt,
                model="Tongyi-MAI/Z-Image-Turbo",
            )
            
            # Convert PIL Image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return {
                'image_base64': image_base64,
                'content_type': 'image/png',
                'prompt': prompt
            }
            
        except Exception as e:
            print(f"Error generating image with Hugging Face: {e}")
            # Fallback to Pollinations API if Hugging Face fails
            return self.generate_image_fallback(prompt)
        
    def generate_image_fallback(self, prompt):
        """Fallback method using Pollinations API if Hugging Face fails"""
        try:
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt)
            
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            image_base64 = base64.b64encode(response.content).decode("utf-8")
            content_type = response.headers.get('Content-Type', 'image/png')
            
            return {
                'image_base64': image_base64,
                'content_type': content_type,
                'prompt': prompt
            }
            
        except Exception as e:
            print(f"Fallback also failed: {e}")
            return None
# PROTECTED VIEWS (require login)
@login_required
def index(request):
    """Main image generator page - requires login"""
    if request.method == 'POST':
        topic = request.POST.get('topic', '')
        title = request.POST.get('title', '')
        
        if topic and title:
            generator = ImageGenerator()
            generated_prompt = generator.generate_prompt(topic, title)
            
            if generated_prompt.startswith("Error:"):
                context = {
                    'error': generated_prompt,
                    'topic': topic,
                    'title': title
                }
                return render(request, 'generator/index.html', context)
            
            image_result = generator.generate_image(generated_prompt)
            
            if image_result and 'error' in image_result:
                # Handle Hugging Face configuration error
                context = {
                    'error': image_result['error'],
                    'topic': topic,
                    'title': title
                }
                return render(request, 'generator/index.html', context)
            
            # Save with current user
            task = ImageGenerationTask.objects.create(
                user=request.user,
                topic=topic,
                title=title,
                generated_prompt=generated_prompt,
                image_data=image_result['image_base64'] if image_result else None,
                content_type=image_result['content_type'] if image_result else None,
                generation_type='automatic'
            )
            
            return redirect('result', task_id=task.id)
    
    return render(request, 'generator/index.html')

@login_required
def direct_generate(request):
    """Direct image generation - requires login"""
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        
        if prompt:
            generator = ImageGenerator()
            image_result = generator.generate_image(prompt)
            
            if image_result and 'error' in image_result:
                # Handle Hugging Face configuration error
                context = {
                    'error': image_result['error'],
                    'prompt': prompt
                }
                return render(request, 'generator/direct_generate.html', context)
            
            if image_result:
                # Save with current user
                task = ImageGenerationTask.objects.create(
                    user=request.user,
                    topic="Direct Generation",
                    title="User Prompt",
                    generated_prompt=prompt,
                    image_data=image_result['image_base64'],
                    content_type=image_result['content_type'],
                    generation_type='direct'
                )
                
                return redirect('result', task_id=task.id)
            else:
                context = {
                    'error': 'Failed to generate image. Please try again.',
                    'prompt': prompt
                }
                return render(request, 'generator/direct_generate.html', context)
    
    return render(request, 'generator/direct_generate.html')

@login_required
def result(request, task_id):
    """Image result page - requires login and ownership"""
    try:
        task = ImageGenerationTask.objects.get(id=task_id, user=request.user)
    except ImageGenerationTask.DoesNotExist:
        messages.error(request, "Image not found or you don't have permission to view it.")
        return redirect('home')
    
    image_data = None
    if task.image_data:
        image_data = f"data:{task.content_type};base64,{task.image_data}"
    
    context = {
        'task': task,
        'image_data': image_data,
    }
    return render(request, 'generator/result.html', context)

@login_required
def user_dashboard(request):
    """User dashboard showing all generated images"""
    images = ImageGenerationTask.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'images': images,
        'total_images': images.count()
    }
    return render(request, 'generator/dashboard.html', context)