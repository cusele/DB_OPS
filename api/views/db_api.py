#!/usr/bin/env python  
# _#_ coding:utf-8 _*_
from rest_framework import viewsets,permissions
from api import serializers
from OpsManage.models import *
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from OpsManage.tasks.sql import sendOrderNotice
from orders.models import Order_System
from OpsManage.data.base import MySQLPool
from OpsManage.data.base import Mongos
from OpsManage.data.base import Rediss
from OpsManage.data.base import MyCAT
from django.http import JsonResponse
from OpsManage.utils.logger import logger
from OpsManage.utils import mysql as MySQL

@api_view(['POST' ])
@permission_required('OpsManage.can_add_database_server_config',raise_exception=True)
def db_list(request,format=None):
    """
    List all order, or create a server assets order.
    """     
    if request.method == 'POST':
        serializer = serializers.DataBaseServerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'DELETE'])
@permission_required('OpsManage.can_change_database_server_config',raise_exception=True)
def db_detail(request, id,format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = DataBase_Server_Config.objects.get(id=id)
    except DataBase_Server_Config.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
 
    if request.method == 'PUT':
        serializer = serializers.DataBaseServerSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_database_server_config'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
    
@api_view(['POST' ])
@permission_required('OpsManage.can_add_inception_server_config',raise_exception=True)
def inc_list(request,format=None):
    """
    List all order, or create a server assets order.
    """     
    if request.method == 'POST':
        serializer = serializers.InceptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'DELETE'])
@permission_required('OpsManage.can_change_inception_server_config',raise_exception=True)
def inc_detail(request, id,format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = Inception_Server_Config.objects.get(id=id)
    except Inception_Server_Config.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = serializers.InceptionSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_inception_server_config'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
# @api_view(['PUT', 'DELETE'])
# @permission_required('OpsManage.can_change_order_systemr',raise_exception=True)
# def sql_order_detail(request, id,format=None):
#     """
#     Retrieve, update or delete a server assets instance.
#     """
#     try:
#         snippet = Order_System.objects.get(id=id)
#     except Order_System.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#     if request.method == 'PUT':
#         if int(request.data.get('order_status')) == 4:
#             sendOrderNotice.delay(id,mask='【已取消】')  
#         elif int(request.data.get('order_status')) == 6:
#             sendOrderNotice.delay(id,mask='【已授权】')  
#         serializer = serializers.AuditSqlOrderSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#      
#     elif request.method == 'DELETE':
#         if not request.user.has_perm('OpsManage.can_delete_order_system'):
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)       
    
    
@api_view(['POST' ])
@permission_required('OpsManage.can_add_sql_custom_high_risk_sql',raise_exception=True)
def sql_custom_list(request,format=None):
    """
    List all order, or create a server assets order.
    """     
    if request.method == 'POST':
        serializer = serializers.CustomSQLSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT', 'DELETE'])
@permission_required('OpsManage.can_change_custom_high_risk_sql',raise_exception=True)
def sql_custom_detail(request, id,format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = Custom_High_Risk_SQL.objects.get(id=id)
    except Custom_High_Risk_SQL.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = serializers.CustomSQLSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_custom_high_risk_sql'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
    
@api_view(['PUT', 'DELETE'])
@permission_required('OpsManage.can_change_sql_execute_histroy',raise_exception=True)
def sql_exec_logs(request, id,format=None):
    try:
        snippet = SQL_Execute_Histroy.objects.get(id=id)
    except SQL_Execute_Histroy.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
     
    if request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_sql_execute_histroy'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['POST','GET'])
@permission_required('OpsManage.can_read_database_server_config',raise_exception=True)  
def db_status(request, id,format=None):
    try:
        dbServer = DataBase_Server_Config.objects.get(id=id)
    except DataBase_Server_Config.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)    
    if request.method == 'POST':
        if dbServer.db_type == 'mysql':
            MySQL_STATUS = {}
            MYSQL = MySQLPool(host=dbServer.db_host,port=dbServer.db_port,user=dbServer.db_user,passwd=dbServer.db_passwd,dbName=dbServer.db_name)
            STATUS = MYSQL.getStatus()
            GLOBAL = MYSQL.getGlobalStatus()
            MySQL_STATUS['base'] = STATUS[0] + GLOBAL
            MySQL_STATUS['pxc'] = STATUS[1]
            MySQL_STATUS['master'] = MYSQL.getMasterStatus()
            MySQL_STATUS['slave'] = MYSQL.getSlaveStatus()
            return JsonResponse({"code":200,"msg":"success","data":MySQL_STATUS})
        elif dbServer.db_type == 'Mongodb':
            MySQL_STATUS = {}
            Mongo = Mongos(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user,passwd=dbServer.db_passwd, dbname=dbServer.db_name)
            MySQL_STATUS['base'] = Mongo.getbaseStatus()
            MySQL_STATUS['pxc'] = []
            MySQL_STATUS['master'] = Mongo.getmasterStatus()
            MySQL_STATUS['slave'] = Mongo.getmReplStatus()
            #return MySQL_STATUS
            return JsonResponse({"code": 200, "msg": "success", "data": MySQL_STATUS})
        elif dbServer.db_type == 'Redis':
            MySQL_STATUS = {}
            Redis = Rediss(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user, passwd=dbServer.db_passwd, dbname=dbServer.db_name)
            MySQL_STATUS['base'] = Redis.getbaseStatus()
            MySQL_STATUS['pxc'] = Redis.getClusterStatus()
            MySQL_STATUS['master'] = Redis.getmasterStatus()
            MySQL_STATUS['slave'] = Redis.getmReplStatus()
            return JsonResponse({"code": 200, "msg": "success", "data": MySQL_STATUS})
        elif dbServer.db_type == 'MyCAT':
            MySQL_STATUS = {}
            MYSQL = MyCAT(host=dbServer.db_host,port=dbServer.db_port, user=dbServer.db_user,  passwd=dbServer.db_passwd, dbname=dbServer.db_name)
            MySQL_STATUS['base'] = MYSQL.getVariables()
            MySQL_STATUS['pxc'] = {}
            MySQL_STATUS['master'] = {}
            MySQL_STATUS['slave'] = {}
            return JsonResponse({"code": 200, "msg": "success", "data": MySQL_STATUS})
        elif dbServer.db_type == 'oracle':
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif dbServer.db_type == 'mssql':
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:  return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST','GET'])
@permission_required('OpsManage.can_read_database_server_config',raise_exception=True)  
def db_org(request, id,format=None):
    try:
        dbServer = DataBase_Server_Config.objects.get(id=id)
    except DataBase_Server_Config.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)    
    if request.method == 'POST':
        if dbServer.db_type == 'mysql':
            MYSQL = MySQLPool(host=dbServer.db_host,port=dbServer.db_port,user=dbServer.db_user,passwd=dbServer.db_passwd,dbName=dbServer.db_name)
            STATUS = MYSQL.getStatus()
            pxcServerList = []
            title = dbServer.db_host + dbServer.db_mark
            if dbServer.db_mode == 1:name = '单例模式'
            elif dbServer.db_mode == 2:name = '主从模式'
            else:
                name = 'PXC模式'
                title = dbServer.db_mark
            MYSQLORG = {
                        'name': name,
                        'title': title,
                        'className': 'product-dept', 
                        'children': []
                    } 
            if dbServer.db_mode == 3:
                for ds in STATUS[1]:
                    if ds.get('name') == 'Wsrep_incoming_addresses':pxcServerList = ds.get('value').split(',')
                slaveData = {}
                for ds in MYSQL.getMasterStatus():
                    if ds.get('name') == 'Slave':slaveData[dbServer.db_host+':'+str(dbServer.db_port)] = ds.get('value')
                for s in pxcServerList:
                    data = {}
                    host = s.split(':')[0]
                    port = s.split(':')[1]
                    data['name'] = host
                    data['title'] = port
                    data['children'] = []
                    if slaveData.has_key(s):
                        data['name'] = 'master'
                        data['title'] = host+':'+port
                        count = 1
                        for d in slaveData.get(s):
                            x = {}
                            host = d.split(':')[0]
                            port = d.split(':')[1]
                            x['name'] = 'slave-' + str(count)
                            x['title'] =  host+':'+port
                            count = count + 1
                            data['children'].append(x)
                    MYSQLORG['children'].append(data)
            elif dbServer.db_mode == 2:
                for ds in MYSQL.getMasterStatus():
                    if ds.get('name') == 'Slave':
                        count = 1
                        for s in ds.get('value'):
                            x = {}
                            host = s.split(':')[0]
                            port = s.split(':')[1]
                            x['name'] = '从机-' + str(count)
                            x['title'] =  host
                            count = count + 1
                            MYSQLORG['children'].append(x)
                count = 0
                for m in MYSQL.getSlaveStatus():
                    if m.get('name') == 'Master_Host':
                        MYSQLORG['children'].append({"name": '主机-' + str(count), "title": m.get('value')})
                        count = count + 1
            return JsonResponse({"code":200,"msg":"success","data":MYSQLORG})
        elif dbServer.db_type == 'Mongodb':
            MYSQL = Mongos(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user,passwd=dbServer.db_passwd, dbname=dbServer.db_name)
            STATUS = MYSQL.getmReplStatus()
            title = dbServer.db_host + str(dbServer.db_mark)
            if dbServer.db_mode == 1:
                name = '单例模式'
            elif dbServer.db_mode == 2:
                name = '主从模式'
            else:
                name = '复本集模式'
                title = dbServer.db_mark
            MYSQLORG = {
                'name': name,
                'title': title,
                'className': 'product-dept',
                'children': []
            }
            count = 0
            for m in MYSQL.getmasterStatus(type=2):
                count = 1
                if m['name']=='repl,sources,host':
                    MYSQLORG['children'].append({"name":'Master-' + str(count),"title":m['value']})
                    count = count + 1
            for ds in MYSQL.getmReplStatus(type=2):
                count = 1
                if ds['name']=='repl,replicationProgress,host':
                    MYSQLORG['children'].append({"name":'Slave-' + str(count),"title":ds['value']})
                    count = count + 1
            return JsonResponse({"code": 200, "msg": "success", "data": MYSQLORG})
        elif dbServer.db_type == 'Redis':
            MYSQL = Rediss(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user, passwd=dbServer.db_passwd, dbname=dbServer.db_name)
            STATUS = MYSQL.getmReplStatus()
            title = dbServer.db_host + str(dbServer.db_mark)
            if dbServer.db_mode == 1:
                name = '单例模式'
            elif dbServer.db_mode == 2:
                name = '主从模式'
            else:
                name = '复本集模式'
                title = dbServer.db_mark
            MYSQLORG = {
                'name': name,
                'title': title,
                'className': 'product-dept',
                'children': []
            }
            if dbServer.db_mode == 3:
                master_list={}
                nodes_list = []
                rs = []
                for m in MYSQL.getClusterStatus(type=2):
                    key=m.get("name")
                    values=m.get("value")
                    if values['flags'] == 'master' or values['flags'] =="myself,master" or values['flags']=="master,fail?":master_list[values['node_id']]={"name":"master:"+str(values['slots'][0][0])+"-"+str(values['slots'][0][1]),"title":key,"children":[]}

                    nodes_list.append(m)
                #列出从机
                for key in nodes_list:
                    if key['value']['master_id'] in master_list.keys():master_list[key['value']['master_id']]['children'].append({"name":"slave","title":key['name']})
                #汇总数据
                for key,value in master_list.items():
                    MYSQLORG['children'].append(value)
                #return JsonResponse({"code": 200, "msg": "success", "data": master_list})
            elif dbServer.db_mode == 2:
                count = 0
                for m in MYSQL.getmasterStatus(type=2):
                    if m.get('name') == 'Master_Host':
                        MYSQLORG['children'].append({"name": 'Master-' + str(count), "title": m.get('value')})
                        count = count + 1
                for ds in MYSQL.getmReplStatus(type=2):
                    MYSQLORG['children'].append({"name":ds['name'],"title":ds['value']['ip']})
            return JsonResponse({"code": 200, "msg": "success", "data": MYSQLORG})