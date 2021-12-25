from django import forms
from taggit.forms import TagWidget
from .models import Quiz


class QuizCreationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg'

    class Meta:
        model = Quiz
        fields = ('name', 'description', 'tags')
        widgets = {
            'tags': TagWidget()
        }
