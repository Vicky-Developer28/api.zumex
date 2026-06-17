from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    Inquiry, Feedback, Subscriber,
    Visitor, VisitorLog, Author, Category, Tag, BlogPost, Comment,
    Technology, ProjectCategory, Project,
    PortfolioProject, Testimonial
)

# ==========================================
# SHARED ADMIN ACTIONS
# ==========================================

@admin.action(description=_("Approve selected items"))
def approve_items(modeladmin, request, queryset):
    queryset.update(approved=True)

@admin.action(description=_("Mark selected as active"))
def activate_items(modeladmin, request, queryset):
    queryset.update(is_active=True)

# ==========================================
# SHARED / NEW MODELS
# ==========================================

@admin.register(Inquiry)
class InquiryAdmin(ModelAdmin):
    list_display = ('full_name', 'email_address', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email_address', 'subject', 'message')
    date_hierarchy = 'created_at'
    
    def get_readonly_fields(self, request, obj=None):
        """Prevent non-superusers from editing inquiries once submitted."""
        if obj and not request.user.is_superuser:
            return ('full_name', 'email_address', 'subject', 'message', 'created_at')
        return ('created_at',)

@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    list_display = ('name', 'company', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'rating', 'created_at')
    search_fields = ('name', 'company', 'feedback_message')
    actions = [approve_items]
    
    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('app_name.change_feedback'):
            return ('name', 'company', 'rating', 'feedback_message', 'created_at')
        return ('created_at',)

@admin.register(Subscriber)
class SubscriberAdmin(ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
    
    def has_add_permission(self, request):
        """Usually, subscribers are added via frontend, prevent manual backend entry unless superuser."""
        return request.user.is_superuser


# ==========================================
# VISITOR LOGS (Strict Audit Trail)
# ==========================================

class VisitorLogInline(TabularInline):
    model = VisitorLog
    extra = 0
    readonly_fields = ('path', 'method', 'referrer', 'timestamp', 'is_blog_detail', 'blog_slug')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Visitor)
class VisitorAdmin(ModelAdmin):
    list_display = ('ip_address', 'country', 'city', 'device', 'os', 'browser', 'total_requests', 'last_seen')
    list_filter = ('country', 'device', 'os', 'browser')
    search_fields = ('ip_address', 'country', 'city')
    readonly_fields = ('ip_address', 'first_seen', 'last_seen', 'total_requests', 'country', 'city', 'device', 'os', 'browser')
    inlines = [VisitorLogInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(VisitorLog)
class VisitorLogAdmin(ModelAdmin):
    list_display = ('visitor', 'path', 'method', 'timestamp', 'is_blog_detail')
    list_filter = ('method', 'is_blog_detail', 'timestamp')
    search_fields = ('visitor__ip_address', 'path', 'blog_slug')
    readonly_fields = ('visitor', 'path', 'method', 'referrer', 'timestamp', 'is_blog_detail', 'blog_slug')
    date_hierarchy = 'timestamp'

    # Strict audit rules: No editing, creating, or deleting logs
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser


# ==========================================
# BLOG & CONTENT MODELS
# ==========================================

@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name', 'role')

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class CommentInline(TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('name', 'email', 'content', 'approved', 'created_at')

@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 'likes', 'created_at')
    list_filter = ('status', 'featured', 'category', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    inlines = [CommentInline]

    fieldsets = (
        (_('Post Information'), {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        (_('Content'), {
            'fields': ('excerpt', 'content')
        }),
        (_('Publishing & Metrics'), {
            'fields': ('status', 'featured', 'views', 'likes', 'created_at', 'updated_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = ['views', 'likes', 'created_at', 'updated_at']
        # Only superusers or users with specific permission can change post status
        if not request.user.has_perm('app_name.publish_blogpost') and not request.user.is_superuser:
            readonly.append('status')
        return readonly

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('name', 'email', 'post', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('name', 'email', 'content')
    readonly_fields = ('created_at',)
    actions = [approve_items]


# ==========================================
# PROJECT & PORTFOLIO MODELS
# ==========================================

@admin.register(Technology)
class TechnologyAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ('title', 'category', 'featured', 'likes', 'created_at')
    list_filter = ('featured', 'category', 'created_at')
    search_fields = ('title', 'short_description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('technologies',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Project Details'), {
            'fields': ('title', 'slug', 'category', 'technologies')
        }),
        (_('Content'), {
            'fields': ('short_description', 'content')
        }),
        (_('Status & Metrics'), {
            'fields': ('featured', 'likes', 'created_at', 'updated_at')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = ['likes', 'created_at', 'updated_at']
        if not request.user.is_superuser:
            readonly.append('featured')
        return readonly

@admin.register(PortfolioProject)
class PortfolioProjectAdmin(ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'category')
    readonly_fields = ('created_at',)

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ('name', 'role', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'role', 'content')
    readonly_fields = ('created_at',)
    actions = [activate_items]