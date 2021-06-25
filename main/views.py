from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Thread, Comment, ThreadChat, ThreadJoinRequest
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

	button_mode = t.getThreadChat().checkAllow(response.user)
	already_requested = len(ThreadJoinRequest.objects.filter(threadchat=t.getThreadChat(), requester=response.user)) > 0

	if response.method == "POST":
		if response.POST.get("new"):
			txt = response.POST.get("new")
			if len(txt) > 0:
				t.comment_set.create(user=response.user, content=txt)
			else:
				print("error: invalid length")
		elif response.POST.get("gochat"):
			return HttpResponseRedirect("/threadchat/%i" % t.getThreadChat().id)
		elif response.POST.get("requestchat"):
			if len(ThreadJoinRequest.objects.filter(threadchat=t.getThreadChat(), requester=response.user)) > 0:
				print("warning: already requested")
			else:
				t.getThreadChat().threadjoinrequest_set.create(requester=response.user, requestee=t.user)
		else:
			print("error: invalid POST")
		return HttpResponseRedirect("/thread/%i" % id)

	return render(response, "main/index.html",
		{"t":t,
		"button_mode":button_mode,
		"len_list":len(t.getThreadChat().user_list.all()) + 1,
		"requested":already_requested}
		)

@login_required(login_url='/loginprompt/')
def create(response):
	if response.method == "POST":
		form = CreateNewThread(response.POST)

		if form.is_valid():
			print(response.POST)
			t = form.cleaned_data["title"]
			c = form.cleaned_data["content"]
			tg = form.cleaned_data["tags"]

			# Require a check cause redirection function filters using title and content.
			if Thread.objects.filter(title=t, content=c).count() > 0:
				print("error: already exists")
				messages.error(response, 'This post already exists. Please try again with different title/content.')
				return render(response, "main/create.html", {"form":form})

			response.user.thread_set.create(title=t, content=c, tags=tg)
			messages.success(response, 'New post successfully created!')

		return HttpResponseRedirect("/view")

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
	if response.method == "POST":
		form = EditProfileForm(response.POST, instance=response.user.userprofile)
		if form.is_valid():
			m = form.cleaned_data["major"]
			form = form.save(commit=False)
			form.major = form.major
			form.save()
			messages.success(response, 'Your profile has been updated!')
		return HttpResponseRedirect("/profile")
	else:
		form = EditProfileForm(instance=response.user.userprofile)
		return render(response, "main/edit_profile.html", {"form":form})
	return render(response, "main/edit_profile.html", {})

@login_required(login_url='/loginprompt/')
def threadchat(response, id):
	tc = ThreadChat.objects.get(id=id)
	all_tc = list(set(ThreadChat.objects.all()))
	for i in reversed(range(len(all_tc))):
		if not all_tc[i].checkAllow(response.user):
			all_tc.remove(all_tc[i])
	if not tc.checkAllow(response.user):
		messages.error(response, 'This chat is private, send a request to join the group.')
		return HttpResponseRedirect("/thread/%i" % id)
	if response.method == "POST":
		if response.POST.get("new"):
			txt = response.POST.get("new")
			if len(txt) > 0:
				tc.chatpost_set.create(user=response.user, content=txt)
			else:
				print("error: invalid length")
		else:
			print("error: invalid POST")
		return HttpResponseRedirect("/threadchat/%i" % id)

	return render(response, "main/threadchat.html", {"tc":tc, "all_tc":all_tc})

@login_required(login_url='/loginprompt/')
def notifications(response):
	nlist = response.user.notifiable_set.all()

	if response.method == "POST":
		accepted = response.POST.get("accepted") == "true"
		for n in nlist:
			if response.POST.get("notif" + str(n.id)) == "clicked":
				n.action(accepted)
		return HttpResponseRedirect("/notifications")

	return render(response, "main/notifications.html", {"nlist":nlist})

def chatlist(response):
	all_tc = list(set(ThreadChat.objects.all()))
	for i in reversed(range(len(all_tc))):
		if not all_tc[i].checkAllow(response.user):
			all_tc.remove(all_tc[i])
	return render(response, "main/chatlist.html", {"all_tc":all_tc})

def search(response):
	s = response.GET['q']
	tlist = Thread.objects.filter(title__icontains=s) | Thread.objects.filter(content__icontains=s)
	# We could do something like a relevance rank but probably no need for now.
	return render(response, "main/view.html", {"tlist":tlist})
