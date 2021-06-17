from django import forms
from .models import UserProfile, Thread
from django.contrib.postgres.forms import SimpleArrayField

class CreateNewThread(forms.Form):
	title = forms.CharField(label="Title", max_length=200)
	content = forms.CharField(label="Content", max_length=200)

class CreateNewComment(forms.Form):
	content = forms.CharField(label="Content", max_length=200)

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['name', 'year', 'faculty', 'major']
