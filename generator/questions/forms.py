from django import forms
from ckeditor.fields import RichTextFormField
from .models import Subject


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
    text2 = forms.CharField(max_length=25)
