from django.db import models
 
class chats(models.Model):
 	msg_from = models.CharField(max_length=255)
 	msg_to = models.CharField(max_length=255)
 	msg=models.CharField(max_length=255)

class users(models.Model):
	name=models.CharField(max_length=25)	
	username=models.CharField(max_length=25)
	password=models.CharField(max_length=25)