from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os

def getDirectory(instance, filename):
	split = os.path.splitext(filename);
	file = "proof" + str(instance.user.doc_counter) +split[1];
	instance.user.doc_counter+=1;
	return f'{instance.user.top_category}/{instance.user.user.username}/proof/{file}';


def getDirectoryUpload(instance, filename):
	file = "doc" + str(instance.user.doc_counter) +".pdf";
	instance.doc_counter+=1;
	return f'{instance.user.top_category}/{instance.user.user.username}/uploads/{file}';


def getDirectoryReceived(instance, filename):
	file = "doc" + instance.user.doc_counter+ ".pdf";
	instance.user.doc_counter+=1;
	return f'{instance.user.top_category}/{instance.user.user.username}/received/{file}';



class allUsers(models.Model):
	user = models.OneToOneField(User, on_delete = models.CASCADE);
	status = models.BooleanField();
	top_category = models.CharField(max_length = 15);
	doc_counter = 1;

	def __str__(self):
		return self.top_category +"-"+ self.user.username;		


class Users(models.Model):
	user = models.OneToOneField(allUsers, on_delete = models.CASCADE);
	sub_category = models.CharField(max_length = 22);
	poi = models.FileField(upload_to = getDirectory, validators = [FileExtensionValidator(['pdf'])], max_length = 250);

	def __str__(self):
		return self.sub_category+"-"+ self.user.user.username;


class Organizations(models.Model):
	user = models.OneToOneField(allUsers, on_delete = models.CASCADE);
	sub_category = models.CharField(max_length = 22);
	desc = models.CharField(max_length = 200);
	pic1 = models.FileField(upload_to = getDirectory, max_length = 250);
	pic2 = models.FileField(upload_to = getDirectory, max_length = 250);
	location = models.CharField(max_length = 50);
	contact = models.CharField(max_length = 12);
	poi = models.FileField(upload_to = getDirectory, validators = [FileExtensionValidator(['pdf'])], max_length = 250);
	
	def __str__(self):
		return self.sub_category+"-"+ self.user.user.username;



class UploadDocuments(models.Model):
	user = models.ForeignKey(allUsers, on_delete = models.CASCADE);
	documents = models.FileField(upload_to = getDirectoryUpload, validators = [FileExtensionValidator(['pdf'])], max_length = 250);
	
	def __str__(self):
		return self.user.user.username;



class ReceivedDocuments(models.Model):
	user = models.ForeignKey(allUsers, on_delete = models.CASCADE);
	recieved_from_user = models.CharField(max_length = 150);
	documents = models.FileField(upload_to = getDirectoryReceived, validators = [FileExtensionValidator(['pdf'])], max_length = 250);
	
	def __str__(self):
		return self.user.user.username;
