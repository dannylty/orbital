from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item, Thread, Comment
from .forms import CreateNewThread, EditProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def home(response):
	return render(response, "main/home.html", {})

@login_required(login_url='/loginprompt/')
# Redirects if not logged in. Not a very nice solution.
def index(response, id):
	t = Thread.objects.get(id=id)

	if response.method == "POST":
		if response.POST.get("new"):
			txt = response.POST.get("new")
			if len(txt) > 0:
				t.comment_set.create(user=response.user, content=txt)
			else:
				print("error: invalid length")
		else:
			print("error: invalid POST")
		return HttpResponseRedirect("/thread/%i" % id)

	return render(response, "main/index.html", {"t":t})

@login_required(login_url='/loginprompt/')
def create(response):
	if response.method == "POST":
		form = CreateNewThread(response.POST)

		if form.is_valid():
			t = form.cleaned_data["title"]
			c = form.cleaned_data["content"]

			# Require a check cause redirection function filters using title and content.
			if Thread.objects.filter(title=t, content=c).count() > 0:
				print("error: already exists")
				return render(response, "main/already_exists.html", {})

			response.user.thread_set.create(title=t, content=c)

		return HttpResponseRedirect("/thread/%i" % response.user.thread_set.get(title=t, content=c).id)


	else:
		form = CreateNewThread()
		return render(response, "main/create.html", {"form":form})

@login_required(login_url='/loginprompt/')
def view(response):
	tlist = Thread.objects.all()
	return render(response, "main/view.html", {"tlist":tlist})

@login_required(login_url='/loginprompt/')
def profile(response):
	return render(response, "main/profile.html", {})

@login_required(login_url='/loginprompt/')
def editprofile(response):

####################################################################################################
	if response.method == "POST":
		form = EditProfileForm(response.POST, instance=response.user.userprofile)

		if form.is_valid():
			m = form.cleaned_data["major"]
			form = form.save(commit=False)
			form.major = form.major
			form.save()
			# messages.success(response, 'Your profile has been updated!')

		return HttpResponseRedirect("/profile")

	else:
		form = EditProfileForm(instance=response.user.userprofile)
		return render(response, "main/edit_profile.html", {"form":form})
####################################################################################################

	return render(response, "main/edit_profile.html", {})