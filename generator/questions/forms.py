from django import forms
from django.shortcuts import get_object_or_404
from taggit.forms import TagWidget
from .models import Subject, Question, Answer


class SubjectCreationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'

    class Meta:
        model = Subject
        fields = ('name', 'description')


class QuestionCreationForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('question', 'tags')
        widgets = {
            'tags': TagWidget()
        }

    # def save(self, commit=True, updated_question_id=None):
    #     if updated_question_id:
    #         instance = get_object_or_404(Question, id=updated_question_id)
    #         instance.question = self.cleaned_data.get('question')
    #         instance.tags = self.cleaned_data.get('tags')
    #
    #     else:
    #         instance = super().save(commit=False)
    #
    #     if commit:
    #         instance.save()
    #         self.save_m2m()
    #     return instance


class AnswerCreationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            if visible.name == 'is_right':
                visible.field.widget.attrs['class'] = 'form-check-input'

    class Meta:
        model = Answer
        fields = ('answer', 'is_right', 'order')

