from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import requests

# ==========================================
# SHARED / NEW MODELS
# ==========================================

class Inquiry(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Replied', 'Replied'),
        ('Closed', 'Closed'),
    )
    full_name = models.CharField(max_length=150)
    email_address = models.EmailField(blank=True,null=True)
    phone_number = models.CharField(max_length=26, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    ppts = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.full_name}"

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='feedback_images/', blank=True, null=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback_message = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.name} ({self.rating}/5)"

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

# ==========================================
# FORMER VICKY MODELS
# ==========================================

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField(unique=True, null=True, blank=True)
    user_agent = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    total_requests = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.ip_address)

class VisitorLog(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name="logs")
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    referrer = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_blog_detail = models.BooleanField(default=False)
    blog_slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return f"{self.visitor.ip_address} -> {self.path}"

class Author(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="authors/", blank=True, null=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class BlogPost(models.Model):
    STATUS_CHOICES = (("draft", "Draft"), ("published", "Published"))
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    cover_image = models.ImageField(upload_to="blogs/covers/", blank=True, null=True)
    excerpt = models.TextField()
    content = models.TextField(blank=True, help_text="Markdown content")
    readme_file = models.FileField(upload_to="blogs/readme/", blank=True, null=True)
    github_readme_url = models.URLField(blank=True, help_text="Raw GitHub README URL")
    read_time = models.PositiveIntegerField(default=5)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.post.title}"

class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Technologies"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProjectCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Project Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    technologies = models.ManyToManyField(Technology, blank=True, related_name="projects")
    short_description = models.TextField(help_text="Shown on project cards")
    content = models.TextField(blank=True, help_text="Markdown content")
    readme_file = models.FileField(upload_to="blogs/readme/", blank=True, null=True)
    github_readme_url = models.URLField(blank=True, help_text="Raw GitHub README URL")
    cover_image = models.ImageField(upload_to="projects/covers/", blank=True, null=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# ==========================================
# FORMER ZUMEX MODELS
# ==========================================

class PortfolioProject(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, help_text="e.g., Web Development, Branding")
    image = models.ImageField(upload_to='portfolio_images/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, help_text="Fallback URL if no file is uploaded")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Portfolio Project"
        verbose_name_plural = "Portfolio Projects"

    def __str__(self):
        return self.title


class Testimonial(models.Model):

    CATEGORY_CHOICES = (
        ('Web Development', 'Web Development'),
        ('Graphic Design', 'Graphic Design'),
        ('Social Media', 'Social Media'),
    )
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="e.g., Startup Founder, CEO")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Web Development')
    content = models.TextField(help_text="The review or comment from the client")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this from the public site")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} - {self.role}"
