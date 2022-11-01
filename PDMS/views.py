from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import allUsers, Users, Organizations, UploadDocuments, ReceivedDocuments
import os


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
		data = {"data" : allUsers.objects.get(user = response.user).user}
		if user.top_category == "admin":
			if response.method == "POST":
				resp = response.POST;
				user_post = allUsers.objects.get(user = response.user).user;
				user_post.first_name = resp.get('name');
				user_post.email = resp.get('email');
				if response.user.check_password(resp.get('current_pass')):
					if resp.get('new_pass') == resp.get('new_pass_confirm'):
						if len(resp.get('new_pass')) != 0:
							user_post.set_password(resp.get("new_pass"));
						user_post.save();
						data["data"] = user_post
						messages.success(response, "Profile Updated successfully !!");
					else:
						messages.error(response, "Invalid credendtials !!");
				else:
					messages.error(response,"Invalid credendtials !!");
				
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



# For delete operation- 
def deleteUser(user):
	if user.top_category == "Users":
		user2 = Users.objects.get(user = user);
		os.remove(user2.poi.path);
		docs = UploadDocuments.objects.filter(user = user);
		for doc in docs:
			os.remove(docs.documents.path);
		docs = ReceivedDocuments.objects.filter(user = user);
		for doc in docs:
			os.remove(docs.documents.url);
	elif user.top_category =="Organizations":
		user2 = Organizations.objects.get(user = user);
		os.remove(user2.poi.path);
		os.remove(user2.pic1.path);
		os.remove(user2.pic2.path);
		docs = UploadDocuments.objects.filter(user = user);
		for doc in docs:
			os.remove(docs.documents.path);
		docs = ReceivedDocuments.objects.filter(user = user);
		for doc in docs:
			os.remove(docs.documents.path);

	user.user.delete();
	user.delete();



#View for documents 
def viewDocuments(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		data = {"data1" : Users.objects.all(),
				"data2" : Organizations.objects.all(),
				"data3": ["Patient","HealthCareProfessional"],
				"data4": ["Hospital","Pharmacy", "Insurance"]
		}
		if user.top_category == "admin":
			if response.method == "POST":
				resp = response.POST;
				user_action = get_object_or_404(User,username = resp.get("username"));
				user_action = get_object_or_404(allUsers, user = user_action);
				if resp.get('action') == "Approve":
					user_action.status = True;
					user_action.save();
				else:
					deleteUser(user_action);
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
		data = {"data1" : Users.objects.all(),
				"data2" : Organizations.objects.all(),
				"data3": ["Patient","HealthCareProfessional"],
				"data4": ["Hospital","Pharmacy", "Insurance"]
		}
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



# View for admin delete user - 
def adminDeleteUser(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if user.top_category == "admin":
			if response.method == "POST":
				resp = response.POST;
				user_action = get_object_or_404(User,username = resp.get("username"));
				user_action = get_object_or_404(allUsers, user = user_action);
				deleteUser(user_action);
				return redirect("search");

	return redirect("home");


# View for search documents - 
def search(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		data = {"data1" : Users.objects.all(),
				"data2" : Organizations.objects.all(),
				"data3": ["Patient","HealthCareProfessional"],
				"data4": ["Hospital","Pharmacy", "Insurance"],
				"data5" : [],
				"data6" : False,
				"data7" : ""
		}
		if user.top_category == "admin":
			if response.method == "POST":
				resp = response.POST;
				r1 = resp.get('Users');
				r2 = resp.get('Name');
				data3 = User.objects.filter(first_name__startswith  = r2);
				data5 = [];
				for ob in data3:
					temp = allUsers.objects.filter(user = ob).first();
					if temp != None:
						if(temp.status == True):
							temp2 = "xxx";
							if temp.top_category == "Users":
								temp2 = Users.objects.get(user = temp);
							elif temp.top_category == "Organizations":
								temp2 = Organizations.objects.get(user = temp);

							if temp2!="xxx" and (temp2.sub_category == r1 or r1 =="all"):
								data5.append(temp2);

				data["data5"] = data5;
				data['data6'] = True;
				s = "Showing result for " + r1 +" category";
				if(r2 != ""):
					s+=" with name "+ r2;
				data["data7"] = s;
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