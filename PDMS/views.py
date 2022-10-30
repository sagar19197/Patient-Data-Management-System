from django.shortcuts import render
from django.http import HttpResponse

# View for homepage.
def home(response):
	return render(response,"PDMS/HomePage.html");

# View for logging in the user
def loginUser(response):
	return render(response,"PDMS/LoginPage.html");

# View for sign up
def registerUser(response):
	return render(response, "PDMS/SignUpPage.html");