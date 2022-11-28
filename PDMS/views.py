from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import allUsers, Users, Organizations, UploadDocuments, ReceivedDocuments,OTP
import os,random
import requests, json, re
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text, force_str, DjangoUnicodeDecodeError
from .utils import maketoken
from datetime import datetime, timedelta, timezone
from django.core.exceptions import ObjectDoesNotExist

# View for homepage.
def home(response):
	c = { "door" : False };
	if response.user.is_authenticated:
		c['door'] = True;
	return render(response,"PDMS/HomePage.html", c);



# View for logging in the user
def loginUser(response):
	if response.user.is_authenticated:
		return redirect("dashboard");
	elif response.method == "POST":

		resp = response.POST;
		check = True;
		username = resp.get('username');
		pass1 = resp.get('password');
		clientKey = response.POST['g-recaptcha-response']

		if username == None or pass1 == None or clientKey == None:
			check = False;
			messages.error(response, "One or more Fields missing!!");

		elif (bool(re.match("^([a-z0-9_\.\+-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", username))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify email in correct format.");
		
		elif (bool(re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,100}$", pass1))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify password in correct format.");

		if check == True:
			clientKey = response.POST['g-recaptcha-response'];
			secretKey = '6Lf8aTgjAAAAAFg3iIqAs5McLmiXbUWsrmZ8DL9P';
			capthchaData = {
			 'secret' : secretKey,
			 'response' : clientKey
			}
			cap_res = requests.post("https://www.google.com/recaptcha/api/siteverify",data = capthchaData);
			cap_res = json.loads(cap_res.text);
			cap_res = cap_res['success'];
			if cap_res == False:
				check = False;

		if check == False:
			messages.error(response, "ERROR: One or more Field are in invalid format !!");
		else:
			user = authenticate(response, username = username,password = pass1);
			
			if user is not None:
				if allUsers.objects.get(user = user).status == False:
					messages.error(response, "ERROR : Please wait, while Admin approves your login request !!")
				else:


					"""
					o = generateOtp();
					subject='OTP for login to PDMS'
					body="Your OTP for login to PDMS is: "+ o;
					email=user.email
					send_mail(subject,body,settings.EMAIL_HOST_USER,[email],fail_silently=False,)
					try:
						otp = OTP.objects.get(user = user);
						otp.otp = o;
						otp.time = datetime.now(timezone.utc);
						otp.save();
					except ObjectDoesNotExist:
						otp = OTP(user = user, otp = o, time = datetime.now(timezone.utc));
						otp.save();

					response.session['pk']=user.email	
					return redirect("otp");

					"""
					login(response, user);
					return redirect("dashboard");

			else:
				messages.error(response,"ERROR : Invalid credendtials !!")
	return render(response,"PDMS/LoginPage.html");


def generateOtp():
	ans=""
	for i in range(0,6):
		r=random.randint(0,9)
		ans=ans+str(r)
	return ans;


def otp(response):
	if response.user.is_authenticated:
		return redirect("loginUser");
	pk=response.session.get('pk');
	if pk is not None:
		user = User.objects.get(email = pk);
		otp = OTP.objects.get(user = user);
		if response.method == "POST":
			del response.session["pk"];
			code = response.POST.get("code");
			if(code == otp.otp):
				
				if(datetime.now(timezone.utc)-otp.time > timedelta(seconds = 60)):
					messages.error(response, "ERROR : OTP Expired!! Please Login again");
					return redirect("loginUser");
				else:
					login(response, user);
					return redirect("dashboard");
			else:
				messages.error(response, "ERROR : Incorret OTP!! Please Login again");
				return redirect("loginUser");
		return render(response, "PDMS/otp.html");

	else:
		return redirect("loginUser");



def checkFile(file_name , format):
	filename = file_name.name.split('.');
	if(len(filename) <= 1 or (filename[0] == "" and len(filename) == 2)):
		return False;
	file_format = str(filename[-1]).lower();
	if(format == "pdf"):
		if(file_format != "pdf"):
			return False;
	else:
		if(file_format != "jpg" and file_format!="jpeg"):
			return False;

	size = file_name.size/1024;
	if(size==0 or size > 2048):
		return False;
	return True;



def registerOrg(response):
	if response.user.is_authenticated:
		return redirect("dashboard");
	elif response.method == "POST":
		resp = response.POST;

		check = True;
		name = resp.get('name');
		username = resp.get('email');
		email = resp.get("email");
		pass1 = resp.get("password1")
		pass2 = resp.get("password2");
		sub_category = resp.get("type");
		poi =  response.FILES["filename"];

		desc = resp.get("desc");
		location = resp.get("location");
		pic1 = response.FILES['img1'];
		pic2 = response.FILES["img2"];
		clientKey = response.POST['g-recaptcha-response'];

		if name == None or username == None or email == None or pass1 == None or pass2 == None or sub_category==None or poi == None or clientKey == None or pic1 == None or pic2 == None or desc == None or location == None:
			check == False;
			messages.error(response, "One or more Fields missing!!");

		elif (bool(re.match("^[A-Za-z\s]{1,20}$", name))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify name in correct format.");
	
		elif (bool(re.match("^([a-z0-9_\.\+-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", username))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify email in correct format.");
			
		elif (bool(re.match("^([a-z0-9_\.\+-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", email))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify email in correct format.");
		
		elif (bool(re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,100}$", pass1))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify password 1 in correct format.");
		
		elif (bool(re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,100}$", pass2))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify password 2 in correct format.");

		elif pass1 != pass2:
			check = False;
			messages.error(response, "ERROR : Password don't match");

		elif (sub_category!="Hospital" and sub_category!="Pharmacy" and sub_category!="Insurance"):
			check = False;
			messages.error(response, "ERROR : Sent Wrong Priviliges");

		elif (bool(re.match("^[a-zA-Z0-9\s]{1,300}$", desc))) == False:
			check = False;
			messages.error(response, "ERROR : Description in invalid format");

		elif (bool(re.match("^[a-zA-Z\s]{1,20}$", location))) == False:
			check = False;
			messages.error(response, "ERROR : Invalid Location format");

		elif checkFile(poi,"pdf") == False:
			check = False;
			messages.error(response, "ERROR : Please Provide Correct File in Proof of Identity");

		elif checkFile(pic1,"jpg") == False:
			check = False;
			messages.error(response, "ERROR : Please Provide Correct File in Picture 1");

		elif checkFile(pic2,"jpg") == False:
			check = False;
			messages.error(response, "ERROR : Please Provide Correct File in Picture 2");	

		elif User.objects.filter(username = username).exists():
			check = False;
			messages.error(response, "ERROR : Email Already Exist, Please register with some other EMAIL");

		if check == True:
			clientKey = response.POST['g-recaptcha-response'];
			secretKey = '6Lf8aTgjAAAAAFg3iIqAs5McLmiXbUWsrmZ8DL9P';
			capthchaData = {
			 'secret' : secretKey,
			 'response' : clientKey
			}
			cap_res = requests.post("https://www.google.com/recaptcha/api/siteverify",data = capthchaData);
			cap_res = json.loads(cap_res.text);
			cap_res = cap_res['success'];
			if cap_res == False:
				check = False;
				messages.error(response, "CAPTHCHA FAILED !!");

		"""
		print("check = ", check);
		print(name,username,email,pass1,pass2,sub_category,poi,desc,location, pic1,pic2);
		"""
		if check == True:
			user = User(first_name = name, username= username, email= email);
			user.is_active = False;
			user.set_password(pass1);
			user.save();
			user1 = user;
			user = allUsers(user = user, top_category = 'Organizations', status = False);
			user.save();
			user = Organizations(user = user ,sub_category = sub_category, poi = poi,desc= desc, pic1 = pic1, pic2 = pic2, location = location);
			user.save();
			
			currenturl=get_current_site(response)
			subject='Verify your Email for PDMS'
			body=render_to_string('PDMS/activate.html',{
            	'user': user1,
                'domain':currenturl,
                'uid':urlsafe_base64_encode(force_bytes(user1.pk)),
                'token': maketoken.make_token(user1)
            })
			send_mail(subject,body,
				settings.EMAIL_HOST_USER,
				[email],
				fail_silently=False)
			messages.success(response, "Please Verify your Email Address to complete the Registration. CHECK YOUR EMAIL FOR VERIFICATION LINK!!");
			return redirect("loginUser");	
	return render(response, "PDMS/SignUpPageOrg.html");


#View for email activation
def activate_user(request, uidb64, token):
    
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        user = None
    if user!=None and maketoken.check_token(user, token) and user.is_active == False:
        user.is_active = True
        user.save()
        messages.success(request,"Your Account has been verified !!");
        return redirect('loginUser')
    return HttpResponse("<h2>Activation Link Invalid</h2>");


# View for sign up
def registerUser(response):
	if response.user.is_authenticated:
		return redirect("dashboard");
	elif response.method == "POST":
		resp = response.POST;

		check = True;
		name = resp.get('name');
		username = resp.get('email');
		email = resp.get("email");
		pass1 = resp.get("password1")
		pass2 = resp.get("password2");
		sub_category = resp.get("type");
		poi =  response.FILES["filename"];
		clientKey = response.POST['g-recaptcha-response'];

		if name == None or username == None or email == None or pass1 == None or pass2 == None or sub_category==None or poi == None or clientKey == None :
			check == False;
			messages.error(response, "One or more Fields missing!!");

		elif (bool(re.match("^[A-Za-z\s]{1,20}$", name))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify name in correct format.");
	
		elif (bool(re.match("^([a-z0-9_\.\+-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", username))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify Username in correct format.");
			
		elif (bool(re.match("^([a-z0-9_\.\+-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", email))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify email in correct format.");
		
		elif (bool(re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,100}$", pass1))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify password 1 in correct format.");
		
		elif (bool(re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,100}$", pass2))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify  password 2 in correct format.");

		elif pass1 != pass2:
			check = False;
			messages.error(response, "ERROR : Password don't match");

		elif (sub_category!="Patient" and sub_category!="HealthCareProfessional"):
			check = False;
			messages.error(response, "ERROR : Sent Wrong Priviliges");

		elif checkFile(poi,"pdf") == False:
			check = False;
			messages.error(response, "ERROR : Please Provide Correct File in Proof of Identity");

		elif User.objects.filter(username = username).exists():
			check = False;
			messages.error(response, "ERROR : Email Already Exist, Please register with some other EMAIL");

		if check == True:
			clientKey = response.POST['g-recaptcha-response'];
			secretKey = '6Lf8aTgjAAAAAFg3iIqAs5McLmiXbUWsrmZ8DL9P';
			capthchaData = {
			 'secret' : secretKey,
			 'response' : clientKey
			}
			cap_res = requests.post("https://www.google.com/recaptcha/api/siteverify",data = capthchaData);
			cap_res = json.loads(cap_res.text);
			cap_res = cap_res['success'];
			if cap_res == False:
				check = False;
				messages.error(response, "CAPTHCHA FAILED !!");

		"""
		print("check = ", check);
		print(name,username,email,pass1,pass2,sub_category,poi);
		"""
		if check == True:
			user = User(first_name = name, username= username, email= email);
			user.is_active = False;
			user.set_password(pass1);
			user.save();
			user1 = user;
			user = allUsers(user = user, top_category = 'Users', status = False);
			user.save();
			user = Users(user = user ,sub_category = sub_category, poi = poi);
			user.save();
			
			currenturl=get_current_site(response)
			subject='Verify your Email for PDMS'
			body=render_to_string('PDMS/activate.html',{
            	'user': user1,
                'domain':currenturl,
                'uid':urlsafe_base64_encode(force_bytes(user1.pk)),
                'token': maketoken.make_token(user1)
            })
			send_mail(subject,body,
				settings.EMAIL_HOST_USER,
				[email],
				fail_silently=False)
			messages.success(response, "Please Verify your Email Address to complete the Registration. CHECK YOUR EMAIL FOR VERIFICATION LINK!!");
			return redirect("loginUser");	
		
	return render(response, "PDMS/SignUpPage.html");



def registerAdmin(response):
	if response.user.is_authenticated:
		return redirect("dashboard");

	elif response.method == "POST":
		resp = response.POST;

		check = True;
		name = resp.get('name');
		username = resp.get('email');
		email = resp.get("email");
		pass1 = resp.get("password1")
		pass2 = resp.get("password2");
		clientKey = response.POST['g-recaptcha-response'];

		if name == None or username == None or email == None or pass1 == None or pass2 == None or clientKey == None :
			check == False;
			messages.error(response, "One or more Fields missing!!");

		elif (bool(re.match("^[A-Za-z\s]{1,20}$", name))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify name in correct format.");
	
		elif (bool(re.match("^([a-z0-9_\.\+-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", username))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify Username in correct format.");
			
		elif (bool(re.match("^([a-z0-9_\.\+-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", email))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify email in correct format.");
		
		elif (bool(re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,100}$", pass1))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify password 1 in correct format.");
		
		elif (bool(re.match("(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,100}$", pass2))) == False:
			check = False;
			messages.error(response, "ERROR : Please specify  password 2 in correct format.");

		elif pass1 != pass2:
			check = False;
			messages.error(response, "ERROR : Password don't match");

		elif User.objects.filter(username = username).exists():
			check = False;
			messages.error(response, "ERROR : Email Already Exist, Please register with some other EMAIL");

		if check == True:
			clientKey = response.POST['g-recaptcha-response'];
			secretKey = '6Lf8aTgjAAAAAFg3iIqAs5McLmiXbUWsrmZ8DL9P';
			capthchaData = {
			 'secret' : secretKey,
			 'response' : clientKey
			}
			cap_res = requests.post("https://www.google.com/recaptcha/api/siteverify",data = capthchaData);
			cap_res = json.loads(cap_res.text);
			cap_res = cap_res['success'];
			if cap_res == False:
				check = False;
				messages.error(response, "CAPTHCHA FAILED !!");

		"""
		print("check = ", check);
		print(name,username,email,pass1,pass2,sub_category,poi);
		"""
		if check == True:
			user = User(first_name = name, username= username, email= email);
			user.is_active = False;
			user.set_password(pass1);
			user.save();
			user1 = user;
			user = allUsers(user = user, top_category = 'admin', status = False);
			user.save();
			
			currenturl=get_current_site(response)
			subject='Verify your Email for PDMS'
			body=render_to_string('PDMS/activate.html',{
            	'user': user1,
                'domain':currenturl,
                'uid':urlsafe_base64_encode(force_bytes(user1.pk)),
                'token': maketoken.make_token(user1)
            })
			send_mail(subject,body,
				settings.EMAIL_HOST_USER,
				[email],
				fail_silently=False)
			messages.success(response, "Please Verify your Email Address to complete the Registration. CHECK YOUR EMAIL FOR VERIFICATION LINK!!");
			return redirect("loginUser");	


	return render(response, "PDMS/SignUpPageAdmin.html");


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
			messages.error(response, "ERROR : Invalid credendtials !!");
	else:
		messages.error(response,"ERROR : Invalid credendtials !!");



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