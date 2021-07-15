from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from polymorphic.models import PolymorphicModel
import string

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=50, default='Anonymous', blank=True)
	year = models.CharField(max_length=10, choices=(('Anonymous', 'Anonymous'),
		('1', '1'),('2', '2'), ('3', '3'), ('4', '4')), default='Anonymous')
	# thread: user profile thread

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

	# If this is not null, then this thread is a profile thread.
	profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True)

	@receiver(post_save, sender=UserProfile)
	def createProfileThread(sender, instance, created, **kwargs):
		if created:
			Thread.objects.create(
				user=instance.user,
				title=str(instance.user) + "'s profile thread",
				profile=instance,
				viewable=False
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
		return self.title

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
		return float(len(c)) / (len(a) + len(b) - len(c))

	def getSimilarlityWithOtherThread(self, other):
		seta = set((self.content + ' ' + self.title)
			.translate(str.maketrans('', '', string.punctuation))
			.split(' '))
		setb = set((other.content + ' ' + other.title)
			.translate(str.maketrans('', '', string.punctuation))
			.split(' '))
		if '' in seta:
			seta.remove('')
		if '' in setb:
			setb.remove('')

		print(seta, setb)
		return Thread.getJaccard(seta, setb)

	def getRelevance(self, user):
		
		pass

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

