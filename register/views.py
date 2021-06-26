from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages

# Create your views here.
def register(response):
	if response.method == "POST":
		form = RegisterForm(response.POST)
		if form.is_valid():
			form.save()
			return redirect("/login")

	else:
		form = RegisterForm()
	return render(response, "register/register.html", {"form":form})

def loginprompt(response):
	return render(response, "register/loginprompt.html", {})

def logout(response):
	messages.success(response, 'Logged out successfully')
	return render(response, "register/loginprompt.html", {})
