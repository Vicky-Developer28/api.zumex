from django.urls import path
from . import views

urlpatterns = [
    # Inquiries
    path('inquiries/', views.inquiry_list_create, name='inquiries'),
    path('inquiries/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    
    # Feedback
    path('feedbacks/', views.feedback_list_create, name='feedbacks'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # AI Query
    path('query/', views.ai_query_handler, name='ai_query'),
    
    # Home & Shared Data
    path('zumex-home/', views.api_zumex_home, name='zumex_home'),
    
    # Blogs
    path('blogs/', views.api_vicky_blogs, name='blogs_list'),
    path('blogs/search/', views.api_vicky_blogs_search, name='blogs_search'),
    path('blogs/<slug:slug>/', views.api_blog_detail, name='blog_detail'),
    path('blogs/<slug:slug>/comment/', views.api_blog_comment, name='blog_comment'),
    
    # Projects
    path('projects/', views.api_project_list, name='project_list'),
    path('projects/<slug:slug>/', views.api_project_detail, name='project_detail'),
]
