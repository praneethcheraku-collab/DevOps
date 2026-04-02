from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import *
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
import pdfplumber
import docx
from .algorithm import *
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone


# Create your views here.
def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken. Please use another email.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose another username.')
            return render(request, 'register.html')

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
        messages.success(request, 'user register successfully')
    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        email = request.POST.get('username')  # This can be 'email' as the user is logging in with email
        password = request.POST.get('password')

        # Authenticate with email and password
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            request.session['login'] = 'user'
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def logout_user(request):
    logout(request)
    request.session.flush()
    return redirect('/')

def read_file(file):
    """
    Function to read content from different types of files:
    - Text files: .txt
    - PDF files: .pdf
    - Word files: .docx
    """

    # For text files
    if file.name.endswith('.txt'):
        return read_text_file(file)

    # For PDF files
    elif file.name.endswith('.pdf'):
        return read_pdf_file(file)

    # For Word files (DOCX)
    elif file.name.endswith('.docx'):
        return read_docx_file(file)
    
    # If file type is unsupported
    return "Unsupported file type"

def read_text_file(file):
    """Read and return content from a text file."""
    try:
        content = file.read().decode('utf-8')
        return content
    except Exception as e:
        return f"Error reading text file: {e}"

def read_pdf_file(file):
    """Read and return content from a PDF file."""
    try:
        content = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content += page.extract_text()
        return content
    except Exception as e:
        return f"Error reading PDF file: {e}"

def read_docx_file(file):
    """Read and return content from a DOCX file."""
    try:
        content = ""
        doc = docx.Document(file)
        for para in doc.paragraphs:
            content += para.text + "\n"
        return content
    except Exception as e:
        return f"Error reading DOCX file: {e}"


@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('files'):
        uploaded_files = request.FILES.getlist('files')
        file_info = []
        for file in uploaded_files:
            # file_instance = FileUpload(
            #     user=request.user,
            #     original_name=file.name,
            #     file=file,
            # )

            file_content = read_file(file)
            print(file_content)
            public_key, private_key = generate_keys()
            print('Public Key (e, N):', public_key)
            print('Private Key (d, N):', private_key)

            ciphertext = encrypt(file_content, public_key)

            print('ciphertext', ciphertext)

            file_upload = FileUpload(user=request.user, original_name=file.name, file=file)
            file_upload.set_public_key(public_key)  # Store the public key (e, N)
            file_upload.set_private_key(private_key)  # Store the private key (d, N)
            file_upload.set_encrypted_content(ciphertext)

            file_upload.save()

            file_info.append({
                'name': file.name,
                'url': file_upload.get_absolute_url(),  # Example: if you have a URL field in FileUpload
            })

        messages.success(request, 'Files uploaded successfully!')
        return JsonResponse({'success': True, 'files': file_info})
        # return redirect('upload_file')  # Redirect to the same page after upload

    # For recent uploads, get the last 5 uploaded files
    recent_uploads = FileUpload.objects.filter(user=request.user).order_by('-uploaded_at')[:5]

    return render(request, 'upload_files.html', {'recent_uploads': recent_uploads})


@login_required
def user_files(request):
    """View all files uploaded by the user"""
    # Get filter parameters
    file_type = request.GET.get('type', 'all')
    sort_by = request.GET.get('sort', '-uploaded_at')
    
    # Get user's files
    files = FileUpload.objects.filter(user=request.user)
    
    # Apply filters
    if file_type != 'all':
        files = filter_files_by_type(files, file_type)
    
    # Apply sorting
    if sort_by in ['uploaded_at', '-uploaded_at', 'original_name', '-original_name']:
        files = files.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(files, 12)  # 12 files per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get file counts for filter badges
    total_files = FileUpload.objects.filter(user=request.user).count()
    image_count = len(filter_files_by_type(FileUpload.objects.filter(user=request.user), 'image'))
    pdf_count = len(filter_files_by_type(FileUpload.objects.filter(user=request.user), 'pdf'))
    document_count = len(filter_files_by_type(FileUpload.objects.filter(user=request.user), 'document'))
    other_count = len(filter_files_by_type(FileUpload.objects.filter(user=request.user), 'other'))
    
    context = {
        'page_obj': page_obj,
        'file_type': file_type,
        'sort_by': sort_by,
        'file_counts': {
            'all': total_files,
            'image': image_count,
            'pdf': pdf_count,
            'document': document_count,
            'other': other_count,
        }
    }
    
    return render(request, 'user_files.html', context)

@login_required
def file_detail(request, file_id):
    """View details of a specific file"""
    file = get_object_or_404(FileUpload, id=file_id, user=request.user)
    
    # Determine file type for styling
    file_extension = file.original_name.split('.')[-1].lower() if file.original_name else 'other'
    file_type = get_file_type(file_extension)
    
    # Get file content for text files
    file_content = None
    if file_type in ['document', 'text']:
        try:
            file_content = read_file_content(file.file)
        except:
            file_content = "Unable to read file content"
    
    context = {
        'file': file,
        'file_type': file_type,
        'file_content': file_content,
        'file_extension': file_extension,
    }
    
    return render(request, 'file_detail.html', context)

@login_required
def delete_file(request, file_id):
    """Delete a file"""
    if request.method == 'POST':
        file = get_object_or_404(FileUpload, id=file_id, user=request.user)
        
        # Delete the physical file from storage
        if file.file:
            if os.path.isfile(file.file.path):
                os.remove(file.file.path)
        
        # Delete the database record
        file_name = file.original_name
        file.delete()
        
        messages.success(request, f'File "{file_name}" has been deleted successfully.')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': f'File "{file_name}" deleted successfully.'})
        
        return redirect('user_files')
    
    return redirect('user_files')

# Helper functions
def get_file_type(extension):
    """Determine file type based on extension"""
    image_types = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico']
    document_types = ['doc', 'docx', 'txt', 'rtf', 'odt']
    pdf_types = ['pdf']
    spreadsheet_types = ['xls', 'xlsx', 'csv', 'ods']
    presentation_types = ['ppt', 'pptx', 'odp']
    archive_types = ['zip', 'rar', '7z', 'tar', 'gz']
    code_types = ['py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'xml', 'json']
    
    if extension in image_types:
        return 'image'
    elif extension in pdf_types:
        return 'pdf'
    elif extension in document_types:
        return 'document'
    elif extension in spreadsheet_types:
        return 'spreadsheet'
    elif extension in presentation_types:
        return 'presentation'
    elif extension in archive_types:
        return 'archive'
    elif extension in code_types:
        return 'code'
    else:
        return 'other'

def filter_files_by_type(queryset, file_type):
    """Filter files by type"""
    if file_type == 'all':
        return queryset
    elif file_type == 'image':
        image_ext = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp']
        return queryset.filter(original_name__iregex=r'\.(' + '|'.join(image_ext) + ')$')
    elif file_type == 'pdf':
        return queryset.filter(original_name__iendswith='.pdf')
    elif file_type == 'document':
        doc_ext = ['doc', 'docx', 'txt', 'rtf', 'odt']
        return queryset.filter(original_name__iregex=r'\.(' + '|'.join(doc_ext) + ')$')
    elif file_type == 'spreadsheet':
        sheet_ext = ['xls', 'xlsx', 'csv', 'ods']
        return queryset.filter(original_name__iregex=r'\.(' + '|'.join(sheet_ext) + ')$')
    elif file_type == 'presentation':
        pres_ext = ['ppt', 'pptx', 'odp']
        return queryset.filter(original_name__iregex=r'\.(' + '|'.join(pres_ext) + ')$')
    elif file_type == 'archive':
        archive_ext = ['zip', 'rar', '7z', 'tar', 'gz']
        return queryset.filter(original_name__iregex=r'\.(' + '|'.join(archive_ext) + ')$')
    elif file_type == 'code':
        code_ext = ['py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'php', 'xml', 'json']
        return queryset.filter(original_name__iregex=r'\.(' + '|'.join(code_ext) + ')$')
    else:
        # For 'other', exclude all known types
        all_ext = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'pdf', 'doc', 'docx', 'txt', 
                  'rtf', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar']
        return queryset.exclude(original_name__iregex=r'\.(' + '|'.join(all_ext) + ')$')

def read_file_content(file_field):
    """Read content of text-based files"""
    try:
        with open(file_field.path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        try:
            with open(file_field.path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return "Unable to read file content"

@login_required
def explore_files(request):
    """View other users' uploaded files"""
    # Get all public files (excluding current user's files)
    public_files = FileUpload.objects.exclude(user=request.user)
    
    # Get files that user already has access to
    accessible_files = FileUpload.objects.filter(
        fileaccess__user=request.user,
        fileaccess__expires_at__gt=timezone.now()
    ) | FileUpload.objects.filter(
        fileaccess__user=request.user,
        fileaccess__expires_at__isnull=True
    )
    
    # Get pending requests
    pending_requests = FileShareRequest.objects.filter(
        requester=request.user,
        status='pending'
    ).values_list('file_id', flat=True)
    
    # Apply filters
    file_type = request.GET.get('type', 'all')
    if file_type != 'all':
        public_files = filter_files_by_type(public_files, file_type)
        accessible_files = filter_files_by_type(accessible_files, file_type)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        public_files = public_files.filter(original_name__icontains=search_query)
        accessible_files = accessible_files.filter(original_name__icontains=search_query)
    
    context = {
        'public_files': public_files,
        'accessible_files': accessible_files,
        'pending_requests': pending_requests,
        'file_type': file_type,
        'search_query': search_query,
    }
    
    return render(request, 'explore_files.html', context)

@login_required
def send_file_request(request, file_id):
    """Send file access request to file owner"""
    if request.method == 'POST':
        try:
            file = get_object_or_404(FileUpload, id=file_id)
            
            # Check if user is not the file owner
            if file.user == request.user:
                return JsonResponse({'success': False, 'error': 'You cannot request access to your own file.'})
            
            # Check if request already exists
            existing_request = FileShareRequest.objects.filter(
                requester=request.user,
                file=file
            ).first()
            
            if existing_request:
                if existing_request.status == 'pending':
                    return JsonResponse({'success': False, 'error': 'You already have a pending request for this file.'})
                elif existing_request.status == 'approved':
                    return JsonResponse({'success': False, 'error': 'You already have access to this file.'})
            
            # Check if user already has access
            if FileAccess.objects.filter(user=request.user, file=file).exists():
                return JsonResponse({'success': False, 'error': 'You already have access to this file.'})
            
            # Create new request
            message = request.POST.get('message', '')
            file_request = FileShareRequest.objects.create(
                requester=request.user,
                file_owner=file.user,
                file=file,
                message=message
            )
            
            # Send notification (you can implement this)
            # send_notification(file.user, f"{request.user.username} requested access to {file.original_name}")
            
            return JsonResponse({
                'success': True, 
                'message': 'File access request sent successfully!',
                'request_id': file_request.id
            })
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def cancel_file_request(request, request_id):
    """Cancel a pending file request"""
    if request.method == 'POST':
        file_request = get_object_or_404(
            FileShareRequest, 
            id=request_id, 
            requester=request.user,
            status='pending'
        )
        
        file_request.status = 'cancelled'
        file_request.save()
        
        return JsonResponse({'success': True, 'message': 'File request cancelled successfully.'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def manage_requests(request):
    """View and manage incoming file requests"""
    incoming_requests = FileShareRequest.objects.filter(
        file_owner=request.user,
        status='pending'
    ).select_related('requester', 'file')
    
    outgoing_requests = FileShareRequest.objects.filter(
        requester=request.user
    ).select_related('file_owner', 'file').order_by('-created_at')
    
    context = {
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
    }
    
    return render(request, 'manage_requests.html', context)

@login_required
def handle_file_request(request, request_id, action):
    """Handle file request (approve/reject)"""
    if request.method == 'POST':
        try:
            file_request = get_object_or_404(
                FileShareRequest, 
                id=request_id, 
                file_owner=request.user,
                status='pending'
            )
            
            if action == 'approve':
                # Grant file access
                file_access, created = FileAccess.objects.get_or_create(
                    user=file_request.requester,
                    file=file_request.file,
                    defaults={'granted_by': request.user}
                )
                
                file_request.status = 'approved'
                file_request.save()
                
                messages.success(request, f"Access granted to {file_request.requester.username} for {file_request.file.original_name}")
                
                return JsonResponse({
                    'success': True, 
                    'message': 'File access granted successfully!',
                    'status': 'approved'
                })
                
            elif action == 'reject':
                file_request.status = 'rejected'
                file_request.save()
                
                messages.success(request, f"Request from {file_request.requester.username} rejected.")
                
                return JsonResponse({
                    'success': True, 
                    'message': 'File request rejected.',
                    'status': 'rejected'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def cancel_outgoing_request(request, request_id):
    """Cancel an outgoing file request"""
    if request.method == 'POST':
        try:
            file_request = get_object_or_404(
                FileShareRequest, 
                id=request_id, 
                requester=request.user,
                status='pending'
            )
            
            file_request.status = 'cancelled'
            file_request.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'File request cancelled successfully.'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def shared_with_me(request):
    """View files shared with the user"""
    # Get files that user has access to through FileAccess
    accessible_files = FileUpload.objects.filter(
        fileaccess__user=request.user
    ).select_related('user').distinct()
    
    # Filter out expired accesses
    accessible_files = [
        file for file in accessible_files 
        if not FileAccess.objects.filter(
            user=request.user, 
            file=file,
            expires_at__lt=timezone.now()
        ).exists()
    ]
    
    # Apply filters if any
    file_type = request.GET.get('type', 'all')
    if file_type != 'all':
        accessible_files = filter_files_by_type(accessible_files, file_type)
    
    context = {
        'accessible_files': accessible_files,
        'file_type': file_type,
    }
    
    return render(request, 'shared_with_me.html', context)

@login_required
def revoke_access(request, file_id, user_id):
    """Revoke file access from a user"""
    if request.method == 'POST':
        file = get_object_or_404(FileUpload, id=file_id, user=request.user)
        file_access = get_object_or_404(FileAccess, file=file, user_id=user_id)
        
        file_access.delete()
        
        # Update any approved requests to cancelled
        FileShareRequest.objects.filter(
            file=file,
            requester_id=user_id,
            status='approved'
        ).update(status='cancelled')
        
        return JsonResponse({'success': True, 'message': 'File access revoked successfully.'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def filter_files_by_type(files, file_type):
    """Filter files by type (example implementation)"""
    # This is a basic implementation - adjust based on your needs
    if file_type == 'document':
        return [f for f in files if f.original_name and any(f.original_name.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt'])]
    elif file_type == 'image':
        return [f for f in files if f.original_name and any(f.original_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])]
    return files 

@login_required
def file_detail_other(request, file_id):
    """View details of a specific file"""
    file = get_object_or_404(FileUpload, id=file_id)
    
    # Determine file type for styling
    file_extension = file.original_name.split('.')[-1].lower() if file.original_name else 'other'
    file_type = get_file_type(file_extension)
    
    # Get file content for text files
    file_content = None
    if file_type in ['document', 'text']:
        try:
            file_content = read_file_content(file.file)
        except:
            file_content = "Unable to read file content"
    
    context = {
        'file': file,
        'file_type': file_type,
        'file_content': file_content,
        'file_extension': file_extension,
    }
    
    return render(request, 'other_view_files.html', context)      


