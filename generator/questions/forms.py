from django import forms
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


class AnswerCreationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            if visible.name == 'is_right':
                visible.field.widget.attrs['class'] = 'form-check-input'

    class Meta:
        model = Answer
        fields = ('answer', 'is_right')


class SearchForm(forms.Form):
    query = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'


class SearchTagForm(forms.Form):
    tag_query = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'

