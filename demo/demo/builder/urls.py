# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from demo.builder.views import (
    FormidableListView, FormidableDetailView, FormidableUpdateView,
    FormidableBuilderView, PeopleCreateView, PeopleListView,
)

urlpatterns = patterns(
    r'',
    url(r'^$', FormidableListView.as_view(), name='formidable-list'),
    url(r'^(?P<pk>\d+)/(?P<role>[-_\w]+)/$', FormidableDetailView.as_view(),
        name='formidable-detail'),
    url(r'^edit/(?P<pk>\d+)$', FormidableUpdateView.as_view(),
        name='formidable-edit'),
    url(r'^builder/(?P<pk>\d+)$', FormidableBuilderView.as_view(),
        name='formidable-builder'),
    url(r'^onboarding/', PeopleCreateView.as_view()),
    url(r'^peoples/', PeopleListView.as_view())
)
