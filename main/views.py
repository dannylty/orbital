from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Thread, Comment, ThreadChat, ThreadJoinRequest, UserProfile
from .forms import CreateNewThread, EditProfileForm, EditThreadForm, EditProfileThreadForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def home(response):
	return render(response, "main/home.html", {})

@login_required(login_url='/loginprompt')
# Redirects if not logged in. Not a very nice solution.
def index(response, id):
	if Thread.objects.filter(id=id).count() == 0:
		messages.error(response, 'This thread does not exist.')
		return HttpResponseRedirect("/")

	t = Thread.objects.get(id=id)

	if not t.isViewable():
		messages.error(response, 'This thread is private.')
		return HttpResponseRedirect("/")

	button_mode = t.getThreadChat().checkAllow(response.user)
	already_requested = len(ThreadJoinRequest.objects.filter(threadchat=t.getThreadChat(), requester=response.user)) > 0
	is_user = 1 if response.user == t.getUser() else 0

	if response.method == "POST":
		if response.POST.get("gochat"):
			return HttpResponseRedirect("/threadchat/%i" % t.getThreadChat().id)
		elif response.POST.get("requestchat"):
			if len(ThreadJoinRequest.objects.filter(threadchat=t.getThreadChat(), requester=response.user)) > 0:
				print("warning: already requested")
			else:
				t.getThreadChat().threadjoinrequest_set.create(requester=response.user, requestee=t.user)
		elif response.POST.get("new"):
			txt = response.POST.get("new")
			if len(txt) > 0:
				t.comment_set.create(user=response.user, content=txt)
			else:
				print("error: invalid length")
		else:
			print("error: invalid POST")
		return HttpResponseRedirect("/thread/%i" % id)

	return render(response, "main/index.html",
		{"t":t,
		"button_mode":button_mode,
		"len_list":len(t.getThreadChat().user_list.all()) + 1,
		"requested":already_requested,
		"is_user":is_user}
		)

@login_required(login_url='/loginprompt')
def editthread(response, id):
	t = Thread.objects.get(id=id)

	if response.user != t.getUser():
		messages.error(response, 'You are not the owner of this thread.')
		return HttpResponseRedirect("/thread/%i" % id)

	if t.isProfileThread():
		return HttpResponseRedirect("/edit_profile_thread")

	if response.method == "POST":
		form = EditThreadForm(response.POST, instance=t)
		if form.is_valid():
			tt = form.cleaned_data["title"]
			c = form.cleaned_data["content"]

			if Thread.objects.filter(title=tt, content=c).count() > 1:
				print("error: already exists")
				messages.error(response, 'This thread already exists. Please try again with different title/content.')
				return HttpResponseRedirect("#")

			t.title = tt
			t.content = c
			t.location = form.cleaned_data["location"]
			t.tags = form.cleaned_data["tags"]
			t.save()

			messages.success(response, 'The thread has been updated!')
		return HttpResponseRedirect("/thread/%i" % id)

	else:
		form = EditThreadForm(instance=t)
		return render(response, "main/edit_thread.html", {"form":form, "id":id})

@login_required(login_url='/loginprompt')
def deletethread(response, id):
	t = Thread.objects.get(id=id)

	if response.user != t.getUser():
		messages.error(response, 'You are not the owner of this thread.')
		return HttpResponseRedirect("/thread/%i" % id)

	t.delete()
	messages.success(response, 'The thread has been deleted!')
	return HttpResponseRedirect("/")

@login_required(login_url='/loginprompt')
def create(response):
	if response.method == "POST":
		form = CreateNewThread(response.POST)

		if form.is_valid():
#			print(response.POST)
			t = form.cleaned_data["title"]
			c = form.cleaned_data["content"]
			tg = form.cleaned_data["tags"]
			loc = form.cleaned_data["location"]

			# Require a check cause redirection function filters using title and content.
			if Thread.objects.filter(title=t, content=c).count() > 0:
				print("error: already exists")
				messages.error(response, 'This thread already exists. Please try again with different title/content.')
				return render(response, "main/create.html", {"form":form})

			response.user.thread_set.create(title=t, content=c, tags=tg, location=loc)
			messages.success(response, 'New thread successfully created!')

		return HttpResponseRedirect("/thread/%i" % Thread.objects.get(title=t, content=c).id)

	else:
		form = CreateNewThread()
		return render(response, "main/create.html", {"form":form})

@login_required(login_url='/loginprompt')
def view(response):
	tlist = Thread.objects.filter(viewable=True).order_by("-created_at")
	tdict = {}
	for t in tlist:
		tdict[t] = t.isProfileThread()
	return render(response, "main/view.html", {"tlist":tlist, "tdict":tdict})

@login_required(login_url='/loginprompt')
def profile(response, id):
	this_userprofile = UserProfile.objects.get(id=id)
	is_curr_user = id == response.user.id
	return render(response, "main/profile.html", {"t":response.user.userprofile.thread,
		"this_userprofile":this_userprofile, "is_curr_user":is_curr_user})

@login_required(login_url='/loginprompt')
def editprofile(response):
	if response.method == "POST":
		form = EditProfileForm(response.POST, instance=response.user.userprofile)
		if form.is_valid():
			m = form.cleaned_data["major"]
			form = form.save(commit=False)
			form.major = form.major
			form.save()
			messages.success(response, 'Your profile has been updated!')
		return HttpResponseRedirect("/profile/%i" % response.user.userprofile.id)
	else:
		form = EditProfileForm(instance=response.user.userprofile)
		return render(response, "main/edit_profile.html", {"form":form})

@login_required(login_url='/loginprompt')
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

@login_required(login_url='/loginprompt')
def notifications(response):
	nlist = response.user.notifiable_set.all()
	tlist = response.user.thread_set.all()
	ndict = {}

	# Populating ndict with {Thread: ThreadJoinRequestNotification} pairs, then
	# removing threads with no requests
	for t in tlist:
		ndict[t] = None
		for n in nlist:
			if n.threadjoinrequest.threadchat.thread == t:
				if ndict[t] == None:
					ndict[t] = [n]
				else:
					ndict[t].append(n)
		if ndict[t] == None:
			ndict.pop(t, None)

	if response.method == "POST":
		for n in nlist:
			if response.POST.get("accepted" + str(n.id)) == "true":
				n.action(True)
			elif response.POST.get("declined" + str(n.id)) == "true":
				n.action(False)
		return HttpResponseRedirect("/notifications")

	return render(response, "main/notifications.html", {"ndict":ndict})

@login_required(login_url='/loginprompt')
def chatlist(response):
	all_tc = list(set(ThreadChat.objects.all()))
	for i in reversed(range(len(all_tc))):
		if not all_tc[i].checkAllow(response.user):
			all_tc.remove(all_tc[i])
	return render(response, "main/chatlist.html", {"all_tc":all_tc})

@login_required(login_url='/loginprompt')
def search(response):
	s = response.GET['q']
	tlist = Thread.objects.filter(title__icontains=s) |\
	Thread.objects.filter(content__icontains=s) |\
	Thread.objects.filter(tags__icontains=s)
	tlist = tlist.filter(viewable=True).order_by("-created_at")
	tdict = {}
	# We could do something like a relevance rank but probably no need for now.
	for t in tlist:
		tdict[t] = t.isProfileThread()
	return render(response, "main/view.html", {"tlist":tlist, "tdict":tdict})


@login_required(login_url='/loginprompt')
def editprofilethread(response):
	t = response.user.userprofile.thread # What is abstraction barrier.
	if response.method == "POST":
		form = EditProfileThreadForm(response.POST, instance=t)
		if form.is_valid():
			form.save()

			# No need to check for duplicate because we know how to redirect.

			messages.success(response, 'The thread has been updated!')
		return HttpResponseRedirect("/profile/%i" % response.user.userprofile.id)

	else:
		form = EditProfileThreadForm(instance=t)
		return render(response, "main/edit_profile_thread.html", {"form":form})
