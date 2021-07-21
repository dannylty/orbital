from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Thread, Comment, ThreadChat, ThreadJoinRequest, UserProfile, PrivateMessageChat, PrivateMessagePost
from .forms import CreateNewThread, EditProfileForm, EditThreadForm, EditProfileThreadForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
	if response.GET.get("sortby") == "relevance":
		response.user.userprofile.view_chronological = False
		response.user.save()
	elif response.GET.get("sortby") == "chronological":
		response.user.userprofile.view_chronological = True
		response.user.save()

	tlist = Thread.objects.filter(viewable=True).order_by("-created_at")
	if not response.user.userprofile.view_chronological:

		corpus = response.user.userprofile.getCorpus()
		print(corpus)
		tlist = sorted(tlist, key=lambda x: x.getRelevance(response.user, corpus), reverse=True)
		# print(tlist)

	tdict = {}
	for t in tlist:
		tdict[t] = t.isProfileThread()
	return render(response, "main/view.html", {"tlist":tlist, "tdict":tdict})

@login_required(login_url='/loginprompt')
def profile(response, id):
	if response.method == "POST":
		# wants to send private message
		if response.POST.get("pm"):
			print("received")
			this_user = UserProfile.objects.get(id=id).user

			first_set = response.user.pmuser1_set.filter(user2=this_user)
			second_set = response.user.pmuser2_set.filter(user1=this_user)
			union_set = first_set.union(second_set)

			# checks no current PrivateMessageChat instance between these 2 users
			if len(union_set) == 0:
				PrivateMessageChat.objects.create(user1=response.user, user2=this_user)
				PrivateMessageChat.objects.create(user2=response.user, user1=this_user)
				first_set = response.user.pmuser1_set.filter(user2=this_user)
				second_set = response.user.pmuser2_set.filter(user1=this_user)
				union_set = first_set.union(second_set)

			id1 = response.user.id
			id2 = id

			return HttpResponseRedirect(f"/pmchat/{id1}{id2}")

		else:
			print("Unknown POST")


	this_userprofile = UserProfile.objects.get(id=id)
	is_curr_user = id == response.user.id
	return render(response, "main/profile.html", {"t":response.user.userprofile.thread,
		"this_userprofile":this_userprofile, "is_curr_user":is_curr_user})

@login_required(login_url='/loginprompt')
def pmchat(response, id1, id2):
	user1 = UserProfile.objects.get(id=id1).user
	user2 = UserProfile.objects.get(id=id2).user
	first_set = user1.pmuser1_set.filter(user2=user2)
	second_set = user1.pmuser2_set.filter(user1=user2)
	union_set = first_set.union(second_set)
	all_pm_posts = list(PrivateMessagePost.objects.filter(pmchat=union_set[0])) + list(PrivateMessagePost.objects.filter(pmchat=union_set[1]))
	all_pm_posts = sorted(all_pm_posts, key=lambda x: x.created_at)

	all_tc = response.user.threadchat_set.all()

	if response.method == "POST":
		if response.POST.get("newpm"):
			txt = response.POST.get("newpm")
			if len(txt) > 0:
				first_set[0].privatemessagepost_set.create(user=response.user, content=txt)
			else:
				print("error: invalid length")
		else:
			print("error: invalid POST")
		return HttpResponseRedirect(response.META.get('HTTP_REFERER', '/'))

	if response.user == user1:
		other_user = user2
	elif response.user == user2:
		other_user = user1
	else:
		# return to previous URL
		return HttpResponseRedirect(response.META.get('HTTP_REFERER', '/'))

	return render(response, "main/pmchat.html", {"all_pm_posts":all_pm_posts,
												"other_user": other_user,
												"all_tc":all_tc,
												"all_pm": response.user.pmuser1_set.all()})


@login_required(login_url='/loginprompt')
def editprofile(response):
	if response.method == "POST":
		form = EditProfileForm(response.POST, instance=response.user.userprofile)
		if form.is_valid():
			form = form.save(commit=False)
			form.save()
			messages.success(response, 'Your profile has been updated!')
		return HttpResponseRedirect("/profile/%i" % response.user.userprofile.id)
	else:
		form = EditProfileForm(instance=response.user.userprofile)
		return render(response, "main/edit_profile.html", {"form":form})

@login_required(login_url='/loginprompt')
def threadchat(response, id):
	tc = ThreadChat.objects.get(id=id)
	all_tc = response.user.threadchat_set.all()
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

	if response.method == "POST":
		for n in nlist:
			if response.POST.get("accepted" + str(n.id)) == "true":
				n.action(True)
			elif response.POST.get("declined" + str(n.id)) == "true":
				n.action(False)
		return HttpResponseRedirect("/notifications")

	return render(response, "main/notifications.html", {"nlist":nlist})

@login_required(login_url='/loginprompt')
def chatlist(response):
	user1_list = response.user.pmuser1_set.all()
	user2_list = response.user.pmuser2_set.all()
	all_pm = list(set(user1_list).union(user2_list))

	return render(response, "main/chatlist.html", {"all_tc":response.user.threadchat_set.all(),
													"all_pm":all_pm})

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
