from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from polymorphic.models import PolymorphicModel
from datetime import datetime
import yake # for keyword extraction

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=50, default='Anonymous', blank=True)
	year = models.CharField(max_length=10, choices=(('Anonymous', 'Anonymous'),
		('1', '1'),('2', '2'), ('3', '3'), ('4', '4')), default='Anonymous')
	view_chronological = models.BooleanField(default=True)

	FACULTY_CHOICES = (
		('Anonymous', 'Anonymous'),
		('Business','Business'),
		('Computing', 'Computing'),
		('Science','Science'),
		('Law','Law'),
		('Wtv','Wtv'),
	)
	faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES, default='Anonymous')
	major = models.CharField(max_length=50, default='Anonymous')

	def __str__(self):
		return self.name + "'s profile"

	# Automatically creates and links when new User instantiated
	@receiver(post_save, sender=User)
	def createUserProfile(sender, instance, created, **kwargs):
		if created:
			UserProfile.objects.create(user=instance)

	@receiver(post_save, sender=User)
	def saveUserProfile(sender, instance, **kwargs):
		instance.userprofile.save()

	def getCorpus(self):
		"""
		Returns all the text from title of content of user's threads
		excluding their profile thread. Meant to be used to calculate
		relevance.
		Uses latest 10 threads in generating corpus.
		"""
		NUM_THREADS = 10
		corpus = ""
		for t in self.user.thread_set.order_by("-created_at")[:min(NUM_THREADS, len(self.user.thread_set.all()))]:
			if not t.isProfileThread():
				corpus += str(t) + " "
		return corpus + self.thread.content

	def getSimValue(self, other):
		value = 0
		if self.year == other.year and self.year != 'Anonymous':
			value += 0.01
		if self.faculty == other.faculty and self.faculty != 'Anonymous':
			value += 0.02
		if self.major == other.major and self.major != 'Anonymous':
			value += 0.05
		return value


class Thread(models.Model):
	LOCATION_CHOICES = (
		('General', 'General'),
		('COM','Computing'),
		('KR MRT', 'KR MRT'),
		('SCI','SCI'),
		('BIZ', 'BIZ'),
		('WTV', 'WTV')
	)

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100, default='', blank=True)
	content = models.CharField(max_length=1000, default='', blank=True)
	location = models.CharField(max_length=30, default='General', choices=LOCATION_CHOICES)
	tags = models.JSONField(default=list, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	viewable = models.BooleanField(default=True)
	is_temp = models.BooleanField(default=False)
	ttl = models.IntegerField(default=0, null=True)

	# If this is not null, then this thread is a profile thread.
	profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True)

	# Keyword extractor for relevance metric
	KW_EXTRACTOR = yake.KeywordExtractor(lan="en", n=1, dedupLim=0.9, top=10, features=None)

	@receiver(post_save, sender=UserProfile)
	def createProfileThread(sender, instance, created, **kwargs):
		if created:
			Thread.objects.create(
				user=instance.user,
				title=str(instance.user) + "'s profile thread",
				profile=instance,
				viewable=False,
				is_temp=False
				)

	@receiver(post_save, sender=UserProfile)
	def saveProfileThread(sender, instance, **kwargs):
		instance.thread.save()

	def isProfileThread(self):
		return self.profile != None

	def getUser(self):
		return self.user

	def getThreadChat(self):
		return self.threadchat

	def __str__(self):
		return self.title + " " + self.content

	def isViewable(self):
		return self.viewable

	class Meta:
		unique_together = (("title", "content"),)

	def getTitle(self):
		return self.title

	@staticmethod
	def getJaccard(a, b):
		"""
		Computes similarity between 2 sets.
		a and b are sets. Use set(mylist).
		"""
		c = a.intersection(b)
		print("Intersection:", c)
		return float(len(c)) / (len(a) + len(b) - len(c))

	# It's possible to cache keywords at the moment the
	# thread is created and update them when it is edited
	# but for a small scale it shouldn't make a difference.
	def getSim(self, other):
		"""
		Compares to another thread.
		Returns 0-1 with 0 being no similarity.
		"""
		a = self.title + ' ' + self.content
		b = other.title + ' ' + other.content
		seta = set(i[0].lower() for i in Thread.KW_EXTRACTOR.extract_keywords(a))
		setb = set(i[0].lower() for i in Thread.KW_EXTRACTOR.extract_keywords(b))
		if len(seta.union(setb)) == 0:
			return 0
		# print(seta, setb)
		return Thread.getJaccard(seta, setb)

	def getSimUser(self, usercorpus):
		"""
		Compares to another user's corpus.
		Returns 0-1 with 0 being no similarity.
		"""
		a = self.title + ' ' + self.content
		b = usercorpus # when you don't know if it's user_corpus or userCorpus
		seta = set(i[0].lower() for i in Thread.KW_EXTRACTOR.extract_keywords(a))
		setb = set(i[0].lower() for i in Thread.KW_EXTRACTOR.extract_keywords(b))
		print("Thread keyword:", seta)
		# print("User keyword:", setb)
		if len(seta.union(setb)) == 0:
			return 0
		# print(seta, setb)
		return Thread.getJaccard(seta, setb)

	def getRelevance(self, user, usercorpus):
		"""
		Returns a generic relevance score for sorting of view page posts.
		usercorpus is left separately and not as a field in user because
		I don't want to waste memory making a copy of text in the
		User/UserProfile class. Intention is to have whatever method
		that calls this calculate the corpus locally and reuse that per
		call to every thread.

		seconds_diff: inverse of the number of seconds since post creation
		"""
		seconds_diff = 1 / (datetime.now() - self.created_at.replace(tzinfo=None)).total_seconds()
		# print("Time diff relevance:", seconds_diff)
		content_sim = 0 if user == self.user else self.getSimUser(usercorpus)
		# no bonus for matching keywords with yourself lol
		# print("Content similarity score:", content_sim)
		user_compat = self.user.userprofile.getSimValue(user.userprofile)
		# print("User compatibility:", user_compat)
		print("Thread relevance:", seconds_diff + content_sim + user_compat, "\n")
		return seconds_diff + content_sim + user_compat

	def checkExpired(self):
		if self.ttl == None:
			return False
		print("Is temp:", self.is_temp, "\n", "Lifetime in seconds:", self.ttl * 86400, "\n", "Time elapsed in seconds:", (datetime.now() - self.created_at.replace(tzinfo=None)).total_seconds())
		return self.is_temp and self.ttl * 86400 <= (datetime.now() - self.created_at.replace(tzinfo=None)).total_seconds()

class Postable(PolymorphicModel):
	"""Abstract class for postable content."""
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.CharField(max_length=200, default='', blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user

class Comment(Postable):
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE)

# Automatically creates and links when new Thread instantiated
class ThreadChat(models.Model):
	thread = models.OneToOneField(Thread, on_delete=models.CASCADE)
	user_list = models.ManyToManyField(User)

	@receiver(post_save, sender=Thread)
	def createThreadChat(sender, instance, created, **kwargs):
		if created:
			ThreadChat.objects.create(thread=instance)
			if not instance.isProfileThread():
				instance.threadchat.addUser(instance.user)

	@receiver(post_save, sender=Thread)
	def saveThreadChat(sender, instance, **kwargs):
		instance.threadchat.save()

	def __str__(self):
		return str(self.thread)

	# Check if requesting user can view the private chat.
	def checkAllow(self, u):
		return u in self.user_list.all() or u == self.thread.getUser()

	# Owner approves user's request to join.
	def addUser(self, u):
		self.user_list.add(u)
		self.save()

	def getThreadTitle(self):
		return self.thread.getTitle()

class ChatPost(Postable):
	threadchat = models.ForeignKey(ThreadChat, on_delete=models.CASCADE)

class PrivateMessageChat(models.Model):
	"""
	To find if there is a pm chat created between users A and B, we need to check
	both cases of user1 = A && user2 = B and user2 = A && user1 = B.

	For instance, we do A.pmuser1_set.filter(user2=B) + A.pmuser2_set.filter(user1=B)
	to find if a chat between A and B exists.
	"""
	user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pmuser1_set")
	user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pmuser2_set")

class PrivateMessagePost(Postable):
	pmchat = models.ForeignKey(PrivateMessageChat, on_delete=models.CASCADE)

class ThreadJoinRequest(models.Model):
	"""Proxy model that represents an add-to-chat request.

	It's possible to skip this step and assign ManyToMany fields in ThreadChat directly
	pointing to Users, but might get troublesome since the ThreadChat owner is hidden
	under ThreadChat.thread.user. Having this would directly create the backwards key
	that we can use (User.requestee_set) to find a user's incoming requests.
	"""
	# The person who requested
	requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requester_set")

	# The owner of the thread
	requestee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requestee_set")
	threadchat = models.ForeignKey(ThreadChat, on_delete=models.CASCADE)

	def addUser(self):
		self.threadchat.addUser(self.requester)

	class Meta:
		unique_together = (("requester", "threadchat"),)

	def __str__(self):
		return str(self.requester) + "-" + str(self.threadchat)

	def getThreadTitle(self):
		return self.threadchat.getThreadTitle()

class Notifiable(PolymorphicModel):
	"""Abstract class for notifications."""
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return str(self.user)

	def action(self, accepted):
	# Override this method
		pass

	def getContent(self):
	# Override this method
		pass

	def getSource(self):
		pass

class ThreadJoinRequestNotification(Notifiable):
	threadjoinrequest = models.OneToOneField(ThreadJoinRequest, on_delete=models.CASCADE)

	# Automatically creates a notif for the requestee when new ThreadJoinRequest instantiated.
	@receiver(post_save, sender=ThreadJoinRequest)
	def createThreadJoinRequestNotification(sender, instance, created, **kwargs):
		if created:
			ThreadJoinRequestNotification.objects.create(user=instance.requestee, threadjoinrequest=instance)

	@receiver(post_save, sender=ThreadJoinRequest)
	def saveThreadJoinRequestNotification(sender, instance, **kwargs):
		instance.threadjoinrequestnotification.save()

	def action(self, accepted):
		if accepted:
			self.threadjoinrequest.addUser()
		self.threadjoinrequest.delete()
		# this will execute CASCADE and this notification gets auto-deleted

	def getSource(self):
		return self.threadjoinrequest.requester

	def getContent(self):
		return "Threadchat Join Request: " + self.threadjoinrequest.getThreadTitle()
