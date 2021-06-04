from django import forms
from .models import UserProfile

class CreateNewList(forms.Form):
	name = forms.CharField(label="Name", max_length=200)
	check = forms.BooleanField(required=False)

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['name', 'year', 'faculty', 'major']