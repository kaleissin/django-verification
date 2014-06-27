from __future__ import unicode_literals

from django import forms

__all__ = ['LookupKeyForm']

class LookupKeyForm(forms.Form):
    key = forms.CharField(max_length=255, required=True)
