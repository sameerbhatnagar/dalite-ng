from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

class CustomPermissionsBackend(ModelBackend):
    """A custom auth backend to validate object-level permissions."""

    def has_perm(self, user_obj, perm, obj=None):
        
        if obj:
            if obj.user == user_obj:
                return super(CustomPermissions, self).has_perm(self, user_obj, perm, obj)
            else:
                raise Exception(PermissionDenied)
                return False
        else:
            return super(CustomPermissions, self).has_perm(self, user_obj, perm)
