from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item
from .forms import CreateNewList, EditProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def home(response):
	return render(response, "main/home.html", {})

@login_required(login_url='/loginprompt/')
# Redirects if not logged in. Not a very nice solution
def index(response, id):
	ls = ToDoList.objects.get(id=id)

	if response.method == "POST":
		print(response.POST)
		if response.POST.get("save"):
			for item in ls.item_set.all():
				if response.POST.get("c" + str(item.id)) == "clicked":
					item.complete = True
				else:
					item.complete = False
				item.save()

		elif response.POST.get("newItem"):
			txt = response.POST.get("new")

			if len(txt) > 2:
				ls.item_set.create(text=txt, complete=False)
			else:
				print("Invalid")
	return render(response, "main/list.html", {"ls":ls})

@login_required(login_url='/loginprompt/')
def create(response):
	if response.method == "POST":
		form = CreateNewList(response.POST)

		if form.is_valid():
			n = form.cleaned_data["name"]
			response.user.todolist_set.create(name=n)

		return HttpResponseRedirect("/%i" %response.user.todolist_set.get(name=n).id)


	else:
		form = CreateNewList()
		return render(response, "main/create.html", {"form":form})

@login_required(login_url='/loginprompt/')
def view(response):
	return render(response, "main/view.html", {})

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
		return render(response, "main/editprofile.html", {"form":form})
####################################################################################################



	return render(response, "main/editprofile.html", {})