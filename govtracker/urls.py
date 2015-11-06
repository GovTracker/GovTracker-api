from django.conf.urls import include, url
from django.contrib import admin
from api import urls as apiUrls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(apiUrls))
]
