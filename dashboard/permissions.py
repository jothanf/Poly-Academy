from rest_framework import permissions

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'teachermodel')

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'studentmodel') 