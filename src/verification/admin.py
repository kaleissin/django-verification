from __future__ import unicode_literals

from django.contrib import admin

from .models import Key, KeyGroup

class KeyAdmin(admin.ModelAdmin):
    model = Key
    list_display = ('key', 'group', 'pub_date', 'claimed_by', 'expires')
    list_filter = ('group', 'claimed_by')
    date_hierarchy = 'pub_date'

class KeyGroupAdmin(admin.ModelAdmin):
    model = KeyGroup
    list_display = ('name', 'ttl', 'has_fact')
    list_filter = ('has_fact',)

admin.site.register(Key, KeyAdmin)
admin.site.register(KeyGroup, KeyGroupAdmin)
