# models.py
from django.db import models
from django.contrib.auth.models import User  # Add this import

class ImageGenerationTask(models.Model):
    # Add foreign key to User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_images')
    
    topic = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    generated_prompt = models.TextField()
    image_data = models.TextField(blank=True, null=True)  # Store base64 image data
    content_type = models.CharField(max_length=100, default='image/png')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add new field to track generation type
    generation_type = models.CharField(
        max_length=20, 
        default='automatic', 
        choices=[('automatic', 'Automatic'), ('direct', 'Direct')]
    )
    
    def __str__(self):
        return f"{self.title} - {self.topic} ({self.user.username})"
    
    class Meta:
        ordering = ['-created_at']  # Show newest first