from django import forms
from .models import UserProfile, Thread

class CreateNewThread(forms.Form):
	TAG_CHOICES = (
		('Chill', 'Chill'),
		('General','General'),
		('Food and Drinks', 'Food and Drinks'),
		('Module','Module'),
	)

	title = forms.CharField(label="Title", max_length=200)
	content = forms.CharField(label="Content", max_length=200)
	tags = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TAG_CHOICES)

class CreateNewComment(forms.Form):
	content = forms.CharField(label="Content", max_length=200)

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['name', 'year', 'faculty', 'major']
