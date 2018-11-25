# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.db import models, migrations
from django.conf import settings


if django.VERSION[:2] <= (1, 8):

    class Migration(migrations.Migration):

        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ]

        operations = [
            migrations.CreateModel(
                name='Key',
                fields=[
                    ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                    ('key', models.CharField(unique=True, max_length=255)),
                    ('fact', models.TextField(null=True, blank=True)),
                    ('pub_date', models.DateTimeField(auto_now_add=True)),
                    ('expires', models.DateTimeField(null=True, blank=True)),
                    ('claimed', models.DateTimeField(null=True, blank=True)),
                    ('claimed_by', models.ForeignKey(related_name='verification_keys', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ],
                options={
                    'ordering': ('-pub_date',),
                    'abstract': False,
                    'get_latest_by': 'pub_date',
                },
                bases=(models.Model,),
            ),
            migrations.CreateModel(
                name='KeyGroup',
                fields=[
                    ('name', models.SlugField(max_length=32, serialize=False, primary_key=True)),
                    ('ttl', models.IntegerField(null=True, verbose_name='Time to live, in minutes', blank=True)),
                    ('generator', models.CharField(max_length=64)),
                    ('has_fact', models.BooleanField(default=False)),
                ],
                options={
                },
                bases=(models.Model,),
            ),
            migrations.AddField(
                model_name='key',
                name='group',
                field=models.ForeignKey(to='verification.KeyGroup'),
                preserve_default=True,
            ),
        ]

else:

    class Migration(migrations.Migration):

        dependencies = [
            migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ]

        operations = [
            migrations.CreateModel(
                name='Key',
                fields=[
                    ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                    ('key', models.CharField(unique=True, max_length=255)),
                    ('fact', models.TextField(null=True, blank=True)),
                    ('pub_date', models.DateTimeField(auto_now_add=True)),
                    ('expires', models.DateTimeField(null=True, blank=True)),
                    ('claimed', models.DateTimeField(null=True, blank=True)),
                    ('claimed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_keys', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ],
                options={
                    'ordering': ('-pub_date',),
                    'abstract': False,
                    'get_latest_by': 'pub_date',
                },
                bases=(models.Model,),
            ),
            migrations.CreateModel(
                name='KeyGroup',
                fields=[
                    ('name', models.SlugField(max_length=32, serialize=False, primary_key=True)),
                    ('ttl', models.IntegerField(null=True, verbose_name='Time to live, in minutes', blank=True)),
                    ('generator', models.CharField(max_length=64)),
                    ('has_fact', models.BooleanField(default=False)),
                ],
                options={
                },
                bases=(models.Model,),
            ),
            migrations.AddField(
                model_name='key',
                name='group',
                field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='verification.KeyGroup'),
                preserve_default=True,
            ),
        ]

