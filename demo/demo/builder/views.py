# -*- coding: utf-8 -*-
from django.http.response import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from formidable.models import Formidable
from django.core.urlresolvers import reverse
from formidable.accesses import get_accesses
from demo.builder.models import People


class FormidableListView(ListView):

    model = Formidable

    def get_context_data(self):
        context = super(FormidableListView, self).get_context_data()
        context['roles'] = get_accesses()
        return context


class FormidableDetailView(DetailView):

    model = Formidable

    def dispatch(self, request, *args, **kwargs):
        request.session['role'] = kwargs['role']
        return super(FormidableDetailView, self).dispatch(
            request, *args, **kwargs
        )


class FormidableUpdateView(UpdateView):

    model = Formidable
    fields = ['label', 'description']

    def get_success_url(self):
        return reverse('builder:formidable-list')


class FormidableBuilderView(DetailView):

    template_name = 'formidable/formidable_builder.html'
    model = Formidable


class PeopleListView(ListView):

    model = People


class PeopleCreateView(CreateView):

    model = People

    def get_form_class(self, *args, **kwargs):
        role_id = self.request.GET.get('access', 'jedi')
        formidable = Formidable.objects.get(label='Jedi')
        return formidable.get_django_form_class(role=role_id)

    def get_form_kwargs(self):
        if self.request.method == 'POST':
            return {'data': self.request.POST}
        return {}

    def form_valid(self, form):
        attrs = [
            ('first_name', 'firstName'),  ('last_name', 'lastName'),
            ('grade', 'radios'), ('birth_date', 'birthDate'),
            ('salary', 'salary'), ('email', 'email')
        ]
        kwargs = {}
        for attr in attrs:
            people_attr, form_attr = attr
            kwargs[people_attr] = form.cleaned_data[form_attr]
        People.objects.create(**kwargs)
        return HttpResponseRedirect('/forms/peoples/')
