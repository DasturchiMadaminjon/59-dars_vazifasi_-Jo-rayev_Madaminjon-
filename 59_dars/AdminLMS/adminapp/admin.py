from django.contrib import admin
from .models import Faculty, Teacher, Student, AuditLog
admin.site.register(Faculty)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(AuditLog)

