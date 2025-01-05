from django.contrib import admin
from .models import Form, Question, Response, Answer

# Register your models here.

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'updated_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'form', 'question_type', 'order', 'required')
    list_filter = ('form', 'question_type', 'required')
    search_fields = ('question_text',)

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('form', 'submitted_at')
    list_filter = ('form', 'submitted_at')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'response', 'answer_text')
    list_filter = ('question__form', 'question__question_type')
    search_fields = ('answer_text',)
