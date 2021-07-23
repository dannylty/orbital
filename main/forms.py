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
	content = forms.CharField(label="Content", max_length=1000, widget=forms.Textarea)
	location = forms.ChoiceField(label="Location", choices=LOCATION_CHOICES)
	tags = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TAG_CHOICES, required=False)
	ttl = forms.IntegerField(label="Thread Duration in Days (Leave blank for permanent thread)", required=False, min_value=0, max_value=999) # if 0, thread is permanent.

class CreateNewComment(forms.Form):
	content = forms.CharField(label="Content", max_length=200)

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['name', 'year', 'faculty', 'major']

class EditThreadForm(forms.ModelForm):
	TAG_CHOICES = (
		('Chill', 'Chill'),
		('General','General'),
		('Food and Drinks', 'Food and Drinks'),
		('Module','Module'),
	)

	tags = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=TAG_CHOICES, required=False)
	content = forms.CharField(label="Content", max_length=1000, widget=forms.Textarea)
	ttl = forms.IntegerField(label="Thread Duration in Days (Leave blank for permanent thread)", required=False, min_value=0, max_value=999) # if 0, thread is permanent.
	class Meta:
		model = Thread
		fields = ['title', 'content', 'location', 'ttl']

class EditProfileThreadForm(forms.ModelForm):
	class Meta:
		model = Thread
		fields = ['content', 'viewable']
