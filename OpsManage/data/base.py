# -*- coding=utf-8 -*-
'''
应用基类（每次应用启动时，都必须调用基类的初始化方法）
@author: welliam.cao<303350019@qq.com> 
@version:1.0 2017年4月12日
'''
import redis
from django.conf import settings
import MySQLdb  
from MySQLdb.cursors import DictCursor  
from DBUtils.PooledDB import PooledDB  
from OpsManage.utils.logger import logger
import urlparse
import urllib
import bson
from pymongo import MongoClient


class APBase(object):
    REDSI_POOL = 10000
    MYSQL_POOLS = dict()
    BASEKEYSLIST = [
                'uptime','slave_running','opened_files','opened_tables','connections','threads_connected',
                'binlog_format','expire_logs_days','log_bin','slow_query_log','connections','threads_connected',
                'slow_launch_time','version'
                ]   
    PXCKEYSLIST = [
                'wsrep_cluster_status','wsrep_connected','wsrep_incoming_addresses',
                'wsrep_cluster_size','wsrep_cluster_status','wsrep_ready','wsrep_local_recv_queue','wsrep_local_send_queue',
                'wsrep_local_state_comment',               
            ]  
    SLAVEKEYSLIST = [
                  'slave_io_state','master_host','master_user','master_port','connect_retry','master_log_file',
                  'read_master_log_pos','relay_master_log_file','exec_master_log_pos','seconds_behind_master',
                  'slave_io_running','slave_sql_running','replicate_do_db','slave_sql_running_state','replicate_ignore_db',
                  'relay_log_pos'
            ]
    MDBLIST = { "uptime":"运行时间",
                 "connections,current":"活动状态的连接数",
                 "connections,available":"剩余多少可供连接",
                 "connections,totalCreated":"总连接数",
                 "metrics,commands,authenticate,failed":"认证失败次数",
                 "locks,Database,acquireCount,r":"库读锁次数",
                 "locks,Database,acquireCount,w":"库写锁次数",
                 "locks,Database,acquireWaitCount,r":"库等代读锁次数",
                 "locks,Database,acquireWaitCount,w":"库等代写锁次数",
                 "network,bytesIn":"网络接收字节数",
                 "network,bytesOut":"活动状态的连接数",
                 "network,numRequests":"网络请求数",
                 "opcounters,insert":"启动后总插入数",
                 "opcounters,query":"启动后总查询数",
                 "opcounters,update":"启动后总更新数",
                 "opcounters,delete":"启动后总删除数",
                 "opcounters,getmore":"启动后执行getMore次数",
                 "opcounters,command":"启动后其他操作的次数",
                 "tcmalloc,generic,current_allocated_bytes":"已经分配过的字节数",
                 "tcmalloc,tcmalloc,pageheap_free_bytes":"空闲页面字节数",
                 "tcmalloc,tcmalloc,pageheap_unmapped_bytes":"未分配页面字节数",
                 "mem,resident":"物理内存消耗单位M",
                 "mem,virtual":"虚拟内存消耗单位M",
                 "wiredTiger,connection,total read I/Os":"总读IO次数",
                 "wiredTiger,connection,total write I/Os":"总写IO次数",
                 "wiredTiger,transaction,transaction checkpoints":"事务检查点",
                 "repl,replicationProgress,host":"Slave服务器",
                 "repl,replicationProgress,rid": "服务器RID",
                 "repl,sources,host": "Master服务器",
                 "repl,sources,syncedTo,time":"最后同步时间(+8H)",
                 "repl,sources,syncedTo,inc": "同步延迟"
                }
    REDISLIST = {
                "role": " 角色",
                "slave_read_only": " 只读从机",
                "connected_slaves": " 从机数量",
                "connected_clients": " 连接的客户端数量",
                "blocked_clients": "正在等待阻塞命令",
                "used_memory": "分配的内存总量",
                "used_memory_rss": "分配的内存总量(包括内存碎片)",
                "used_memory_peak": "使用的物理内存峰值",
                "used_memory_lua": "Lua引擎所使用的内存大小",
                "aof_current_size": "aof当前大小",
                "aof_base_size": "aof上次启动或rewrite的大小",
                "aof_pending_bio_fsync": "后台IO队列中等待fsync任务的个数",
                "aof_delayed_fsync": "延迟的fsync计数器 TODO",
                "total_connections_received": "运行以来连接过的客户端的总数量",
                "total_commands_processed": "运行以来执行过的命令的总数量",
                "instantaneous_ops_per_sec": "每秒执行的命令个数",
                "total_net_input_bytes": "总输入网络流量",
                "total_net_output_bytes": "总输出网络流量",
                "instantaneous_input_kbps": "网络实时进口速率",
                "instantaneous_output_kbps": "网络实时出口速率",
                "rejected_connections": "拒绝连接的个数",
                "sync_full": "完全同步次数",
                "sync_partial_ok": "部分同步成功数",
                "sync_partial_err": "部分同步失败数",
                "expired_keys": "过期的key的总数",
                "evicted_keys": "删除过的key的数量",
                "keyspace_hits": "命中key 的次数",
                "keyspace_misses": "没命中key 的次数",
                "latest_fork_usec": "上次的fork操作使用的时间(单位ms)",
                "connected_slaves": "连接从机数量",
                "master_repl_offset": "数据同步偏移量",
                "repl_backlog_size": "后台日志大小",
                "used_cpu_sys": "系统cpu使用量",
                "used_cpu_user": "用户cpu使用量",
                "used_cpu_sys_children": "后台进程的sys cpu使用率",
                "used_cpu_user_children": "后台进程的user cpu使用率",
                "keyss": "KEY个数",
                "expires": "过期KEY个数",
                "avg_ttl": "平均过期时间",
                "uptime_in_seconds": " 启动时间"
                }
    MyCATLIST = {
            "NET_IN": "网络进数据",
            "NET_OUT": "网络出数据",
            "REACT_COUNT": "作用SQL数量",
            "R_QUEUE": " IO读队列",
            "W_QUEUE": "IO写队列",
            "FREE_BUFFER": "空余缓存",
            "TOTAL_BUFFER": "总缓存",
            "BU_PERCENT": "缓存使用率",
            "BU_WARNS": "创建BUFFER",
            "FC_COUNT": "FC统计",
            "BC_COUNT": "BC统计",
            "SQL_SUM_R": "SQL统计读",
            "INDEX":"主写节点",
            "SQL_SUM_W": "SQL统计写",
            "ACTIVE_COUNT": "线程积压",
            "TASK_QUEUE_SIZE": "线程池待处理SQL",
            "COMPLETED_TASK": "线程池已完成的SQL",
            "TOTAL_TASK": "线程池总的SQL",
            "CACHE_CUR": "当前缓存中数量",
            "CACHE_ACCESS": "缓存连接次数",
            "CACHE_HIT": "缓存命中次数",
            "CACHE_PUT": "写缓存次数",
            "CACHE_MAX": "缓存最大数",
            "CONN_ACTIVE": "连接使用数",
            "CONN_IDLE": "连接空闲数",
            "CONN_EXECUTE": "连接执行数",
            "RS_CODE": "DB异常数",
            "RS_INFO": "DB异常信息"
        }
    @staticmethod
    def getRedisConnection(db):
        '''根据数据源标识获取Redis连接池'''
        if db==APBase.REDSI_POOL:
            args = settings.REDSI_KWARGS_LPUSH
            if settings.REDSI_LPUSH_POOL == None:
                settings.REDSI_LPUSH_POOL = redis.ConnectionPool(host=args.get('host'), port=args.get('port'), db=args.get('db'))
            pools = settings.REDSI_LPUSH_POOL  
        connection = redis.Redis(connection_pool=pools)
        return connection


class MySQLPool(APBase):
    def __init__(self,host,port,user,passwd,dbName,):
        self.poolKeys = host+dbName+str(port)
        if self.poolKeys not in MySQLPool.MYSQL_POOLS.keys():
            self._conn = self._getTupleConn(host,port,user,passwd,dbName)
            MySQLPool.MYSQL_POOLS[self.poolKeys] = self._conn
        self._conn = MySQLPool.MYSQL_POOLS.get(self.poolKeys)
        if not isinstance(self._conn,str):self._cursor = self._conn.cursor()

    def _getDictConn(self,host,port,user,passwd,dbName):
        '''返回字典类型结果集'''
        if APBase.MYSQL_POOLS.get(self.poolKeys) is None:
            try:
                pool = PooledDB(creator=MySQLdb, mincached=1 , maxcached=20 ,
                                      host=host , port=port , user=user , passwd=passwd ,
                                      db=dbName,use_unicode=False,charset='utf8',
                                      cursorclass=DictCursor)
                APBase.MYSQL_POOLS[self.poolKeys] = pool
                return APBase.MYSQL_POOLS.get(self.poolKeys).connection()
            except Exception, ex:
                logger.error(msg="创建字典类型连接池失败: {ex}".format(ex=ex))
                return str(ex)

    def _getTupleConn(self,host,port,user,passwd,dbName):
        '''返回列表类型结果集'''
        if APBase.MYSQL_POOLS.get(self.poolKeys) is None:
            try:
                pool = PooledDB(creator=MySQLdb, mincached=1 , maxcached=20 ,
                                      host=host , port=port , user=user , passwd=passwd ,
                                      db=dbName,use_unicode=False,charset='utf8')
                APBase.MYSQL_POOLS[self.poolKeys] = pool
                return APBase.MYSQL_POOLS.get(self.poolKeys).connection()
            except Exception, ex:
                logger.error(msg="创建列表类型连接池失败: {ex}".format(ex=ex))
                return str(ex)

    def queryAll(self,sql):
        if isinstance(self._conn,str):return self._conn
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchall()
            return (count,result)
        except Exception,ex:
            logger.error(msg="MySQL查询失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            return str(ex)


    def queryOne(self,sql):
        if isinstance(self._conn,str):return self._conn
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchone()
            return (count,result)
        except Exception,ex:
            logger.error(msg="MySQL查询失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            return str(ex)



    def queryMany(self,sql,num,param=None):
        if isinstance(self._conn,str):return self._conn
        """ 
        @summary: 执行查询，并取出num条结果 
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来 
        @param num:取得的结果条数 
        @return: result list/boolean 查询到的结果集 
        """
        try:
            count = self._cursor.execute(sql,param)
            index = self._cursor.description
            colName = []
            for i in index:
                colName.append(i[0])
            result = self._cursor.fetchmany(size=num)
            return (count,result,colName)
        except Exception,ex:
            logger.error(msg="MySQL查询失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            return str(ex)

    def execute(self,sql,num=1000):
        if isinstance(self._conn,str):return self._conn
        try:
            count = self._cursor.execute(sql)
            index = self._cursor.description
            colName = []
            if index:
                for i in index:
                    colName.append(i[0])
            result = self._cursor.fetchmany(size=num)
            self._conn.commit()
            return (count,result,colName)
        except Exception, ex:
            logger.error(msg="MySQL执行sql失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            return str(ex)

    def getStatus(self):
        status = self.execute(sql='show status;')
        baseList = []
        pxcList = []
        if isinstance(status, tuple):
            for ds in status[1]:
                data = {}
                data['value'] = ds[1]
                data['name'] = ds[0].capitalize()
                if ds[0].lower() in APBase.BASEKEYSLIST:baseList.append(data)
                if ds[0].lower() in APBase.PXCKEYSLIST:pxcList.append(data)
        return baseList,pxcList

    def getGlobalStatus(self):
        baseList = []
        logs = self.execute(sql='show global variables;')
        if isinstance(logs, tuple):
            for ds in logs[1]:
                data = {}
                if ds[0].lower() in APBase.BASEKEYSLIST:
                    data['value'] = ds[1]
                    data['name'] = ds[0].capitalize()
                    baseList.append(data)
        return baseList

    def getMasterStatus(self):
        masterList = []
        master_status = self.execute(sql='show master status;')
        slave_host = self.execute(sql="SELECT host FROM INFORMATION_SCHEMA.PROCESSLIST WHERE COMMAND like 'Binlog Dump%';")
        if isinstance(master_status, tuple):
            if master_status[1]:
                count = 0
                for ds in master_status[2]:
                    data = {}
                    data["name"] = ds
                    data["value"] = master_status[1][0][count]
                    count = count + 1
                    masterList.append(data)
        if isinstance(slave_host, tuple):
            if slave_host[1]:
                sList = []
                for ds in slave_host[1]:
                    sList.append(ds[0])
                masterList.append({"name":"Slave","value":sList})
        return  masterList


    def getSlaveStatus(self):
        slaveList = []
        slaveStatus = self.execute(sql="show slave status;")
        if isinstance(slaveStatus, tuple):
            if slaveStatus[1]:
                for ds1 in slaveStatus[1]:
                    count = 0
                    for ds in slaveStatus[2]:
                        data = {}
                        if ds.lower() in APBase.SLAVEKEYSLIST:
                            data["name"] = ds
                            #data["value"] = slaveStatus[1][rows_id][count]
                            data["value"] = ds1[count]
                            slaveList.append(data)
                        count = count + 1
        return slaveList

    def close(self,isEnd=1):
        """ 
        @summary: 释放连接池资源 
        """
        try:
            self._cursor.close()
            self._conn.close()
        except:
            pass

class MySQL(object):
    def __init__(self,host,port,dbname,user,passwd):
        self._conn = self.connect(host, port, dbname, user, passwd)
        self._cursor = self._conn.cursor()

    def connect(self,host,port,dbname,user,passwd):
        try:
            conn = MySQLdb.connect(host,user,passwd,dbname,port)
            conn.execute('set names utf8');
            return conn
        except MySQLdb.Error,ex:
            return False

    def execute(self,sql,num=1000):
        try:
            count = self._cursor.execute(sql)
            index = self._cursor.description
            colName = []
            if index:
                for i in index:
                    colName.append(i[0])
            result = self._cursor.fetchmany(size=num)
            self._conn.commit()
            return (count,result,colName)
        except Exception, ex:
            logger.error(msg="MySQL执行失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            self.conn.rollback()
            count = 0
            result = None
        finally:
            return count,result


    def queryAll(self,sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchall()
            return count,result
        except Exception,ex:
            logger.error(msg="MySQL查询失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            count = 0
            result = None
        finally:
            return count, result

    def queryOne(self,sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchone()
            return count,result
        except Exception,ex:
            logger.error(msg="MySQL查询失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            result = None
        finally:
            return result

    def getVariables(self):
        rc, rs =  self.queryAll(sql='show global variables;')
        dataList = []
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList.append(rcd)
        data_dict={}
        for item in dataList:
            data_dict[item[0]] = item[1]
        return data_dict

    def getStatus(self):
        rc, rs = self.queryAll(sql='show global status;')
        dataList = []
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList.append(rcd)
        data_dict={}
        for item in dataList:
            data_dict[item[0]] = item[1]
        return data_dict

    def getWaitThreads(self):
        rs = self.queryOne(sql="select count(1) as count from information_schema.processlist where state <> '' and user <> 'repl' and time > 2;")
        if rs != None:return rs
        else:return {}

    def getMasterSatus(self):
        rs = self.queryOne(sql="show master status;")
        if rs != None:return rs
        else:return {}

    def getReplStatus(self):
        rs = self.queryOne(sql='show slave status;')
        if rs != None:return rs
        else:return {}

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception,ex:
            print ex


class MyCAT(object):
    def __init__(self,host,port,dbname,user,passwd):
        self._conn = self.connect(host, port, dbname, user, passwd)
        self._cursor = self._conn.cursor()

    def connect(self,host,port,dbname,user,passwd):
        try:
            conn = MySQLdb.connect(host,user,passwd,dbname,port,cursorclass=MySQLdb.cursors.DictCursor,charset="utf8")
            return conn
        except MySQLdb.Error,ex:
            return False

    def execute(self,sql,num=1000):
        try:
            count = self._cursor.execute(sql)
            index = self._cursor.description
            colName = []
            if index:
                for i in index:
                    colName.append(i[0])
            result = self._cursor.fetchmany(size=num)
            self._conn.commit()
            return (count,result,colName)
        except Exception, ex:
            logger.error(msg="MySQL执行失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            self.conn.rollback()
            count = 0
            result = None
        finally:
            return count,result


    def queryAll(self,sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchall()
            return count,result
        except Exception,ex:
            logger.error(msg="MySQL查询失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            count = 0
            result = None
        finally:
            return count, result

    def queryOne(self,sql):
        try:
            count = self._cursor.execute(sql)
            result = self._cursor.fetchone()
            return count,result
        except Exception,ex:
            logger.error(msg="MySQL查询失败: {ex} sql:{sql}".format(ex=ex,sql=sql))
            result = None
        finally:
            return result

    def getVariables(self,type=1):
        #填写列名
        dataList = {}
        for key ,value in APBase.MyCATLIST.items():
            if key == 'RS_INFO':dataList[key]=''
            else:dataList[key]=0 
        #SQL 统计信息
        rc, rs =  self.queryAll(sql='show @@sql.sum;')
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList['SQL_SUM_R']=dataList['SQL_SUM_R']+int(rcd['R'])
                dataList['SQL_SUM_W']=dataList['SQL_SUM_W']+int(rcd['W'])
        #进程信息
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
            dataList["BU_PERCENT"] = 100 - round(dataList["FREE_BUFFER"] /dataList['TOTAL_BUFFER'], 2)*100;
        #线程池的执行情况 
        rc, rs = self.queryAll(sql='show @@threadpool;')
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList['ACTIVE_COUNT'] = dataList['ACTIVE_COUNT'] + int(rcd['ACTIVE_COUNT'])
                dataList['TASK_QUEUE_SIZE'] = dataList['TASK_QUEUE_SIZE'] + int(rcd['TASK_QUEUE_SIZE'])
                dataList['COMPLETED_TASK'] = dataList['COMPLETED_TASK'] + int(rcd['COMPLETED_TASK'])
                dataList['TOTAL_TASK'] = dataList['TOTAL_TASK'] + int(rcd['TOTAL_TASK'])

        #缓存情况
        rc, rs = self.queryAll(sql='show @@cache;')
        if rc != 0 and rs != None:
            for rcd in rs:
                if rcd['CACHE'] == 'SQLRouteCache':
                    dataList['CACHE_CUR'] = dataList['CACHE_CUR'] + int(rcd['CUR'])
                    dataList['CACHE_ACCESS'] = dataList['CACHE_ACCESS'] + int(rcd['ACCESS'])
                    dataList['CACHE_HIT'] = dataList['CACHE_HIT'] + int(rcd['HIT'])
                    dataList['CACHE_PUT'] = dataList['CACHE_PUT'] + int(rcd['PUT'])
                    dataList['CACHE_MAX'] = dataList['CACHE_MAX'] + int(rcd['MAX'])

        #连接情况
        rc, rs = self.queryAll(sql='show @@datanode;')
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList['CONN_ACTIVE'] = dataList['CONN_ACTIVE'] + int(rcd['ACTIVE'])
                dataList['CONN_IDLE'] = dataList['CONN_IDLE'] + int(rcd['IDLE'])
                dataList['CONN_EXECUTE'] = dataList['CONN_EXECUTE'] + int(rcd['EXECUTE'])
                dataList['INDEX'] = dataList['INDEX'] + int(rcd['INDEX'])

        #主机心跳状态
        rc, rs = self.queryAll(sql='show @@heartbeat;')
        if rc != 0 and rs != None:
            for rcd in rs:
                if rcd['RS_CODE'] != 1:
                    dataList['RS_CODE'] = dataList['RS_CODE'] + 1
                    dataList['RS_INFO'] = dataList['RS_INFO'] +' DB:'+ str(rcd['HOST'])+' RS_CODE:'+str(rcd['RS_CODE']);
        
        data_dict=[]
        if type == 1 :
            for key,value in dataList.items():
                data_dict.append({"name":APBase.MyCATLIST[key],"value":dataList[key]})
        else:
            data_dict.append(dataList)
        return data_dict

    def getglobalVariables(self):
        rc, rs = self.queryAll(sql='show global variables')
        dataList = {}
        if rc != 0 and rs != None:
            for rcd in rs:
                dataList[str(rcd["Variable_name"].upper())]= rcd["Value"]
        return dataList

    def getglobalstatus(self):
        rc, rs = self.queryAll(sql='show global status')
        dataList = {}
        if rc != 0 and rs != None:
            for rcd in rs:
                if rcd["Value"].isdigit()==False:
                    dataList[str(rcd["Variable_name"].upper())]=  rcd["Value"]
                else:
                    dataList[str(rcd["Variable_name"].upper())] = float(rcd["Value"])
        return dataList
    
    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception,ex:
            print ex


class Mongos(object):
    def __init__(self, host, port, dbname, user, passwd):
        url = 'mongodb://' + str(user) + ':' + urllib.quote_plus(passwd) + '@' + str(host) + ':' + str(port) + '/' + str(dbname)
        self._conn = self.connects(url)
        #self.db = self.conn.admin
        #self.rs = self.db.command('replSetGetStatus')

    def connects(self, url):
        try:
            conn = MongoClient( host=url)
            return conn
        except 'mongodb connect false !', ex:
            return False
            # return url

    def  mongo_info_list(self,info, keyname):
        rs = {}
        keyname1 = ''
        if isinstance(info, dict):
            for key, value in info.items():
                keyname1 = ''
                if keyname == '':keyname1=key
                else: keyname1= keyname + ',' + key
                if isinstance(value, dict):
                    rs =dict(rs.items()+self.mongo_info_list(value, keyname1).items())
                elif isinstance(value, list):
                    rs =dict(rs.items() + self.mongo_info_list(value, keyname1).items())
                else:
                    rs[keyname1] = str(value)
        elif isinstance(info, list):
            for key in info:
                if isinstance(key, dict):
                    rs=dict(rs.items() + self.mongo_info_list(key, keyname).items())
                elif isinstance(key, list):
                    rs =dict(rs.items() + self.mongo_info_list(key, keyname).items())
                else:
                    rs[keyname]=str(key)
        else:
            rs[keyname] = str(info)  
        return rs

    def mongo_info_list1(self, info, keyname):
        rs = []
        keyname1=''
        if isinstance(info, dict):
            for key, value in info.items():
                keyname1 = ''
                if keyname == '': keyname1 = key
                else: keyname1 = keyname + ',' + key
                if isinstance(value, dict):
                    rs.append(self.mongo_info_list1(value, keyname1))
                elif isinstance(value, list):
                    rs.append(self.mongo_info_list1(value, keyname1))
                else:
                    rs.append({keyname1:str(value)})
        elif isinstance(info, list):
            for key in info:
                if isinstance(key, dict):
                    rs.append( self.mongo_info_list1(key, keyname))
                elif isinstance(key, list):
                    rs.append(self.mongo_info_list1(key, keyname))
                else:
                    rs.append({keyname:str(key)})
        else:
            rs.append({keyname:str(info)})
        return rs

    def getbaseStatus(self,type=1):
        self.db = self._conn.admin
        #info = self.db.command(bson.son.SON([('serverStatus',1),('repl',1)]))
        info = self.db.command( 'serverStatus' )
        rs=[]
        info_dict={}
        info_dict=(self.mongo_info_list(info,''))
        data_list= {}
        if isinstance(info_dict, dict):
            for key,value in info_dict.items():
                data_list[key]=value
        if type==2 :
            for key,value in data_list.items():
                rs.append({"name":key,"value":value})
        elif type==3 :
            rs.append(info_dict)
        else:
            for key, value in APBase.MDBLIST.items():
                if key in data_list.keys(): rs.append({"name": value, "value": data_list[key]})
        rs = sorted(rs)
        if rs != None:
            return rs
        else:
            return {}

    def getmasterStatus(self,type=1):
        self.db = self._conn.admin
        info = self.db.command(bson.son.SON([('serverStatus',1),('repl',1)]))["repl"]["sources"]
        rs = []
        info_dict = {}
        info_dict = (self.mongo_info_list(info, ''))
        data_list = {}
        if isinstance(info_dict, dict):
            for key, value in info_dict.items():
                data_list["repl,sources,"+key] = value
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

    def getmReplStatus(self,type=1):
        self.db = self._conn.admin
        info = self.db.command(bson.son.SON([('serverStatus',1),('repl',2)]))["repl"]["replicationProgress"]
        rs = []
        data_list = {}
        for ls in info:
            if ls["host"]!=":27017":
                for key, value in  ls.items():
                    if type==2 :
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

    def find_list(self, dbname='logdb',tbname='mysql_slow',sql='',col=''):
        if sql=='' or col=='' :
            return {}
        db = self._conn[dbname]
        rs=[]
        for rows in  db[tbname].find(sql,col) :
            data={}
            for key,value in col.items():
                data[key]=rows[key]
            rs.append(data)
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


class Rediss(object):
    def __init__(self, host, port, dbname, user, passwd):
        self._conn = self.connects(host, port, dbname, user, passwd)

    def connects(self, host, port, dbname, user, passwd):
        try:
            conn = redis.StrictRedis(host=host, port=port, db=dbname,  password=passwd, encoding='utf-8', decode_responses=True)
            return conn
        except 'redis connect false !', ex:
            return False
            # return url



    def getbaseStatus(self,type=1):
        info = self._conn.info()
        rs = []
        dblist=['db0','db1','db2','db3','db4','db5','db6','db7','db8','db9','db10','db11','db12','db13','db14','db15','db16']
        keyss = 0
        expires=0
        avg_ttle=0
        data_list = {}
        #数据处理
        if isinstance(info, dict):
            for key, value in info.items():
                if key in dblist:
                    keyss=keyss+int(value['keys'])
                    expires=expires+int(value['expires'])
                    avg_ttle=avg_ttle+int(value['avg_ttl'])*int(value['keys'])
                else:
                    data_list[key]= value

            data_list['keyss']= keyss
            data_list['expires'] = expires
            data_list['avg_ttl'] = avg_ttle/keyss
        if type==2 :
            for key, value in data_list.items():
                rs.append({"name": key, "value": value})
        elif type==3:
            rs.append(data_list)
        else:
            #替换中文
            for key, value in APBase.REDISLIST.items():
                if key in data_list.keys(): rs.append({"name":value,"value":data_list[key]})
        rs=sorted(rs)
        if rs != None:
            return rs
        else:
            return {}

    def getmasterStatus(self,type=1):
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
            if type == 2:
                for key, value in info.items():
                    rs.append({"name": key, "value": value})
            if type == 3:
                for key, value in masterkey.items():
                    if key in info.keys():  data_list[value]=info[key]
                rs.append(data_list)
            else:
                # 替换中文
                for key, value in masterkey.items():
                    if key in info.keys(): rs.append({"name": value, "value": info[key]})
        if rs != None:
            return rs
        else:
            return {}

    def getmReplStatus(self,type=1):
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
            count = 0
            for key, value in info.items():
                if isinstance(value ,dict):
                    if type == 2:
                        rs.append({"name": key, "value": value})
                    if type == 3:
                        data_list[count] = {}
                        for key1, value1 in value.items():
                            if key1 in slavekey.keys(): data_list[count][slavekey[key1]]=value1
                        count = count + 1
                    else:
                        for key1, value1 in value.items():
                            if key1 in slavekey.keys(): rs.append({"name": slavekey[key1]+str(count), "value": value1})
                        count = count + 1
            if type == 3:rs.append(data_list)
        if rs != None:
            return rs
        else:
            return {}

    def getClusterStatus(self, type=1):
        rs = []
        cluster_status=self._conn.info('cluster')['cluster_enabled']
        if cluster_status == 1 :
            info = self._conn.cluster('nodes')
            clusterkey = {
                "ip": " 节点IP",
                "slots": "主从延迟",
                "port": " 从机端口",
                "flags":"角色信息",
                "connected": "状态"
            }
            if isinstance(info, dict):
                count = 1
                for key, value in info.items():
                    if type == 2:rs.append({"name": key, "value": value})
                    else: rs.append({"name": clusterkey['ip']+str(count), "value": key})
                    if isinstance(value, dict):
                        for key1, value1 in value.items():
                            if type == 1:
                                if key1 in clusterkey.keys(): rs.append({"name": clusterkey[key1]+str(count), "value": value1})
                    count = count + 1
                if type==3:
                    rs=[]
                    rs.append(info)
            #rs.append(info)
        if rs != None:
            return rs
        else:
            return {}

    def getvariable(self, type=1):
        rs = []
        info = self._conn.config_get('*')
        if isinstance(info, dict):
            if type==3 :
                rs.append(info)
            else:
                for key, value in info.items():
                    rs.append({"name": key, "value": value})
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


if __name__=='__main__':
    try:
        mysql = MySQL('192.168.88.230',33061,'mysql','root','welliam')
    except Exception,ex:
        print ex 
    print mysql.getVariables()