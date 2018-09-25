# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-26 17:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('OpsManage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_System',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_user', models.SmallIntegerField(verbose_name='\u5de5\u5355\u7533\u8bf7\u4ebaid')),
                ('order_subject', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u5de5\u5355\u7533\u8bf7\u4e3b\u9898')),
                ('order_executor', models.SmallIntegerField(verbose_name='\u5de5\u5355\u5904\u7406\u4ebaid')),
                ('order_status', models.IntegerField(choices=[(1, '\u5df2\u62d2\u7edd'), (2, '\u5ba1\u6838\u4e2d'), (3, '\u5df2\u90e8\u7f72'), (4, '\u5f85\u6388\u6743'), (5, '\u5df2\u6267\u884c'), (6, '\u5df2\u56de\u6eda'), (7, '\u5df2\u64a4\u56de'), (8, '\u5df2\u6388\u6743'), (9, '\u5df2\u5931\u8d25')], default='\u5ba1\u6838\u4e2d', verbose_name='\u5de5\u5355\u72b6\u6001')),
                ('order_level', models.IntegerField(blank=True, choices=[(0, '\u975e\u7d27\u6025'), (1, '\u7d27\u6025')], null=True, verbose_name='\u5de5\u5355\u7d27\u6025\u7a0b\u5ea6')),
                ('order_type', models.IntegerField(choices=[(0, 'SQL\u5ba1\u6838'), (1, '\u4ee3\u7801\u90e8\u7f72'), (2, '\u6587\u4ef6\u4e0a\u4f20'), (3, '\u6587\u4ef6\u4e0b\u8f7d')], verbose_name='\u5de5\u5355\u7c7b\u578b')),
                ('order_cancel', models.TextField(blank=True, null=True, verbose_name='\u53d6\u6d88\u539f\u56e0')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='\u5de5\u5355\u53d1\u5e03\u65f6\u95f4')),
                ('modify_time', models.DateTimeField(auto_now=True, verbose_name='\u5de5\u5355\u6700\u540e\u4fee\u6539\u65f6\u95f4')),
            ],
            options={
                'verbose_name_plural': '\u5de5\u5355\u7cfb\u7edf\u8868',
                'db_table': 'opsmanage_order_system',
                'verbose_name': '\u5de5\u5355\u7cfb\u7edf\u8868',
                'permissions': (('can_read_order_system', '\u8bfb\u53d6\u5de5\u5355\u7cfb\u7edf\u6743\u9650'), ('can_change_order_systemr', '\u66f4\u6539\u5de5\u5355\u7cfb\u7edf\u6743\u9650'), ('can_add_order_system', '\u6dfb\u52a0\u5de5\u5355\u7cfb\u7edf\u6743\u9650'), ('can_delete_order_system', '\u5220\u9664\u5de5\u5355\u7cfb\u7edf\u6743\u9650')),
            },
        ),
        migrations.CreateModel(
            name='Project_Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_content', models.TextField(verbose_name='\u5de5\u5355\u7533\u8bf7\u5185\u5bb9')),
                ('order_branch', models.CharField(blank=True, max_length=50, null=True, verbose_name='\u5206\u652f\u7248\u672c')),
                ('order_comid', models.CharField(blank=True, max_length=100, null=True, verbose_name='\u7248\u672cid')),
                ('order_tag', models.CharField(blank=True, max_length=50, null=True, verbose_name='\u6807\u7b7e')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.Order_System')),
                ('order_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_project', to='OpsManage.Project_Config', verbose_name='\u9879\u76eeid')),
            ],
            options={
                'db_table': 'opsmanage_project_order',
                'verbose_name': '\u4ee3\u7801\u90e8\u7f72\u5de5\u5355\u8868',
                'verbose_name_plural': '\u4ee3\u7801\u90e8\u7f72\u5de5\u5355\u8868',
                'permissions': (('can_read_project_order', '\u8bfb\u53d6\u4ee3\u7801\u90e8\u7f72\u5de5\u5355\u6743\u9650'), ('can_change_project_order', '\u66f4\u6539\u4ee3\u7801\u90e8\u7f72\u5de5\u5355\u6743\u9650'), ('can_add_project_order', '\u6dfb\u52a0\u4ee3\u7801\u90e8\u7f72\u5de5\u5355\u9650'), ('can_delete_project_order', '\u5220\u9664\u4ee3\u7801\u90e8\u7f72\u5de5\u5355\u6743\u9650')),
            },
        ),
        migrations.CreateModel(
            name='SQL_Audit_Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_type', models.CharField(max_length=10, verbose_name='sql\u7c7b\u578b')),
                ('order_sql', models.TextField(blank=True, null=True, verbose_name='\u5f85\u5ba1\u6838SQL\u5185\u5bb9')),
                ('order_file', models.FileField(upload_to='./sql/', verbose_name='sql\u811a\u672c\u8def\u5f84')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='orders.Order_System')),
                ('order_db', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_db', to='OpsManage.DataBase_Server_Config', verbose_name='\u6570\u636e\u5e93id')),
            ],
            options={
                'db_table': 'opsmanage_sql_audit_order',
                'verbose_name': 'SQL\u5ba1\u6838\u5de5\u5355\u8868',
                'verbose_name_plural': 'SQL\u5ba1\u6838\u5de5\u5355\u8868',
                'permissions': (('can_read_sql_audit_order', '\u8bfb\u53d6SQL\u5ba1\u6838\u5de5\u5355\u6743\u9650'), ('can_change_sql_audit_order', '\u66f4\u6539SQL\u5ba1\u6838\u5de5\u5355\u6743\u9650'), ('can_add_sql_audit_order', '\u6dfb\u52a0SQL\u5ba1\u6838\u5de5\u5355\u6743\u9650'), ('can_delete_sql_audit_order', '\u5220\u9664SQL\u5ba1\u6838\u5de5\u5355\u6743\u9650')),
            },
        ),
        migrations.CreateModel(
            name='SQL_Order_Execute_Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(max_length=20)),
                ('errlevel', models.IntegerField(verbose_name='\u9519\u8bef\u4fe1\u606f')),
                ('stagestatus', models.CharField(max_length=40)),
                ('errormessage', models.TextField(blank=True, null=True, verbose_name='\u9519\u8bef\u4fe1\u606f')),
                ('sqltext', models.TextField(blank=True, null=True, verbose_name='SQL\u5185\u5bb9')),
                ('affectrow', models.IntegerField(blank=True, null=True, verbose_name='\u5f71\u54cd\u884c\u6570')),
                ('sequence', models.CharField(db_index=True, max_length=30, verbose_name='\u5e8f\u53f7')),
                ('backup_db', models.CharField(blank=True, max_length=100, null=True, verbose_name='Inception\u5907\u4efd\u670d\u52a1\u5668')),
                ('execute_time', models.CharField(max_length=20, verbose_name='\u8bed\u53e5\u6267\u884c\u65f6\u95f4')),
                ('sqlsha', models.CharField(blank=True, max_length=50, null=True, verbose_name='\u662f\u5426\u542f\u52a8OSC')),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.SQL_Audit_Order', verbose_name='orderid')),
            ],
            options={
                'db_table': 'opsmanage_sql_execute_result',
                'verbose_name': 'SQL\u5de5\u5355\u6267\u884c\u8bb0\u5f55\u8868',
                'verbose_name_plural': 'SQL\u5de5\u5355\u6267\u884c\u8bb0\u5f55\u8868',
            },
        ),
        migrations.AlterUniqueTogether(
            name='order_system',
            unique_together=set([('order_subject', 'order_user', 'order_type')]),
        ),
    ]
