# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-26 17:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='\u5206\u7c7b\u540d\u79f0')),
            ],
            options={
                'db_table': 'opsmanage_wiki_category',
                'verbose_name': 'wiki\u5206\u7c7b',
                'verbose_name_plural': 'wiki\u5206\u7c7b',
                'permissions': (('can_read_wiki_category', '\u8bfb\u53d6\u5206\u7c7b\u6743\u9650'), ('can_change_wiki_category', '\u66f4\u6539\u5206\u7c7b\u6743\u9650'), ('can_add_wiki_category', '\u6dfb\u52a0\u5206\u7c7b\u6743\u9650'), ('can_delete_wiki_category', '\u5220\u9664\u5206\u7c7b\u6743\u9650')),
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='\u8bc4\u8bba\u7528\u6237')),
                ('email', models.EmailField(max_length=255, verbose_name='\u90ae\u7bb1')),
                ('url', models.URLField(blank=True, verbose_name='\u6587\u7ae0\u5730\u5740')),
                ('text', models.TextField(verbose_name='\u6587\u7ae0\u7c7b\u5bb9')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='\u8bc4\u8bba\u65f6\u95f4')),
            ],
            options={
                'db_table': 'opsmanage_wiki_comment',
                'verbose_name': 'wiki\u6587\u7ae0\u8bc4\u8bba',
                'verbose_name_plural': 'wiki\u6587\u7ae0\u8bc4\u8bba',
                'permissions': (('can_read_wiki_comment', '\u8bfb\u53d6\u8bc4\u8bba\u6743\u9650'), ('can_change_wiki_comment', '\u66f4\u6539\u8bc4\u8bba\u6743\u9650'), ('can_add_wiki_comment', '\u6dfb\u52a0\u8bc4\u8bba\u6743\u9650'), ('can_delete_wiki_comment', '\u5220\u9664\u8bc4\u8bba\u6743\u9650')),
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=70, unique=True, verbose_name='\u6807\u9898')),
                ('content', models.TextField(verbose_name='\u7c7b\u5bb9')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('modified_time', models.DateTimeField(auto_now_add=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u521b\u5efa\u8005')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.Category', verbose_name='\u5206\u7c7b')),
            ],
            options={
                'db_table': 'opsmanage_wiki_post',
                'verbose_name': 'wiki\u6587\u7ae0',
                'verbose_name_plural': 'wiki\u6587\u7ae0',
                'permissions': (('can_read_wiki_post', '\u8bfb\u53d6\u6587\u7ae0\u6743\u9650'), ('can_change_wiki_post', '\u66f4\u6539\u6587\u7ae0\u6743\u9650'), ('can_add_wiki_post', '\u6dfb\u52a0\u6587\u7ae0\u6743\u9650'), ('can_delete_wiki_post', '\u5220\u9664\u6587\u7ae0\u6743\u9650')),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='\u6807\u7b7e\u7c7b\u578b')),
            ],
            options={
                'db_table': 'opsmanage_wiki_tag',
                'verbose_name': 'wiki\u6807\u7b7e',
                'verbose_name_plural': 'wiki\u6807\u7b7e',
                'permissions': (('can_read_wiki_tag', '\u8bfb\u53d6\u6807\u7b7e\u6743\u9650'), ('can_change_wiki_tag', '\u66f4\u6539\u6807\u7b7e\u6743\u9650'), ('can_add_wiki_tag', '\u6dfb\u52a0\u6807\u7b7e\u6743\u9650'), ('can_delete_wiki_tag', '\u5220\u9664\u6807\u7b7e\u6743\u9650')),
            },
        ),
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, to='wiki.Tag', verbose_name='\u6807\u7b7e'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wiki.Post', verbose_name='\u6587\u7ae0id'),
        ),
    ]
