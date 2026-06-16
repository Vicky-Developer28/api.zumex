from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    Inquiry, Feedback, Subscriber,
    Visitor, VisitorLog, Author, Category, Tag, BlogPost, Comment,
    Technology, ProjectCategory, Project,
    PortfolioProject, Testimonial
)

# ==========================================
# SHARED / NEW MODELS
# ==========================================

@admin.register(Inquiry)
class InquiryAdmin(ModelAdmin):
    list_display = ('full_name', 'email_address', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email_address', 'subject', 'message')
    readonly_fields = ('created_at',)

@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    list_display = ('name', 'company', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'rating', 'created_at')
    search_fields = ('name', 'company', 'feedback_message')
    readonly_fields = ('created_at',)

@admin.register(Subscriber)
class SubscriberAdmin(ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)


# ==========================================
# FORMER VICKY MODELS
# ==========================================

class VisitorLogInline(TabularInline):
    model = VisitorLog
    extra = 0
    readonly_fields = ('path', 'method', 'referrer', 'timestamp', 'is_blog_detail', 'blog_slug')
    can_delete = False

@admin.register(Visitor)
class VisitorAdmin(ModelAdmin):
    list_display = ('ip_address', 'country', 'city', 'device', 'os', 'browser', 'total_requests', 'last_seen')
    list_filter = ('country', 'device', 'os', 'browser')
    search_fields = ('ip_address', 'country', 'city')
    readonly_fields = ('first_seen', 'last_seen', 'total_requests')
    inlines = [VisitorLogInline]

@admin.register(VisitorLog)
class VisitorLogAdmin(ModelAdmin):
    list_display = ('visitor', 'path', 'method', 'timestamp', 'is_blog_detail')
    list_filter = ('method', 'is_blog_detail', 'timestamp')
    search_fields = ('visitor__ip_address', 'path', 'blog_slug')
    readonly_fields = ('timestamp',)

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

@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 'likes', 'created_at')
    list_filter = ('status', 'featured', 'category', 'created_at')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    readonly_fields = ('views', 'likes', 'created_at', 'updated_at')
    inlines = [CommentInline]

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('name', 'email', 'post', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('name', 'email', 'content')
    readonly_fields = ('created_at',)

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
    readonly_fields = ('likes', 'created_at', 'updated_at')


# ==========================================
# FORMER ZUMEX MODELS
# ==========================================

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