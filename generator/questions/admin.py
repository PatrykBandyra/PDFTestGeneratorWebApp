from django.contrib import admin
from .models import Subject, Question, Answer


admin.site.register(Subject)
admin.site.register(Answer)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    ordering = ('order',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'subject', 'created', 'edited', 'last_use']
    search_fields = ['question']
    date_hierarchy = 'created'
    list_filter = ['author', 'subject', 'created', 'edited', 'last_use']
    raw_id_fields = ('author',)
    ordering = ('-created',)
    inlines = [AnswerInline]
