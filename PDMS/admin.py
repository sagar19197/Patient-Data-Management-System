from django.contrib import admin
from .models import Users, Organizations, UploadDocuments, ReceivedDocuments, Admin

# Register your models here.
admin.site.register(Users);
admin.site.register(Organizations);
admin.site.register(UploadDocuments);
admin.site.register(ReceivedDocuments);
admin.site.register(Admin);
