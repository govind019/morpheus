from django.db import models
from django.contrib.auth.models import User
import json
from django.utils import timezone

# Create your models here.

class Form(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'Text'),
        ('dropdown', 'Dropdown'),
        ('checkbox', 'Checkbox'),
    )

    form = models.ForeignKey(Form, related_name='questions', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.IntegerField()
    required = models.BooleanField(default=False)
    options = models.TextField(blank=True, null=True)  # JSON string for dropdown/checkbox options

    def get_options(self):
        if self.options:
            return json.loads(self.options)
        return []

    def set_options(self, options_list):
        self.options = json.dumps(options_list)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.form.title} - {self.question_text}"

class Response(models.Model):
    form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=timezone.now)
    completion_time = models.IntegerField(null=True, blank=True)  # Time in seconds
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.pk:  # New response
            self.start_time = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Response to {self.form.title} at {self.submitted_at}"

class Answer(models.Model):
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()  # Store all answers as text, parse based on question type

    def __str__(self):
        return f"Answer to {self.question.question_text}"
