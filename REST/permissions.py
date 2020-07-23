from rest_framework import permissions


class InOwnerList(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access/edit.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return request.user in obj.owner.all()


class InAssignmentOwnerList(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access/edit.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return request.user in obj.assignment.owner.all()
