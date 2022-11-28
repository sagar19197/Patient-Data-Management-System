from django.contrib import admin
from .models import allUsers,Users, Organizations, UploadDocuments, ReceivedDocuments, OTP

# Register your models here.
admin.site.register(allUsers);
admin.site.register(Users);
admin.site.register(Organizations);
admin.site.register(UploadDocuments);
admin.site.register(ReceivedDocuments);
admin.site.register(OTP);
