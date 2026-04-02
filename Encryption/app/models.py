# models.py
from django.db import models
from django.contrib.auth.models import User
import os
import json
from django.urls import reverse
from django.utils import timezone

class FileUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    original_name = models.CharField(max_length=255, null=True)
    file = models.FileField(upload_to=os.path.join('static', 'files'), blank=True, null=True)
    
    # Store the public and private keys as JSON objects
    public_key = models.JSONField(blank=True, null=True)
    private_key = models.JSONField(blank=True, null=True)
    
    encrypted_content = models.TextField(null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.original_name
    
    def get_absolute_url(self):
        # Assuming you have a URL pattern for serving the file
        return reverse('file_detail', args=[str(self.id)])

    def get_file_size_display(self):
        size = self.file.size
        if size < 1024:
            return f"{size} Bytes"
        elif size < 1048576:
            return f"{size // 1024} KB"
        elif size < 1073741824:
            return f"{size // 1048576} MB"
        else:
            return f"{size // 1073741824} GB"

    # Set public key as a JSON object
    def set_public_key(self, public_k):
        """Store public key as a tuple (e, N), where N is a tuple (x, y, z)."""
        public_key_data = {
            'e': public_k
        }
        self.public_key = public_key_data

    # Set private key as a JSON object
    def set_private_key(self, prive_k):
        """Store private key as a tuple (d, N), where N is a tuple (x, y, z)."""
        private_key_data = {
            'd': prive_k,
        }
        self.private_key = private_key_data

    # Get public key from JSON object
    def get_public_key(self):
        """Return public key as a tuple (e, N)."""
        return self.public_key['e'], self.public_key['N']

    # Get private key from JSON object
    def get_private_key(self):
        """Return private key as a tuple (d, N)."""
        return self.private_key['d'], self.private_key['N']
    
    def set_encrypted_content(self, encrypted_tuple):
        """Store encrypted content as a string in the format (value1, value2, value3)."""
        self.encrypted_content = f"({encrypted_tuple[0]}, {encrypted_tuple[1]}, {encrypted_tuple[2]})"

    def get_encrypted_content(self):
        """Retrieve encrypted content as a tuple."""
        if self.encrypted_content:
            # Parse the string into a tuple
            encrypted_content = self.encrypted_content.strip("()").split(", ")
            return tuple(map(int, encrypted_content))  # Convert the string values to integers
        return None
        
class FileShareRequest(models.Model):
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_requests_sent')
    file_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_requests_received')
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['requester', 'file']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.requester.username} -> {self.file_owner.username} for {self.file.original_name}"

class FileAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_access')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'file']
        ordering = ['-granted_at']
    
    def __str__(self):
        return f"{self.user.username} can access {self.file.original_name}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
        
