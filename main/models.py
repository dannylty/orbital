from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
# from django.contrib.postgres.fields import ArrayField

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=50, default='Anonymous', blank=True)
	year = models.CharField(max_length=10, choices=(('Anonymous', 'Anonymous'),
		('1', '1'),('2', '2'), ('3', '3'), ('4', '4')), default='anon')

	FACULTY_CHOICES = (
		('Anonymous', 'Anonymous'),
		('Business','Business'),
		('Computing', 'Computing'),
	    ('Science','Science'),
	    ('Law','Law'),
	    ('Wtv','Wtv'),
    )
	faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES, default='anon')
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
	TAG_CHOICES = (
		('Chill', 'Chill'),
		('General','General'),
		('Food and Drinks', 'Food and Drinks'),
	    ('Module','Module'),
    )

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100, default='', blank=True)
	content = models.CharField(max_length=200, default='', blank=True)
#	tags = ArrayField(models.CharField(max_length=20, default='', blank=True), default='', blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def checkAllow(self, user):
		return True

	def __str__(self):
		return self.title

class Comment(models.Model):
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.CharField(max_length=200, default='', blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "Comment: " + self.content

# Automatically creates and links when new Thread instantiated
class ThreadChat(models.Model):
	thread = models.OneToOneField(Thread, on_delete=models.CASCADE)
	user_list = models.ManyToManyField(User)

	@receiver(post_save, sender=Thread)
	def createThreadChat(sender, instance, created, **kwargs):
		if created:
			ThreadChat.objects.create(thread=instance)

	@receiver(post_save, sender=Thread)
	def saveThreadChat(sender, instance, **kwargs):
		instance.threadchat.save()

	def __str__(self):
		return str(self.thread)

	# Owner approves user's request to join.
	def addUser(self, u):
		pass

	# User finds thread and requests to join.
	def requestUser(self, u):
		pass
		
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

	def __str_(self):
		return "ThreadJoinRequest: " + self.requester + self.owner

