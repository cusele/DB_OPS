# -*- coding=utf-8 -*-
'''
监控文件 
@version:1.0 2018年8月1日
'''
#加载类库
import redis
from django.conf import settings
import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
import urlparse 
import urllib
import json
import bson
from pymongo import MongoClient
import sys

#通用配置
class APBase(object):
    REDSI_POOL = 10000
    MYSQL_POOLS = dict()
    MYSQLLIST = {
        "Aborted_clients": 1,
        "Aborted_connects": 1,
        "Binlog_cache_disk_use": 1,
        "Binlog_cache_use": 1,
        "Bytes_received": 1,
        "Bytes_sent": 1,
        "Com_commit": 1,
        "Com_rollback": 1,
        "Connections": 1,
        "Created_tmp_disk_tables": 1,
        "Created_tmp_files": 1,
        "Created_tmp_tables": 1,
        "Innodb_buffer_pool_bytes_data": 0,
        "Innodb_buffer_pool_bytes_dirty": 0,
        "Innodb_buffer_pool_pages_flushed": 1,
        "Innodb_buffer_pool_pages_free": 0,
        "Innodb_buffer_pool_pages_misc": 0,
        "Innodb_buffer_pool_pages_total": 0,
        "innodb_buffer_pool_reads": 1,
        "innodb_buffer_pool_read_ahead": 0,
        "innodb_buffer_pool_read_requests": 1,
        "Innodb_buffer_pool_wait_free": 1,
        "Innodb_buffer_pool_write_requests": 1,
        "Innodb_data_fsyncs": 1,
        "innodb_data_read": 1,
        "innodb_data_reads": 1,
        "Innodb_data_writes": 1,
        "Innodb_data_written": 1,
        "Innodb_dblwr_pages_written": 1,
        "Innodb_dblwr_writes": 1,
        "Innodb_log_writes": 1,
        "Innodb_log_write_requests": 1,
        "Innodb_os_log_fsyncs": 1,
        "Innodb_os_log_written": 1,
        "Innodb_pages_created": 1,
        "Innodb_pages_read": 1,
        "Innodb_pages_written": 1,
        "Innodb_page_size": 0,
        "Innodb_rows_deleted": 1,
        "Innodb_rows_inserted": 1,
        "Innodb_rows_read": 1,
        "Innodb_rows_updated": 1,
        "Innodb_row_lock_current_waits": 1,
        "Innodb_row_lock_time": 1,
        "Innodb_row_lock_waits": 0,
        "Key_blocks_unused": 0,
        "Key_blocks_used": 0,
        "Key_reads": 1,
        "Key_read_requests": 1,
        "Key_writes": 1,
        "Key_write_requests": 1,
        "Max_used_connections": 1,
        "Opened_files": 1,
        "Opened_tables": 1,
        "Open_files": 0,
        "Open_tables": 0,
        "Qcache_hits": 1,
        "Qcache_inserts": 1,
        "Qcache_not_cached": 1,
        "Qcache_queries_in_cache": 1,
        "Qcache_total_blocks": 0,
        "Queries": 1,
        "Questions": 1,
        "Select_full_join": 1,
        "Select_full_range_join": 1,
        "Select_scan": 1,
        "Slow_queries": 1,
        "Sort_merge_passes": 1,
        "Sort_range": 1,
        "Sort_rows": 1,
        "Sort_scan": 1,
        "Table_locks_immediate": 1,
        "Table_locks_waited": 1,
        "Table_open_cache_hits": 1,
        "Table_open_cache_misses": 1,
        "Threads_cached": 0,
        "Threads_connected": 0,
        "Threads_created": 1,
        "Threads_running": 0,
        "Uptime": 1
    }
    PXCKEYSLIST = [
        'wsrep_cluster_status', 'wsrep_connected', 'wsrep_incoming_addresses',
        'wsrep_cluster_size', 'wsrep_cluster_status', 'wsrep_ready', 'wsrep_local_recv_queue', 'wsrep_local_send_queue',
        'wsrep_local_state_comment',
    ]
    SLAVEKEYSLIST = [ 'seconds_behind_master', 'slave_io_running', 'slave_sql_running' 'relay_log_pos']
    MDBLIST = {"uptime":{"col":"uptime","values":1},
                "connections,current":{"col":"connections_current","values":0},
                "connections,available":{"col":"connections_available","values":0},
                "connections,totalCreated":{"col":"connections_totalCreated","values":1},
                "metrics,commands,authenticate,failed":{"col":"metrics_commands_authenticate_failed","values":1},
                "locks,Database,acquireCount,r":{"col":"locks_Database_acquireCount_r","values":1},
                "locks,Database,acquireCount,w":{"col":"locks_Database_acquireCount_w","values":1},
                "locks,Database,acquireWaitCount,r":{"col":"locks_Database_acquireWaitCount_r","values":1},
                "locks,Database,acquireWaitCount,w":{"col":"locks_Database_acquireWaitCount_w","values":1},
                "network,bytesIn":{"col":"network_bytesIn","values":1},
                "network,bytesOut":{"col":"network_bytesOut","values":1},
                "network,numRequests":{"col":"network_numRequests","values":1},
                "opcounters,insert":{"col":"opcounters_insert","values":1},
                "opcounters,query":{"col":"opcounters_query","values":1},
                "opcounters,update":{"col":"opcounters_update","values":1},
                "opcounters,delete":{"col":"opcounters_delete","values":1},
                "opcounters,getmore":{"col":"opcounters_getmore","values":1},
                "opcounters,command":{"col":"opcounters_command","values":1},
                "tcmalloc,generic,current_allocated_bytes":{"col":"tcmalloc_generic_current_allocated_bytes","values":0},
                "tcmalloc,tcmalloc,pageheap_free_bytes":{"col":"tcmalloc_tcmalloc_pageheap_free_bytes","values":0},
                "tcmalloc,tcmalloc,pageheap_unmapped_bytes":{"col":"tcmalloc_tcmalloc_pageheap_unmapped_bytes","values":0},
                "mem,resident":{"col":"mem_resident","values":0},
                "mem,virtual":{"col":"mem_virtual","values":0},
                "wiredTiger,connection,total read I/Os":{"col":"wiredTiger_connection_totalreadIOs","values":1},
                "wiredTiger,connection,total write I/Os":{"col":"wiredTiger_connection_totalwriteIOs","values":1},
                "wiredTiger,transaction,transaction checkpoints":{"col":"wiredTiger_transaction_transaction_checkpoints","values":1}
               }
    REDISLIST = {
        "connected_clients":0,
        "blocked_clients":0,
        "used_memory":0,
        "used_memory_rss":0,
        "used_memory_peak":0,
        "used_memory_lua":0,
        "aof_current_size":1,
        "aof_base_size":1,
        "aof_pending_bio_fsync":0,
        "aof_delayed_fsync":1,
        "total_connections_received":1,
        "total_commands_processed":1,
        "instantaneous_ops_per_sec":0,
        "total_net_input_bytes":1,
        "total_net_output_bytes":1,
        "instantaneous_input_kbps":0,
        "instantaneous_output_kbps":0,
        "rejected_connections":1,
        "sync_full":1,
        "sync_partial_ok":1,
        "sync_partial_err":1,
        "expired_keys":1,
        "evicted_keys":1,
        "keyspace_hits":1,
        "keyspace_misses":1,
        "latest_fork_usec":0,
        "connected_slaves":1,
        "master_repl_offset":1,
        "repl_backlog_size":1,
        "used_cpu_sys":1,
        "used_cpu_user":1,
        "used_cpu_sys_children":1,
        "used_cpu_user_children":0,
        "keyss":1,
        "expires":0,
        "avg_ttl":0,
        "uptime_in_seconds":1
    }
    MyCATLIST = {
        "NET_IN":1,
        "NET_OUT":1,
        "REACT_COUNT":1,
        "R_QUEUE":0,
        "W_QUEUE":0,
        "FREE_BUFFER":0,
        "TOTAL_BUFFER":0,
        "BU_PERCENT":0,
        "BU_WARNS":1,
        "FC_COUNT":1,
        "BC_COUNT":1,
        "SQL_SUM_R":1,
        "SQL_SUM_W":1,
        "ACTIVE_COUNT":0,
        "TASK_QUEUE_SIZE":0,
        "COMPLETED_TASK":1,
        "TOTAL_TASK":1,
        "CACHE_CUR":0,
        "CACHE_ACCESS":1,
        "CACHE_HIT":1,
        "CACHE_PUT":1,
        "CACHE_MAX":0,
        "CONN_ACTIVE":0,
        "CONN_IDLE":0,
        "CONN_EXECUTE":1,
        "RS_CODE":0,
        "INDEX":0
    }


#MySQL连接
class MySQL(object):
    def __init__(self, host, port, dbname, user, passwd):
        self._conn = self.connect(host, port, dbname, user, passwd)
        self._cursor = self._conn.cursor()

    def connect(self, host, port, dbname, user, passwd):
        try:
            conn = MySQLdb.connect(host, user, passwd, dbname, port, cursorclass=MySQLdb.cursors.DictCursor)
            return conn
        except MySQLdb.Error, ex:
            return False

    def execute(self, sql, num=1000):
        try:
            count = 0
            result = None
            count = self._cursor.execute(sql)
            index = self._cursor.description
            colName = []
            if index:
                for i in index:
                    colName.append(i[0])
            result = self._cursor.fetchmany(size=num)
            self._conn.commit()
            return (count, result, colName)
        except Exception, ex:
            self.conn.rollback()
            count = 0
            result = None
        finally:
            return count, result

    def queryAll(self, sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchall()
            return count, result
        except Exception, ex:
            count = 0
            result = None
        finally:
            return count, result

    def queryOne(self, sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchone()
            return count, result
        except Exception, ex:
            result = None
        finally:
            return result

    def getVariables(self):
        rc, rs = self.queryAll(sql='show global variables;')
        dataList = []
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList.append(rcd)
        data_dict = {}
        for item in dataList:
            data_dict[item[0]] = item[1]
        return data_dict

    def getStatus(self):
        rc, rs = self.queryAll(sql='show global status;')
        dataList = []
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList.append(rcd)
        data_dict = {}
        for item in dataList:
            data_dict[item[0]] = item[1]
        return data_dict

    def getWaitThreads(self):
        rs = self.queryOne(
            sql="select count(1) as count from information_schema.processlist where state <> '' and user <> 'repl' and time > 2;")
        if rs != None:
            return rs
        else:
            return {}

    def getMasterSatus(self):
        rs = self.queryOne(sql="show master status;")
        if rs != None:
            return rs
        else:
            return {}

    def getReplStatus(self):
        rs = self.queryOne(sql='show slave status;')
        if rs != None:
            return rs
        else:
            return {}

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception, ex:
            print ex

#MyCAT连接
class MyCAT(object):
    def __init__(self, host, port, dbname, user, passwd):
        self._conn = self.connect(host, port, dbname, user, passwd)
        self._cursor = self._conn.cursor()

    def connect(self, host, port, dbname, user, passwd):
        try:
            conn = MySQLdb.connect(host, user, passwd, dbname, port, cursorclass=MySQLdb.cursors.DictCursor)
            return conn
        except MySQLdb.Error, ex:
            return False

    def execute(self, sql, num=1000):
        try:
            count = self._cursor.execute(sql)
            index = self._cursor.description
            colName = []
            if index:
                for i in index:
                    colName.append(i[0])
            result = self._cursor.fetchmany(size=num)
            self._conn.commit()
            return (count, result, colName)
        except Exception, ex:
            self.conn.rollback()
            count = 0
            result = None
        finally:
            return count, result

    def queryAll(self, sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchall()
            return count, result
        except Exception, ex:
            count = 0
            result = None
        finally:
            return count, result

    def queryOne(self, sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchone()
            return count, result
        except Exception, ex:
            result = None
        finally:
            return result

    def getVariables(self, type=1):
        # 填写列名
        dataList = {}
        for key, value in APBase.MyCATLIST.items():
            if key == 'RS_INFO':
                dataList[key] = ''
            else:
                dataList[key] = 0
            # SQL 统计信息
        rc, rs = self.queryAll(sql='show @@sql.sum;')
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList['SQL_SUM_R'] = dataList['SQL_SUM_R'] + int(rcd['R'])
                dataList['SQL_SUM_W'] = dataList['SQL_SUM_W'] + int(rcd['W'])
        # 进程信息
        rc, rs = self.queryAll(sql='show @@processor;')
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList['NET_IN'] = dataList['NET_IN'] + int(rcd['NET_IN'])
                dataList['NET_OUT'] = dataList['NET_OUT'] + int(rcd['NET_OUT'])
                dataList['REACT_COUNT'] = dataList['REACT_COUNT'] + int(rcd['REACT_COUNT'])
                dataList['R_QUEUE'] = dataList['R_QUEUE'] + int(rcd['R_QUEUE'])
                dataList['W_QUEUE'] = dataList['W_QUEUE'] + int(rcd['W_QUEUE'])
                dataList['FREE_BUFFER'] = dataList['FREE_BUFFER'] + int(rcd['FREE_BUFFER'])
                dataList['TOTAL_BUFFER'] = dataList['TOTAL_BUFFER'] + int(rcd['TOTAL_BUFFER'])
                dataList['BU_WARNS'] = dataList['BU_WARNS'] + int(rcd['BU_WARNS'])
                dataList['FC_COUNT'] = dataList['FC_COUNT'] + int(rcd['FC_COUNT'])
                dataList['BC_COUNT'] = dataList['BC_COUNT'] + int(rcd['BC_COUNT'])
            dataList["BU_PERCENT"] = 100 - round(dataList["FREE_BUFFER"] / dataList['TOTAL_BUFFER'], 2) * 100;
        # 线程池的执行情况
        rc, rs = self.queryAll(sql='show @@threadpool;')
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList['ACTIVE_COUNT'] = dataList['ACTIVE_COUNT'] + int(rcd['ACTIVE_COUNT'])
                dataList['TASK_QUEUE_SIZE'] = dataList['TASK_QUEUE_SIZE'] + int(rcd['TASK_QUEUE_SIZE'])
                dataList['COMPLETED_TASK'] = dataList['COMPLETED_TASK'] + int(rcd['COMPLETED_TASK'])
                dataList['TOTAL_TASK'] = dataList['TOTAL_TASK'] + int(rcd['TOTAL_TASK'])

        # 缓存情况
        rc, rs = self.queryAll(sql='show @@cache;')
        if rc != 0 and rs != None:
            for rcd in rs:
                if rcd['CACHE'] == 'SQLRouteCache':
                    dataList['CACHE_CUR'] = dataList['CACHE_CUR'] + int(rcd['CUR'])
                    dataList['CACHE_ACCESS'] = dataList['CACHE_ACCESS'] + int(rcd['ACCESS'])
                    dataList['CACHE_HIT'] = dataList['CACHE_HIT'] + int(rcd['HIT'])
                    dataList['CACHE_PUT'] = dataList['CACHE_PUT'] + int(rcd['PUT'])
                    dataList['CACHE_MAX'] = dataList['CACHE_MAX'] + int(rcd['MAX'])

        # 连接情况
        rc, rs = self.queryAll(sql='show @@datanode;')
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList['CONN_ACTIVE'] = dataList['CONN_ACTIVE'] + int(rcd['ACTIVE'])
                dataList['CONN_IDLE'] = dataList['CONN_IDLE'] + int(rcd['IDLE'])
                dataList['CONN_EXECUTE'] = dataList['CONN_EXECUTE'] + int(rcd['EXECUTE'])
                dataList['INDEX'] = dataList['INDEX'] + int(rcd['INDEX'])

        # 主机心跳状态
        rc, rs = self.queryAll(sql='show @@heartbeat;')
        if rc != 0 and rs != None:
            for rcd in rs:
                if rcd['RS_CODE'] != 1:
                    dataList['RS_CODE'] = dataList['RS_CODE'] + 1
                    dataList['RS_INFO'] = dataList['RS_INFO'] + ' DB:' + str(rcd['HOST']) + ' RS_CODE:' + str(
                        rcd['RS_CODE']);

        data_dict = []
        if type == 1:
            for key, value in dataList.items():
                data_dict.append({"name": APBase.MyCATLIST[key], "value": dataList[key]})
            return data_dict
        else: 
            return dataList

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception, ex:
            print ex

#MongoDB连接
class Mongos(object):
    def __init__(self, host, port, dbname, user, passwd):
        url = 'mongodb://' + str(user) + ':' + urllib.quote_plus(passwd) + '@' + str(host) + ':' + str(
            port) + '/' + str(dbname)
        self._conn = self.connects(url)
        # self.db = self.conn.admin
        # self.rs = self.db.command('replSetGetStatus')

    def connects(self, url):
        try:
            conn = MongoClient(host=url)
            return conn
        except 'mongodb connect false !', ex:
            return False
            # return url

    def mongo_info_list(self, info, keyname):
        rs = {}
        keyname1 = ''
        if isinstance(info, dict):
            for key, value in info.items():
                keyname1 = ''
                if keyname == '':
                    keyname1 = key
                else:
                    keyname1 = keyname + ',' + key
                if isinstance(value, dict):
                    rs = dict(rs.items() + self.mongo_info_list(value, keyname1).items())
                elif isinstance(value, list):
                    rs = dict(rs.items() + self.mongo_info_list(value, keyname1).items())
                else:
                    rs[keyname1] = str(value)
        elif isinstance(info, list):
            for key in info:
                if isinstance(key, dict):
                    rs = dict(rs.items() + self.mongo_info_list(key, keyname).items())
                elif isinstance(key, list):
                    rs = dict(rs.items() + self.mongo_info_list(key, keyname).items())
                else:
                    rs[keyname] = str(key)
        else:
            rs[keyname] = str(info)
        return rs

    def mongo_info_list1(self, info, keyname):
        rs = []
        keyname1 = ''
        if isinstance(info, dict):
            for key, value in info.items():
                keyname1 = ''
                if keyname == '':
                    keyname1 = key
                else:
                    keyname1 = keyname + ',' + key
                if isinstance(value, dict):
                    rs.append(self.mongo_info_list1(value, keyname1))
                elif isinstance(value, list):
                    rs.append(self.mongo_info_list1(value, keyname1))
                else:
                    rs.append({keyname1: str(value)})
        elif isinstance(info, list):
            for key in info:
                if isinstance(key, dict):
                    rs.append(self.mongo_info_list1(key, keyname))
                elif isinstance(key, list):
                    rs.append(self.mongo_info_list1(key, keyname))
                else:
                    rs.append({keyname: str(key)})
        else:
            rs.append({keyname: str(info)})
        return rs

    def getbaseStatus(self, type=1):
        self.db = self._conn.admin
        # info = self.db.command(bson.son.SON([('serverStatus',1),('repl',1)]))
        info = self.db.command('serverStatus')
        rs = []
        info_dict = {}
        info_dict = (self.mongo_info_list(info, ''))
        data_list = {}
        if isinstance(info_dict, dict):
            for key, value in info_dict.items():
                data_list[key] = value
        if type == 2:
            for key, value in data_list.items():
                rs.append({"name": key, "value": value})
        else:
            for key, value in APBase.MDBLIST.items():
                if key in data_list.keys(): rs.append({"name": value, "value": data_list[key]})
        rs = sorted(rs)
        if rs != None:
            return rs
        else:
            return {}

    def getmasterStatus(self, type=1):
        self.db = self._conn.admin
        info = self.db.command(bson.son.SON([('serverStatus', 1), ('repl', 1)]))["repl"]["sources"]
        rs = []
        info_dict = {}
        info_dict = (self.mongo_info_list(info, ''))
        data_list = {}
        if isinstance(info_dict, dict):
            for key, value in info_dict.items():
                data_list["repl,sources," + key] = value
        if type == 2:
            for key, value in data_list.items():
                rs.append({"name": key, "value": value})
        else:
            for key, value in APBase.MDBLIST.items():
                if key in data_list.keys(): rs.append({"name": value, "value": data_list[key]})
        rs = sorted(rs)
        if rs != None:
            return rs
        else:
            return {}

    def getmReplStatus(self, type=1):
        self.db = self._conn.admin
        info = self.db.command(bson.son.SON([('serverStatus', 1), ('repl', 2)]))["repl"]["replicationProgress"]
        rs = []
        data_list = {}
        for ls in info:
            if ls["host"] != ":27017":
                for key, value in ls.items():
                    if type == 2:
                        keyname = "repl,replicationProgress," + key
                        rs.append({"name": keyname, "value": str(value)})
                    else:
                        if "repl,replicationProgress," + key in APBase.MDBLIST:
                            keyname = APBase.MDBLIST["repl,replicationProgress," + key]
                            rs.append({"name": keyname, "value": str(value)})

        if rs != None:
            return rs
        else:
            return {}

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception, ex:
            print ex

#Redis连接
class Rediss(object):
    def __init__(self, host, port, dbname, user, passwd):
        self._conn = self.connects(host, port, dbname, user, passwd)

    def connects(self, host, port, dbname, user, passwd):
        try:
            conn = redis.StrictRedis(host=host, port=port, db=dbname, password=passwd, encoding='utf-8',
                                     decode_responses=True)
            return conn
        except 'redis connect false !', ex:
            return False
            # return url

    def getbaseStatus(self, type=1):
        info = self._conn.info()
        rs = []
        dblist = ['db0', 'db1', 'db2', 'db3', 'db4', 'db5', 'db6', 'db7', 'db8', 'db9', 'db10', 'db11', 'db12', 'db13',
                  'db14', 'db15', 'db16']
        keyss = 0
        expires = 0
        avg_ttle = 0
        data_list = {}
        # 数据处理
        if isinstance(info, dict):
            for key, value in info.items():
                if key in dblist:
                    keyss = keyss + int(value['keys'])
                    expires = expires + int(value['expires'])
                    avg_ttle = avg_ttle + int(value['avg_ttl']) * int(value['keys'])
                else:
                    data_list[key] = value

            data_list['keyss'] = keyss
            data_list['expires'] = expires
            data_list['avg_ttl'] = avg_ttle / keyss
        if type == 2:
            for key, value in data_list.items():
                rs.append({"name": key, "value": value})
        else:
            # 替换中文
            for key, value in APBase.REDISLIST.items():
                if key in data_list.keys(): rs.append({"name": value, "value": data_list[key]})
        rs = sorted(rs)
        if rs != None:
            return rs
        else:
            return {}

    def getmasterStatus(self, type=1):
        info = self._conn.info('replication')
        masterkey = {
            "master_host": " 主机IP",
            "master_port": " 主机端口",
            "master_sync_in_progress": "主从延迟",
            "master_link_status": "复制状态"
        }
        rs = []
        data_list = {}
        if isinstance(info, dict):
            for key, value in info.items():
                data_list[key] = value

        if type == 2:
            for key, value in data_list.items():
                rs.append({"name": key, "value": value})
        else:
            # 替换中文
            for key, value in masterkey.items():
                if key in data_list.keys(): rs.append({"name": value, "value": data_list[key]})
        if rs != None:
            return rs
        else:
            return {}

    def getmReplStatus(self, type=1):
        info = self._conn.info('replication')
        rs = []
        slavekey = {
            "ip": " 从机IP",
            "lag": "主从延迟",
            "port": " 从机端口",
            "state": "复制状态"
        }
        data_list = {}
        if isinstance(info, dict):
            count = 1
            for key, value in info.items():
                if isinstance(value, dict):
                    if type == 2:
                        rs.append({"name": key, "value": value})
                    else:
                        for key1, value1 in value.items():
                            if key1 in slavekey.keys(): rs.append(
                                {"name": slavekey[key1] + str(count), "value": value1})
                        count = count + 1
        if rs != None:
            return rs
        else:
            return {}

    def getClusterStatus(self, type=1):
        rs = []
        cluster_status = self._conn.info('cluster')['cluster_enabled']
        if cluster_status == 1:
            info = self._conn.cluster('nodes')
            clusterkey = {
                "ip": " 节点IP",
                "slots": "主从延迟",
                "port": " 从机端口",
                "flags": "角色信息",
                "connected": "状态"
            }
            if isinstance(info, dict):
                count = 1
                for key, value in info.items():
                    if type == 2:
                        rs.append({"name": key, "value": value})
                    else:
                        rs.append({"name": clusterkey['ip'] + str(count), "value": key})
                    if isinstance(value, dict):
                        for key1, value1 in value.items():
                            if type == 1:
                                if key1 in clusterkey.keys(): rs.append(
                                    {"name": clusterkey[key1] + str(count), "value": value1})
                    count = count + 1
                    # rs.append(info)
        if rs != None:
            return rs
        else:
            return {}

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception, ex:
            print ex


if __name__ == '__main__':
    #获取参数
    dbid = sys.argv[1]
    if dbid.isdigit()==False:sys.exit()
    #数据库配置
    monitor_db = {
        'dbname': 'opsmanage',
        'user': 'ops_user',
        'port': 13306,
        'passwd': 'ops_password',
        'host': '127.0.0.1'
        }
    #连接数据
    db_conn = MySQL(host=monitor_db['host'], port=monitor_db['port'], dbname=monitor_db['dbname'], user=monitor_db['user'], passwd=monitor_db['passwd'] )
    dbid_info  = db_conn.queryOne("SELECT id,  db_type, db_name, db_host, db_mode, db_user, db_passwd, db_port FROM  opsmanage_database_server_config WHERE id="+str(dbid))

    if dbid_info==None:sys.exit()
    elif dbid_info['db_type']=='mysql':
        #MySQL处理
        dbid_old = db_conn.queryOne("SELECT * FROM  opsmanage_mysql_status WHERE dbid="+str(dbid)+" AND checktime>DATE_ADD(NOW(),INTERVAL -1 HOUR) ORDER BY id DESC LIMIT 1 ")

        #插入监控信息
        sql_in="INSERT INTO opsmanage_mysql_status(dbid,checktime"
        sql_value=") values("+str(dbid)+",now()"

        obj_conn=MySQL(host=dbid_info['db_host'], port=dbid_info['db_port'], dbname=dbid_info['db_name'], user=dbid_info['db_user'], passwd=dbid_info['db_passwd'] )
        obj_base=obj_conn.execute("SHOW GLOBAL STATUS;")
        for k in obj_base[1]:
            if k['Variable_name'] in APBase.MYSQLLIST.keys():
                sql_in = sql_in + ','+ str(k['Variable_name'])
                sql_value = sql_value + ','+str(k['Value'])
                if APBase.MYSQLLIST[k['Variable_name']] == 1 :
                    if dbid_old==None:value=k['Value']
                    else:
                        #print(k['Variable_name']+'_UP')
                        if k['Variable_name']+'_UP' in dbid_old.keys():value=round(float(k['Value']))-round(float(dbid_old[k['Variable_name']]))
                        else : value=k['Value']
                    if value < 0 : value=0
                    sql_in = sql_in + ','+ str(k['Variable_name']) + '_UP'
                    sql_value = sql_value + ','+ str(value)
        #复制信息
        obj_slave = obj_conn.execute("SHOW SLAVE STATUS;")
        if obj_slave[1]!=None:
            io_run=1
            sql_run=1
            sendtime=0
            slog=''
            for k in obj_slave[1]:
                if k['Slave_IO_Running'] != 'Yes': io_run=2
                if k['Slave_SQL_Running'] != 'Yes': sql_run = 2
                if k['Seconds_Behind_Master'] >sendtime: sendtime = k['Seconds_Behind_Master']
                slog = slog+'|'+str(k['Channel_Name'])+'|'+str(k['Slave_SQL_Running_State'])+'|'+str(k['Last_IO_Error'])+'|'+str(k['Last_SQL_Errno'])
            sql_in = sql_in + ', iorun ,sqlrun,sendtime,slog'
            sql_value = sql_value + ','+ str(io_run)+','+str(sql_run)+','+str(sendtime)+',"'+slog.replace('"','')+'"'
        #拼接SQL并写入
        sql_all=sql_in+sql_value+');'
        db_conn.execute(sql_all)
    elif dbid_info['db_type']=='Redis':
        #Redis处理
        dbid_old = db_conn.queryOne("SELECT * FROM  opsmanage_redis_status WHERE dbid=" + str(dbid) + " AND checktime>DATE_ADD(NOW(),INTERVAL -1 HOUR) ORDER BY id DESC LIMIT 1 ")

        # 插入监控信息
        sql_in = "INSERT INTO opsmanage_redis_status(dbid,checktime"
        sql_value = ") values(" + str(dbid) + ",now()"

        obj_conn = Rediss(host=dbid_info['db_host'], port=dbid_info['db_port'], dbname=dbid_info['db_name'], user=dbid_info['db_user'], passwd=dbid_info['db_passwd'])
        obj_base = obj_conn.getbaseStatus(type=2) 
        for k in obj_base :
            if k['name'] in APBase.REDISLIST.keys():
                sql_in = sql_in + ',' + str(k['name'])
                sql_value = sql_value + ',' + str(k['value'])
                if APBase.REDISLIST[k['name']] == 1:
                    if dbid_old == None:
                        value = k['value']
                    else:
                        # print(k['Variable_name']+'_UP')
                        if k['name'] + '_UP' in dbid_old.keys():
                            value = round(float(k['value'])) - round(float(dbid_old[k['name']]))
                        else:
                            value = k['value']
                    if value < 0: value = 0
                    sql_in = sql_in + ',' + str(k['name']) + '_UP'
                    sql_value = sql_value + ',' + str(value)
        # 复制信息
        obj_slave = obj_conn.getmasterStatus(type=2)
        if obj_slave  != None:
            is_master = 0 #是否主机 0 不是 1 是
            master_status = 2 #主机连接状态 1 正常 2 异常
            for k in obj_slave:
                if k['name']=='role' and k['value']=='slave':is_master = 0
                elif k['name']=='role' and k['value']=='master':is_master = 1
                if k['name']=='master_link_status' and k['value']=='up':master_status=1
            if is_master == 1: master_status = 1
            sql_in = sql_in + ', is_master ,master_status'
            sql_value = sql_value + ',' + str(is_master) + ',' + str(master_status)
        # 拼接SQL并写入
        sql_all = sql_in + sql_value + ');'
        db_conn.execute(sql_all)
    elif dbid_info['db_type'] == 'Mongodb':
        # Redis处理
        dbid_old = db_conn.queryOne("SELECT * FROM  opsmanage_mongodb_status WHERE dbid=" + str(  dbid) + " AND checktime>DATE_ADD(NOW(),INTERVAL -1 HOUR) ORDER BY id DESC LIMIT 1 ")

        # 插入监控信息
        sql_in = "INSERT INTO opsmanage_mongodb_status(dbid,checktime"
        sql_value = ") values(" + str(dbid) + ",now()"

        obj_conn = Mongos(host=dbid_info['db_host'], port=dbid_info['db_port'], dbname=dbid_info['db_name'], user=dbid_info['db_user'], passwd=dbid_info['db_passwd'])
        obj_base = obj_conn.getbaseStatus(type=2)
        for k in obj_base:
            if k['name'] in APBase.MDBLIST.keys():
                sql_in = sql_in + ',' + str(APBase.MDBLIST[k['name']]['col'])
                sql_value = sql_value + ',' + str(k['value'])
                if APBase.MDBLIST[k['name']]['values'] == 1:
                    if dbid_old == None:
                        value = k['value']
                    else:
                        # print(k['Variable_name']+'_UP')
                        if APBase.MDBLIST[k['name']]['col'] + '_UP' in dbid_old.keys():
                            value = round(float(k['value'])) - round(float(dbid_old[APBase.MDBLIST[k['name']]['col']]))
                        else:
                            value = k['value']
                    if value < 0: value = 0
                    sql_in = sql_in + ',' + str(APBase.MDBLIST[k['name']]['col']) + '_UP'
                    sql_value = sql_value + ',' + str(value)
        # 复制信息
        obj_slave = obj_conn.getmasterStatus(type=2)
        if obj_slave != None :
            syncedTotime = 0  # 是否主机 0 不是 1 是
            for k in obj_slave:
                if k['name'] == 'repl,sources,syncedTo,inc' :syncedTotime=k['value']
            sql_in = sql_in + ', syncedTotime'
            sql_value = sql_value + ',' + str(syncedTotime)
        # 拼接SQL并写入
        sql_all = sql_in + sql_value + ');'
        db_conn.execute(sql_all)
        #print(sql_all)
    elif dbid_info['db_type']=='MyCAT':
        #Redis处理
        dbid_old = db_conn.queryOne("SELECT * FROM  opsmanage_mycat_status WHERE dbid=" + str(dbid) + " AND checktime>DATE_ADD(NOW(),INTERVAL -1 HOUR) ORDER BY id DESC LIMIT 1 ")

        # 插入监控信息
        sql_in = "INSERT INTO opsmanage_mycat_status(dbid,checktime"
        sql_value = ") values(" + str(dbid) + ",now()"

        obj_conn = MyCAT(host=dbid_info['db_host'], port=dbid_info['db_port'], dbname=dbid_info['db_name'], user=dbid_info['db_user'], passwd=dbid_info['db_passwd'])
        obj_base = obj_conn.getVariables(type=2)
        #print(obj_base)
        #sys.exit()
        for k,v in obj_base.items() :
            if k in APBase.MyCATLIST.keys():
                sql_in = sql_in + ',' + str(k)
                sql_value = sql_value + ',' + str(v)
                if APBase.MyCATLIST[k] == 1:
                    if dbid_old == None:
                        value = v
                    else:
                        if k + '_UP' in dbid_old.keys():value = round(float(v)) - round(float(dbid_old[k]))
                        else:value =v
                    if value < 0: value = 0
                    sql_in = sql_in + ',' + str(k) + '_UP'
                    sql_value = sql_value + ',' + str(value)
        #update_up
        UPTIME_OLD=0
        UPTIME_UP=0
        if 'UPTIME' in dbid_old.keys():
            if dbid_old['UPTIME'] != None: UPTIME_OLD=dbid_old['UPTIME']
        sql_in = sql_in + ',' + 'UPTIME,UPTIME_UP'
        sql_value = sql_value + ', UNIX_TIMESTAMP(),UNIX_TIMESTAMP()-'+str(UPTIME_OLD)

        # 拼接SQL并写入
        sql_all = sql_in + sql_value + ');'
        db_conn.execute(sql_all.replace('INDEX','`INDEX`'))
        print(sql_all.replace('INDEX','`INDEX`'))