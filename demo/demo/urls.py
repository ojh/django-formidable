from django.conf.urls import include, url
from django.contrib import admin

from demo.views import FormPreview

urlpatterns = [
    # Examples:
    # url(r'^$', 'demo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^api/', include('formidable.urls', namespace='formidable')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^preview/(?P<pk>\d+)/', FormPreview.as_view()),
    url(r'^forms/', include('demo.builder.urls', namespace='builder')),
]
