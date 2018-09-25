#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
import json,re,csv,os,datetime,time
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import User,Group
from django.db.models import Q 
from django.db import connection
from django.contrib.auth.decorators import login_required
from OpsManage.models import (DataBase_Server_Config,Inception_Server_Config,
                              Custom_High_Risk_SQL,SQL_Audit_Control,
                              Service_Assets,Server_Assets,SQL_Execute_Histroy,
                              Project_Assets,Monitor_mysql)
from orders.models import Order_System,SQL_Audit_Order,SQL_Order_Execute_Result
from OpsManage.tasks.sql import sendOrderNotice,recordSQL
from django.contrib.auth.decorators import permission_required
from OpsManage.utils.inception import Inception
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from OpsManage.data.base import MySQLPool,MyCAT,Mongos,Rediss
from OpsManage.utils.binlog2sql import Binlog2sql
from OpsManage.utils import base,mysql
from django.http import StreamingHttpResponse,HttpResponse
from OpsManage.utils.logger import logger
from collections import Counter
def getBaseAssets():
    try:
        groupList = Group.objects.all()
    except:
        groupList = []
    try:
        serviceList = Service_Assets.objects.all()
    except:
        serviceList = []
    try:
        zoneList = Zone_Assets.objects.all()
    except:
        zoneList = []
    try:
        projectList = Project_Assets.objects.all()
    except:
        projectList = []
    try:
        monitor_column={
            'redis':{
                    "uptime_in_seconds":"启动时间",
                    "uptime_in_seconds_UP":"启动时间",
                    "aof_base_size":"aof上次启动或rewrite的大小",
                    "aof_base_size_UP":"aof上次启动或rewrite的大小",
                    "aof_current_size":"aof当前大小",
                    "aof_current_size_UP":"aof当前大小",
                    "aof_delayed_fsync":"延迟的fsync计数器 TODO",
                    "aof_delayed_fsync_UP":"延迟的fsync计数器 TODO",
                    "aof_pending_bio_fsync":"后台IO队列中等待fsync任务的个数",
                    "avg_ttl":"平均过期时间",
                    "blocked_clients":"正在等待阻塞命令",
                    "connected_clients":"连接的客户端数量",
                    "connected_slaves":"连接从机数量",
                    "connected_slaves_UP":"连接从机数量",
                    "evicted_keys":"删除过的key的数量",
                    "evicted_keys_UP":"删除过的key的数量",
                    "expired_keys":"过期的key的总数",
                    "expired_keys_UP":"过期的key的总数",
                    "expires":"过期KEY个数",
                    "instantaneous_input_kbps":"网络实时进口速率",
                    "instantaneous_ops_per_sec":"每秒执行的命令个数",
                    "instantaneous_output_kbps":"网络实时出口速率",
                    "keyss":"KEY个数",
                    "keyspace_hits":"命中key 的次数",
                    "keyspace_hits_UP":"命中key 的次数",
                    "keyspace_misses":"没命中key 的次数",
                    "keyspace_misses_UP":"没命中key 的次数",
                    "keyss_UP":"KEY个数",
                    "latest_fork_usec":"上次的fork操作使用的时间(单位ms)",
                    "master_repl_offset":"数据同步偏移量",
                    "master_repl_offset_UP":"数据同步偏移量",
                    "rejected_connections":"拒绝连接的个数",
                    "rejected_connections_UP":"拒绝连接的个数",
                    "repl_backlog_size":"后台日志大小",
                    "repl_backlog_size_UP":"后台日志大小",
                    "sync_full":"完全同步次数",
                    "sync_full_UP":"完全同步次数",
                    "sync_partial_err":"部分同步失败数",
                    "sync_partial_err_UP":"部分同步失败数",
                    "sync_partial_ok":"部分同步成功数",
                    "sync_partial_ok_UP":"部分同步成功数",
                    "total_commands_processed":"运行以来执行过的命令的总数量",
                    "total_commands_processed_UP":"运行以来执行过的命令的总数量",
                    "total_connections_received":"运行以来连接过的客户端的总数量",
                    "total_connections_received_UP":"运行以来连接过的客户端的总数量",
                    "total_net_input_bytes":"总输入网络流量",
                    "total_net_input_bytes_UP":"总输入网络流量",
                    "total_net_output_bytes":"总输出网络流量",
                    "total_net_output_bytes_UP":"总输出网络流量",
                    "used_cpu_sys":"系统cpu使用量",
                    "used_cpu_sys_children":"后台进程的sys cpu使用率",
                    "used_cpu_sys_children_UP":"后台进程的sys cpu使用率",
                    "used_cpu_sys_UP":"系统cpu使用量",
                    "used_cpu_user":"用户cpu使用量",
                    "used_cpu_user_children":"后台进程的user cpu使用率",
                    "used_cpu_user_UP":"用户cpu使用量",
                    "used_memory":"分配的内存总量",
                    "used_memory_lua":"Lua引擎所使用的内存大小",
                    "used_memory_peak":"使用的物理内存峰值",
                    "used_memory_rss":"分配的内存总量(包括内存碎片)",
                    "is_master":"是否主机 0 不是 1 是",
                    "master_status":"主机连接状态 1 正常 2 异常"
                    },
            'mysql':{
                    "Aborted_clients":"由于客户端没有正确关闭连接导致客户端终止而中断的连接数。",
                    "Aborted_clients_UP":"Aborted_clients 的增理字段 ",
                    "Aborted_connects":"试图连接到MySQL服务器而失败的连接数。",
                    "Aborted_connects_UP":"Aborted_connects 的增理字段 ",
                    "Binlog_cache_disk_use":"使用临时文件日志数",
                    "Binlog_cache_disk_use_UP":"Binlog_cache_disk_use 的增理字段 ",
                    "Binlog_cache_use":"使用临时二进制日志缓存的事务数量。",
                    "Binlog_cache_use_UP":"Binlog_cache_use 的增理字段 ",
                    "Bytes_received":"接收字节数",
                    "Bytes_received_UP":"接收字节数增量",
                    "Bytes_sent":"发送字节数",
                    "Bytes_sent_UP":"发送字节数增量",
                    "Connections":"试图连接到(不管是否成功)MySQL服务器的连接数。",
                    "Connections_UP":"Connections 的增理字段 ",
                    "Created_tmp_disk_tables":"服务器执行语句时在硬盘上自动创建的临时表的数量",
                    "Created_tmp_disk_tables_UP":"Created_tmp_disk_tables  的增理字段 ",
                    "Created_tmp_files":"mysqld已经创建的临时文件的数量",
                    "Created_tmp_files_UP":"Created_tmp_files 的增理字段 ",
                    "Created_tmp_tables":"服务器执行语句时自动创建的内存中的临时表的数量",
                    "Created_tmp_tables_UP":"Created_tmp_tables 的增理字段 ",
                    "Innodb_buffer_pool_bytes_data":"包含数据的字节数(脏或干净)",
                    "Innodb_buffer_pool_bytes_dirty":"当前的脏页数(字节)",
                    "Innodb_buffer_pool_pages_flushed":"要求清空的缓冲池页数",
                    "Innodb_buffer_pool_pages_flushed_UP":"要求清空的缓冲池页数",
                    "Innodb_buffer_pool_pages_free":"空页数",
                    "Innodb_buffer_pool_pages_misc":"忙的页数",
                    "Innodb_buffer_pool_pages_total":"缓冲池总大小(页数)",
                    "innodb_buffer_pool_reads":"不能满足INNODB必须单页读取的缓冲池中的逻辑读数量",
                    "innodb_buffer_pool_reads_UP":"innodb_buffer_pool_reads   的增理字段 ",
                    "innodb_buffer_pool_read_ahead":"后台预读线程读取到INNODB缓冲池的页由于未被查询使用而驱逐的数量",
                    "innodb_buffer_pool_read_requests":"已经完成逻辑读请求数",
                    "innodb_buffer_pool_read_requests_UP":"innodb_buffer_pool_read_requests 的增理字段 ",
                    "Innodb_buffer_pool_wait_free":"等待页面清空页数",
                    "Innodb_buffer_pool_wait_free_UP":"Innodb_buffer_pool_wait_free  的增理字段 ",
                    "Innodb_buffer_pool_write_requests":"向INNODB缓冲池的写数量",
                    "Innodb_buffer_pool_write_requests_UP":"Innodb_buffer_pool_write_requests  的增理字段 ",
                    "Innodb_data_fsyncs":"fsync()操作数。",
                    "Innodb_data_fsyncs_UP":"Innodb_data_fsyncs  的增理字段 ",
                    "innodb_data_read":"至此已经读取的数据数量(字节)",
                    "innodb_data_reads":"数据读总数量",
                    "innodb_data_reads_UP":"innodb_data_reads 的增理字段 ",
                    "innodb_data_read_UP":"innodb_data_read 的增理字段 ",
                    "Innodb_data_writes":"数据写总数量。",
                    "Innodb_data_writes_UP":"Innodb_data_writes  的增理字段 ",
                    "Innodb_data_written":"至此已经写入的数据量(字节)",
                    "Innodb_data_written_UP":"Innodb_data_written  的增理字段 ",
                    "Innodb_dblwr_pages_written":"双写操作执行的页的数量。",
                    "Innodb_dblwr_pages_written_UP":"Innodb_dblwr_pages_written  的增理字段 ",
                    "Innodb_dblwr_writes":"已经执行的双写操作的数量",
                    "Innodb_dblwr_writes_UP":"Innodb_dblwr_writes  的增理字段 ",
                    "Innodb_log_writes":"向日志文件的物理写数量",
                    "Innodb_log_writes_UP":"Innodb_log_writes  的增理字段 ",
                    "Innodb_log_write_requests":"日志写请求数。",
                    "Innodb_log_write_requests_UP":"Innodb_log_write_requests 的增理字段 ",
                    "Innodb_os_log_fsyncs":"向日志文件完成的fsync()写数量",
                    "Innodb_os_log_fsyncs_UP":"Innodb_os_log_fsyncs 的增理字段 ",
                    "Innodb_os_log_written":"写入日志文件的字节数",
                    "Innodb_os_log_written_UP":"Innodb_os_log_written 的增理字段 ",
                    "Innodb_pages_created":"创建的页数。",
                    "Innodb_pages_created_UP":"Innodb_pages_created 的增理字段 ",
                    "Innodb_pages_read":"读取的页数。",
                    "Innodb_pages_read_UP":"Innodb_pages_read 的增理字段 ",
                    "Innodb_pages_written":"写入的页数。",
                    "Innodb_pages_written_UP":"Innodb_pages_written 的增理字段 ",
                    "Innodb_page_size":"编译的INNODB页大小(默认16KB)",
                    "Innodb_rows_deleted":"从INNODB表删除的行数",
                    "Innodb_rows_deleted_UP":"Innodb_rows_deleted 的增理字段 ",
                    "Innodb_rows_inserted":"插入到INNODB表的行数",
                    "Innodb_rows_inserted_UP":"Innodb_rows_inserted 的增理字段 ",
                    "Innodb_rows_read":"从INNODB表读取的行数",
                    "Innodb_rows_read_UP":"Innodb_rows_read 的增理字段 ",
                    "Innodb_rows_updated":"INNODB表内更新的行数",
                    "Innodb_rows_updated_UP":"Innodb_rows_updated 的增理字段 ",
                    "Innodb_row_lock_current_waits":"当前等待的待锁定的行数",
                    "Innodb_row_lock_current_waits_UP":"Innodb_row_lock_current_waits 的增理字段 ",
                    "Innodb_row_lock_time":"行锁定花费的总时间，单位毫秒。",
                    "Innodb_row_lock_time_UP":"Innodb_row_lock_time 的增理字段 ",
                    "Innodb_row_lock_waits":"一行锁定必须等待的时间数",
                    "Key_blocks_unused":"键缓存内未使用的块数量。你可以使用该值来确定使用了多少键缓存；",
                    "Key_blocks_used":"键缓存内使用的块数量。该值为高水平线标记，说明已经同时最多使用了多少块",
                    "Key_reads":"从硬盘读取键的数据块的次数。如果Key_reads较大，则Key_buffer_size值可能太小。可以用Key_reads/Key_read_requests计算缓存损失率",
                    "Key_reads_UP":"Key_reads 的增理字段 ",
                    "Key_read_requests":"从缓存读键的数据块的请求数",
                    "Key_read_requests_UP":"Key_read_requests 的增理字段 ",
                    "Key_writes":"向硬盘写入将键的数据块的物理写操作的次数",
                    "Key_writes_UP":"Key_writes 的增理字段 ",
                    "Key_write_requests":"将键的数据块写入缓存的请求数",
                    "Key_write_requests_UP":"Key_write_requests 的增理字段 ",
                    "Max_used_connections":"服务器启动后已经同时使用的连接的最大数量。",
                    "Max_used_connections_UP":"Max_used_connections 的增理字段 ",
                    "Opened_files":"已经打开的表的数量。如果Opened_tables较大，table_cache 值可能太小",
                    "Opened_files_UP":"Opened_files 的增理字段 ",
                    "Opened_tables":"当前已经打开表的数量",
                    "Opened_tables_UP":"当前已经打开表的数量增量",
                    "Open_files":"打开的文件的数目",
                    "Open_tables":"当前打开的表的数量",
                    "Qcache_hits":"查询缓存被访问的次数",
                    "Qcache_hits_UP":"Qcache_hits 的增理字段 ",
                    "Qcache_inserts":"加入到缓存的查询数量",
                    "Qcache_inserts_UP":"Qcache_inserts 的增理字段 ",
                    "Qcache_not_cached":"非缓存查询数(不可缓存，或由于QUERY_CACHE_TYPE设定值未缓存)。",
                    "Qcache_not_cached_UP":"Qcache_not_cached 的增理字段 ",
                    "Qcache_queries_in_cache":"登记到缓存内的查询的数量",
                    "Qcache_queries_in_cache_UP":"Qcache_queries_in_cache 的增理字段 ",
                    "Qcache_total_blocks":"查询缓存内的总块数",
                    "Queries":"已经发送给服务器的命令的个数",
                    "Queries_UP":"Queries 的增理字段 ",
                    "Questions":"已经发送给服务器的查询的个数。QUESTIONS",
                    "Questions_UP":"Questions 的增理字段 ",
                    "Select_full_join":"没有使用索引的联接的数量。如果该值不为0,你应仔细检查表的索引。",
                    "Select_full_join_UP":"Select_full_join 的增理字段 ",
                    "Select_full_range_join":"在引用的表中使用范围搜索的联接的数量。",
                    "Select_full_range_join_UP":"Select_full_range_join 的增理字段 ",
                    "Select_scan":"对第一个表进行完全扫描的联接的数量。",
                    "Select_scan_UP":"Select_scan 的增理字段 ",
                    "Slow_queries":"查询时间超过long_query_time秒的查询的个数",
                    "Slow_queries_UP":"Slow_queries 的增理字段 ",
                    "Sort_merge_passes":"排序算法已经执行的合并的数量。如果这个变量值较大，应考虑增加sort_buffer_size系统变量的值",
                    "Sort_merge_passes_UP":"Sort_merge_passes  的增理字段 ",
                    "Sort_range":"在范围内执行的排序的数量。",
                    "Sort_range_UP":"Sort_range 的增理字段 ",
                    "Sort_rows":"已经排序的行数。",
                    "Sort_rows_UP":"Sort_rows 的增理字段 ",
                    "Sort_scan":"通过扫描表完成的排序的数量。",
                    "Sort_scan_UP":"Sort_scan 的增理字段 ",
                    "Table_locks_immediate":"立即获得的表的锁的次数",
                    "Table_locks_immediate_UP":"Table_locks_immediate 的增理字段 ",
                    "Table_locks_waited":"不能立即获得的表的锁的次数。如果该值较高，并且有性能问题，你应首先优化查询，然后拆分表或使用复制",
                    "Table_locks_waited_UP":"Table_locks_waited 的增理字段 ",
                    "Table_open_cache_hits":"命中的table_open_cache",
                    "Table_open_cache_hits_UP":"Table_open_cache_hits 的增理字段 ",
                    "Table_open_cache_misses":"没有命中的数",
                    "Table_open_cache_misses_UP":"Table_open_cache_misses 的增理字段 ",
                    "Threads_cached":"线程缓存内的线程的数量",
                    "Threads_connected":"当前打开的连接的数量",
                    "Threads_created":"创建用来处理连接的线程数。如果Threads_created较大，你可能要增加thread_cache_size值。缓存访问率的计算方法Threads_created/Connections。",
                    "Threads_created_UP":"Threads_created 的增理字段 ",
                    "Threads_running":"激活的(非睡眠状态)线程数。",
                    "Uptime":"服务器已经运行的时间(以秒为单位)",
                    "Uptime_UP":"Uptime 的增理字段 ",
                    "Com_commit":"提交次数",
                    "Com_commit_UP":"提交增长",
                    "Com_rollback":"回滚次数",
                    "Com_rollback_UP":"回滚增长",
                    "iorun":"复制IO进程状态 1正常 2异常",
                    "sqlrun":"复制SQL进程状态 1正常 2异常",
                    "sendtime":"延迟时间 ",
                    "slog":"复制SQL日志"
                    },
            "mongodb":{
                        "connections_available":"剩余多少可供连接",
                        "connections_current":"活动状态的连接数",
                        "connections_totalCreated":"总连接数",
                        "connections_totalCreated_UP":"总连接数的增长",
                        "locks_Database_acquireCount_r":"库读锁次数",
                        "locks_Database_acquireCount_r_UP":"库读锁次数的增长",
                        "locks_Database_acquireCount_w":"库写锁次数",
                        "locks_Database_acquireCount_w_UP":"库写锁次数的增长",
                        "locks_Database_acquireWaitCount_r":"库等代读锁次数",
                        "locks_Database_acquireWaitCount_r_UP":"库等代读锁次数的增长",
                        "locks_Database_acquireWaitCount_w":"库等代写锁次数",
                        "locks_Database_acquireWaitCount_w_UP":"库等代写锁次数的增长",
                        "mem_resident":"物理内存消耗单位M",
                        "mem_virtual":"虚拟内存消耗单位M",
                        "metrics_commands_authenticate_failed":"认证失败次数",
                        "metrics_commands_authenticate_failed_UP":"认证失败次数的增长",
                        "network_bytesIn":"网络接收字节数",
                        "network_bytesIn_UP":"网络接收字节数的增长",
                        "network_bytesOut":"活动状态的连接数",
                        "network_bytesOut_UP":"活动状态的连接数的增长",
                        "network_numRequests":"网络请求数",
                        "network_numRequests_UP":"网络请求数的增长",
                        "opcounters_command":"启动后其他操作的次数",
                        "opcounters_command_UP":"启动后其他操作的次数的增长",
                        "opcounters_delete":"启动后总删除数",
                        "opcounters_delete_UP":"启动后总删除数的增长",
                        "opcounters_getmore":"启动后执行getMore次数",
                        "opcounters_getmore_UP":"启动后执行getMore次数的增长",
                        "opcounters_insert":"启动后总插入数",
                        "opcounters_insert_UP":"启动后总插入数的增长",
                        "opcounters_query":"启动后总查询数",
                        "opcounters_query_UP":"启动后总查询数的增长",
                        "opcounters_update":"启动后总更新数",
                        "opcounters_update_UP":"启动后总更新数的增长",
                        "tcmalloc_generic_current_allocated_bytes":"已经分配过的字节数",
                        "tcmalloc_tcmalloc_pageheap_free_bytes":"空闲页面字节数",
                        "tcmalloc_tcmalloc_pageheap_unmapped_bytes":"未分配页面字节数",
                        "wiredTiger_connection_totalreadIOs":"总读IO次数",
                        "wiredTiger_connection_totalreadIOs_UP":"总读IO次数的增长",
                        "wiredTiger_connection_totalwriteIOs":"总写IO次数",
                        "wiredTiger_connection_totalwriteIOs_UP":"总写IO次数的增长",
                        "wiredTiger_transaction_transaction_checkpoints":"事务检查点",
                        "wiredTiger_transaction_transaction_checkpoints_UP":"事务检查点的增长",
                        "uptime":"运行时间",
                        "uptime_UP":"运行时间的增长",
                        "syncedTotime":"主从延迟"},
            "mycat":{
                    "UPTIME_UP":"启动时间",
                    "ACTIVE_COUNT":"线程积压",
                    "BC_COUNT":"BC统计",
                    "BC_COUNT_UP":"BC统计",
                    "BU_PERCENT":"缓存使用率",
                    "BU_WARNS":"临时创建新的BUFFER的次数",
                    "BU_WARNS_UP":"临时创建新的BUFFER的次数",
                    "CACHE_ACCESS":"缓存连接次数",
                    "CACHE_ACCESS_UP":"缓存连接次数",
                    "CACHE_CUR":"当前缓存中数量",
                    "CACHE_HIT":"缓存命中次数",
                    "CACHE_HIT_UP":"缓存命中次数",
                    "CACHE_MAX":"缓存最大数",
                    "CACHE_PUT":"写缓存次数",
                    "CACHE_PUT_UP":"写缓存次数",
                    "COMPLETED_TASK":"线程池已完成的SQL",
                    "COMPLETED_TASK_UP":"线程池已完成的SQL",
                    "CONN_ACTIVE":"连接使用数",
                    "CONN_EXECUTE":"连接执行数",
                    "CONN_EXECUTE_UP":"连接执行数",
                    "CONN_IDLE":"连接空闲数",
                    "FC_COUNT":"FC统计",
                    "FC_COUNT_UP":"FC统计",
                    "FREE_BUFFER":"空余缓存",
                    "NET_IN":"网络进数据",
                    "NET_IN_UP":"网络进数据",
                    "NET_OUT":"网络出数据",
                    "NET_OUT_UP":"网络出数据",
                    "REACT_COUNT":"作用SQL数量",
                    "REACT_COUNT_UP":"作用SQL数量",
                    "R_QUEUE":"IO读队列",
                    "SQL_SUM_R":"SQL统计读",
                    "SQL_SUM_R_UP":"SQL统计读",
                    "SQL_SUM_W":"SQL统计写",
                    "SQL_SUM_W_UP":"SQL统计写",
                    "TASK_QUEUE_SIZE":"线程池待处理SQL",
                    "TOTAL_BUFFER":"总缓存",
                    "TOTAL_TASK":"线程池总的SQL",
                    "TOTAL_TASK_UP":"线程池总的SQL",
                    "W_QUEUE":"IO写队列",
                    "RS_CODE":"DB异常数",
                    "RS_INFO":"DB异常信息",
                    "INDEX":"主写节点"
                    }
        }
    except:
        monitor_column={}
    return {"group":groupList,"service":serviceList,"zone":zoneList,'project':projectList,"monitor_column":monitor_column}


@login_required()
@permission_required('OpsManage.can_add_database_server_config',login_url='/noperm/')
def db_config(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        sqlList = Custom_High_Risk_SQL.objects.all()
        dataBaseList = DataBase_Server_Config.objects.all()
        serviceList = Service_Assets.objects.all()
        serList = Server_Assets.objects.all()
        projectList = Project_Assets.objects.all()
        try:
            config = SQL_Audit_Control.objects.get(id=1)
            gList = json.loads(config.audit_group)
            audit_group = []
            for g in gList:
                audit_group.append(int(g))
            for g in groupList:
                if g.id in audit_group:g.count = 1
        except Exception,ex:
            logger.warn(msg="获取SQL审核配置信息失败: {ex}".format(ex=str(ex)))
            config = None
        try:
            incept = Inception_Server_Config.objects.get(id=1)
        except Exception, ex:
            logger.warn(msg="获取Inception服务器信息失败: {ex}".format(ex=str(ex)))
            incept = None
        return render(request,'database/db_config.html',{"user":request.user,"incept":incept,
                                                        "dataBaseList":dataBaseList,"sqlList":sqlList,
                                                        "config":config,"groupList":groupList,
                                                        "serviceList":serviceList,"serList":serList,
                                                        "projectList":projectList}
                      )

@login_required()
@permission_required('OpsManage.can_add_database_server_list', login_url='/noperm/')
def db_search(request):
    if request.method == "POST"  :
        groupList = Group.objects.all()
        projectList = Project_Assets.objects.all()
        databaseFieldsList = [n.name for n in DataBase_Server_Config._meta.fields]
        assetsList = []
        data = dict()
        # 格式化查询条件
        for (k, v) in request.POST.items():
            if v is not None and v != u'' and k != 'type':
                data[k] = v
        ServerAssetIntersection = list(set(data.keys()).intersection(set(databaseFieldsList)))
        if data.has_key('ip'):
            for ds in DataBase_Server_Config.objects.filter(ip=data.get('ip')):
                if ds.assets not in assetsList: assetsList.append(ds.assets)
        else:
            if len(ServerAssetIntersection) > 0:
                assetsData = dict()
                serverList = [a.id for a in DataBase_Server_Config.objects.filter(**data)]
                assetsData['id__in'] = serverList
                assetsList.extend(DataBase_Server_Config.objects.filter(**assetsData))
            elif  len(ServerAssetIntersection) > 0:
                for ds in DataBase_Server_Config.objects.filter(**data):
                    if ds.assets not in assetsList: assetsList.append(ds.assets)
        if request.POST.get('type') == '2':dataList={}
        else:dataList = []
        for a in assetsList:
            db_env=''
            if a.db_env == 'test' :
                db_env = '''<span class="label label-success">测试</span>'''
            elif a.db_env == 'prod' :
                db_env = '''<span class="label label-info">正式</span>'''
            db_mode = ''
            if a.db_mode == 1:
                db_mode = '''<span class="label label-info">单例</span>'''
            elif a.db_mode == 2:
                db_mode = '''<span class="label label-info">主从</span>'''
            elif a.db_mode == 3:
                db_mode = '''<span class="label label-success">PXC</span>'''
            db_group = ''
            db_group =  '''{groupname}'''.format(groupname=Group.objects.get(id=a.db_group).name)
            db_project = ''
            db_project = '''{project_name}'''.format(project_name=Project_Assets.objects.get(id=a.db_project).project_name)
            if request.POST.get('type') == '2':
                dataList[a.id]=a.db_mark
                #dataList.append({"id": a.id, "ip": a.db_host, "info": a.db_mark})
            else:
                dataList.append(
                    {"详细":a.id,
                     "id": a.id,
                     "环境类型":  db_env,
                     "架构类型": db_mode,
                     "DB类型": a.db_type,
                     "使用组": db_group,
                     "项目": db_project,
                     "数据库地址": a.db_host,
                     "账户": a.db_user,
                     "端口": a.db_port,
                     "标签": a.db_mark,
                     "操作": '<div><div class="btn-group"><button type="button" class="btn btn-xs btn-default" data-toggle="modal" data-target="#myDatabaseEditModal-'+str(a.id)+'"><abbr title="編輯"><i class="fa fa-edit"></i></button></div><div class="btn-group"><a href="javascript:" onclick="getMySQLOrgChat(this,'+str(a.id)+')"><button class="btn btn-default btn-xs"  data-toggle="modal" data-target="#mysqlOrgChatModal"><i class="glyphicon glyphicon-zoom-in  bigger-110 icon-only"></i></button></a></div><div class="btn-group"><button type="button" class="btn btn-xs btn-default" onclick="delDatabaseSever(this,'+"''"+str(a.db_host)+"-"+str(a.db_name)+"',"+str(a.id)+')"><abbr title="删除"><i class="fa fa-trash"></i></button></div></div>'
                     }
                )
        return JsonResponse({'msg': "数据查询成功", "code": 200, 'data': dataList, 'count': 0})
 

@login_required()
@permission_required('OpsManage.can_add_database_server_list', login_url='/noperm/')
def db_list(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        sqlList = Custom_High_Risk_SQL.objects.all()
        dataBaseList = DataBase_Server_Config.objects.all()
        serviceList = Service_Assets.objects.all()
        serList = Server_Assets.objects.all()
        projectList = Project_Assets.objects.all()
        return render(request, 'database/db_list.html', {"user": request.user, "baseAssets":getBaseAssets(),
                                                           "dataBaseList": dataBaseList, "sqlList": sqlList,
                                                            "groupList": groupList,
                                                           "serviceList": serviceList, "serList": serList,
                                                           "projectList": projectList}
                      )

@login_required()
@permission_required('OpsManage.can_add_database_server_monitor', login_url='/noperm/')
def db_monitor(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        sqlList = Custom_High_Risk_SQL.objects.all()
        dataBaseList = DataBase_Server_Config.objects.all()
        serviceList = Service_Assets.objects.all()
        serList = Server_Assets.objects.all()
        projectList = Project_Assets.objects.all()
        return render(request, 'database/db_monitor.html', {"user": request.user,
                                                           "dataBaseList": dataBaseList, "sqlList": sqlList,
                                                            "groupList": groupList,"baseAssets":getBaseAssets(),
                                                           "serviceList": serviceList, "serList": serList,
                                                           "projectList": projectList}
                      )
    if request.method == "POST":
        data={}
        for (k, v) in request.POST.items():
            if v is not None and v != u'' and k != 'db_column' and k != 'db_id':
                if v!="" and v!=" " and v !="-1" and v is not None:
                    data[k] = v
        
        serverList = [str(a.id) for a in DataBase_Server_Config.objects.filter(**data)]
        monitor_column=getBaseAssets() 
        monitor_col=monitor_column['monitor_column']
        db_list=''
        v_dbname=''
        v_info=''
        v_type=1
        if 'db_id' in request.POST.keys() :
            if int(request.POST.get('db_id')) > 0 :
                db_list=request.POST.get('db_id')
            else:
                v_type=2
                db_list=",".join(serverList)
        else:
            db_list = ",".join( serverList)
            v_type = 2


        #获取列名
        col_list = ''
        if 'db_column' in request.POST.keys():
            if  request.POST.get('db_column') != "":
                col_list = request.POST.get('db_column')
        #处理MySQL监控
        if data['db_type'].lower()=='mysql':
            if col_list=='' or col_list=='-1':
                if v_type == 2:col_list1="sum(QUESTIONS_UP)/max(UPTIME_UP)  QPS,sum(Com_commit_UP+Com_rollback_UP)/max(UPTIME_UP) TPS,sum(Innodb_rows_inserted_UP)/max(UPTIME_UP) IPS,sum(Innodb_rows_deleted_UP)/max(UPTIME_UP) DPS,sum(Innodb_rows_updated_UP)/max(UPTIME_UP) UPS,sum(Threads_connected) CONN,sum(Innodb_rows_read_UP)/max(UPTIME_UP)  RPS"
                else:col_list1="QUESTIONS_UP/UPTIME_UP  QPS,(Com_commit_UP+Com_rollback_UP)/UPTIME_UP TPS,Innodb_rows_inserted_UP/UPTIME_UP IPS,Innodb_rows_deleted_UP/UPTIME_UP DPS,Innodb_rows_updated_UP/UPTIME_UP UPS,Threads_connected CONN,Innodb_rows_read_UP/UPTIME_UP  RPS"
                data_list=[{"name":"查询","data":[]},
                            {"name":"事务","data":[]},
                            {"name":"插入","data":[]},
                            {"name":"删除","data":[]},
                            {"name":"更新","data":[]},
                            {"name":"连接","data":[]} ]
                #主标题
                v_info = "所有状态"
                # 没选列情况
                s_type=1
            elif col_list in monitor_col['mysql'].keys():
                # 主标题
                v_info = monitor_col['mysql'][col_list]
                data_list = [{"name": v_info, "data": []}]

                if col_list[-3:]=='_UP':
                    if v_type==2 :col_list1="sum("+col_list+')/max(UPTIME_UP) as value '
                    else:col_list1=col_list+'/UPTIME_UP as value '
                else:
                    if v_type==2 :col_list1="sum("+col_list+")"
                    else:col_list1=col_list
                #return JsonResponse({"code": 200, "data": col_list})
                #单列情况
                s_type=2
            else:
                return JsonResponse({"code": 200, "data": {}})
            #SQL查询数据
            if v_type == 2:sql_all="select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time,"+col_list1+" from opsmanage_mysql_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"
            else:sql_all="select UNIX_TIMESTAMP(checktime)*1000+28800000 unit_time,"+col_list1+" from opsmanage_mysql_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day)"
        elif data['db_type'].lower() == 'redis':
            if col_list=='' or col_list=='-1':
                #所有服务器
                if v_type==2 :col_list1="sum(total_commands_processed_UP)/max(uptime_in_seconds_UP)  QPS,sum(total_connections_received_UP)/max(uptime_in_seconds_UP) CONN,ifnull(sum(keyspace_hits_UP)/sum(keyspace_misses_UP+keyspace_hits_UP)*100,0) KEYSS,sum(total_net_input_bytes_UP)/max(uptime_in_seconds_UP*1024) as net_input,sum(total_net_output_bytes_UP)/max(uptime_in_seconds_UP*1024) as net_output,sum(keyss_UP)/max(uptime_in_seconds_UP) as key_up"
                else:col_list1="total_commands_processed_UP/uptime_in_seconds_UP  QPS,total_connections_received_UP/uptime_in_seconds_UP CONN,ifnull(keyspace_hits_UP/(keyspace_misses_UP+keyspace_hits_UP)*100,0) KEYSS,total_net_input_bytes_UP/(uptime_in_seconds_UP*1024) as net_input,total_net_output_bytes_UP/(uptime_in_seconds_UP*1024) as net_output,keyss_UP/uptime_in_seconds_UP as key_up"
                data_list=[{"name":"操作","data":[]},
                            {"name":"连接","data":[]},
                            {"name":"KEY命中率","data":[]},
                            {"name":"入网流量MB","data":[]},
                            {"name":"出网流量MB","data":[]},
                            {"name":"KEY增量","data":[]}]
                #主标题
                v_info = "所有状态"
                # 没选列情况
                s_type=1
            elif col_list in monitor_col['redis'].keys():
                # 主标题
                v_info = monitor_col['redis'][col_list]
                data_list = [{"name": v_info, "data": []}]
                if col_list[-3:]=='_UP':
                    if v_type==2 :col_list1="sum("+col_list+')/max(uptime_in_seconds_UP) as value '
                    else:col_list1=col_list+'/uptime_in_seconds_UP as value '
                else:
                    if v_type==2 :col_list1="sum("+col_list+")"
                    else:col_list1=col_list
                #return JsonResponse({"code": 200, "data": col_list1})
                #单列情况
                s_type=2
            else:
                return JsonResponse({"code": 200, "data": {}})
            #SQL查询数据
            if v_type == 2:sql_all="select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time,"+col_list1+" from opsmanage_redis_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"
            else:sql_all="select UNIX_TIMESTAMP(checktime)*1000+28800000 unit_time,"+col_list1+" from opsmanage_redis_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day)"
        elif data['db_type'].lower() == 'mycat':
            if col_list=='' or col_list=='-1':
                #所有服务器
                if v_type==2 :col_list1="sum(conn_execute_up)/max(UPTIME_UP) CONN,sum(COMPLETED_TASK_UP)/max(UPTIME_UP)  QPS,sum(sql_sum_r_up)/max(uptime_up) RPS,sum(sql_sum_w_up)/max(uptime_up) WPS,sum(ACTIVE_COUNT)  ACN "
                else:col_list1="conn_execute_up/UPTIME_UP CONN,COMPLETED_TASK_UP/UPTIME_UP  QPS,sql_sum_r_up/uptime_up RPS,sql_sum_w_up/uptime_up WPS,ACTIVE_COUNT  ACN"
                data_list=[{"name":"连接","data":[]},
                            {"name":"处理","data":[]},
                            {"name":"每秒读取","data":[]},
                            {"name":"每秒写入","data":[]},
                            {"name":"线程积压","data":[]}]
                #主标题
                v_info = "所有状态"
                # 没选列情况
                s_type=1
            elif col_list in monitor_col['mycat'].keys():
                # 主标题
                v_info = monitor_col['mycat'][col_list]
                data_list = [{"name": v_info, "data": []}]
                if col_list[-3:]=='_UP':
                    if v_type==2 :col_list1="sum("+col_list+')/max(UPTIME_UP) as value '
                    else:col_list1=col_list+'/UPTIME_UP as value '
                else:
                    if v_type==2 :col_list1="sum("+col_list+")"
                    else:col_list1=col_list
                #return JsonResponse({"code": 200, "data": col_list1})
                #单列情况
                s_type=2
            else:
                return JsonResponse({"code": 200, "data": {}})
            #SQL查询数据
            if v_type == 2:sql_all="select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time,"+col_list1+" from opsmanage_mycat_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"
            else:sql_all="select UNIX_TIMESTAMP(checktime)*1000+28800000 unit_time,"+col_list1+" from opsmanage_mycat_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day)"
        elif data['db_type'].lower() == 'mongodb':
            if col_list=='' or col_list=='-1':
                #所有服务器
                if v_type==2 :col_list1="sum(opcounters_query_UP)/max(UPTIME_UP)  QPS,sum(opcounters_getmore_UP)/max(UPTIME_UP) GPS,sum(opcounters_insert_UP)/max(UPTIME_UP) IPS,sum(opcounters_delete_UP)/max(UPTIME_UP) DPS,sum(connections_current) CONN,sum(opcounters_update_UP)/max(UPTIME_UP) UPS "
                else:col_list1=" opcounters_query_UP/UPTIME_UP  QPS,opcounters_getmore_UP/UPTIME_UP GPS,opcounters_insert_UP/UPTIME_UP IPS,opcounters_delete_UP/UPTIME_UP DPS,connections_current CONN,opcounters_update_UP/UPTIME_UP UPS "
                data_list=[{"name":"查询","data":[]},
                            {"name":"导出","data":[]},
                            {"name":"插入","data":[]},
                            {"name":"删除","data":[]},
                            {"name":"连接","data":[]},
                            {"name":"更新","data":[]}] 
                #主标题
                v_info = "所有状态"
                # 没选列情况
                s_type=1
            elif col_list in monitor_col['mongodb'].keys():
                # 主标题
                v_info = monitor_col['mongodb'][col_list]
                data_list = [{"name": v_info, "data": []}]
                if col_list[-3:]=='_UP':
                    if v_type==2 :col_list1="sum("+col_list+')/max(UPTIME_UP) as value '
                    else:col_list1=col_list+'/UPTIME_UP as value '
                else:
                    if v_type==2 :col_list1="sum("+col_list+")"
                    else:col_list1=col_list
                #return JsonResponse({"code": 200, "data": col_list1})
                #单列情况
                s_type=2
            else:
                return JsonResponse({"code": 200, "data": {}})
            #SQL查询数据
            if v_type == 2:sql_all="select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time,"+col_list1+" from opsmanage_mongodb_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"
            else:sql_all="select UNIX_TIMESTAMP(checktime)*1000+28800000 unit_time,"+col_list1+" from opsmanage_mongodb_status where dbid in ("+db_list+") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day)"
        else:
            return JsonResponse({"code": 200, "data": {}})
        #return JsonResponse({"code": 200, "data": sql_all})
        cursor = connection.cursor()
        cursor.execute(sql_all)
        data_all = cursor.fetchall()
        # 图表名称
        if v_type == 1:
            dbid_it = {"id": int(db_list)}
            v_dbname = [str(a.db_mark) for a in DataBase_Server_Config.objects.filter(**dbid_it)]
        else:
            v_dbname = data['db_type'] + '集合'

        # 是否单列查询 1 所有状态  2 单列查询
        if s_type == 1:
            # 数据输出
            for key in data_all:
                for i in range(len(data_list)):
                    data_list[i]["data"].append([int(key[0]), float(key[i + 1])])
        else:
            # 数据输出
            for key in data_all:
                data_list[0]["data"].append([int(key[0]), float(key[1])])
        #配置图形类型
        config = {
            # 配置主标题
            "title":{"text":v_info},
            # 子标题
            "subtitle": {"text":v_dbname}, 
            # 数据轴
            "series":data_list,
            }
        # JSON输出
        return JsonResponse({"code": 200, "data": config })


@login_required()
@permission_required('OpsManage.can_add_database_server_report', login_url='/noperm/')
def db_report(request):
    if request.method == "GET":
        groupList = Group.objects.all()
        sqlList = Custom_High_Risk_SQL.objects.all()
        dataBaseList = DataBase_Server_Config.objects.all()
        serviceList = Service_Assets.objects.all()
        serList = Server_Assets.objects.all()
        projectList = Project_Assets.objects.all()
        return render(request, 'database/db_report.html', {"user": request.user,
                                                            "dataBaseList": dataBaseList, "sqlList": sqlList,
                                                            "groupList": groupList, "baseAssets": getBaseAssets(),
                                                            "serviceList": serviceList, "serList": serList,
                                                            "projectList": projectList}
                      )
    if request.method == "POST":
        data = {}
        for (k, v) in request.POST.items():
            if v is not None and v != u'' and k != 'db_column' and k != 'db_id':
                if v != "" and v != " " and v != "-1" and v is not None:
                    data[k] = v
        #标准变量
        serverList = [ str(a.id) for a in DataBase_Server_Config.objects.filter(**data)]
        monitor_column = getBaseAssets()
        monitor_col = monitor_column['monitor_column']
        #连接数据库
        cursor = connection.cursor()
        if 'db_id' in request.POST.keys():
            if int(request.POST.get('db_id')) > 0:
                db_list = request.POST.get('db_id')
                serverList=[request.POST.get('db_id')]
                dbid_it = {"id": int(db_list)}
                v_dbname = [str(a.db_mark) for a in DataBase_Server_Config.objects.filter(**dbid_it)]
            else:
                db_list = ",".join(serverList)
                v_dbname = data['db_type'] + '集合'
        else:
            db_list = ",".join(serverList)
            v_dbname = data['db_type'] + '集合'
        today=datetime.datetime.strftime(datetime.datetime.today(),'%Y-%m-%d 08:00:00')
        endtime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(today, "%Y-%m-%d %H:%M:%S")))
        stime = endtime - datetime.timedelta(days=1) 
        report_data={"report":[],"log":{}}
        log_data = []
        data_info = {}
        ip_list =[]
        # 处理MySQL监控
        if data['db_type'].lower() == 'mysql':
            col_list1 = "QUESTIONS_UP/UPTIME_UP  QPS,(Com_commit_UP+Com_rollback_UP)/UPTIME_UP TPS,Innodb_rows_inserted_UP/UPTIME_UP IPS,Innodb_rows_deleted_UP/UPTIME_UP DPS,Innodb_rows_updated_UP/UPTIME_UP UPS,Threads_connected CONN,Innodb_rows_read_UP/UPTIME_UP  RPS"
            data_list = [{"name": "查询", "data": []}, {"name": "事务", "data": []}, {"name": "连接", "data": []}]
            # 没选列情况
            sql_all = "select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time,sum(QUESTIONS_UP)/max(UPTIME_UP)  QPS,sum(Com_commit_UP+Com_rollback_UP)/max(UPTIME_UP) TPS,sum(Threads_connected) CONN from opsmanage_mysql_status where dbid in (" + db_list + ") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"

            #报告数据
            data_info = {"数据库状态":{"col":'主机,启动时间天,记录数M,版本,索引大小MB,数据大小MB,数据总大小MB,发送MB,接收MB,数据目录,total',"data":[]}
                            ,"连接信息":{"col":'主机,当前连接,活跃连接,未正确关闭连接,试图连接,最大连接数,最大使用连接,最大连接时间,total',"data":[]}
                            ,"主从状态":{"col":'主机,复制名称,主机IP,复制IO进程,复制SQL进程,延迟时间,主库文件,主库POST,复制SQL日志,SQL应用日志',"data":[]}
                            ,"性能信息":{"col":'主机,每秒查询数(QPS),每秒事务数TPS,Key Buffer读命中,Key Buffer写命中,InnoDB Buffer命中率,Query Cache状态,Query Cache命中率,Query Cache碎片率,total',"data":[]}
                            ,"内存信息":{"col":'主机,读入缓冲区</br>read_buffer_size(MB),随机读缓冲区<br>read_rnd_buffer_size(MB),排序缓冲区<br>sort_buffer_size(MB),排序缓冲区<br>sort_buffer_size(MB),线程栈内存<br>thread_stack(MB),Join临时缓冲区<br>join_buffer_size(MB),binlog缓存区<br>binlog_cache_size(MB),已经分配线程内存(MB),最大使用线程内存(MB),total',"data":[]}
                            ,"缓存信息":{"col":'主机,INNODB缓存区</br>innodb_buffer_pool_size(MB),INNODB日志缓存区<br>innodb_log_buffer_size(MB),键与索引缓冲区<br>key_buffer_size(MB),查询缓冲区<br>query_cache_size(MB),临时表缓冲区<br>tmp_table_size(MB),创建内存表最大值<br>max_heap_table_size(MB),全局缓存区(MB),总缓存区(MB),total',"data":[]}
                            ,"优化建议":{"col":'主机,参数,现值(MB),建议值,判定条件,备注',"data":[]}
                            ,"大表信息": {"col": '主机,数据库,表名,索引大小MB,数据总大小MB,记录数M,存储引擎,表说明,total', "data": []}
                            ,"无主键表": {"col": '主机,数据库,表名,索引大小MB,数据总大小MB,记录数M,存储引擎,表说明,total', "data": []}
                            ,"日志信息":{"col":'主机,日志文件,GTID',"data":[]}
                         ,"list":"数据库状态,连接信息,主从状态,性能信息,内存信息,缓存信息,优化建议,大表信息,无主键表,日志信息"
                         }
            for dbid in serverList:
                dbServer = DataBase_Server_Config.objects.get(id=dbid)
                MYSQL = MyCAT(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user, passwd=dbServer.db_passwd, dbname=dbServer.db_name)
                ip_list.append(dbServer.db_host)
                baseinfo=MYSQL.queryOne("SELECT CEIL(SUM(data_length)/1024/1024) 'DATA_MB',CEIL(SUM(index_length)/1024/1024) 'INDEX_MB', CEIL(SUM(table_rows)/1024/1024) 'Row_M',@@VERSION 'vers' FROM information_schema.tables")
                status_row=MYSQL.getglobalstatus()
                master_row=MYSQL.queryOne("SHOW MASTER STATUS")
                slave_row = MYSQL.queryAll("SHOW SLAVE STATUS")[1]
                variables_row = MYSQL.getglobalVariables()
                tab_row = MYSQL.queryAll("SELECT table_schema,table_name,engine,CEIL(table_rows/1024/1024) 'Row_M',ifnull(table_comment,'无') as 'table_comment',CEIL(index_length/1024/1024) 'INDEX_MB',CEIL(data_length/1024/1024) 'MB',CEIL((data_length+index_length)/1024/1024) 'TM' FROM information_schema.tables WHERE  table_schema NOT IN ('information_schema','mysql','sys','performance_schema')    ORDER BY engine<>'INNODB' and table_type='BASE TABLE' desc ,data_length DESC LIMIT 5")[1]
                tab_nopk_row = MYSQL.queryAll("SELECT a.table_schema,a.table_name,a.engine,ifnull(a.table_comment,'无') as 'table_comment',CEIL(a.table_rows/1024/1024) 'Row_M',CEIL(index_length/1024/1024) 'INDEX_MB',CEIL(a.data_length/1024/1024) 'MB',CEIL((data_length+index_length)/1024/1024) 'TM'   FROM information_schema.TABLES a  LEFT  JOIN information_schema.TABLE_CONSTRAINTS b  ON a.TABLE_NAME=b.TABLE_NAME AND a.TABLE_SCHEMA=b.TABLE_SCHEMA AND b.CONSTRAINT_TYPE='PRIMARY KEY' WHERE b.TABLE_NAME IS NULL  AND a.TABLE_SCHEMA NOT IN ('information_schema','mysql','sys','performance_schema') AND a.TABLE_TYPE ='BASE TABLE'  and 1=1 ")[1]
                #主机信息
                if status_row and variables_row:vtype=1
                else:continue

                # #数据库状态
                if baseinfo:
                    data_info["数据库状态"]["data"].append({"name":"数据库状态","主机":dbServer.db_mark,"版本":baseinfo["vers"]
                                ,"数据大小MB":baseinfo["DATA_MB"],"索引大小MB":baseinfo["INDEX_MB"],"记录数M":baseinfo["Row_M"]
                                ,"数据总大小MB":int(baseinfo["DATA_MB"])+int(baseinfo["INDEX_MB"])   ,"启动时间天":round(status_row['UPTIME']/3600/24,2)
                                ,"发送MB":round(status_row['BYTES_SENT'] /1024/1024,0),'接收MB':round(status_row['BYTES_RECEIVED']/1024/1024,0)
                                    ,'数据目录':variables_row['DATADIR']})
                #无主键表
                if tab_row :
                    for i in tab_row:
                        data_info["大表信息"]["data"].append({"name": "大表信息", "主机": dbServer.db_mark, "数据库": i["table_schema"], "表名": i["table_name"],
                                        "存储引擎": i["engine"], "索引大小MB": i["INDEX_MB"],
                                        "记录数M": i["Row_M"], "数据总大小MB": i["TM"] ,
                                        "表说明":  i['table_comment']})
                if tab_nopk_row:
                    for i in tab_nopk_row:
                        data_info["无主键表"]["data"].append( {"name": "无主键表", "主机": dbServer.db_mark, "数据库": i["table_schema"], "表名": i["table_name"],
                                        "存储引擎": i["engine"],"索引大小MB": i["INDEX_MB"],
                                        "记录数M": i["Row_M"], "数据总大小MB": i["TM"],
                                        "表说明":  i['table_comment'] })


                #连接信息
                data_info["连接信息"]["data"].append({"name": "连接信息", "主机": dbServer.db_mark, "未正确关闭连接": status_row['ABORTED_CLIENTS']
                                    , "试图连接": status_row['ABORTED_CONNECTS'] , "当前连接": status_row['THREADS_CONNECTED']
                                    , "活跃连接": status_row['THREADS_RUNNING'] , "最大使用连接": status_row['MAX_USED_CONNECTIONS']
                                    ,"最大连接数": variables_row['MAX_CONNECTIONS']
                                    ,"最大连接时间": ('无' if "MAX_USED_CONNECTIONS_TIME" not in status_row.keys() else status_row["MAX_USED_CONNECTIONS_TIME"] )
                                   })

                #日志信息
                if master_row:
                    data_info["日志信息"]["data"].append({"name": "日志信息", "主机": dbServer.db_mark, "日志文件": master_row['File']
                                    , "位置": master_row['Position'], "GTID": master_row['Executed_Gtid_Set'] })
                #主从状态
                if slave_row:
                    for i in slave_row:
                        data_info["主从状态"]["data"].append({"name": "主从状态", "主机": dbServer.db_mark, "复制IO进程": i["Slave_IO_Running"], "复制SQL进程": i["Slave_SQL_Running"],
                                             "主机IP": i["Master_Host"],"复制名称":i["Channel_Name"],
                                             "延迟时间": i["Seconds_Behind_Master"], "复制SQL日志": i["Slave_SQL_Running_State"]  ,
                                             "主库文件": i['Master_Log_File'],"主库POST": i['Read_Master_Log_Pos'],
                                             "主库GTID范围": i['Retrieved_Gtid_Set'],"SQL应用日志": i['Slave_IO_State']})
                #性能信息
                data_info["性能信息"]["data"].append({"name": "性能信息", "主机": dbServer.db_mark, "每秒查询数(QPS)": round(status_row['QUESTIONS']/status_row['UPTIME'],2)
                                        , "每秒事务数TPS": round((status_row["COM_COMMIT"]+status_row["COM_ROLLBACK"])/status_row['UPTIME'],2)
                                        , "Key Buffer读命中": round((1-status_row['KEY_READS']/(status_row['KEY_READ_REQUESTS']+1))*100,2), "Key Buffer写命中": round((1-status_row['KEY_WRITES']/(status_row['KEY_WRITE_REQUESTS']+1))*100,2)
                                        , "InnoDB Buffer命中率": round((1-status_row['INNODB_BUFFER_POOL_READS']/(status_row['INNODB_BUFFER_POOL_READ_REQUESTS']+1))*100,2), "Query Cache状态": ("已启用" if variables_row["QUERY_CACHE_TYPE"] != 0 else "未启用")
                                        , "Query Cache命中率": round((1-status_row['QCACHE_HITS']/(status_row['QCACHE_HITS']+status_row['QCACHE_INSERTS']+status_row['QCACHE_NOT_CACHED']+1))*100,2), "Query Cache碎片率": round((status_row['QCACHE_FREE_BLOCKS'])/(status_row['QCACHE_TOTAL_BLOCKS']+1),2)
                                     })
                
                #内存信息
                thread_buffers=float(variables_row['READ_BUFFER_SIZE']) +float(variables_row['READ_RND_BUFFER_SIZE']) + float(variables_row['SORT_BUFFER_SIZE']) +float(variables_row['THREAD_STACK']) +float(variables_row['JOIN_BUFFER_SIZE']) +float(variables_row['BINLOG_CACHE_SIZE'])
                global_buffers=float(variables_row['INNODB_BUFFER_POOL_SIZE']) +float(variables_row['INNODB_LOG_BUFFER_SIZE']) + float(variables_row['KEY_BUFFER_SIZE']) +float(variables_row['QUERY_CACHE_SIZE']) +float(variables_row['TMP_TABLE_SIZE']) + float(variables_row['MAX_HEAP_TABLE_SIZE'])
                data_info["内存信息"]["data"].append({"name": "内存信息", "主机": dbServer.db_mark,
                                     '读入缓冲区</br>read_buffer_size(MB)': round( float(variables_row['READ_BUFFER_SIZE'])/1024/1024, 2),
                                     '随机读缓冲区<br>read_rnd_buffer_size(MB)': round( float(variables_row['READ_RND_BUFFER_SIZE']) / 1024 / 1024, 2),
                                     '排序缓冲区<br>sort_buffer_size(MB)': round( float(variables_row['SORT_BUFFER_SIZE']) / 1024 / 1024, 2),
                                     '线程栈内存<br>thread_stack(MB)': round(float(variables_row['THREAD_STACK']) / 1024 / 1024, 2),
                                          'Join临时缓冲区<br>join_buffer_size(MB)': round(float(variables_row['JOIN_BUFFER_SIZE']) / 1024 / 1024, 2),
                                          'binlog缓存区<br>binlog_cache_size(MB)': round(float(variables_row['BINLOG_CACHE_SIZE']) / 1024 / 1024, 2),
                                          '已经分配线程内存(MB)': round(thread_buffers * float(status_row['THREADS_CONNECTED']) / 1024 / 1024, 2),
                                          '最大使用线程内存(MB)': round( thread_buffers * float(variables_row['MAX_CONNECTIONS']) / 1024 / 1024, 2)
                                          })
                data_info["缓存信息"]["data"].append({"name": "缓存信息", "主机": dbServer.db_mark,
                                          'INNODB缓存区</br>innodb_buffer_pool_size(MB)': round( float(variables_row['INNODB_BUFFER_POOL_SIZE']) / 1024 / 1024, 2),
                                          'INNODB日志缓存区<br>innodb_log_buffer_size(MB)': round( float(variables_row['INNODB_LOG_BUFFER_SIZE']) / 1024 / 1024, 2),
                                          '键与索引缓冲区<br>key_buffer_size(MB)': round(  float(variables_row['KEY_BUFFER_SIZE']) / 1024 / 1024, 2),
                                          '查询缓冲区<br>query_cache_size(MB)': round( float(variables_row['QUERY_CACHE_SIZE']) / 1024 / 1024, 2),
                                        '临时表缓冲区<br>tmp_table_size(MB)': round(float(variables_row['TMP_TABLE_SIZE'])/ 1024 / 1024, 2),
                                        '创建内存表最大值<br>max_heap_table_size(MB)': round(float(variables_row['MAX_HEAP_TABLE_SIZE'])/ 1024 / 1024, 2),
                                        '全局缓存区(MB)': round(global_buffers / 1024 / 1024, 2),
                                        '总缓存区(MB)': round((global_buffers + thread_buffers * float(status_row['THREADS_CONNECTED'])) / 1024 / 1024, 2)
                                    })
                #优化建议
                opt_list=[]
                opt_list.append(['innodb_buffer_pool_size' ,
                                round(float(variables_row['INNODB_BUFFER_POOL_SIZE']) / 1024 / 1024, 2),
                                round((float(status_row['INNODB_BUFFER_POOL_PAGES_DATA']) * 100) /(float(status_row['INNODB_BUFFER_POOL_PAGES_TOTAL'])+1), 2),
                                round(float(status_row['INNODB_BUFFER_POOL_PAGES_DATA']) *float(status_row[ 'INNODB_PAGE_SIZE']) * 1.05 / 1024 / 1024, 2),
                                "INNODB_BUFFER_POOL_PAGES_DATA<br>/INNODB_BUFFER_POOL_PAGES_TOTAL<br>比率大于95增加,小于减小"])

                opt_list.append(['binlog_cache_size', round(float(variables_row['BINLOG_CACHE_SIZE']) / 1024 / 1024, 2) ,
                                float(status_row['BINLOG_CACHE_DISK_USE']), '1MB', 'BINLOG_CACHE_DISK_USE大于1可增加,BINLOG_CACHE_USE:'+str(round(
                                float(status_row['BINLOG_CACHE_USE']) / 1024 / 1024, 2))+'MB' ]);

                opt_list.append(['thread_cache_size', round(float(variables_row['THREAD_CACHE_SIZE']), 2),
                                 round((float(status_row['CONNECTIONS']) -float(status_row['THREADS_CREATED'])) / (float(status_row['CONNECTIONS'])+1) * 100, 2),
                                 '3G内存以上64<', '(CONNECTIONS-THREADS_CREATED)/CONNECTIONS<br>小于95%考虑增加']);

                opt_list.append(['table_open_cache', round(float(variables_row['TABLE_OPEN_CACHE']), 2),
                                 round((float(status_row['OPEN_TABLES']) * 100) / (float(variables_row['TABLE_OPEN_CACHE'])+1), 2),
                                 (float(status_row['OPEN_TABLES']) * 1.05), 'OPEN_TABLES/TABLE_OPEN_CACHE， 大于99%需增加']);

                opt_list.append(['key_buffer_size', round(float(variables_row['KEY_BUFFER_SIZE']) / 1024 / 1024, 2),
                                 round(float(status_row['KEY_READS']) / (float(status_row['KEY_READ_REQUESTS'])+1) * 100, 3),
                                 '32M', 'KEY_READS/KEY_READ_REQUESTS, 大于0.01考虑增加,使用innodb建议32M']);

                opt_list.append(['sort_buffer_size', round(float(variables_row['SORT_BUFFER_SIZE']) / 1024 / 1024, 2),
                                 round(float(status_row['SORT_MERGE_PASSES'])),
                                 '无', 'SORT_MERGE_PASSES持续变大可增加']);

                opt_list.append(['read_buffer_size', round(float(variables_row['READ_BUFFER_SIZE'])/ 1024 / 1024, 2),
                                 round(float(status_row['HANDLER_READ_RND_NEXT']) /(float(status_row['COM_SELECT'])+1), 0),
                                 '无', 'HANDLER_READ_RND_NEXT/COM_SELECT,比率超过4000需加大']);

                opt_list.append(['tmp_table_size', round(float(variables_row['TMP_TABLE_SIZE']) / 1024 / 1024, 2),
                                 round(float(status_row['CREATED_TMP_DISK_TABLES'])/(float(status_row['CREATED_TMP_TABLES'])+1) * 100, 0),
                                 '无', 'CREATED_TMP_DISK_TABLES/CREATED_TMP_TABLES, 比率超过5%需加大']);
                for i in opt_list:
                    data_info["优化建议"]["data"].append({"name": "优化建议", "主机": dbServer.db_mark,
                                               '备注': i[4],
                                            "参数": i[0],
                                            '现值(MB)': i[1],
                                            '判定条件':i[2],
                                            '建议值':i[3]
                                            })
                #锁情况
                #innodb
                #合并数据
                #data_item=dict(Counter(data_item) + Counter(data_info))
                #return JsonResponse({"code": 200, "data": serverList})


            report_data["report"]={"item":data_info ,"dbtype":'mysql'}

            #日志数据
            logdb = settings.DATABASES['logdb']
            loginfo = Mongos(host=logdb['HOST'], port=logdb['PORT'], user=logdb['USER'], passwd=logdb['PASSWORD'], dbname=logdb['NAME'])
            sql={ "ip":ip_list,"@timestamp": {'$gte':stime,'$lt':endtime},"query":{"$exists":"true"} }
            col={"query_time":1,"lock_time":1,"rows_sent":1,"rows_examined":1,"query":1,"action":1}
            #取数据
            rs=loginfo.find_list(dbname='logdb',tbname='mysql_slow',sql=sql,col=col)
            sql_info={}
            table_info={}
            for key in rs:
                query_sql=''
                info=key
                #SQL匹配
                info['sql']=re.sub("'(.*?)'|\d{2,}|\d",'*',key['query'].lower())
                info['sql']=re.sub("(\*\,){2,}|(\*\,\ ){2,}", '*', info['sql'])
                if len(key['query'])>101 :info['sql_all']=str(key['query'][0:50])+'...'+str(key['query'][-50:])
                else: info['sql_all']=key['query']

                replace_list=["\r\n", "\r", "\n", '\t','  ',]
                for st in replace_list:
                    info['sql'] = info['sql'].replace(st, ' ').replace("  ,",',').replace(", ",',')
                    info['sql_all'] = info['sql_all'].replace(st, ' ').replace('`', '')
                info['sql'] =info['sql'].replace('`', '').replace("*, *",'*').replace("* , *",'*').replace("*,*",'*').replace("**",'*')

                #获取表名
                if info['action'].lower()=='select' :
                    tbname=''
                    tbname_list = info['sql'].replace("  "," ").split(" from ")
                    count=0
                    for key in tbname_list:
                        if count>0 :
                            tbx_list=key.replace("  "," ").split(" ")
                            for k in tbx_list:
                                if len(k)>=1 and len(k)<6:
                                    if str(k[:1]) != '(' and str(k) !="" and str(k[:1])!=' ' :
                                        if str(k).find('.')>0 :tbname=k.split(".")[1]
                                        else: tbname=str(k)
                                    else:continue
                                elif len(k)>=7 :
                                    if str(k[:7])=='(select':break
                                    if str(k[1])!='(' and  str(k[:6])!='select':
                                        if str(k).find('.')>0 :tbname=k.split(".")[1]
                                        else: tbname=str(k)
                                    else:break
                                elif len(k)==6:
                                    if str(k[1])!='(' and str(k[:6])!='select' and str(k) !="" and str(k[1])!=' '  :
                                        if str(k).find('.')>0 :tbname=k.split(".")[1]
                                        else: tbname=str(k)
                                    elif str(k[:6])=='select':break
                                elif len(k)==1 :
                                    if str(k)!='(' and  str(k) !="" and str(k)!=' ' :
                                         tbname=str(k)
                                    else:continue
                                else:break
                                if tbname!="" and tbname!=" " :break
                        if tbname!="" and tbname!=" " : break
                        count=count+1
                elif  info['action'].lower()=='update' :
                    tbname_list = info['sql'].replace("  ", " ").split(" ")
                    #return JsonResponse({"code": 200, "data": table_info, "SQL": tbname_list})
                    if tbname_list[1].find('.')>0: tbname = tbname_list[1].split(".")[1]
                    else: tbname = tbname_list[1]
                elif info['action'].lower() == 'delete':
                    tbname_list = info['sql'].replace("  ", " ").split(" ")
                    if tbname_list[2].find('.')>0: tbname = tbname_list[2].split(".")[1]
                    else: tbname = tbname_list[2]
                else:
                    tbname_list = info['sql'].replace("  ", " ").split(" ")
                    if tbname_list[2].find('.')>0: tbname = tbname_list[2].split(".")[1]
                    else:  tbname = tbname_list[2]
                # 表名过滤
                tbname = tbname.replace(")", "").replace(";", "")
                if tbname not in sql_info.keys():sql_info[tbname]={}
                # sql集合
                if info['sql'] in sql_info[tbname].keys():
                    if float(info["query_time"]) > sql_info[tbname][info['sql']]["max_query"]:
                        sql_info[tbname][info['sql']]["max_query"] = float(info["query_time"])
                    sql_info[tbname][info['sql']] = {
                                        "query_time": float(info["query_time"]) + sql_info[tbname][info['sql']]["query_time"],
                                        "lock_time": float(info["lock_time"]) + sql_info[tbname][info['sql']]["lock_time"],
                                        "rows_sent": float(info["rows_sent"])+ sql_info[tbname][info['sql']]["rows_sent"],
                                        "rows_examined": float(info["rows_examined"]) + sql_info[tbname][info['sql']]["rows_examined"],
                                        "max_query": sql_info[tbname][info['sql']]["max_query"],
                                        "count": 1 + sql_info[tbname][info['sql']]["count"],"sql":sql_info[tbname][info['sql']]["sql"]}
                else:
                    sql_info[tbname][info['sql']] = {"query_time": float(info["query_time"]),
                                      "lock_time": float(info["lock_time"]),
                                      "rows_sent": float(info["rows_sent"]),
                                      "rows_examined": float(info["rows_examined"]),
                                      "max_query": float(info["query_time"]), "count": 1,"sql":info['sql_all']}

                if tbname in table_info.keys():
                    if float(info["query_time"]) > table_info[tbname]["max_query"]: table_info[tbname]["max_query"]=float(info["query_time"])
                    table_info[tbname] = {"query_time": float(info["query_time"])+table_info[tbname]["query_time"], "lock_time": float(info["lock_time"])+table_info[tbname]["lock_time"], "rows_sent": float(info["rows_sent"])+table_info[tbname]["rows_sent"], "rows_examined": float(info["rows_examined"])+table_info[tbname]["rows_examined"],  "max_query":table_info[tbname]["max_query"] , "count": 1+table_info[tbname]["count"]}
                else:
                    table_info[tbname] = {"query_time": float(info["query_time"]), "lock_time": float(info["lock_time"]),  "rows_sent": float(info["rows_sent"]),  "rows_examined": float(info["rows_examined"]), "max_query": float(info["query_time"]),  "count":  1}
            #数据合并
            table_info=sorted(table_info.items(), key=lambda e: e[1]["query_time"], reverse=True)
            sql_sort=[]
            for key in table_info:
                sql_sort.append({"table":key[0],"sql":sorted(sql_info[key[0]].items(), key=lambda e: e[1]["query_time"], reverse=True)})

            report_data["log"] = {"table_info": table_info, "sql": sql_sort,"dbtype":'mysql'}
        elif data['db_type'].lower() == 'redis':
            # 所有服务器
            col_list1 = "total_commands_processed_UP/uptime_in_seconds_UP  QPS,total_connections_received_UP/uptime_in_seconds_UP CONN,ifnull(keyspace_hits_UP/(keyspace_misses_UP+keyspace_hits_UP)*100,0) KEYSS,total_net_input_bytes_UP/(uptime_in_seconds_UP*1024) as net_input,total_net_output_bytes_UP/(uptime_in_seconds_UP*1024) as net_output,keyss_UP/uptime_in_seconds_UP as key_up"
            data_list = [{"name": "操作", "data": []}, {"name": "连接", "data": []}, {"name": "KEY命中率", "data": []},{"name": "入网流量MB", "data": []},{"name": "出网流量MB", "data": []},{"name": "KEY增量", "data": []}]
            # SQL查询数据
            sql_all = "select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time," + col_list1 + " from opsmanage_redis_status where dbid in (" + db_list + ") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"
            # 报告数据
            data_info = {"数据库状态": {"col":'', "data": []}
                            , "统计信息": {"col":'', "data": []}
                            , "主从状态": {"col":'', "data": []}
                            , "性能信息": {"col":'', "data": []}
                            , "内存信息": {"col":'', "data": []}
                            , "持久化信息": {"col":'', "data": []}
                            , "集群信息": {"col": '', "data": [],"cluster":{}}
                            , "list": "数据库状态,统计信息,主从状态,性能信息,内存信息,持久化信息,集群信息"
                         }
            for dbid in serverList:
                dbServer = DataBase_Server_Config.objects.get(id=dbid)
                MYSQL = Rediss(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user, passwd=dbServer.db_passwd, dbname=dbServer.db_name)
                ip_list.append(dbServer.db_host)
                status_row = MYSQL.getbaseStatus(type=3)[0]
                master_row = {"master":MYSQL.getmasterStatus(type=3)[0],"slave":MYSQL.getmReplStatus(type=3)}
                variable_row=MYSQL.getvariable(type=3)[0]
                cluster_row=MYSQL.getClusterStatus(type=3)[0]
                #return JsonResponse({"code": 200, "data": cluster_row})
                data_info["数据库状态"]["col"]='主机,IP,端口,版本号,启动时间(天),角色,集群状态,已用内存M,空闲内存M,总内存M,使用率,total'
                data_info["数据库状态"]["data"].append({"主机":dbServer.db_mark,"IP":dbServer.db_host,"端口":dbServer.db_port,
                                                        "版本号":status_row['redis_version'],"启动时间(天)":round(float(status_row['uptime_in_seconds'])/86000,2),
                                                        "角色":status_row['role'],"集群状态":("集群模式" if status_row['cluster_enabled']==1 else "非集群" ),
                                                        "已用内存M":round(float(status_row['used_memory'])/1024/1024,2),
                                                        "空闲内存M":round((float(variable_row['maxmemory'])-float(status_row['used_memory']))/1024/1024,2),
                                                        "总内存M": round(float(variable_row['maxmemory'])/1024/1024,2),
                                                        "使用率":round(float(status_row['used_memory'])/float(variable_row['maxmemory'])*100,2)
                                                        })
                data_info["统计信息"]["col"] = '主机,IP,端口,总命令M,每秒命令,过期KEY,驱逐KEY,成功查到M,未查到M,命中率,频道数,模式数,total'
                data_info["统计信息"]["data"].append(
                                {"主机": dbServer.db_mark, "IP": dbServer.db_host, "端口": dbServer.db_port,
                                 "总命令M":round(float(status_row['total_commands_processed']) / 1024 / 1024, 2) ,
                                 "每秒命令":status_row['instantaneous_ops_per_sec'],
                                 "过期KEY": status_row['expired_keys'],
                                 "驱逐KEY":status_row['evicted_keys'],
                                 "成功查到M":round(float(status_row['keyspace_hits'])/ 1024 / 1024, 2),
                                 "未查到M":round(float(status_row['keyspace_misses'])/ 1024 / 1024, 2),
                                 "命中率":round(float(status_row['keyspace_hits']) / (float(status_row['keyspace_hits']) +1+float(status_row['keyspace_misses']))*100, 2),
                                 "频道数":status_row['pubsub_channels'],
                                 "模式数":status_row['pubsub_patterns']
                            })
                data_info["主从状态"]["col"] = '主机,IP,端口,角色,对象IP,对象端口,复制状态,延迟'
                if '主从延迟' in master_row["master"].keys():
                    data_info["主从状态"]["data"].append(
                        {"主机": dbServer.db_mark, "IP": dbServer.db_host, "端口": dbServer.db_port,
                         "角色": status_row['role'],
                         "对象IP": master_row["master"][" 主机IP"],
                         "对象端口": master_row["master"][" 主机端口"],
                         "复制状态": master_row["master"]["复制状态"],
                         "延迟": master_row["master"]["主从延迟"]
                         })
                if len(master_row["slave"])>0:
                    for key  in master_row["slave"] :
                        for key1,value in key.items():
                            data_info["主从状态"]["data"].append(
                                {"主机": dbServer.db_mark, "IP": dbServer.db_host, "端口": dbServer.db_port,
                                 "角色": status_row['role'],
                                 "对象IP": value[" 从机IP"],
                                 "对象端口": value[" 从机端口"],
                                 "复制状态": value["复制状态"],
                                 "延迟": value["主从延迟"]
                                 })
                data_info["性能信息"]["col"] = '主机,CPU_SYS使用,CPU_User使用,后台CPU_SYS,后台CPU_User,总输入GB,总输出GB,每秒输入(kbps),每秒输出(kbps),total'
                data_info["性能信息"]["data"].append(
                    {"主机": dbServer.db_mark,
                     "CPU_SYS使用": status_row['used_cpu_sys'],
                     "CPU_User使用": status_row['instantaneous_ops_per_sec'],
                     "后台CPU_SYS": status_row['used_cpu_sys_children'],
                     "后台CPU_User": status_row['used_cpu_user_children'],
                     "总输入GB": round(float(status_row['total_net_input_bytes']) / 1024 / 1024/1024, 2),
                     "总输出GB": round(float(status_row['total_net_output_bytes']) / 1024 / 1024/1024, 2),
                     "每秒输入(kbps)":  status_row['instantaneous_input_kbps'] ,
                     "每秒输出(kbps)": status_row['instantaneous_output_kbps']
                     })
                data_info["内存信息"]["col"] = '主机,占用内存,常驻内存GB,消耗峰值,Lua引擎GB,占用率,内存使用率,空闲内存G,Key数量(M),过期KEY(M),平均TTL,total'
                data_info["内存信息"]["data"].append(
                    {"主机": dbServer.db_mark,
                     "占用内存": status_row['used_memory_human'],
                     "常驻内存GB": round(float(status_row['used_memory_rss']) / 1024 / 1024 / 1024, 3),
                     "消耗峰值": status_row['used_memory_peak_human'],
                     "Lua引擎GB": round(float(status_row['used_memory_lua']) / 1024 / 1024 / 1024, 2),
                     "占用率": round(float(status_row['used_memory']) / (float(status_row['used_memory_rss'])+1)*100,2),
                     "内存使用率": round(float(status_row['used_memory_rss']) / (float(variable_row['maxmemory']) + 1) * 100, 2),
                     "空闲内存G": round((float(variable_row['maxmemory']) - float(status_row['used_memory'])) / 1024 / 1024/1024,2),
                     "Key数量(M)": status_row['keyss'],
                     "平均TTL": status_row['avg_ttl'],
                     "过期KEY(M)": status_row['expires']
                     })


                data_info["持久化信息"]["col"] = '主机,AOF状态,RDB状态,RDB未落盘,RDB最后落盘,RDB最后状态,RDB最后耗时,AOF大小GB,AOF最后状态,AOF最后耗时,AOF缓存,total'
                data_info["持久化信息"]["data"].append(
                    {"主机": dbServer.db_mark,
                     "AOF状态": ("关闭" if status_row['aof_enabled'] == 0 else "开启"),
                     "RDB状态": ("关闭" if variable_row['save'] == "" else "开启"),
                     "RDB未落盘": status_row['rdb_changes_since_last_save'],
                     "RDB最后落盘": status_row['rdb_last_save_time'],
                     "RDB最后状态": status_row['rdb_last_bgsave_status'],
                     "RDB最后耗时":  status_row['rdb_last_bgsave_time_sec'] ,
                     "AOF大小GB": round(float(status_row['aof_current_size']) / 1024 / 1024 / 1024, 2),
                     "AOF最后状态": status_row['aof_last_bgrewrite_status'],
                     "AOF最后耗时": status_row['aof_last_rewrite_time_sec'],
                     "AOF缓存": status_row['aof_buffer_length']
                     })

                for key,value in cluster_row.items():
                    if key not in data_info["集群信息"]["cluster"].keys():data_info["集群信息"]["cluster"][key]=value

            data_info["集群信息"]["col"] = '主机,状态,角色,数据段,Master,total'
            for key,value in data_info["集群信息"]["cluster"].items():
                value["master"]=''
                for key1,value1 in data_info["集群信息"]["cluster"].items():
                    if value["master_id"]==value1["node_id"]:value["master"]=key1
                data_info["集群信息"]["data"].append(
                    {"主机": key,
                     "状态": ("在线" if value['connected'] else "离线"),
                     "角色": ("主机" if "master"  in value['flags'] else "从机") ,
                     "数据段":value["slots"],
                     "Master": value['master']
                     })

            report_data["report"] = {"item": data_info, "dbtype": 'mysql'}
            # 日志数据
            logdb = settings.DATABASES['logdb']
            loginfo = Mongos(host=logdb['HOST'], port=logdb['PORT'], user=logdb['USER'], passwd=logdb['PASSWORD'], dbname=logdb['NAME'])
            sql = {"beat.name": ip_list, "@timestamp": {'$gte': stime, '$lt': endtime} }
            col = {  "@timestamp": 1, "message": 1}
            # 取数据
            rs = loginfo.find_list(dbname='logdb', tbname='redis', sql=sql, col=col)
            sql_info = {}
            table_info = {}
            for key in rs:
                query_sql = ''
                info = key
                # SQL匹配
                info['sql'] = re.sub("'(.*?)'|\d{2,}|\d|\#", '*', key['message'].lower())
                info['sql'] = re.sub('(\*\,){2,}|(\*\,\ ){2,}|\"(.*?)\"', '*', info['sql'])
                replace_list = ["\r\n", "\r", "\n", '\t', '##']
                for st in replace_list:
                    info['sql'] = info['sql'].replace(st, '').replace("  ,", ',').replace(", ", ',').replace("..", "")
                info['sql'] = info['sql'].replace('`', '').replace("*, *", '*').replace("* , *", '*').replace("*,*",'*').replace("**", '*')

                if len(info['sql']) > 151: info['sql'] = info['sql'][:150]
                # sql集合
                if info['sql'] in sql_info.keys():

                    sql_info[info['sql']] = {  "count": sql_info[info['sql']]["count"] + 1 }
                else:
                    sql_info[info['sql']] = { "count": 1 }
            # 合成数据
            sql_info = sorted(sql_info.items(), key=lambda e: e[1], reverse=True)
            report_data["log"] = {"table_info": "", "sql": sql_info,"dbtype":'redis'}
        elif data['db_type'].lower() == 'mycat':
            # 所有服务器
            col_list1 = "sum(conn_execute_up)/max(UPTIME_UP) CONN,sum(COMPLETED_TASK_UP)/max(UPTIME_UP)  QPS,sum(sql_sum_r_up)/max(uptime_up) RPS,sum(sql_sum_w_up)/max(uptime_up) WPS,sum(ACTIVE_COUNT)  ACN "
            data_list = [{"name": "连接", "data": []},{"name": "处理", "data": []},{"name": "每秒读取", "data": []}, {"name": "每秒写入", "data": []}, {"name": "线程积压", "data": []}]
            # SQL查询数据
            sql_all = "select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time," + col_list1 + " from opsmanage_mycat_status where dbid in (" + db_list + ") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"
            # 报告数据
            data_info = {"用户统计": {"col": '', "data": []}
                , "主机心跳": {"col": '', "data": []}
                , "线程池信息": {"col": '', "data": []}
                , "库信息": {"col": '', "data": []}
                , "表访问信息": {"col": '', "data": []}
                , "连接信息": {"col": '', "data": []}
                , "慢查询信息": {"col": '', "data": []}

                , "list": "用户统计,主机心跳,线程池信息,连接信息,库信息,表访问信息,慢查询信息"
                         }
            for dbid in serverList:
                dbServer = DataBase_Server_Config.objects.get(id=dbid)
                MYSQL = MyCAT(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user, passwd=dbServer.db_passwd, dbname=dbServer.db_name)
                ip_list.append(dbServer.db_host)
                slave_row = MYSQL.queryAll("SHOW SLAVE STATUS")[1]
                variable= MYSQL.getVariables(type=2)
                user_row = MYSQL.queryAll("show @@sql.sum")[1]
                for key in user_row:
                    data_info["用户统计"]["col"] = '主机,用户名,读取M,写入M,读写率,时段-06|-13|-18|-22,毫秒10|-200|-1s|1s,最后时间,total'
                    data_info["用户统计"]["data"].append({"主机": dbServer.db_mark,
                                                       "用户名": key['USER'],
                                                       "读取M": round(float(key['R'])/1024/1024, 2),
                                                       "写入M": round(float(key['W'])/1024/1024, 2),
                                                       "读写率": key['R%'],
                                                       "时段-06|-13|-18|-22": key["TIME_COUNT"],
                                                       "毫秒10|-200|-1s|1s": key["TTL_COUNT"],
                                                       "最后时间": datetime.datetime.utcfromtimestamp( int(str(key['LAST_TIME'])[:10])).strftime("%Y-%m-%d %H:%M:%S")

                                                       })
                user_row = MYSQL.queryAll("show @@heartbeat")[1]
                for key in user_row:
                    data_info["主机心跳"]["col"] = '主机,名称,类型,IP,健康,状态,超时,时间,停止'
                    data_info["主机心跳"]["data"].append({"主机": dbServer.db_mark,
                                                      "名称": key['NAME'],
                                                      "类型": key["TYPE"],
                                                      "IP": key["HOST"],
                                                      "健康": ("正常" if key['RS_CODE']==1 else "异常") ,
                                                      "状态": key["STATUS"],
                                                      "超时": key["TIMEOUT"],
                                                      "时间": key["LAST_ACTIVE_TIME"],
                                                      "停止":key["STOP"]

                                                      })
                user_row = MYSQL.queryAll("show @@threadpool")[1]
                for key in user_row:
                    data_info["线程池信息"]["col"] = '主机,名称,数量,线程积压,待处理SQL,已完成的SQL,总SQL'
                    data_info["线程池信息"]["data"].append({"主机": dbServer.db_mark,
                                                      "名称": key['NAME'],
                                                      "数量": key["POOL_SIZE"],
                                                      "线程积压": key["ACTIVE_COUNT"],
                                                      "待处理SQL": key["TASK_QUEUE_SIZE"],
                                                      "已完成的SQL": key["COMPLETED_TASK"],
                                                      "总SQL": key["TOTAL_TASK"]
                                                      })
                user_row = MYSQL.queryAll("show @@datanode")[1]
                for key in user_row:
                    data_info["库信息"]["col"] = '主机,名称,真实库,主写节点,类型,空闲,最大连接,总执行,RECOVERY_TIME'
                    data_info["库信息"]["data"].append({"主机": dbServer.db_mark,
                                                       "名称": key['NAME'],
                                                       "真实库": key["DATHOST"],
                                                       "主写节点": key["INDEX"],
                                                       "类型": key["TYPE"],
                                                       "空闲": key["IDLE"],
                                                       "最大连接": key["SIZE"],
                                                        "总执行":key["TOTAL_TIME"],
                                                       "RECOVERY_TIME":key["RECOVERY_TIME"]
                                                       })

                user_row = MYSQL.queryAll("show @@sql.sum.table")[1]
                for key in user_row:
                    data_info["表访问信息"]["col"] = '主机,表名,读次数K,写次数K,读写率,关联表,关联次数'
                    data_info["表访问信息"]["data"].append({"主机": dbServer.db_mark,
                                                     "表名": key['TABLE'],
                                                     "读次数K": round(float(key['R'])/1024/1024, 2),
                                                     "写次数K": round(float(key['W'])/1024/1024, 2),
                                                     "读写率": key["R%"],
                                                     "关联表": key["RELATABLE"],
                                                     "关联次数": key["RELACOUNT"]
                                                     })
                user_row = MYSQL.queryAll("show @@connection.sql")[1]
                for key in user_row:
                    data_info["连接信息"]["col"] = '主机,IP,用户,库名,开始时间,执行时间,SQL'
                    data_info["连接信息"]["data"].append({"主机": dbServer.db_mark,
                                                       "IP": key['HOST'],
                                                       "用户": key["USER"],
                                                       "库名": key["SCHEMA"],
                                                       "开始时间": datetime.datetime.utcfromtimestamp( int(str(key['START_TIME'])[:10])).strftime("%Y-%m-%d %H:%M:%S"),
                                                       "执行时间": key["EXECUTE_TIME"],
                                                       "SQL": key["SQL"]
                                                       })
                user_row = MYSQL.queryAll("show @@sql.slow")[1]
                for key in user_row:
                    data_info["慢查询信息"]["col"] = '主机,IP,用户,开始时间,执行时间,SQL'
                    data_info["慢查询信息"]["data"].append({"主机": dbServer.db_mark,
                                                      "IP": key['IP'],
                                                      "用户": key["USER"],
                                                      "开始时间": datetime.datetime.utcfromtimestamp(
                                                          int(str(key['START_TIME'])[:10])).strftime(
                                                          "%Y-%m-%d %H:%M:%S"),
                                                      "执行时间": key["EXECUTE_TIME"],
                                                      "SQL": key["SQL"]
                                                      })

            report_data["report"] = {"item": data_info, "dbtype": 'mysql'}
            # 日志数据
            logdb = settings.DATABASES['logdb']
            loginfo = Mongos(host=logdb['HOST'], port=logdb['PORT'], user=logdb['USER'], passwd=logdb['PASSWORD'], dbname=logdb['NAME'])
            sql = {"ip": ip_list, "@timestamp": {'$gte': stime, '$lt': endtime}}
            col = {"@timestamp": 1, "message": 1}
            # 取数据
            rs = loginfo.find_list(dbname='logdb', tbname='mycat', sql=sql, col=col)
            sql_info = {}
            table_info = {}
            for key in rs:
                query_sql = ''
                info = key
                # SQL匹配
                info['sql'] = re.sub("'(.*?)'|\d{2,}|\d|\#", '*', key['message'].lower())
                info['sql'] = re.sub('(\*\,){2,}|(\*\,\ ){2,}|\"(.*?)\"', '*', info['sql'])
                replace_list = ["\r\n", "\r", "\n", '\t', '##']
                for st in replace_list:
                    info['sql'] = info['sql'].replace(st, '').replace("  ,", ',').replace(", ", ',').replace("..", "")
                info['sql'] = info['sql'].replace('`', '').replace("*, *", '*').replace("* , *", '*').replace("*,*", '*').replace("**", '*')

                if len(info['sql']) > 151: info['sql'] = info['sql'][:150]
                # sql集合
                if info['sql'] in sql_info.keys():
                    sql_info[info['sql']] = {"count": sql_info[info['sql']]["count"] + 1,"sql":sql_info[info['sql']]["sql"]}
                else:
                    sql_info[info['sql']] = {"count": 1,"sql":key["message"]}
            # 合成数据
            sql_info = sorted(sql_info.items(), key=lambda e: e[1], reverse=True)
            report_data["log"] = {"table_info": "", "sql": sql_info ,"dbtype":'mycat'}
        elif data['db_type'].lower() == 'mongodb':
            # 所有服务器
            col_list1 = "sum(opcounters_query_UP)/max(UPTIME_UP)  QPS,sum(opcounters_getmore_UP)/max(UPTIME_UP) GPS,sum(opcounters_insert_UP)/max(UPTIME_UP) IPS,sum(opcounters_delete_UP)/max(UPTIME_UP) DPS,sum(connections_current) CONN,sum(opcounters_update_UP)/max(UPTIME_UP) UPS "
            data_list = [{"name": "查询", "data": []},{"name": "导出", "data": []},{"name": "插入", "data": []},{"name": "删除", "data": []},{"name": "连接", "data": []}, {"name": "更新", "data": []}]
            # SQL查询数据
            sql_all = "select ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000 unit_time," + col_list1 + " from opsmanage_mongodb_status where dbid in (" + db_list + ") and checktime>=DATE_ADD(NOW(),INTERVAL -1 day) group by ROUND(UNIX_TIMESTAMP(checktime)/60)*60000+28800000"
            # 报告数据
            data_info = {"数据库状态": {"col": '', "data": []}
                        , "内存分配": {"col": '', "data": []}
                        , "性能信息": {"col": '', "data": []} 
                        , "WT缓存": {"col": '', "data": []}
                        , "WT性能": {"col": '', "data": []} 
                        , "list": "数据库状态,内存分配,性能信息,WT缓存,WT性能"
                         }


            for dbid in serverList:
                dbServer = DataBase_Server_Config.objects.get(id=dbid)
                MYSQL = Mongos(host=dbServer.db_host, port=dbServer.db_port, user=dbServer.db_user, passwd=dbServer.db_passwd, dbname=dbServer.db_name)
                ip_list.append(dbServer.db_host)
                baseinfo_row=MYSQL.getbaseStatus(type=3)[0]
                master_row=MYSQL.getmasterStatus(type=2)
                slave_row=MYSQL.getmReplStatus(type=2)
                #return JsonResponse({"code": 200, "data": baseinfo_row }) 
                if baseinfo_row:
                    data_info["数据库状态"]["col"] = '主机,进程名,版本,角色,存储引擎,运行时间,活动连接,可用连接,网络接收GB,网络发送GB'
                    data_info["数据库状态"]["data"].append({"主机": dbServer.db_mark,
                                                      "进程名": baseinfo_row['process'],
                                                      "版本": baseinfo_row["version"],
                                                      "角色":  ("Master" if baseinfo_row["repl,ismaster"]!="False" else "slave") ,
                                                      "存储引擎": baseinfo_row["storageEngine,name"],
                                                      "运行时间": round(float(baseinfo_row["uptime"])/86400,2),
                                                      "活动连接": baseinfo_row["connections,current"],
                                                      "可用连接": baseinfo_row["connections,available"],
                                                      "网络接收GB": round(float(baseinfo_row["network,bytesIn"])/1024/1024/1024,2),
                                                      "网络发送GB": round(float(baseinfo_row["network,bytesOut"])/1024/1024/1024,2)
                                                      })
                    data_info["内存分配"]["col"] = '主机,物理内存MB,虚拟内存MB,数据映射MB,访问磁盘页,heap内存GB,分配过GB,空闲页面GB,线程最大GB,total'
                    data_info["内存分配"]["data"].append({"主机": dbServer.db_mark,
                                                      "物理内存MB": baseinfo_row['mem,resident'],
                                                      "虚拟内存MB": baseinfo_row["mem,virtual"],
                                                      "数据映射MB": baseinfo_row["mem,mapped"],
                                                      "访问磁盘页": baseinfo_row["extra_info,page_faults"],
                                                      "heap内存GB": round(float(baseinfo_row["extra_info,heap_usage_bytes"])/1024/1024/1024,2),
                                                      "分配过GB": round(float(baseinfo_row["tcmalloc,generic,current_allocated_bytes"])/1024/1024/1024,2),
                                                      "空闲页面GB":round(float(baseinfo_row["tcmalloc,tcmalloc,pageheap_free_bytes"])/1024/1024/1024,2),
                                                      "线程最大GB":round(float(baseinfo_row["tcmalloc,tcmalloc,max_total_thread_cache_bytes"])/1024/1024/1024,2)
                                                      })
                    data_info["性能信息"]["col"] = '主机,总插入数MB,总查询数MB,总更新数MB,总删除数MB,getmoreMB,其他操作MB,读锁次数GB,写锁次数GB,等代读锁GB,等代写锁GB,total'
                    data_info["性能信息"]["data"].append({"主机": dbServer.db_mark,
                                                      "总插入数MB": round(float(baseinfo_row['opcounters,insert'])/1024/1024,2),
                                                      "总查询数MB": round(float(baseinfo_row['opcounters,query'])/1024/1024,2),
                                                      "总更新数MB": round(float(baseinfo_row['opcounters,update'])/1024/1024,2),
                                                      "总删除数MB": round(float(baseinfo_row['opcounters,delete'])/1024/1024,2),
                                                      "getmoreMB": round(float(baseinfo_row['opcounters,getmore'])/1024/1024,2),
                                                      "其他操作MB": round(float(baseinfo_row['opcounters,command'])/1024/1024,2),
                                                      "读锁次数GB": round(float(baseinfo_row["locks,Global,acquireCount,r"])/1024/1024/1024,2),
                                                      "写锁次数GB": round(float(baseinfo_row["locks,Global,acquireCount,W"])/1024/1024/1024,2),
                                                      "等代读锁GB": round(float(baseinfo_row["locks,Global,acquireWaitCount,r"])/1024/1024/1024,2),
                                                      "等代写锁GB": round(float(baseinfo_row["locks,Global,acquireWaitCount,W"])/1024/1024/1024,2)
                                                      })
                    data_info["WT缓存"]["col"] = '主机,块读字节MB,块写字节MB,块读次数MB,块写次数MB,读入缓存MB,写入缓存MB,当前缓存页K,页面读入G,页面写入G,total'
                    data_info["WT缓存"]["data"].append({"主机": dbServer.db_mark,
                                                      "块读字节MB": round(float(baseinfo_row['wiredTiger,block-manager,bytes read'])/1024/1024,2),
                                                      "块写字节MB": round(float(baseinfo_row['wiredTiger,block-manager,bytes written'])/1024/1024,2),
                                                      "块读次数MB": round(float(baseinfo_row['wiredTiger,block-manager,blocks read'])/1024/1024,2),
                                                      "块写次数MB": round(float(baseinfo_row['wiredTiger,block-manager,blocks written'])/1024/1024,2),
                                                      "读入缓存MB": round(float(baseinfo_row['wiredTiger,cache,bytes read into cache'])/1024/1024,2),
                                                      "写入缓存MB": round(float(baseinfo_row['wiredTiger,cache,bytes written from cache'])/1024/1024,2),
                                                      "当前缓存页K": round(float(baseinfo_row["wiredTiger,cache,pages currently held in the cache"])/1024 ,2),
                                                      "页面读入G": round(float(baseinfo_row["wiredTiger,cache,pages read into cache"])/1024/1024/1024,2),
                                                      "页面写入G": round(float(baseinfo_row["wiredTiger,cache,pages written from cache"])/1024/1024/1024,2), 
                                                      })
                    data_info["WT性能"]["col"] = '主机,打开文件,内存分配数M,内存空闲数M,重新分配数M,读IO次数M,写IO次数M,当前事务数,活动连接,事务开始G,checkpointsG,当前运行事务数,事务最大时间,total'
                    data_info["WT性能"]["data"].append({"主机": dbServer.db_mark,
                                                      "打开文件": baseinfo_row['wiredTiger,connection,files currently open'],
                                                      "内存分配数M": round(float(baseinfo_row['wiredTiger,connection,memory allocations'])/1024/1024,2),
                                                      "内存空闲数M": round(float(baseinfo_row['wiredTiger,connection,memory frees'])/1024/1024,2),
                                                      "重新分配数M": round(float(baseinfo_row['wiredTiger,connection,memory re-allocations'])/1024/1024,2),
                                                      "读IO次数M": round(float(baseinfo_row['wiredTiger,connection,total read I/Os'])/1024/1024,2),
                                                      "写IO次数M": round(float(baseinfo_row['wiredTiger,cache,bytes written from cache'])/1024/1024,2),
                                                      "当前事务数": baseinfo_row["wiredTiger,session,open cursor count"],
                                                      "活动连接": baseinfo_row["wiredTiger,session,open session count"],
                                                      "事务开始G": round(float(baseinfo_row["wiredTiger,transaction,transaction begins"])/1024/1024/1024,2),
                                                      "checkpointsG": round(float(baseinfo_row["wiredTiger,transaction,transaction checkpoints"])/1024/1024/1024,2),
                                                      "当前运行事务数": baseinfo_row["wiredTiger,transaction,transaction checkpoint currently running"],
                                                      "事务最大时间": baseinfo_row["wiredTiger,transaction,transaction checkpoint max time (msecs)"],
                                                      })

                
            report_data["report"] = {"item": data_info, "dbtype": 'mysql'}
            # 日志数据
            logdb = settings.DATABASES['logdb']
            loginfo = Mongos(host=logdb['HOST'], port=logdb['PORT'], user=logdb['USER'], passwd=logdb['PASSWORD'],  dbname=logdb['NAME'])
            sql = {"ip": ip_list, "@timestamp": {'$gte': stime, '$lt': endtime}, "body": {"$exists": "true"}}
            col = {"body": 1, "component": 1, "message": 1 }
            # 取数据
            rs = loginfo.find_list(dbname='logdb', tbname='mongodb_log', sql=sql, col=col)
            sql_info = {}
            table_info = {}
            for key in rs:
                query_sql = ''
                info = key
                # SQL匹配
                info['sql'] = re.sub("'(.*?)'|\d{2,}|\d|\#", '*', key['body'].lower())
                info['sql'] = re.sub('(\*\,){2,}|(\*\,\ ){2,}|\"(.*?)\"', '*', info['sql'])
                replace_list = ["\r\n", "\r", "\n", '\t', '##' ]
                for st in replace_list:
                    info['sql'] = info['sql'].replace(st, '').replace("  ,", ',').replace(", ", ',').replace("..","")
                info['sql'] = info['sql'].replace('`', '').replace("*, *", '*').replace("* , *", '*').replace("*,*",'*').replace("**", '*')

                if len(key['body']) > 301:  info['sql_all'] = str(key['body'][0:250]) + '...' + str(key['body'][-50:])
                else: info['sql_all'] = key['body']
                tbname_list = key['body'].replace("  ", " ").split(" ")
                comtype=tbname_list[0]
                if tbname_list[1].find('.') > 0:
                    tbname = tbname_list[1].split(".")[1]
                    dbname = tbname_list[1].split(".")[0]
                    if tbname_list[-1].find("ms")>0 : stime = int(tbname_list[-1].split("ms")[0])
                    else:stime=0
                else:
                    tbname = tbname_list[1]
                    dbname = ''
                    if tbname_list[-1].find("ms")>0 : stime = int(tbname_list[-1].split("ms")[0])
                    else:stime=0
                #table_info
                if tbname not in sql_info.keys(): sql_info[tbname] = {}
                if len(info['sql'])>151:info['sql'] =info['sql'] [:150]
                # sql集合
                if info['sql'] in sql_info[tbname].keys():
                    if stime > sql_info[tbname][info['sql']]["max_query"]: sql_info[tbname][info['sql']]["max_query"] = stime
                    sql_info[tbname][info['sql']] = {"query_time": sql_info[tbname][info['sql']]["query_time"]+stime, "count": sql_info[tbname][info['sql']]["count"]+1, "commend": info["component"], "dbname": dbname,"max_query":sql_info[tbname][info['sql']]["max_query"],"sql":sql_info[tbname][info['sql']]["sql"]}
                else:
                    sql_info[tbname][info['sql']]={"query_time":stime,"count":1,"commend":info["component"],"dbname":dbname,"max_query":stime,"sql":info["sql_all"]}

                if tbname in table_info.keys():
                    if stime > table_info[tbname]["max_query"]: table_info[tbname]["max_query"] = stime
                    table_info[tbname] = {"query_time": stime+table_info[tbname]["query_time"],  "max_query":table_info[tbname]["max_query"] , "count": 1+table_info[tbname]["count"],"commend":info["component"],"dbname":dbname }
                else:
                    table_info[tbname] = {"query_time": stime ,  "max_query":stime , "count": 1 ,"commend":info["component"],"dbname":dbname }
            #合成数据
            table_info = sorted(table_info.items(), key=lambda e: e[1]["query_time"], reverse=True)
            sql_sort = []
            for key in table_info:
                sql_sort.append({"table": key[0], "sql": sorted(sql_info[key[0]].items(), key=lambda e: e[1]["query_time"],reverse=True)})

            report_data["log"] = {"table_info": table_info, "sql": sql_sort,"dbtype":'mongodb'}
        else:
            return JsonResponse({"code": 200, "data": {}})
        #走势图数据
        cursor.execute(sql_all)
        data_all = cursor.fetchall()
        # 数据输出
        for key in data_all:
            for i in range(len(data_list)):
                data_list[i]["data"].append([int(key[0]), float(key[i + 1])])
        # 配置图形类型
        config = { "title": {"text": "所有状态"}, "subtitle": {"text": v_dbname}, "series": data_list}
        # JSON输出
        return JsonResponse({"code": 200, "data": config, "report": report_data})


@login_required()
@permission_required('OpsManage.can_read_sql_audit_order',login_url='/noperm/')
def db_sqlorder_run(request,id):
    try:
        if request.user.is_superuser:order = Order_System.objects.get(id=id)
        else:order = Order_System.objects.filter(Q(order_user=request.user.id,id=id) | Q(order_executor=request.user.id,id=id))[0]
        incept = Inception_Server_Config.objects.get(id=1)
        if request.user.id != order.order_executor:order.prem = 0
        else:order.prem = 1
    except Exception,ex:
        logger.error(msg="执行SQL[{id}]错误: {ex}".format(id=id,ex=str(ex)))
        return render(request,'database/db_sqlorder_run.html',{"user":request.user,"errinfo":"工单不存在，或者您没有权限处理这个工单"})
    try:
        inceptRbt = Inception(
                   host=incept.db_backup_host,
                   name=order.sql_audit_order.order_db.db_name,
                   user=order.sql_audit_order.order_db.db_user,
                   passwd=order.sql_audit_order.order_db.db_passwd,
                   port=order.sql_audit_order.order_db.db_port
                   )
    except Exception,ex:
        return render(request,'database/db_sqlorder_run.html',{"user":request.user,"errinfo":"Inception配置错误"})
    if request.method == "GET":
        oscStatus = None
        sqlResultList = []
        rollBackSql = []
        order.order_user = User.objects.get(id=order.order_user).username
        order.order_executor = User.objects.get(id=order.order_executor).username
        try:
            order.sql_audit_order.order_db.db_service = Service_Assets.objects.get(id=order.sql_audit_order.order_db.db_service)
        except Exception, ex:
            order.sql_audit_order.order_db.db_service = '未知'
        if order.order_status in [5,6,9] and order.sql_audit_order.order_type=='online':
            sqlResultList = SQL_Order_Execute_Result.objects.filter(order=order.sql_audit_order)
            for ds in sqlResultList:
                if ds.backup_db.find('None') == -1:
                    result = inceptRbt.getRollBackTable(
                                                   host=incept.db_backup_host, user=incept.db_backup_user,
                                                   passwd=incept.db_backup_passwd, dbName=ds.backup_db,
                                                   port=incept.db_backup_port, sequence=str(ds.sequence).replace('\'','')
                                                   )
                    if len(ds.sqlsha) > 0:oscStatus = inceptRbt.getOscStatus(sqlSHA1=ds.sqlsha)
                    if result.get('status') == 'success' and result.get('data'):
                        tableName = result.get('data')[0]
                        rbkSql = inceptRbt.getRollBackSQL(
                                                       host=incept.db_backup_host, user=incept.db_backup_user,
                                                       passwd=incept.db_backup_passwd, dbName=ds.backup_db,
                                                       port=incept.db_backup_port, tableName=tableName,
                                                       sequence=str(ds.sequence).replace('\'',''),
                                                       )
                    else:
                        rollBackSql = ["Ops！数据库服务器 - {host} 可能未开启binlog或者未开启备份功能，获取回滚SQL失败。".format(host=order.sql_audit_order.order_db.db_host,dbname=order.sql_audit_order.order_db.db_name)]
                        return render(request,'database/db_sqlorder_run.html',{"user":request.user,"order":order,"sqlResultList":sqlResultList,"rollBackSql":rollBackSql,"rbkSql":0,"oscStatus":oscStatus})
                    if rbkSql.get('status') == 'success' and rbkSql.get('data'):
                        for sql in rbkSql.get('data'):
                            rollBackSql.append(sql[0])
        elif  order.sql_audit_order.order_type=='file':
            filePath = os.getcwd() + '/upload/' + str(order.sql_audit_order.order_file)
            with open(filePath, 'r') as f:
                order.sql_audit_order.order_sql = f.read()
        return render(request,'database/db_sqlorder_run.html',{"user":request.user,"order":order,"sqlResultList":sqlResultList,"rollBackSql":rollBackSql,"oscStatus":oscStatus})

    elif request.method == "POST":
        if request.POST.get('type') == 'exec' and order.order_status == 8 and order.prem == 1:
            try:
                count = SQL_Order_Execute_Result.objects.filter(order=order.sql_audit_order).count()
                if count > 0:return JsonResponse({'msg':"该SQL已经被执行过，请勿重复执行","code":500,'data':[]})
            except Exception,ex:
                logger.warn(msg="执行SQL[{id}]错误: {ex}".format(id=id,ex=str(ex)))
            if  order.sql_audit_order.order_type == 'online':
                try:
                    config = SQL_Audit_Control.objects.get(id=1)
                    incept = Inception(
                                       host=order.sql_audit_order.order_db.db_host,
                                       name=order.sql_audit_order.order_db.db_name,
                                       user=order.sql_audit_order.order_db.db_user,
                                       passwd=order.sql_audit_order.order_db.db_passwd,
                                       port=order.sql_audit_order.order_db.db_port
                                       )
                    if config.t_backup_sql == 0 and order.sql_audit_order.order_db.db_env == 'test':action = '--disable-remote-backup;'
                    elif config.p_backup_sql == 0 and order.sql_audit_order.order_db.db_env == 'prod':action = '--disable-remote-backup;'
                    else:action = None
                    result = incept.execSql(order.sql_audit_order.order_sql,action)
                    if result.get('status') == 'success':
                        count = 0
                        sList = []
                        for ds in result.get('data'):
                            try:
                                SQL_Order_Execute_Result.objects.create(
                                                                        order = order.sql_audit_order,
                                                                        errlevel = ds.get('errlevel'),
                                                                        stage = ds.get('stage'),
                                                                        stagestatus = ds.get('stagestatus'),
                                                                        errormessage = ds.get('errmsg'),
                                                                        sqltext =  ds.get('sql'),
                                                                        affectrow = ds.get('affected_rows'),
                                                                        sequence = ds.get('sequence'),
                                                                        backup_db = ds.get('backup_dbname'),
                                                                        execute_time = ds.get('execute_time'),
                                                                        sqlsha = ds.get('sqlsha1'),
                                                                        )
                            except Exception, ex:
                                logger.error(msg="记录SQL错误: {ex}".format(ex=str(ex)))
                            if ds.get('errlevel') > 0 and ds.get('errmsg'):count = count + 1
                            sList.append({'sql':ds.get('sql'),'row':ds.get('affected_rows'),'errmsg':ds.get('errmsg')})
                        if count > 0:
                            order.order_status = 9
                            order.save()
                            sendOrderNotice.delay(order.id,mask='【执行失败】')
                            return JsonResponse({'msg':"执行失败，请检查SQL语句","code":500,'data':sList})
                        else:
                            order.order_status = 5
                            order.save()
                            sendOrderNotice.delay(order.id,mask='【已执行】')
                            return JsonResponse({'msg':"SQL执行成功","code":200,'data':sList})
                    else:
                        return JsonResponse({'msg':result.get('errinfo'),"code":500,'data':[]})
                except Exception, ex:
                    logger.error(msg="执行SQL[{id}]错误: {ex}".format(id=id,ex=str(ex)))
                    return JsonResponse({'msg':str(ex),"code":200,'data':[]})
            elif order.sql_audit_order.order_type == 'file':
                filePath = os.getcwd() + '/upload/' + str(order.sql_audit_order.order_file)
                rc,rs = mysql.loads(
                                    host=order.sql_audit_order.order_db.db_host,
                                    dbname=order.sql_audit_order.order_db.db_name,
                                    user=order.sql_audit_order.order_db.db_user,
                                    passwd=order.sql_audit_order.order_db.db_passwd,
                                    port=order.sql_audit_order.order_db.db_port,
                                    sql=filePath
                                    )
                if rc == 0:
                    order.order_status = 8
                    order.save()
                    sendOrderNotice.delay(order.id,mask='【已执行】')
                    return JsonResponse({'msg':"SQL执行成功","code":200,'data':rs})
                else:
                    order.order_status = 9
                    order.save()
                    sendOrderNotice.delay(order.id,mask='【已失败】')
                    return JsonResponse({'msg':"SQL执行失败：{rs}".format(rs=str(rs)),"code":500,'data':[]})

        elif  request.POST.get('type') == 'rollback' and order.order_status == 5 and order.prem == 1:
            rollBackSql = []
            sqlResultList = SQL_Order_Execute_Result.objects.filter(order=order.sql_audit_order)
            for ds in sqlResultList:
                if ds.backup_db.find('None') == -1:
                    result = inceptRbt.getRollBackTable(
                                                   host=incept.db_backup_host, user=incept.db_backup_user,
                                                   passwd=incept.db_backup_passwd, dbName=ds.backup_db,
                                                   port=incept.db_backup_port, sequence=str(ds.sequence).replace('\'','')
                                                   )
                    if result.get('status') == 'success':
                        tableName = result.get('data')[0]
                        rbkSql = inceptRbt.getRollBackSQL(
                                                       host=incept.db_backup_host, user=incept.db_backup_user,
                                                       passwd=incept.db_backup_passwd, dbName=ds.backup_db,
                                                       port=incept.db_backup_port, tableName=tableName,
                                                       sequence=str(ds.sequence).replace('\'',''),
                                                       )
                    if rbkSql.get('status') == 'success':
                        for sql in rbkSql.get('data'):
                            rollBackSql.append(sql[0])
            if rollBackSql:
                rbkSql = Inception(
                                   host=order.sql_audit_order.order_db.db_host,
                                   name=order.sql_audit_order.order_db.db_name,
                                   user=order.sql_audit_order.order_db.db_user,
                                   passwd=order.sql_audit_order.order_db.db_passwd,
                                   port=order.sql_audit_order.order_db.db_port
                                   )
                for sql in rollBackSql:
                    result = rbkSql.rollback(sql)
                    if result.get('status') == 'error':#回滚时如果其中一条出现错误就停止回滚
                        return JsonResponse({'msg':"SQL回滚失败：" + result.get('errinfo'),"code":500,'data':[]})
                #回滚语句如果全部执行成功则修改状态
                order.order_status = 6
                order.save()
                sendOrderNotice.delay(order.id,mask='【已回滚】')
                return JsonResponse({'msg':"SQL回滚成功","code":200,'data':[]})
            else:
                return JsonResponse({'msg':"没有需要执行的回滚SQL语句","code":500,'data':[]})
        else:
            return JsonResponse({'msg':"SQL已经被执行","code":500,'data':[]})


@login_required()
@permission_required('OpsManage.change_sql_audit_control',login_url='/noperm/')
def db_sql_control(request):
    if request.method == "POST":
        try:
            count = SQL_Audit_Control.objects.filter(id=1).count()
        except:
            count = 0
        gList = []
        for g in request.POST.getlist('audit_group',[]):
            gList.append(g)
        if count > 0:
            try:
                SQL_Audit_Control.objects.filter(id=1).update(
                                                            t_auto_audit = request.POST.get('t_auto_audit'),
                                                            t_backup_sql = request.POST.get('t_backup_sql'), 
                                                            t_email = request.POST.get('t_email'), 
                                                            p_auto_audit = request.POST.get('p_auto_audit'), 
                                                            p_backup_sql  = request.POST.get('p_backup_sql'), 
                                                            p_email = request.POST.get('p_email'),   
                                                            audit_group = json.dumps(gList),                                                                  
                                                            )
                return JsonResponse({'msg':"修改成功","code":200,'data':[]})
            except Exception, ex:
                logger.error(msg="更新数据表[opsmanage_sql_audit_control]错误: {ex}".format(ex=str(ex)))
                return JsonResponse({'msg':"修改失败："+str(ex),"code":500,'data':[]}) 
        else:
            try:
                SQL_Audit_Control.objects.create(
                                                t_auto_audit = request.POST.get('t_auto_audit'),
                                                t_backup_sql = request.POST.get('t_backup_sql'), 
                                                t_email = request.POST.get('t_email'), 
                                                p_auto_audit = request.POST.get('p_auto_audit'), 
                                                p_backup_sql  = request.POST.get('p_backup_sql'), 
                                                p_email = request.POST.get('p_email'), 
                                                audit_group = json.dumps(gList),  
                                                )   
                return JsonResponse({'msg':"修改成功","code":200,'data':[]})
            except Exception,ex:
                logger.error(msg="写入数据表[opsmanage_sql_audit_control]错误: {ex}".format(ex=str(ex)))
                return JsonResponse({'msg':"修改失败: "+str(ex),"code":500,'data':[]}) 
            
@login_required()
@permission_required('OpsManage.can_read_sql_audit_order',login_url='/noperm/')
def db_sqlorder_osc(request,id):
    if request.method == "POST" and request.POST.get('model') == 'query':
        order = SQL_Audit_Order.objects.get(id=id)
        inceptRbt = Inception()           
        sqlResultList = SQL_Order_Execute_Result.objects.filter(order=order)
        for ds in sqlResultList:
            if ds.backup_db.find('None') == -1:
                if ds.sqlsha:
                    result = inceptRbt.getOscStatus(sqlSHA1=ds.sqlsha) 
                    if result.get('status') == 'success':
                        return JsonResponse({"code":200,"data":result.get('data')})
                    else:return JsonResponse({"code":500,"data":result.get('data')}) 
    elif request.method == "POST" and request.POST.get('model') == 'stop':
        order = SQL_Audit_Order.objects.get(id=id)
        inceptRbt = Inception()           
        sqlResultList = SQL_Order_Execute_Result.objects.filter(order=order)
        for ds in sqlResultList:
            if ds.backup_db.find('None') == -1:
                if ds.sqlsha:
                    result = inceptRbt.stopOsc(sqlSHA1=ds.sqlsha) 
                    if result.get('status') == 'success':
                        return JsonResponse({"code":200,"data":result.get('data')})
                    else:
                        return JsonResponse({"code":500,"data":result.get('errinfo')})
       
 
        
@login_required()
@permission_required('OpsManage.can_add_database_server_config',login_url='/noperm/')
def db_ops(request): 
    if request.method == "GET":
        dataBaseList = DataBase_Server_Config.objects.all()
        serviceList = Service_Assets.objects.all()
        projectList = Project_Assets.objects.all()
        return render(request,'database/db_ops.html',{"user":request.user,"dataBaseList":dataBaseList,"serviceList":serviceList,"projectList":projectList}) 
    
    elif request.method == "POST" and request.POST.get('model') == 'binlog':#通过获取数据库的binlog版本
        try:
            dbServer = DataBase_Server_Config.objects.get(id=request.POST.get('ops_db'))
        except:
            dbServer = None
        if dbServer:
            mysql = MySQLPool(host=dbServer.db_host,port=dbServer.db_port,user=dbServer.db_user,passwd=dbServer.db_passwd,dbName=dbServer.db_name)
            result = mysql.queryAll(sql='show binary logs;')
            binLogList = []
            if isinstance(result,tuple):
                for ds in result[1]:
                    binLogList.append(ds[0]) 
        return JsonResponse({'msg':"数据查询成功","code":200,'data':binLogList,'count':0})  

    elif request.method == "POST" and request.POST.get('model') == 'querydb':#根据业务类型查询数据库
        dataList = []
        dbSerlist = DataBase_Server_Config.objects.filter(db_env=request.POST.get('db_env'),db_project=request.POST.get('db_project'),db_type=request.POST.get('db_type'))
        for ds in dbSerlist:
            data = dict()
            data['id'] = ds.id
            data['db_name'] = ds.db_name
            data['db_host'] = ds.db_host
            data['db_mark'] = ds.db_mark
            dataList.append(data)
        return JsonResponse({'msg':"数据查询成功","code":200,'data':dataList})

    elif request.method == "POST" and request.POST.get('model') == 'opslist':#根据数据库类型查询操作列表
        dataList = []
        if request.POST.get('db_type')=='MySQL':
            dataList = [{"id":1,"name":"DML回滚语句"},
                        {"id":2,"name":"SQL优化建议"},
                        {"id":3,"name":"执行DQL语句"},
                        {"id":4,"name":"执行原生SQL语句"},
                        {"id":5,"name":"OSC修改表结构"}
                        ]
        elif request.POST.get('db_type')=='Redis':
            dataList = [{"id":1,"name":"导出键"},
                        {"id":2,"name":"写入键"},
                        {"id":3,"name":"执行DQL语句"},
                        {"id":4,"name":"执行原生SQL语句"}
                        ]
        elif request.POST.get('db_type')=='Mongodb':
            dataList = [{"id":1,"name":"导出表数据"},
                        {"id":2,"name":"SQL优化建议"},
                        {"id":3,"name":"执行DQL语句"},
                        {"id":4,"name":"执行原生SQL语句"}
                        ]
        elif request.POST.get('db_type')=='MyCAT':
            dataList = [{"id":1,"name":"应用配置"},
                        {"id":2,"name":"清除统计信息"},
                        {"id":3,"name":"执行DQL语句"},
                        {"id":4,"name":"执行原生SQL语句"}
                        ]
        else:
            dataList = []
        return JsonResponse({'msg':"数据查询成功","code":200,'data':dataList})
    elif request.method == "POST" and request.POST.get('model') == 'opsinfo' :  
        if request.POST.get('db_type')=='MySQL':
            if request.method == "POST" and request.POST.get('opsTag') == '1':#通过binlog获取DML
                sqlList = []
                try:
                    dbServer = DataBase_Server_Config.objects.get(id=int(request.POST.get('dbId')))
                except Exception, ex:
                    sqlList.append(ex)
                    dbServer = None
                if dbServer:
                    conn_setting = {'host': dbServer.db_host, 'port': dbServer.db_port, 'user': dbServer.db_user, 'passwd': dbServer.db_passwd, 'charset': 'utf8'}
                    #flashback=True获取DML回滚语句
                    binlog2sql = Binlog2sql(connection_settings=conn_setting,             
                                            back_interval=1.0, only_schemas=dbServer.db_name,
                                            end_file='', end_pos=0, start_pos=4,
                                            flashback=True,only_tables='', 
                                            no_pk=False, only_dml=True,stop_never=False, 
                                            sql_type=['INSERT', 'UPDATE', 'DELETE'], 
                                            start_file=request.POST.get('binlog'), 
                                            start_time=request.POST.get('startime'), 
                                            stop_time=request.POST.get('endtime'),)
                    sqlList = binlog2sql.process_binlog()
                return JsonResponse({'msg':"获取binlog数据成功","code":200,'data':sqlList,'tag':1}) 
            elif request.method == "POST" and request.POST.get('opsTag') == '2':#优化建议
                try:
                    dbServer = DataBase_Server_Config.objects.get(id=int(request.POST.get('dbId')))
                except Exception, ex:
                    dbServer = None   
                if dbServer:    
                    #先通过Inception审核语句
                    incept = Inception(
                                       host=dbServer.db_host,name=dbServer.db_name,
                                       user=dbServer.db_user,passwd=dbServer.db_passwd,
                                       port=dbServer.db_port
                                       )
                    result = incept.checkSql(request.POST.get('sql'))
                    if result.get('status') == 'success':
                        count = 0
                        errStr = ''
                        for ds in result.get('data'):
                            if ds.get('errlevel') > 0 and ds.get('errmsg'):
                                count = count + 1
                                errStr = errStr +ds.get('errmsg')
                        if count > 0:return JsonResponse({'msg':"审核失败，请检查SQL语句","code":500,'data':errStr,'tag':2}) 
                    else:
                        return JsonResponse({'msg':"Inception审核失败","code":500,'data':result.get('errinfo'),'tag':2})             
                    status,result = base.getSQLAdvisor(host=dbServer.db_host, user=dbServer.db_user,
                                                       passwd=dbServer.db_passwd, dbname=dbServer.db_name, 
                                                       sql=request.POST.get('sql'),port=dbServer.db_port)
                    if status == 0:
                        return JsonResponse({'msg':"获取SQL优化数据成功","code":200,'data':result,'tag':2}) 
                    else:
                        return JsonResponse({'msg':"获取SQL优化数据失败","code":500,'data':result,'tag':2}) 
                else:return JsonResponse({'msg':"获取SQL优化数据失败","code":500,'data':[],'tag':2})
                
            elif request.method == "POST" and request.POST.get('opsTag') == '3':#执行DQL
                if re.match(r"^(\s*)?select(\S+)?(.*)", request.POST.get('sql').lower()):            
                    try:
                        dbServer = DataBase_Server_Config.objects.get(id=int(request.POST.get('dbId')))
                    except Exception, ex:
                        dbServer = None 
                    if dbServer:
                        mysql = MySQLPool(host=dbServer.db_host,port=dbServer.db_port,user=dbServer.db_user,passwd=dbServer.db_passwd,dbName=dbServer.db_name)
                        result = mysql.queryMany(sql=request.POST.get('sql'),num=1000)
                        if isinstance(result,str):
                            recordSQL.delay(exe_user=str(request.user),exe_db=dbServer,exe_sql=request.POST.get('sql'),exec_status=0,exe_result=str) 
                            return JsonResponse({'msg':"数据查询失败","code":500,'data':result,'tag':3})  
                    recordSQL.delay(exe_user=str(request.user),exe_db=dbServer,exe_sql=request.POST.get('sql'),exec_status=1,exe_result=None)  
                    return JsonResponse({'msg':"数据查询成功","code":200,'data':{"colName":result[2],"dataList":result[1]},'count':result[0],'tag':3})  
                else:return JsonResponse({'msg':"数据查询失败","code":500,'data':"不是DQL类型语句",'tag':3}) 
                
            elif request.method == "POST" and request.POST.get('opsTag') == '4' and request.user.is_superuser:#执行原生SQL         
                try:
                    dbServer = DataBase_Server_Config.objects.get(id=int(request.POST.get('dbId')))
                except Exception, ex:
                    dbServer = None 
                if dbServer:
                    mysql = MySQLPool(host=dbServer.db_host,port=dbServer.db_port,user=dbServer.db_user,passwd=dbServer.db_passwd,dbName=dbServer.db_name)
                    result = mysql.execute(sql=request.POST.get('sql'),num=1000)
                    if isinstance(result,str):
                        recordSQL.delay(exe_user=str(request.user),exe_db=dbServer,exe_sql=request.POST.get('sql'),exec_status=0,exe_result=result) 
                        return JsonResponse({'msg':"数据查询失败","code":500,'data':result,'tag':3}) 
                    else:
                        if result[0] == 0:return JsonResponse({'msg':"数据查询成功","code":200,'data':"SQL执行成功",'tag':3})
                    recordSQL.delay(exe_user=str(request.user),exe_db=dbServer,exe_sql=request.POST.get('sql'),exec_status=1,exe_result=None)    
                    return JsonResponse({'msg':"数据查询成功","code":200,'data':{"colName":result[2],"dataList":result[1]},'count':result[0],'tag':3}) 
                else:return JsonResponse({'msg':"数据查询失败","code":500,'data':str(ex),'tag':3}) 
            else:return JsonResponse({'msg':"数据操作失败","code":500,'data':"您可能没有权限操作此项目",'tag':3})   
        elif request.POST.get('db_type')=='Redis':
            dataList = [{"id":1,"name":"导出键"},
                        {"id":2,"name":"写入键"},
                        {"id":3,"name":"执行DQL语句"},
                        {"id":4,"name":"执行原生SQL语句"}
                        ]
        elif request.POST.get('db_type')=='Mongodb':
            dataList = [{"id":1,"name":"导出表数据"},
                        {"id":2,"name":"SQL优化建议"},
                        {"id":3,"name":"执行DQL语句"},
                        {"id":4,"name":"执行原生SQL语句"}
                        ]
        elif request.POST.get('db_type')=='MyCAT':
            dataList = [{"id":1,"name":"应用配置"},
                        {"id":2,"name":"清除统计信息"},
                        {"id":3,"name":"执行DQL语句"},
                        {"id":4,"name":"执行原生SQL语句"}
                        ]
        else:
            dataList = []
        return JsonResponse({'msg':"数据查询成功","code":200,'data':dataList})    
    
    
@login_required()
@permission_required('OpsManage.can_read_sql_execute_histroy',login_url='/noperm/')
def db_sql_logs(request,page):  
    if request.method == "GET":
        allSqlLogsList = SQL_Execute_Histroy.objects.all().order_by('-id')[0:2000]
        paginator = Paginator(allSqlLogsList, 25)          
        try:
            sqlLogsList = paginator.page(page)
        except PageNotAnInteger:
            sqlLogsList = paginator.page(1)
        except EmptyPage:
            sqlLogsList = paginator.page(paginator.num_pages)        
        return render(request,'database/db_logs.html',{"user":request.user,"sqlLogsList":sqlLogsList}) 
    
@login_required()
@permission_required('OpsManage.can_add_database_server_list',login_url='/noperm/')
def db_sql_dumps(request): 
    if request.method == "POST":#执行原生SQL  
        try:
            dbServer = DataBase_Server_Config.objects.get(id=int(request.POST.get('dbId')))
        except Exception, ex:
            dbServer = None 
        if dbServer:
            mysql = MySQLPool(host=dbServer.db_host,port=dbServer.db_port,user=dbServer.db_user,passwd=dbServer.db_passwd,dbName=dbServer.db_name)
            result = mysql.execute(sql=request.POST.get('sql'),num=1000)
            if isinstance(result,str):
                return JsonResponse({'msg':"不支持导出功能","code":500,'data':result,'tag':3}) 
            else:
                if result[0] == 0:return JsonResponse({'msg':"不支持导出功能","code":200,'data':"SQL执行成功",'tag':3})  
            file_name = "query_result.csv"    
            with open(file_name,"w") as csvfile: 
                writer = csv.writer(csvfile,dialect='excel')
                #先写入columns_name
                writer.writerow(result[2])
                #写入多行用writerows
                for ds in result[1]:
                    writer.writerows([list(ds)])               
            response = StreamingHttpResponse(base.file_iterator(file_name))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename="{file_name}'.format(file_name=file_name)
            return response                           