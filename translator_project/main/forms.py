from django import forms
from .models import Upload

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('hi', 'Hindi'),
    ('gu', 'Gujarati'),
    ('fr', 'French'),
    ('es', 'Spanish'),
    ('de', 'German'),
]

class UploadForm(forms.ModelForm):
    source_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label="From Language")
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, label="To Language")

    class Meta:
        model = Upload
        fields = ['file', 'source_language', 'language']
