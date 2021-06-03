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
	name = models.CharField(max_length=50, blank=True)
	year = models.IntegerField(null=True)
	faculty = models.CharField(max_length=50, blank=True)
	major = models.CharField(max_length=50, blank=True)

	def __str__(self):
		return self.name + "'s profile"

	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			UserProfile.objects.create(user=instance)

	@receiver(post_save, sender=User)
	def save_user_profile(sender, instance, **kwargs):
		instance.userprofile.save()