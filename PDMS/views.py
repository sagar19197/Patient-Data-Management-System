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



def registerOrg(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if user.top_category == "admin" or user.status == True:
			return redirect("dashboard");
	elif response.method == "POST":
		resp = response.POST;
		name = resp.get('name');
		username = resp.get('username');
		email = resp.get("email");
		pass1 = resp.get("password1")
		pass2 = resp.get("password2");
		sub_category = resp.get("type");
		poi =  response.FILES["filename"];

		desc = resp.get("desc");
		location = resp.get("location");
		phn = resp.get("phn");
		pic1 = response.FILES['img1'];
		pic2 = response.FILES["img2"];

		#print(name,username,email,pass1,pass2,sub_category,poi,desc,location, phn, pic1,pic2);
		user = User(first_name = name, username= username, email= email);
		user.set_password(pass1);
		user.save();
		user = allUsers(user = user, top_category = 'Organizations', status = False);
		user.save();
		user = Organizations(user = user ,sub_category = sub_category, poi = poi,desc= desc, pic1 = pic1, pic2 = pic2, location = location, contact = phn);
		user.save();
		messages.success(response, "Profile Share Successfully, Now wait for admin to approve !!")
	return redirect("registerUser");


# View for sign up
def registerUser(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if user.top_category == "admin" or user.status == True:
			return redirect("dashboard");
	elif response.method == "POST":
		resp = response.POST;
		name = resp.get('name');
		username = resp.get('username');
		email = resp.get("email");
		pass1 = resp.get("password1")
		pass2 = resp.get("password2");
		sub_category = resp.get("type");
		poi =  response.FILES["filename"];
		#print(name,username,email,pass1,pass2,sub_category,poi);
		user = User(first_name = name, username= username, email= email);
		user.set_password(pass1);
		user.save();
		user = allUsers(user = user, top_category = 'Users', status = False);
		user.save();
		user = Users(user = user ,sub_category = sub_category, poi = poi);
		user.save();
		messages.success(response, "Profile Share Successfully, Now wait for admin to approve!!")
	return render(response, "PDMS/SignUpPage.html");



def editProfile(response,data):
	resp = response.POST;
	user_post = allUsers.objects.get(user = response.user).user;
	user_post.first_name = resp.get('name');
	user_post.email = resp.get('email');

	u11 = allUsers.objects.get(user = response.user);
	if u11.top_category == "Organizations":
		u1 = Organizations.objects.get(user = u11);
		u1.desc = resp.get("desc");
		u1.location = resp.get("location");
		u1.contact = resp.get("contact");

	if response.user.check_password(resp.get('current_pass')):
		if resp.get('new_pass') == resp.get('new_pass_confirm'):
			if len(resp.get('new_pass')) != 0:
				user_post.set_password(resp.get("new_pass"));
			user_post.save();
			if u11.top_category == "Organizations":
				u1.save();
				data["data2"] = u1;
			data["data"] = user_post
			messages.success(response, "Profile Updated successfully !!");
		else:
			messages.error(response, "Invalid credendtials !!");
	else:
		messages.error(response,"Invalid credendtials !!");



#View for dashboad -
def dashboard(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		data = {"data" : allUsers.objects.get(user = response.user).user}
		if user.top_category == "admin":
			if response.method == "POST":
				editProfile(response,data);
			return render(response,"PDMS/AdminDashboard.html",data);

		elif user.status == True:
			if user.top_category == "Users":
				if response.method == "POST":
					editProfile(response,data);
				return render(response,"PDMS/UserDashboard.html",data);

			elif user.top_category == "Organizations":
				s = allUsers.objects.get(user = response.user);
				s = Organizations.objects.get(user = s);
				data["data2"] = s;
				if response.method == "POST":
					editProfile(response,data);
				
				return render(response,"PDMS/OrganizationDashboard.html",data);
				
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


# For showing upload files - 
def ShowUploads(user):
	l = [];
	if user.top_category == "Users":
		user2 = Users.objects.get(user = user);
		if(os.path.exists(user2.poi.path)):
			l.append(user2.poi);
		docs = UploadDocuments.objects.filter(user = user);
		for doc in docs:
			if os.path.exists(doc.documents.path):
				l.append(doc.documents);
			else:
				doc.delete();
	elif user.top_category =="Organizations":
		user2 = Organizations.objects.get(user = user);
		if(os.path.exists(user2.poi.path)):
			l.append(user2.poi);
		if(os.path.exists(user2.poi.path)):
			l.append(user2.pic1);
		if(os.path.exists(user2.poi.path)):
			l.append(user2.pic2);

		docs = UploadDocuments.objects.filter(user = user);
		for doc in docs:
			if os.path.exists(doc.documents.path):
				l.append(doc.documents);
			else:
				doc.delete();

	return l;



def userDeleteUpload(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if user.top_category == "Users":
			if response.method == "POST":
				resp = response.POST;
				path = resp.get('link')

				if(os.path.exists(path)):
					os.remove(path);
				return redirect("viewDocuments");

	return redirect("home");

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
				if response.method == "POST":
					doc = UploadDocuments(user = user, documents = response.FILES["doc"]); 
					doc.save();
				data = { "data1" : ShowUploads(user)};
				return render(response,"PDMS/UserDocuments.html", data);

			elif user.top_category == "Organizations":
				if response.method == "POST":
					doc = UploadDocuments(user = user, documents = response.FILES["doc"]); 
					doc.save();
				data = { "data1" : ShowUploads(user)};
				return render(response,"PDMS/UserDocuments.html", data);
				
	return redirect("home");


# For showing receivied files - 
def ShowReceived(user):
	l = [];
	if user.top_category == "Users":
		user2 = Users.objects.get(user = user);
		docs = ReceivedDocuments.objects.filter(user = user);
		for doc in docs:
			if os.path.exists(doc.documents.path):
				l.append(doc);
			else:
				doc.delete();
	elif user.top_category =="Organizations":
		docs = ReceivedDocuments.objects.filter(user = user);
		for doc in docs:
			if os.path.exists(doc.documents.path):
				l.append(doc);
			else:
				doc.delete();

	return l;


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
				data = { "data1" : ShowReceived(user)};
				return render(response,"PDMS/UserRecievedDocuments.html", data);
			elif user.top_category == "Organizations":
				data = { "data1" : ShowReceived(user)};
				return render(response,"PDMS/UserRecievedDocuments.html", data);
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


def userSendDoc(response):
	if response.user.is_authenticated:
		user = get_object_or_404(allUsers, user = response.user);
		if response.method == "POST":
			resp = response.POST;
			user_action = get_object_or_404(User,username = resp.get("username"));
			user_action = get_object_or_404(allUsers, user = user_action);
			r = ReceivedDocuments(user = user_action, recieved_from_user = user.user.username, documents = resp.get("Documents"));
			r.save();
	return redirect('search');

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
					data["data3"] = ["HealthCareProfessional"]
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
					data["data8"] = ShowUploads(user);
					
					return render(response,"PDMS/PatientSearch.html",data);

				elif sub_user.sub_category == "HealthCareProfessional":
					data["data3"] = ["Patient"]
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
					data["data8"] = ShowUploads(user);
					
					return render(response,"PDMS/PatientSearch.html",data);
			elif user.top_category == "Organizations":
				sub_user = get_object_or_404(Organizations, user = user);
				if sub_user.sub_category == "Hospital":
					data["data3"] = ["Patient"]
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
					data["data8"] = ShowUploads(user);
					
					return render(response,"PDMS/PatientSearch.html",data);
				elif sub_user.sub_category == "Pharmacy":
					data["data3"] = ["Patient"]
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
					data["data8"] = ShowUploads(user);
					
					return render(response,"PDMS/PatientSearch.html",data);
				elif sub_user.sub_category == "Insurance":
					data["data3"] = ["Patient"]
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
					data["data8"] = ShowUploads(user);
					
					return render(response,"PDMS/PatientSearch.html",data);
	return redirect("home");


#View for logout - 
def logoutUser(response):
	if response.user.is_authenticated:
		logout(response);
		return redirect("home");
	return redirect("home");