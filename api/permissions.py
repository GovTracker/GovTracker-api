from rest_framework.permissions import IsAdminUser

class IsAdminOrSelfOrAnon(IsAdminUser):
    """
    Allow access to admin users or the user herself/himself.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        elif (request.user and type(obj) == type(request.user) and
              obj == request.user):
            return True
        return False

    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        pk = view.kwargs.get('pk')
        try:
            pk = int(pk)
        except Exception:
            pk = None
        if request.method == 'POST' and 'POST' in view.allowed_methods and pk is None:
            # Likely a POST against the list view, we will allow for user creation
            return True
        else:
            if request.user:
                user = request.user
                if user.is_staff:
                    return True
                elif user.is_authenticated():
                    if pk and pk != user.pk:
                        return False
                    if not pk:
                        # deny access to list
                        return False
                    return True
            else:
                return False
