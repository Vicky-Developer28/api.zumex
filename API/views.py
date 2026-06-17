import json
import logging
from functools import wraps

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.db.models import Q

# Import all your models
from .models import (
    Inquiry, Feedback, BlogPost, Project, PortfolioProject,
    Testimonial, Subscriber, Comment, Technology
)

logger = logging.getLogger(__name__)
logger.warning("API views.py loaded")

# -----------------------------------------------------------------------------
# SECURITY DECORATOR
# -----------------------------------------------------------------------------
def token_required(view_func):
    """
    Validates Bearer token in the Authorization header.
    Automatically applies csrf_exempt to avoid decorator ordering bugs.
    """
    @wraps(view_func)
    def wrap(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        expected_token = f"Bearer {getattr(settings, 'API_SHARED_SECRET', '')}"
        
        if auth_header == expected_token:
            return view_func(request, *args, **kwargs)
            
        logger.warning(f"Unauthorized API access attempt. Header provided: {auth_header}")
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # CRITICAL FIX: Bake CSRF exemption directly into the auth wrapper.
    # This guarantees CSRF checks are skipped for token-based API calls.
    return csrf_exempt(wrap)

# -----------------------------------------------------------------------------
# API VIEWS
# -----------------------------------------------------------------------------

@token_required
@require_http_methods(["GET", "POST"])
def inquiry_list_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            inquiry = Inquiry.objects.create(
                full_name=data.get('full_name'),
                email_address=data.get('email_address'),
                phone_number=data.get('phone_number', ''),
                subject=data.get('subject'),
                message=data.get('message'),
                ppts=data.get('ppts'),
            )
            return JsonResponse({'id': inquiry.id, 'message': 'Inquiry created'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            logger.error(f"Inquiry Creation Error: {e}")
            return JsonResponse({'error': 'Failed to create inquiry'}, status=500)
        
    # GET Request
    try:
        inquiries = list(Inquiry.objects.values())
        return JsonResponse({'inquiries': inquiries}, safe=False, status=200)
    except Exception as e:
        logger.error(f"Inquiry Fetch Error: {e}")
        return JsonResponse({'error': 'Failed to fetch inquiries'}, status=500)

@token_required
@require_http_methods(["GET", "PATCH", "DELETE"])
def inquiry_detail(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk)
    
    if request.method == 'GET':
        return JsonResponse({'id': inquiry.id, 'full_name': inquiry.full_name, 'status': inquiry.status})
        
    elif request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            if 'status' in data:
                inquiry.status = data['status']
                inquiry.save(update_fields=['status'])
            return JsonResponse({'id': inquiry.id, 'status': inquiry.status})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
            
    elif request.method == 'DELETE':
        inquiry.delete()
        return HttpResponse(status=204)

@token_required
@require_http_methods(["GET", "POST"])
def feedback_list_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            feedback = Feedback.objects.create(
                name=data.get('name'),
                company=data.get('company', ''),
                designation=data.get('designation', ''),
                rating=int(data.get('rating', 5)),
                feedback_message=data.get('feedback_message')
            )
            return JsonResponse({'id': feedback.id, 'message': 'Feedback submitted'}, status=201)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid payload or data types'}, status=400)
            
    # GET Request
    feedbacks = list(Feedback.objects.filter(approved=True).values())
    return JsonResponse(feedbacks, safe=False)

@token_required
@require_POST
def newsletter_subscribe(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)
            
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        return JsonResponse({'message': 'Successfully subscribed', 'created': created}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

@token_required
@require_POST
def ai_query_handler(request):
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '')
        bot_reply = f"AI Processed: {user_query}"
        return JsonResponse({'response': bot_reply}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

@token_required
@require_GET
def api_zumex_home(request):
    projects = list(PortfolioProject.objects.values('id', 'title', 'category', 'image_url')[:6])
    testimonials = list(Testimonial.objects.filter(is_active=True).values('id', 'name', 'role', 'category', 'content'))
    return JsonResponse({'projects': projects, 'testimonials': testimonials})

@token_required
@require_GET
def api_vicky_blogs(request):
    posts = list(BlogPost.objects.filter(status="published").values(
        'id', 'title', 'slug', 'excerpt', 'read_time', 'views', 'created_at'
    ).order_by("-published_at"))
    return JsonResponse({'posts': posts})

@token_required
@require_GET
def api_blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status="published")
    
    # Increment view count
    post.views += 1
    post.save(update_fields=["views"])
    
    post_data = {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'excerpt': post.excerpt,
        'content': post.content,
        'read_time': post.read_time,
        'views': post.views,
        'created_at': post.created_at.isoformat() if post.created_at else None,
        'category': post.category.name if hasattr(post, 'category') and post.category else None,
    }
    
    comments = list(post.comments.filter(approved=True).order_by("-created_at").values('name', 'content', 'created_at'))
    
    related = list(BlogPost.objects.filter(category=post.category, status="published")
                   .exclude(id=post.id).values('title', 'slug', 'excerpt')[:3])

    return JsonResponse({'post': post_data, 'comments': comments, 'related_posts': related})

@token_required
@require_POST
def api_blog_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    try:
        data = json.loads(request.body)
        Comment.objects.create(
            post=post,
            name=data.get('name'),
            email=data.get('email'),
            content=data.get('content'),
            approved=True
        )
        return JsonResponse({'message': 'Comment submitted successfully'}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

@token_required
@require_GET
def api_vicky_blogs_search(request):
    query = request.GET.get('q', '').strip()
    posts = BlogPost.objects.filter(status="published")
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    posts_data = list(posts.values('title', 'slug', 'excerpt', 'read_time', 'views'))
    return JsonResponse({'posts': posts_data, 'query': query})

@token_required
@require_GET
def api_project_list(request):
    projects = Project.objects.prefetch_related("technologies").select_related("category")
    
    technology = request.GET.get("technology")
    search = request.GET.get("q")
    
    if technology:
        projects = projects.filter(technologies__slug=technology)
    if search:
        projects = projects.filter(title__icontains=search)
        
    projects_data = [
        {
            'title': p.title,
            'slug': p.slug,
            'short_description': p.short_description,
            'category': p.category.name if hasattr(p, 'category') and p.category else None,
            'technologies': [tech.name for tech in p.technologies.all()]
        }
        for p in projects
    ]
        
    tech_list = list(Technology.objects.values('name', 'slug'))
    
    return JsonResponse({
        'projects': projects_data,
        'technologies': tech_list,
        'active_technology': technology,
        'search': search
    })

@token_required
@require_GET
def api_project_detail(request, slug):
    project = get_object_or_404(Project.objects.prefetch_related("technologies"), slug=slug)
    data = {
        'title': project.title,
        'slug': project.slug,
        'content': project.content,
        'github_url': project.github_url,
        'live_url': project.live_url,
        'technologies': [tech.name for tech in project.technologies.all()]
    }
    return JsonResponse({'project': data})
