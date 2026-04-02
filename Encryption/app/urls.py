from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout_user/', logout_user, name='logout_user'),
    path('upload_file/', upload_file, name='upload_file'),
    path('files/', user_files, name='user_files'),
    path('file/<int:file_id>/', file_detail, name='file_detail'),
    path('file/delete/<int:file_id>/', delete_file, name='delete_file'),
    path('explore/',explore_files, name='explore_files'),
    path('shared/', shared_with_me, name='shared_with_me'),
    path('manage-requests/',manage_requests, name='manage_requests'),
    path('request/<int:request_id>/<str:action>/', handle_file_request, name='handle_file_request'),
    path('request/<int:request_id>/cancel/', cancel_outgoing_request, name='cancel_outgoing_request'),
    path('shared-with-me/', shared_with_me, name='shared_with_me'),
    path('revoke-access/<int:file_id>/<int:user_id>/', revoke_access, name='revoke_access'),
    path('file/<int:file_id>/request/', send_file_request, name='send_file_request'),
    path('files/<int:file_id>/', file_detail_other, name='file_detail_other')

]