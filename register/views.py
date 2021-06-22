from django.shortcuts import render, redirect
from .forms import RegisterForm

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
	return render(response, "register/logout.html", {})