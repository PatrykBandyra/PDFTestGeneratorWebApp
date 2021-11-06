from django import forms
from ckeditor.fields import RichTextFormField
from .models import Subject, Question


class SubjectCreationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'

    class Meta:
        model = Subject
        fields = ('name', 'description')


class TestForm(forms.Form):
    text = RichTextFormField()


class QuestionCreationForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('question',)
