from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import allUsers, Users, Organizations, UploadDocuments, ReceivedDocuments



# View for homepage.
def home(response):
	c = { "door" : False };
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if user.top_category == "admin" or user.status == True:
			c['door'] = True;
	return render(response,"PDMS/HomePage.html", c);



# View for logging in the user
def loginUser(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if user.top_category == "admin" or user.status == True:
			return redirect("dashboard");
		else:
			return redirect("home");
	elif response.method == "POST":
		resp = response.POST;
		user = authenticate(response, username = resp.get('username'),password = resp.get('password'));
		if user is not None:
			login(response,user);
			if allUsers.objects.get(user = response.user).status == True or allUsers.objects.get(user = response.user).top_category == "admin":
				return redirect("dashboard");
			else:
				logout(response);
				messages.error(response, "Please wait, while Admin approves your login request !!")
		else:
			messages.error(response,"Invalid credendtials !!")
	return render(response,"PDMS/LoginPage.html");



# View for sign up
def registerUser(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if user.top_category == "admin" or user.status == True:
			return redirect("dashboard");
		else:
			return redirect("home");
	return render(response, "PDMS/SignUpPage.html");



#View for dashboad -
def dashboard(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		data = {"data" : allUsers.objects.all()}
		if user.top_category == "admin":
			return render(response,"PDMS/AdminDashboard.html",data);
		elif user.status == True:
			if user.top_category == "Users":
				return render(response,"PDMS/UserDashboard.html");
			elif user.top_category == "Organizations":
				sub_user = get_object_or_404(Organizations, user = user);
				if sub_user.sub_category == "Hospital":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Pharmacy":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Insurance":
					return render(response,"PDMS/AdminDashboard.html");
	return redirect("home");



#View for documents 
def viewDocuments(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		data = {"data" : allUsers.objects.all()}
		if user.top_category == "admin":
			return render(response,"PDMS/AdminApprove.html",data);
		elif user.status == True:
			if user.top_category == "Users":
				return render(response,"PDMS/UserDocuments.html");
			elif user.top_category == "Organizations":
				sub_user = get_object_or_404(Organizations, user = user);
				if sub_user.sub_category == "Hospital":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Pharmacy":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Insurance":
					return render(response,"PDMS/AdminDashboard.html");
	return redirect("home");



# View for recieved documents - 
def viewRecieved(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		data = {"data" : allUsers.objects.all()}
		if user.top_category == "admin":
			return render(response,"PDMS/AdminAllUsers.html",data);
		elif user.status == True:
			if user.top_category == "Users":
				return render(response,"PDMS/UserRecievedDocuments.html");
			elif user.top_category == "Organizations":
				sub_user = get_object_or_404(Organizations, user = user);
				if sub_user.sub_category == "Hospital":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Pharmacy":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Insurance":
					return render(response,"PDMS/AdminDashboard.html");
	return redirect("home");



# View for search documents - 
def search(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		data = {"data" : allUsers.objects.all()}
		if user.top_category == "admin":
			return render(response,"PDMS/AdminSearch.html",data);
		elif user.status == True:
			if user.top_category == "Users":
				sub_user = get_object_or_404(Users, user = user);
				if sub_user.sub_category == "Patient":
					return render(response,"PDMS/PatientSearch.html");
				elif sub_category == "HealthCareProfessional":
					return render(response,"PDMS/AdminDashboard.html");
			elif user.top_category == "Organizations":
				sub_user = get_object_or_404(Organizations, user = user);
				if sub_user.sub_category == "Hospital":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Pharmacy":
					return render(response,"PDMS/AdminDashboard.html");
				elif sub_user.sub_category == "Insurance":
					return render(response,"PDMS/AdminDashboard.html");
	return redirect("home");


#View for logout - 
def logoutUser(response):
	if response.user.is_authenticated:
		logout(response);
		return redirect("home");
	return redirect("home");