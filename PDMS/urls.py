from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginUser, name = "loginUser"),
    path('signup/', views.registerUser, name = "registerUser"),
    path('signupOrg/', views.registerOrg, name = "registerOrg"),
    path('signupAdmin/', views.registerAdmin, name = "registerAdmin"),
    path('dashboard/', views.dashboard, name = "dashboard"),
    path('viewDocuments/', views.viewDocuments, name= "viewDocuments"),
    path('viewRecieved/',views.viewRecieved, name = "viewRecieved"),
    path('search/', views.search, name = "search"),
    path('logout/', views.logoutUser, name = "logoutUser"),
    path('deleteUser/', views.adminDeleteUser, name = "adminDeleteUser"),
    path('deleteUpload/', views.userDeleteUpload, name = "userDeleteUpload"),
    path('sendDoc/', views.userSendDoc, name= "userSendDoc"),
    path('activate/<uidb64>/<token>', views.activate_user, name="activate"),
    path('otp/',views.otp,name="otp")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)