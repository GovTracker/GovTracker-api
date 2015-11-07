from rest_framework import viewsets, status
from django.contrib.auth import get_user_model
from api import permissions
from api.serializers.user import UserSerializer, UserCreateSerializer

UserModel = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    model = UserModel
    queryset = UserModel.objects.all()
    permission_classes = (permissions.IsAdminOrSelfOrAnon,)
    serializer_class = UserSerializer
    serializer_create_class = UserCreateSerializer

    def dispatch(self, request, *args, **kwargs):
        req = self.initialize_request(request, *args, **kwargs)
        if kwargs.get('pk') == 'current' and req.user.is_authenticated():
            kwargs['pk'] = req.user.pk
        return super(UserViewSet, self).dispatch(request, *args, **kwargs)

    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )
        assert self.serializer_create_class is not None, (
            "'%s' should either include a `serializer_create_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )
        pk = self.kwargs.get('pk')
        try:
            pk = int(pk)
        except Exception:
            pk = None
        if self.request.method == 'POST' and 'POST' in self.allowed_methods and pk is None:
            # Likely a POST against the list view, we will allow for user creation
            return self.serializer_create_class
        else:
            return self.serializer_class

