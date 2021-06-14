from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver # for profile
from django.db.models.signals import post_save # for profile

# Create your models here.
class ToDoList(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Item(models.Model):
	todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
	text = models.CharField(max_length=300)
	complete = models.BooleanField()

	def __str__(self):
		return self.text

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

	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			UserProfile.objects.create(user=instance)

	@receiver(post_save, sender=User)
	def save_user_profile(sender, instance, **kwargs):
		instance.userprofile.save()

class Thread(models.Model):
	# threadid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=100, default='', blank=True)
	content = models.CharField(max_length=200, default='', blank=True)

	def checkAllow(user):
		return True

	def __str__(self):
		return self.content

class Comment(models.Model):
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.CharField(max_length=200, default='', blank=True)

	def __str__(self):
		return "Comment: " + self.content

