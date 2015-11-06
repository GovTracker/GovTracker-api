from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, base_name='user')

urlpatterns = [
    url(r'^v1/', include(router.urls, namespace='v1')),
    url(r'^drf/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^auth/login/$', 'rest_framework_jwt.views.obtain_jwt_token', name='obtain_jwt_token'),
    url(r'^auth/refresh/$', 'rest_framework_jwt.views.refresh_jwt_token', name='refresh_jwt_token'),
    url(r'^auth/verify/$', 'rest_framework_jwt.views.verify_jwt_token', name='verify_jwt_token'),
]
