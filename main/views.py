from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item
from .forms import CreateNewList
from django.contrib.auth.decorators import login_required

# Create your views here.

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


def home(response):
	return render(response, "main/home.html", {})

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