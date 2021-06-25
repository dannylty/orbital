from django import forms
from .models import UserProfile, Thread

class CreateNewThread(forms.Form):
	TAG_CHOICES = (
		('Chill', 'Chill'),
		('General','General'),
		('Food and Drinks', 'Food and Drinks'),
		('Module','Module'),
	)

	LOCATION_CHOICES = (
		('General', 'General'),
		('COM','Computing'),
		('KR MRT', 'KR MRT'),
		('SCI','SCI'),
		('BIZ', 'BIZ'),
		('WTV', 'WTV')
	)

	title = forms.CharField(label="Title", max_length=200)
	content = forms.CharField(label="Content", max_length=1000)
	location = forms.ChoiceField(label="Location", choices=LOCATION_CHOICES)
	tags = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TAG_CHOICES, required=False)

class CreateNewComment(forms.Form):
	content = forms.CharField(label="Content", max_length=200)

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['name', 'year', 'faculty', 'major']
