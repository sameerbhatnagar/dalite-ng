from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

class CustomPermissions(ModelBackend):
    """A custom auth backend to validate object-level permissions."""

    def has_perm(self, user_obj, perm, obj=None):
        print('Custom backend:')
        print(self)
        print(user_obj)
        print(perm)
        print(obj)

        # Test if getting called at all...
        return False

        if obj:
            if obj.user == user_obj:
                return super(CustomPermissions, self).has_perm(self, user_obj, perm, obj)
            else:
                raise Exception(PermissionDenied)
                return False
        else:
            return True
