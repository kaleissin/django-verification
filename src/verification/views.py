from __future__ import unicode_literals

import logging
_LOG = logging.getLogger(__name__)

from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.base import ContextMixin
from django.views.generic import TemplateView, FormView, DetailView, View
from django.shortcuts import render, get_object_or_404

from verification.models import Key, KeyGroup, VerificationError

class ClaimContextMixin(object):
    default_group = ''
    model = Key

    def get_key_arg(self):
        urlkey = self.kwargs.get('key', '')
        if not urlkey:
            urlkey = self.request.POST.get('key', '')
        if not urlkey:
            urlkey = self.request.GET.get('key', '')
        return urlkey

    def get_group_arg(self):
        urlgroup = self.kwargs.get('group', '')
        if not urlgroup:
            urlgroup = self.request.POST.get('group', '')
        if not urlgroup:
            urlgroup = self.request.GET.get('group', '')
        if not urlgroup:
            urlgroup = self.default_group
        return urlgroup

    def get_group(self, group=''):
        self.group = get_object_or_404(KeyGroup, name=group)
        return self.group

    def get_key(self, key, group=''):
        group = self.get_group(group)
        self.key = get_object_or_404(self.model, key=key, group=group)
        return self.key

    def foo(self):
        keyarg = self.get_key_arg()
        grouparg = self.get_group_arg()
        key = self.get_key(key=keyarg, group=grouparg)
        return key

    def get_context_data(self, **kwargs):
        context = super(ClaimContextMixin, self).get_context_data(**kwargs)
        key = self.foo()
        context['key'] = key
        context['group'] = key.group
        return context

class ClaimMixin(ClaimContextMixin, ContextMixin):
    success_url = 'verification-success'

    def claim(self, key, group=''):
        key = self.get_key(key, group if group else self.group)
        group = key.group
        user = self.request.user
        if user.is_authenticated() and user.is_active:
            # Logged in user claims key
            claimant = user
        elif key.claimed_by is not None:
            # Pre-stored user claims key
            claimant = key.claimed_by
        else:
            raise VerificationError('No valid user to claim the key')
        key.claim(claimant)
        self.key = key
        return key

    def get_success_url(self):
        if self.success_url:
            url = reverse(self.success_url, kwargs=self.kwargs)
            return url
        raise ImproperlyConfigured('No URL to redirect to. Provide a success_url.')

    def _claim(self):
        key = self.get_key_arg()
        group = self.get_group_arg()
        self.claim(key, group)
        url = self.get_success_url()
        return HttpResponseRedirect(url)

class ClaimOnGetMixin(object):

    def get(self, request, *args, **kwargs):
        return self._claim()

class ClaimOnPostMixin(object):

    def post(self, request, *args, **kwargs):
        return self._claim()

class ClaimOnGetView(ClaimOnGetMixin, ClaimMixin, View):
    """Claim a key for a logged-in user by visiting a "magic" url"""
    http_method_names = ['get', 'head', 'options', 'trace'] 
claim_get = ClaimOnGetView.as_view()

class ClaimOnPostUrlView(ClaimOnPostMixin, ClaimMixin, TemplateView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    template_name = 'verification/claim_verify.html'
claim_post_url = ClaimOnPostUrlView.as_view()

class AbstractClaimOnPostFormView(ClaimMixin, FormView):
    """Inherit and set form_class. Expects "key" and group" either as kwargs or as fields on the form."""
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    template_name = 'verification/claim_form.html'

    def form_valid(self, form):
        return self._claim()

class ClaimSuccessView(ClaimContextMixin, DetailView):
    template_name = 'verification/success.html'
    http_method_names = ['get', 'head', 'options', 'trace']

    def get_queryset(self):
        self.model.objects.filter
claim_success = ClaimSuccessView.as_view()
