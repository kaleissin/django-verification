from __future__ import unicode_literals

import logging
_LOG = logging.getLogger(__name__)

from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.base import ContextMixin
from django.views.generic import TemplateView, FormView, View
from django.shortcuts import render, get_object_or_404

from verification.models import Key, KeyGroup, VerificationError
from verification.forms import LookupKeyForm

class KeyLookupMixin(object):
    model = Key
    keygroup = ''

    def get_group_from_string(self, group=''):
        self.group = get_object_or_404(KeyGroup, name=group)
        return self.group

    def get_key_from_string(self, key, group=''):
        group = self.get_group_from_string(group if group else self.keygroup)
        self.key = get_object_or_404(self.model, key=key, group=group)
        return self.key


class ClaimContextMixin(KeyLookupMixin, ContextMixin):
    """Gets key and group from context:
    First checks url, then POST args, then GET args"""

    def get_key_arg(self):
        """Look for the Key in the url, post args or get args.
        No fallback."""
        urlkey = self.kwargs.get('key', '')
        if not urlkey:
            urlkey = self.request.POST.get('key', '')
        if not urlkey:
            urlkey = self.request.GET.get('key', '')
        return urlkey

    def get_group_arg(self):
        """Look for the KeyGroup in the url, post args or get args.
        Falls back to the `keygroup` set on the class."""
        urlgroup = self.kwargs.get('group', '')
        if not urlgroup:
            urlgroup = self.request.POST.get('group', '')
        if not urlgroup:
            urlgroup = self.request.GET.get('group', '')
        if not urlgroup:
            urlgroup = self.keygroup
        return urlgroup

    def get_context_data(self, **kwargs):
        context = super(ClaimContextMixin, self).get_context_data(**kwargs)
        keyarg = self.get_key_arg()
        grouparg = self.get_group_arg()
        key = self.get_key_from_string(key=keyarg, group=grouparg)
        context['key'] = key
        context['group'] = key.group
        return context

class ClaimMixin(KeyLookupMixin):
    success_url = 'verification-success'

    def claim(self, key, group=''):
        key = self.get_key_from_string(key, group)
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

class UrlClaimMixin(ClaimMixin, ClaimContextMixin):
    def _claim(self):
        key = self.get_key_arg()
        group = self.get_group_arg()
        self.claim(key, group)
        url = self.get_success_url()
        return HttpResponseRedirect(url)

class ClaimOnGetMixin(UrlClaimMixin):

    def get(self, request, *args, **kwargs):
        return self._claim()

class ClaimOnPostMixin(UrlClaimMixin):

    def post(self, request, *args, **kwargs):
        return self._claim()

class ClaimOnGetView(ClaimOnGetMixin, View):
    """Claim a key for a logged-in user by visiting a "magic" url"""
    http_method_names = ['get', 'head', 'options', 'trace'] 
claim_get = ClaimOnGetView.as_view()

class ClaimOnPostUrlView(ClaimOnPostMixin, TemplateView):
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    template_name = 'verification/claim_verify.html'
claim_post_url = ClaimOnPostUrlView.as_view()

class AbstractClaimOnPostFormView(UrlClaimMixin, FormView):
    """Inherit and set form_class. Expects "key" and group" as kwargs."""
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    template_name = 'verification/claim_form.html'

    def form_valid(self, form):
        return self._claim()

class AbstractClaimView(ClaimMixin, FormView):
    model = Key
    form_class = LookupKeyForm
    template_name = 'verification/claim_key.html'

    def get_queryset(self):
        """Limit to available Keys of specified KeyGroup"""
        if not self.keygroup:
            raise ImproperlyConfigured("Keygroup not set")
        return self.model._default_manager.available().filter(group=self.keygroup)

    def form_valid(self, form):
        keystring = form.cleaned_data['key']
        self.kwargs = {
            'key': keystring,
            'group': self.keygroup
        }
        key = self.claim(keystring, self.keygroup)
        return HttpResponseRedirect(self.get_success_url())

class ClaimSuccessView(ClaimContextMixin, TemplateView):
    template_name = 'verification/success.html'
    http_method_names = ['get', 'head', 'options', 'trace']
claim_success = ClaimSuccessView.as_view()
