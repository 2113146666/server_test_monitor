# -*- coding:utf-8 -*-
import os, sys
import functools
import time
import platform
import multiprocessing
import traceback
import re
import datetime
from optparse import OptionParser
import copy
from collections import namedtuple
import socket
# import random
import subprocess
import signal
import json
import threading
import collections
# import csv
import uuid
import gc
# import hashlib
import logging
import locale
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# import zlib
sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)).split('auto_test')[0], 'auto_test').replace('\\', '/'))

try:
    from common_lib.src.config import *
except Exception as e:
    GLOBAL_VAR = collections.namedtuple('GLOBAL_VAR', ["thread_lock", "STOP", 'console_handler', 'LOG_CONSOLE_LEVEL',
                                                       'LOG_FILE_LEVEL',
                                                       "RUN_MODE", "MONITOR_INTERVAL", "TEST_TOTAL_TIME",
                                                       "pname_list", "SERVER_TYPE", 'PLATFORM'])
    GLOBAL_VAR.thread_lock = threading.Lock()
    GLOBAL_VAR.STOP = False
    GLOBAL_VAR.console_handler = logging.StreamHandler()
    GLOBAL_VAR.LOG_CONSOLE_LEVEL = logging.INFO  # 默认值，也可从python参数指定
    GLOBAL_VAR.LOG_FILE_LEVEL = logging.INFO  # 默认值，也可从python参数指定
    ERROR_CODE_SUCCESS = 0  # 无错误码，执行成功
    ERROR_CODE_UNKNOWN_ERROR = -1  # 未知错误
    ERROR_CODE_BASH_CMD = 1000  # bash命令执行失败
    ERROR_CODE_SOCKET_CREATE = 201  # socket创建失败
    ERROR_CODE_TCP_CONNECT = 203  # tcp连接失败
    ERROR_CODE_SOCKET_BIND = 202  # socket bind失败
    ERROR_CODE_TCP_SSL_WRAP = 205  # tcp ssl握手失败
    ERROR_CODE_WEBSOCKET_HANDSHAKE = 210  # websocket handshake失败
    ERROR_CODE_SCRIPT_SYNTAX_ERROR = 10  # 代码语法错误
GLOBAL_VAR.LOW_PERFORMANCE = False
ERROR_CODE_JUMP_ASSET_EXIST_MULTI = 3001  # jump server查询到的资产不唯一
ERROR_CODE_JUMP_ASSET_IS_NONE = 3002  # jump server查询不到该资产
ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST = 3003  # jump server 远端机器username不存在
ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE = 3004  # jump server 远端机器python版本不支持
ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT = 3005  # jump server 远端机器username认证错误
ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL = 3006 # jump server 远端机器系统不支持，如win系统




if sys.version_info < (3, 0):
    reload(sys)
    # sys.setdefaultencoding('utf8')  #中文不行
    sys.setdefaultencoding(locale.getpreferredencoding())
    import ConfigParser as cf
else:
    import configparser as cf



# 默认值，也可从python参数指定
def _get_current_code_py_path_and_name():
    try:
        py_name = os.path.basename(os.path.abspath(__file__)).replace('\\', '/')
        py_path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    except:
        py_path = os.getcwd().replace('\\', '/')  # 275不支持__file__
        py_name = os.path.basename(sys.argv[0]).replace('\\', '/')

    return py_name, py_path


PYTHON_FILE_NAME = _get_current_code_py_path_and_name()[0]
PYTHON_FILE_PATH = _get_current_code_py_path_and_name()[1]
DATA_FILE_PATH = os.path.join(PYTHON_FILE_PATH, "../common_data").replace('\\', '/')
logger = logging

# black, red, green, yellow, blue, purple, cyan and white
if not logging.getLogger('').handlers:  # arm系统空的logger能获取到句柄,因此加上特有的标签chfshan不会相互影响
    __color_fmt = '%(log_color)s%(levelname)1.1s %(asctime)s.%(msecs)03d %(threadName)s %(module)s:%(funcName)s[%(lineno)d] %(purple)s %(message)s'
    __date_fmt = "%y%m%d %H:%M:%S"
    __fmt = "%(levelname)1.1s %(asctime)s.%(msecs)03d %(threadName)s %(module)s:%(funcName)s[%(lineno)d] %(message)s"
    __colors_config = {  # black red green yellow blue cyan white
        'DEBUG': 'bold_cyan',  # cyan white
        'INFO': 'bold_green',
        'WARNING': 'bold_blue',  # yellow
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_yellow', }
    colorlog = None
    formatter = logging.Formatter(__fmt, datefmt=__date_fmt)
    try:
        import colorlog as colorlog
    except BaseException:
        os.system('pip install colorlog')
    try:
        import colorlog as colorlog

        formatter = colorlog.ColoredFormatter(
            fmt=__color_fmt,
            datefmt=__date_fmt,
            log_colors=__colors_config)
    except BaseException:
        pass
    logging.root.setLevel(logging.NOTSET)  # 不设置默认warining, 且跟handler比取高的
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(GLOBAL_VAR.LOG_CONSOLE_LEVEL)
    GLOBAL_VAR.console_handler = console_handler
    # print('log file = %s'% os.path.join(os.path.split(os.path.realpath(__file__))[0], 'monitor.log').replace('\\','/'))
    # file_handler = TimedRotatingFileHandler(filename=os.path.join(PYTHON_FILE_PATH, 'monitor.log').replace('\\','/'),
    #                                          when='D',
    #                                          interval=1,
    #                                          backupCount=int(5),
    #                                          delay=True,
    #                                          encoding='utf-8'
    #                                          )
    _log_file = os.path.join(PYTHON_FILE_PATH, 'monitor.log').replace('\\', '/')
    print('log file = %s' % _log_file)
    file_handler = RotatingFileHandler(filename=_log_file,
                                       mode='a',
                                       maxBytes=25 * 1024 * 1024,
                                       backupCount=int(1),
                                       encoding='utf-8', delay=True)

    file_handler.setFormatter(formatter)
    file_handler.setLevel(GLOBAL_VAR.LOG_FILE_LEVEL)
    # a = logger.getLogger(__name__)
    # a.addHandler(file_handler)
    logger = logging.getLogger()  # 有些系统空的logger能获取到句柄,必须加上特有的标签如chfshan不会相互影响
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    # logger.getLogger('').addHandler(file_handler)
    # logger.getLogger('').addHandler(console_handler)
    logger.warning('monitor reset log')
logger.critical('usage:\npython monitor_system.py')

logger.critical('##########MONITOR SYSTEM START...########## start cmd=\n%s' % str(sys.argv))
REMOTE_WORK_PATH = 'MONITOR_SYSTEM/'
CLIENT_BASIC_INFO_FILE_NAME = 'info.csv'

import re, os, time
from collections import namedtuple


def time_sleep(sleep_time=1.0):
    """
    :label [System&Monitor]:系统操作和性能监控相关
    """
    now_time = time.time()
    while True:
        time.sleep(0.05)
        if (time.time() - now_time) >= float(sleep_time):
            break


'''[2023.6.27]chfshan,打印表格'''
def print_table(datas=None,headers=None,title='',description='',tablefmt='simple',need_print_table = True,flag_add_in_line_start='',alignment='^'):
    """打印表格
    :label [RegulationManager]:规范类(设计/输入输出等)
    把组好的list数据,按指定表格样式打印出来.
    :param data: [list]@notblink 待打印的数据,格式为list套list,嵌套list即为表格中的一行,@example:[['chfshan',18,'dev3'],['wwchen',17,'dev3']]
    :param headers: [list]@notblink 表格的表头, @example:['Name','Age','Depart']
    :param title: [string] 表名
    :param tablefmt: [string] 表格样式名,可选3种: "grid"-网格;"simple"-简洁;"csv"-适配csv的逗号分隔模式,@default='simple'
    :param need_print: [bool] consonle log中打印一份该表格,True-打印,False-仅返回已组好表格的字符串,@default=True
    :param alignment: [string] 表格的对齐方式,提供三种: "^"-居中, "<"-左对齐,">"-右对齐,@default='^'
    :return: [string] 按指定格式组好的表格字符串,具体见usage
    :raises ValueError: datas或headers为入参
    :raises IOError: 访问表格object出现异常.
    :usage:
        example1:打印含有title的grid表格
            print_table(datas=[['chfshan',18,'dev3'],['wwchen',17,'dev3']],headers = ['Name', 'Age', 'Depart'],title='dev3 members',tablefmt='grid',description='dev3 members')
            [输出]
            :dev3 members
            -------|---|------
             Name  |Age|Depart
            =======|===|======
            chfshan|18 | dev3
            -------|---|------
            wwchen |17 | dev3

        example2:打印含有title和描述的simple表格
            print_table(datas=[['chfshan',18,'dev3'],['wwchen',17,'dev3']],headers = ['Name', 'Age', 'Depart'],title='dev3 members',tablefmt='simple',description='3 members')
            [输出]
            :3 members
            :dev3 members
            -------|---|------
             Name  |Age|Depart
            -------|---|------
            chfshan|18 | dev3
            wwchen |17 | dev3

    """
    try:
        if not datas or not headers:
            raise ValueError

        _max_row_length = max([len(i) for i in datas+[headers]])    #最长的列数


        headers = headers + ['']*(_max_row_length-len(headers))     #headers不够长的，list中拼上空的元素

        datas = [_data+['']*(_max_row_length-len(_data)) for _data in datas] #datas不够长的，list中拼上空的元素

        # for column in zip(headers,*datas):
        #     logger.critical(column)
        # max_lengths = [max(len(str(item)) for item in column) for column in zip(headers,*datas)]

        max_lengths = [max(max(len(str(data)) for data in str(item).split('\n')) for item in column) for column in zip(headers,*datas)]





        # 处理样式
        _delimiter_data = "|"
        _delimiter_line = '|'
        _alignment = alignment.strip() #对齐方式    ^居中, <左对齐,>右对齐

        table = '\n'
        _fmt = ''
        _fmt_head = _delimiter_line.join("-" * (max_length) for max_length in max_lengths)
        if tablefmt == 'grid':
            _delimiter_line = '|'
            _fmt = _delimiter_line.join("-" * (max_length) for max_length in max_lengths)
            _fmt_head = _delimiter_line.join("=" * (max_length) for max_length in max_lengths)
        if tablefmt == 'csv':
            _fmt = ''
            _delimiter_line = ' '
            _delimiter_data = ','
            _fmt_head = _delimiter_line.join("=" * (max_length) for max_length in max_lengths)

        if flag_add_in_line_start:
            flag_add_in_line_start = flag_add_in_line_start+'   ' #+_delimiter_line

        '''拼待打印的字符串'''
        # 表名和表描述
        if description:
            table += flag_add_in_line_start +':' + description + '\n'
        if title:
            table += flag_add_in_line_start +':' + title + '\n'
        #分隔符
        table += flag_add_in_line_start + _delimiter_line.join("-" * (max_length) for max_length in max_lengths)
        table += '\n'

        # 表头
        # f"^{max_lengths[i]}"
        table = table + flag_add_in_line_start + _delimiter_data.join(format(header,"^{}".format(max_lengths[i])) for i, header in enumerate(headers)) +'\n'
        table = table + flag_add_in_line_start + _fmt_head
        table += '\n'
        # 数据行
        for row in datas:
            table += flag_add_in_line_start + _delimiter_data.join(format(str(item),_alignment+"{}".format(max_lengths[i])) for i,item in enumerate(row)) +'\n'
            if _fmt:
                table += flag_add_in_line_start + _fmt
                table += '\n'

        if need_print_table:
            logger.error('\n'+table)
    except Exception as e:
        logger.info('failed - reason is %s' % str(e))
        return ''

    return '\n'+table


'''[2023.2.1]chfshan,本机信息获取，如cpu信息、使用率、python可执行路径、执行指定命令等'''


class LocalClient(object):
    """
    :label [System&Monitor]:系统操作和性能监控相关
    """
    CLOCK_TICKS = 100
    if hasattr(os, "sysconf"):
        CLOCK_TICKS = os.sysconf("SC_CLK_TCK")

    def __init__(self):
        self.error_code = None
        self.error_msg = None
        self.popen_returncode = None
        self.host_name = None
        self.error_code = -1
        self.cpu_count = self.get_cpu_count()
        self._psutil = None
        self._is_sudo_support = None
        self._current_path = None
        self._sys_cpu_name_list = []
        self._sys_cpu_namedtuple = namedtuple('sys_cputimes',
                                              [])  # namedtuple('sys_cputimes',['user', 'nice', 'system', 'idle', 'iowait', 'hardirq', 'softirq','steal', 'guest','guest_nice'])
        self._coding = locale.getpreferredencoding()
        self._last_cpu_all_times = {}
        self._last_data = {'p_cpu_time': {}, 'cpu_time': {}}

    '''[2022.7.26] add by chfshan,执行本机命令,返回命令结果'''

    def run_cmd(self, command, input=None, need_run_with_sudo=False, need_log_result=True,timeout=5):
        """执行本机命令,返回命令结果
        :param cmd: [string]具体命令
        :param input: [bytes] 发给child process的信号, 一般为None
        :param need_run_with_sudo: [bool] 只针对linux,命令是否要基于sudo执行
        :return: [string 或 None]命令结果,失败返回False,并赋值self.error_msg
        """
        # import subprocess
        # import traceback
        # import sys
        # import locale
        # _coding = locale.getpreferredencoding()
        result = False
        # stderr = None
        self.error_code = ERROR_CODE_SUCCESS
        self.error_msg = ''

        # None: 不确定
        if self._is_sudo_support is None:
            p = subprocess.Popen('sudo pwd', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate(input)
            if p.returncode != 0:  # sudo部分机子 sudo + cmd 报错, ipvt10如121.247报"you must have a tty to run sudo", ucm报sudo不支持.另python远程执行sudo永远不会返回必须等超时
                if str(stderr).find('sudo: not found') != -1 or str(stderr).find('tty to run') != -1:
                    self._is_sudo_support = False
                else:
                    self._is_sudo_support = True
            elif not stderr:
                self._is_sudo_support = True

        if self._is_sudo_support is True and need_run_with_sudo is True and not str(command).strip().startswith('sudo'):
            command = 'sudo ' + str(command)
        # 本机不支持，命令中删除sudo
        if self._is_sudo_support is False:
            command = str(command).replace('sudo ', ' ')

        # 执行命令
        try:
            p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            stdout, stderr = p.communicate(input)

            try:
                stderr = stderr.decode(encoding=self._coding).strip()
            except:
                pass

            try:
                stdout = stdout.decode(encoding=self._coding).strip()
            except:
                pass

            result = stdout
            if str(stdout).find(str(stderr)) == -1:
                if (type(stderr) == bytes and type(stdout) == bytes):
                    result = stdout + stderr
                else:
                    result = str(stdout) + '\n' + str(stderr)

            if p.returncode != 0 or stderr:
                self.error_code = ERROR_CODE_BASH_CMD
                raise Exception('p.returncode=%s,stderror=%s,stdout=%s,father=%s' % (
                str(p.returncode), str(stderr), str(stdout), str(sys._getframe(1).f_code.co_name)))

            #
            #
            # if stderr and not stdout:  # sudo netstat -nap|grep -i  执行失败, p.returncode=0,err有值,stdout无值,  ucm上netstat -nap执行失败，stdout有值,stderr也有值, win ping 'www.XXXX.com' returncode=1,sdtout有值stderr无值  #win  nslookup www.XXXXXXX_test returncode=0,stdout和error都有值
            #     try:
            #         stderr = stderr.decode(encoding=_coding).strip()
            #     except:
            #         stderr = stderr.strip()
            #     raise Exception('p.returncode=%s,stderror=%s' % (str(p.returncode),str(stderr)))

            #
            # if p.returncode != 0:  # java version执行成功, p.returncode=127,err有值,stdout无值
            #     raise Exception('p.returncode=%s,stderror=%s,stdout=%s' % (str(p.returncode), str(stderr), str(stdout)))
            # if p.returncode == 0:  # java version执行成功, p.returncode=127,err有值,stdout无值
            #     try:
            #         result = stdout.decode(encoding=_coding).strip()
            #     except:
            #         result = stdout.strip()
            # else:
            #     try:
            #         stdout = stdout.decode(encoding=_coding).strip()
            #     except:
            #         stdout = stdout.strip()
            #     raise Exception('p.returncode=%s,stderror=%s,stdout=%s' % (str(p.returncode),str(stderr),str(stdout.decode(encoding=_coding).strip())))
        except Exception:
            self.error_code = ERROR_CODE_UNKNOWN_ERROR
            self.error_msg = str(traceback.format_exc())  # + '_' + str(e)

        _is_sucess = "sucess" if not self.error_msg else "fail"
        if need_log_result:
            logging.info("run [ %s ] %s,result=%s,Ecode=%s,father=%s" % (str(command), _is_sucess,str(result)[0:30], str(self.error_code), str(sys._getframe(1).f_code.co_name)))
        return result

    def _call_psutil_(self):
        self._psutil = import_third_module(module_name="psutil",
                                           reason='gather client sys data, if failed, only monitor no sys data, no other affect',
                                           _need_print_log=False)

    def get_cpu_count(self):
        cpu_count = multiprocessing.cpu_count()
        try:
            if not cpu_count:
                search = re.compile('cpu\d')
                with open("/proc/stat", "rt") as f:
                    for line in f:
                        line = line.split(' ')[0]
                        if search.match(line):
                            cpu_count += 1
                f.close()
            if cpu_count == 0:  # '''grep -c processor /proc/cpuinfo'''
                with open('/proc/cpuinfo', "rb") as f:
                    for line in f:
                        if line.lower().startswith(b'processor'):
                            cpu_count += 1
                f.close()
        except Exception as e:
            logger.warning('get_cpu_count faild=%s' % str(e))
        return cpu_count

    def _get_cpu_name_list(self):
        return_result = ['cpuall']
        for i in range(self.get_cpu_count()):
            return_result.append('cpu%d' % i)
        return return_result

    '''[2022.8.30] add by chfshan,获取本机cpu使用率'''

    def _get_cpu_times(self):
        """

        :param as_process:
        :param process_pid_list:
        :return: [dict]
         as_process=Flase:
            {'cpuall':sys_cputimes(user=7466888.85, nice=43.7, system=2767327.47, idle=563435315.73, iowait=193917.45, irq=0.0, softirq=50465.92)}
        as_process=True:
            {'pid':sys_cputimes(user=7466888.85, nice=43.7, system=2767327.47, idle=563435315.73, iowait=193917.45, irq=0.0, softirq=50465.92)}
        """
        # sys_cputimes = namedtuple('sys_cputimes',['user', 'nice', 'system', 'idle', 'iowait', 'hardirq', 'softirq', 'steal', 'guest','guest_nice'])  # 仅Linux >= 2.6.11时有steal,Linux >= 2.6.24有'guest',Linux >= 3.2.0有guest_nice
        sys_cpu_stat_file = '/proc/stat'
        cpu_times = collections.OrderedDict()  # {'cpuall':}
        try:
            h_file = open(sys_cpu_stat_file, "rb")

            for line in h_file.readlines():
                if str(line).lower().find('cpu') == -1:
                    continue
                if type(line) == bytes:  # ucm上py38是bytes
                    line = line.decode('utf-8')
                values = line.split()
                cpu_name = values[0].strip()
                if str(cpu_name).lower().endswith('cpu'):
                    cpu_name = 'cpuall'
                    if len(self._sys_cpu_namedtuple._fields) < 1:
                        _sys_cpu_namedtuple = namedtuple('sys_cputimes',
                                                         ['user', 'nice', 'system', 'idle', 'iowait', 'hardirq',
                                                          'softirq',
                                                          'steal', 'guest',
                                                          'guest_nice'])  # 仅Linux >= 2.6.11时有steal,Linux >= 2.6.24有'guest',Linux >= 3.2.0有guest_nice
                        self._sys_cpu_namedtuple = namedtuple('sys_cputimes',
                                                              _sys_cpu_namedtuple._fields[0:len(values) - 1])

                # fields = [float(x) / self.CLOCK_TICKS for x in fields]
                fields = [float(x) for x in values[1:]]
                cpu_times.update({cpu_name: self._sys_cpu_namedtuple(*fields)})
                # if cpu_name.lower().strip() == 'cpuall' and only_cpu_all is True:
                #     break
            h_file.close()
        except:
            pass
        return cpu_times

    def _get_cpu_times_by_dict(self):
        """

        :param as_process:
        :param process_pid_list:
        :return: [dict]
         as_process=Flase:
            {'cpuall':sys_cputimes(user=7466888.85, nice=43.7, system=2767327.47, idle=563435315.73, iowait=193917.45, irq=0.0, softirq=50465.92)}
        as_process=True:
            {'pid':sys_cputimes(user=7466888.85, nice=43.7, system=2767327.47, idle=563435315.73, iowait=193917.45, irq=0.0, softirq=50465.92)}
        """
        # sys_cputimes = namedtuple('sys_cputimes',['user', 'nice', 'system', 'idle', 'iowait', 'hardirq', 'softirq', 'steal', 'guest','guest_nice'])  # 仅Linux >= 2.6.11时有steal,Linux >= 2.6.24有'guest',Linux >= 3.2.0有guest_nice
        sys_cpu_stat_file = '/proc/stat'
        cpu_times = collections.OrderedDict()  # {'cpuall':}
        try:
            h_file = open(sys_cpu_stat_file, "rb")

            for line in h_file.readlines():
                if str(line).lower().find('cpu') == -1:
                    continue
                if type(line) == bytes:  # ucm上py38是bytes
                    line = line.decode('utf-8')
                values = line.split()
                cpu_name = values[0].strip()
                if str(cpu_name).lower().endswith('cpu'):
                    cpu_name = 'cpuall'
                    if len(self._sys_cpu_name_list) < 1:
                        _sys_cpu_name_list = ['user', 'nice', 'system', 'idle', 'iowait', 'hardirq', 'softirq', 'steal',
                                              'guest',
                                              'guest_nice']  # 仅Linux >= 2.6.11时有steal,Linux >= 2.6.24有'guest',Linux >= 3.2.0有guest_nice
                        self._sys_cpu_name_list = _sys_cpu_name_list[0:len(values) - 1]

                fields = [float(x) for x in values[1:]]
                cpu_times.update({cpu_name: dict(zip(self._sys_cpu_name_list, fields))})
                # if cpu_name.lower().strip() == 'cpuall' and only_cpu_all is True:
                #     break
            h_file.close()
        except:
            pass
        return cpu_times

    def _get_process_cpu_times(self, process_pid_list=None):
        cpu_times = collections.OrderedDict()  # {'cpuall':}
        # process_cputimes = namedtuple('process_cputimes',['utime', 'stime', 'cutime', 'cstime', 'thread_num', 'start_time', 'vmsize','rss'])
        process_cputimes = namedtuple('process_cputimes', ['utime', 'stime', 'cutime', 'cstime'])
        for process_pid in process_pid_list:
            if not process_pid:
                continue
            process_stat_file = str('/proc/%(pid)s/stat') % {'pid': str(process_pid)}
            try:
                with open(process_stat_file, 'rb') as f:
                    values = f.readline().split()
                    utime = float(values[13])
                    stime = float(values[14])
                    cutime = float(values[15])
                    cstime = float(values[16])
                    thread_num = values[19]
                    start_time = values[21]
                    vmsize = values[22]
                    res = values[23]
                    fields = [utime, stime, cutime, cstime]
                    cpu_times.update({str(process_pid): process_cputimes(*fields)})
                f.close()
            except:
                pass
        return cpu_times

    def get_cpu_static_info(self):
        # return_result = {}
        # _cpu_time = self._get_cpu_times_by_dict()
        # for _cpu_name,_cpu_times in _cpu_time.items():
        #     _name_list = [_cpu_name+'_'+ _cpu_time_name for _cpu_time_name in self._sys_cpu_name_list]
        #     return_result.update(dict(zip(_name_list,_cpu_times)))

        return self._get_cpu_times_by_dict()

    '''[2023.10.19] chfshan , 获取本机内存使用率,单位KB'''

    def get_memory_usage(self, proc_meminfo_data=None):
        """获取本机内存使用率,单位KB
        :param proc_meminfo_data: [string] 外部已经取出的/proc/meminfo的数据,该函数会解析
        :return: [dict] key=proc_meminfo的key,示例如下
         {'time':'20231103 10:52:36','memtotal':1744768.0,'memfree':38960.0,'memavailable':538848.0,'buffers':0.0,'cached':559648.0,'swapcached':51072.0,'active':539788.0,'inactive':854584.0,'active(anon)':291156.0,'inactive(anon)':584752.0,'active(file)':248632.0,'inactive(file)':269832.0,'unevictable':3072.0,'mlocked':0.0,'swaptotal':1048572.0,'swapfree':645528.0,'zswap':0.0,'zswapped':0.0,'dirty':32.0,'writeback':0.0,'anonpages':803100.0,'mapped':132448.0,'shmem':41184.0,'kreclaimable':71536.0,'slab':172960.0,'sreclaimable':71536.0,'sunreclaim':101424.0,'kernelstack':17296.0,'pagetables':15608.0,'nfs_unstable':0.0,'bounce':0.0,'writebacktmp':0.0,'commitlimit':1920956.0,'committed_as':4573664.0,'vmalloctotal':133143592960.0,'vmallocused':29456.0,'vmallocchunk':0.0,'percpu':912.0,'hardwarecorrupted':0.0,'anonhugepages':315392.0,'shmemhugepages':0.0,'shmempmdmapped':0.0,'filehugepages':0.0,'filepmdmapped':0.0,'cmatotal':0.0,'cmafree':0.0,'hugepages_total':0.0,'hugepages_free':0.0,'hugepages_rsvd':0.0,'hugepages_surp':0.0,'hugepagesize':2048.0,'hugetlb':0.0}

        :usage:
         # 场景1 自动取
         print(LocalClient.get_memory_usage())
         # 场景2 外部取好入参
         remote_server = SSHConnection(host='192.168.130.113',port=22,username='root',password='grandstream.')
         proc_meminfo_data = remote_server.execute_command('cat /proc/meminfo')
         print(LocalClient.get_memory_usage(proc_meminfo_data))


        """
        return_result = collections.OrderedDict()
        _time = str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': _time})

        if 'linux' in sys.platform or proc_meminfo_data:  # linux系统获取cpu使用率，从proc获取
            try:
                _h_file = None
                if proc_meminfo_data is None:
                    _h_file = open('/proc/meminfo', 'r')
                    proc_meminfo_data = _h_file.readlines()
                else:
                    proc_meminfo_data = proc_meminfo_data.split('\n') if type(
                        proc_meminfo_data) != list else proc_meminfo_data

                for data in proc_meminfo_data:
                    data = str(data).lower().replace('\n', '').replace('\r', '').replace(' ', '').replace('kb',
                                                                                                          '').split(':')
                    if len(data) >= 2:
                        return_result.update({str(data[0]).replace(":", '').lower(): round(float(data[-1]), 2)})
                try:
                    used = return_result['memtotal'] - return_result['memfree'] - return_result['buffers'] - \
                           return_result['cached'] - return_result['sreclaimable']
                    return_result.update({'used': used})
                except:
                    pass
                _h_file.close()
            except:
                pass

        elif 'win32' in sys.platform:  # windows系统获取cpu使用率，依赖第三方库
            try:
                # _free = os.popen('wmic ComputerSystem get TotalPhysicalMemory').read()
                _free = subprocess.check_output(['wmic', 'OS', 'get', 'FreePhysicalMemory'])
            except subprocess.CalledProcessError:
                self._psutil = import_third_module('psutil')
                _free = self._psutil.virtual_memory().free

            _free = _free.decode('utf-8') if type(_free) != str else _free
            _free = re.findall('\d+', _free)
            # _free = self.psutil.virtual_memory().free/1024
            # _total = self.psutil.virtual_memory().total/1024
            # _available = self.psutil..virtual_memory().available/1024
            # _used = self.psutil..virtual_memory().used/1024
            if len(_free) > 0:
                return_result.update({'memfree': round(float(_free[0]) / 1024, 2)})
            try:
                _total = subprocess.check_output(['wmic', 'ComputerSystem', 'get', 'TotalPhysicalMemory'])
            except (Exception, subprocess.CalledProcessError):
                self._psutil = import_third_module('psutil')
                _total = self._psutil.virtual_memory().total
            _total = _total.decode('utf-8') if type(_total) != str else _total
            _total = re.findall('\d+', _total)

            if len(_total) > 0:
                return_result.update({'memtotal': round(float(_total[0]) / 1024, 2)})

        return return_result

    def get_disk_usage(self):
        """
        return
            'used':磁盘标识_使用率,'free':剩余磁盘容量单位Bytes
        """
        return_result = collections.OrderedDict()
        _time = str(time.strftime("%Y%m%d %H:%M:%S"))
        _disk_usage = ''
        if 'linux' in sys.platform:
            _result = self.run_cmd(command='df -h', need_run_with_sudo=True)

            for _data in _result.split('\n'):
                try:
                    __data_line = _data.split()
                    if len(__data_line) < 3 or 'tmpfs' in __data_line[0]:
                        continue
                    _use_percent = int(__data_line[-2].replace('%', ''))
                    _available = __data_line[-3]  # 单位bytes
                    return_result.update({__data_line[-1] + '_' + 'use': _use_percent})
                    return_result.update({__data_line[-1] + '_' + 'free': _available})
                    return_result.update({__data_line[-1] + '_' + 'total': __data_line[-5]})
                except:
                    pass

        elif 'win32' in sys.platform:  # windows系统获取cpu使用率，依赖第三方库
            try:
                _disk_usage = subprocess.check_output(['wmic', 'LogicalDisk', "get", "Caption,FreeSpace,Size"])
            except:
                return return_result
            _disk_usage = _disk_usage.decode('utf-8') if type(_disk_usage) != str else _disk_usage
            for _data in _disk_usage.replace('\r', '').split('\n'):
                try:
                    __data = _data.split()
                    if _data.startswith('Caption') or len(__data) != 3:
                        continue
                    _flag = str(__data[0]).replace(':', '') + '_'
                    __free = round(float(__data[1]), 2)
                    __total = round(float(__data[2]), 2)
                    _use_percent = round(100 * (__total - __free) / __total, 2)
                    return_result.update(
                        {_flag + 'free': __free, _flag + 'use': _use_percent, _flag + 'total': __total})
                except:
                    continue
        return return_result

    '''[chfshan]2023.2.8获取进程的cpu使用率，支持同时获取多个进程的cpu使用率'''

    def get_process_cpu_usage(self, process_pid_list, interval=1):
        """
        获取进程的cpu使用率
        :param process_pid_list:[list of int] 进程的进程id, 如[3466,6898] 获取两个进程的cpu使用率
        :param interval:[int] auto,1,2,3.., =auto 根据监控间隔获取，即上一次和这次的间隔，从self._last_data中取上一次的
        :return: [dict] 进程的cpu使用率 如: {'3466': 50.6, '6898': 0.5} 进程3466使用率50.6%, 进程6898使用率0.5%
        """
        if type(process_pid_list) == str:
            process_pid_list = [process_pid_list]
        return_result = collections.OrderedDict()
        _time = str(time.strftime("%Y%m%d %H:%M:%S"))
        if 'linux' in sys.platform:  # linux系统获取cpu使用率，从proc获取

            def calculate(process_t1, process_t2, total_t1=None, total_t2=None, interval=1):
                # total_time = utime + stime + cutime + cstime
                # pcpu1 = sum(process_t1)
                # pcpu2 = sum(process_t2)
                # t1_total_time = sum(total_t1)
                # t2_total_time = sum(total_t2)

                pcpu1 = process_t1.utime + process_t1.stime + process_t1.cutime + process_t1.cstime
                pcpu2 = process_t2.utime + process_t2.stime + process_t2.cutime + process_t2.cstime

                '''算法1,进程占用的cpu/整机的cpu*核数，算儿童进程,clouducm项目中gs_avs很忙时不准(和top有差距)'''
                # t1_total_time = sum(total_t1)
                # t2_total_time = sum(total_t2)
                # _cpu_usage = round(100 * ((pcpu2 - pcpu1) / (t2_total_time - t1_total_time) / self.CLOCK_TICKS) * int(
                #     self.cpu_count), 2)
                # logger.critical(('c+s+cu+cs/cpu_all:',_cpu_usage,process_t1))

                '''算法2,进程占用的cpu/整机的cpu无idle*核数，算儿童进程,clouducm项目中gs_avs很忙时不准(和top有差距)'''
                # t1_total_time_no_idle = sum(total_t1) - total_t1.idle
                # t2_total_time_no_idle = sum(total_t2) - total_t2.idle
                # logger.critical(('c+s+cu+cs/cpu_busy:', round(100 * ((pcpu2 - pcpu1) / (t2_total_time_no_idle - t1_total_time_no_idle) / self.CLOCK_TICKS) * int(
                #     self.cpu_count), 2), process_t1))

                '''算法3,,进程占用的cpu/整机的cpu无idle*核数，不算儿童进程,clouducm项目中gs_avs很忙时不准(和top有差距)'''
                # pcpu1 = process_t1.utime + process_t1.stime
                # pcpu2 = process_t2.utime + process_t2.stime
                # t1_total_time = sum(total_t1) - total_t1.idle
                # t2_total_time = sum(total_t2) - total_t2.idle
                # _cpu = round(100 * (pcpu2 - pcpu1) / (t2_total_time - t1_total_time) * int(self.cpu_num), 2)

                '''算法4,进程占用的cpu，算儿童进程,clouducm项目中gs_avs+gwn项目中api进程，在很忙时跟top基本一致'''
                _cpu_usage_no_all = round(100 * ((pcpu2 - pcpu1) / self.CLOCK_TICKS) / interval, 2)
                if _cpu_usage_no_all > int(self.cpu_count) * 100:
                    _cpu_usage_no_all = int(self.cpu_count) * 100

                # logger.critical(('c+s+cu+cs', _cpu_usage_no_all, process_t1))
                # return _cpu_usage
                return _cpu_usage_no_all

            _et = _st = time.time()

            pre_process_cpu = None
            if interval != 'auto':
                pre_process_cpu = self._get_process_cpu_times(process_pid_list=process_pid_list)
                time.sleep(float(interval) - (time.time() - _st))
            else:
                _et = time.time()
                if len(self._last_data['p_cpu_time']) == 2:
                    pre_process_cpu = self._last_data['p_cpu_time'][1]
                    interval = _et - self._last_data['p_cpu_time'][0]
            after_process_cpu = self._get_process_cpu_times(process_pid_list=process_pid_list)

            self._last_data.update({'p_cpu_time': (_et, after_process_cpu)})
            for process_pid, after_cpu_times in after_process_cpu.items():
                try:
                    # self.process_cpu_used = calculate(cpu_times, after_process_cpu[process_pid], pre_cpu_all['cpuall'],
                    #                                   after_cpu_all['cpuall'])
                    process_cpu_used = calculate(process_t1=pre_process_cpu[process_pid], process_t2=after_cpu_times,
                                                 interval=interval)
                    return_result.update({process_pid: process_cpu_used})
                except Exception:
                    logger.warning('process_cpu_percent[%s] fail=%s' % (
                        str(process_pid) + ":" + str(after_cpu_times),
                        str(traceback.format_exc())))  # TODO_get_cpu_times

            # logger.critical(('#####',pre_process_cpu,return_result))
        elif 'win32' in sys.platform:  # windows系统获取cpu使用率，依赖第三方库
            for _pid in process_pid_list:
                if not _pid:
                    continue
                _p = self._psutil.Process(_pid)
                return_result.update({str(_pid): round(_p.cpu_percent(), 2)})

        logger.critical(('#####P_CPU,interval=%s' % str(interval), process_pid_list, return_result))
        return return_result

    '''[2023.10.19] chfshan , 获取本机cpu使用率'''

    def get_cpu_usage(self, interval=1):
        """获取当前cpu使用率
        :param interval: [bool]几秒内的cpu使用率
        :param kwargs: [可变参数], 目前支持  process_pid_list=[XXX],为get_process_cpu_usage调用
        :return: [dict] 示例如: {'cpuall':90,'cpu0':80,'cpu1':70}
        :usage:
            print(get_cpu_usage())   #{'cpuall':90,'cpu0':80,'cpu1':70}
            print(get_cpu_usage(only_cpu_all=True))   #{'cpuall':90}

        """
        return_result = collections.OrderedDict()
        _time = str(time.strftime("%Y%m%d %H:%M:%S"))

        return_result.update({'time': _time})
        try:

            if 'linux' in sys.platform:  # linux系统获取cpu使用率，从proc获取
                # sys_cputimes = namedtuple('sys_cputimes',['user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq','steal','guest','guest_nice']) #仅Linux >= 2.6.11时有steal,Linux >= 2.6.24有'guest',Linux >= 3.2.0有guest_nice
                # process_cputimes = namedtuple('process_cputimes', ['utime', 'stime',  'cutime',  'cstime','thread_num','start_time','vmsize','rss'])

                def calculate(t1, t2, name_flag='', interval=1, only_get_cpuall_and_busy=False):
                    # result = dict()
                    import collections
                    result = {}
                    if not t1:
                        return result
                    for (_cpu_name, value) in t1.items():
                        # if only_get_cpuall_and_busy and _cpu_name != 'cpuall':
                        #     continue
                        t1_all = sum(value)
                        t1_busy = t1_all - value.idle

                        t2_all = sum(t2[_cpu_name])
                        t2_busy = t2_all - t2[_cpu_name].idle

                        # this usually indicates a float precision issue
                        if t2_busy <= t1_busy:
                            result.update({_cpu_name: 0.0})
                            continue
                            # return 0.0
                        busy_delta = t2_busy - t1_busy
                        all_delta = t2_all - t1_all
                        busy_perc = 100 * busy_delta / all_delta  # (busy_delta/interval)  / (all_delta /interval)
                        # logger.critical((t1_all,t2_all,all_delta))
                        if _cpu_name == 'cpuall':
                            if hasattr(value, 'steal'):
                                steal_percent = 100 * (t2[_cpu_name].steal - value.steal) / all_delta
                                result.update({_cpu_name + '_steal': round(steal_percent, 1)})
                            user_percent = 100 * (t2[_cpu_name].user - value.user) / all_delta
                            sys_percent = 100 * (t2[_cpu_name].system - value.system) / all_delta
                            iowait_percent = 100 * (t2[_cpu_name].iowait - value.iowait) / all_delta
                            softirq_percent = 100 * (t2[_cpu_name].softirq - value.softirq) / all_delta
                            hardirq_percent = 100 * (t2[_cpu_name].hardirq - value.hardirq) / all_delta
                            result.update({name_flag + _cpu_name + '_user': round(user_percent, 1)})
                            result.update({name_flag + _cpu_name + '_sys': round(sys_percent, 1)})
                            result.update({name_flag + _cpu_name + '_iowait': round(iowait_percent, 1)})
                            result.update({name_flag + _cpu_name + '_softirq': round(softirq_percent, 1)})
                            result.update({name_flag + _cpu_name + '_hardirq': round(hardirq_percent, 1)})
                        result.update({name_flag + _cpu_name: round(busy_perc, 1)})
                        # logger.critical(('#####CPU',interval,busy_perc,t1_all,t2_all,t1_busy,t2_busy))
                    return result

                _st = time.time()
                t1 = self._get_cpu_times()
                time.sleep(float(interval) - (time.time() - _st))
                t2 = self._get_cpu_times()
                _now_time = time.time()

                try:
                    return_result = calculate(self._last_cpu_all_times.get('cpu_time'), t2,
                                              interval=_now_time - self._last_cpu_all_times.get('timestamp'),
                                              name_flag=str(GLOBAL_VAR.MONITOR_INTERVAL) + 's_',
                                              only_get_cpuall_and_busy=True)
                except:
                    pass

                self._last_cpu_all_times.update({'timestamp': _now_time, 'cpu_time': t2})
                # logger.critical(('#####CPU', 'new',self._last_cpu_all_times))
                return_result.update(calculate(t1, t2, interval=1))
                '''[2024.05.22]kliang clean log for jenkins'''
                # logger.critical(
                #     ('#####CPU,interval=', _now_time - self._last_cpu_all_times.get('timestamp'), return_result))

            elif 'win32' in sys.platform:  # windows系统获取cpu使用率，依赖第三方库
                try:
                    _cpuall = subprocess.check_output(['wmic', 'cpu', 'get', 'loadpercentage'])
                except (Exception, subprocess.CalledProcessError):
                    self._psutil = import_third_module('psutil')
                    _cpuall = self._psutil.cpu_percent(interval=1)
                _cpuall = _cpuall.decode('utf-8') if type(_cpuall) != str else _cpuall
                _cpuall = re.findall('\d+', _cpuall)
                if len(_cpuall) > 0:
                    return_result.update({'cpuall': _cpuall[0]})  # windows
        except Exception:
            logger.warning('failed=%s' % traceback.format_exc())

        return return_result

    '''[2022.8.12] chfshan,获取python可执行命令的路径,如已加入环境变量，不带路径'''

    def get_python_execute_path(self):
        """
        获取python可执行文件
        :return: [string] 返回启动该python的python.exe文件所在 ,如: c:/python27/python.exe 或 /usr/bin/python
        """
        return sys.executable

    def get_pip_execute_path(self):
        return str(self.get_python_execute_path()) + ' -m pip '

    '''2023-04-24,xlzhou,执行需要交互输入的本机命令，返回命令结果（比如ssh，scp，su -等）'''

    def run_cmd_need_input(self, command, command_args=[], custom_expect_and_input={}, password=None, ensure_yes=True,
                           timeout=5,need_log_result=True):
        '''
        command = '/usr/bin/ssh'
        command_args = ['root@192.168.121.247',
                '-p', '26222',
                '-o', 'NumberOfPasswordPrompts=2',
                '-o', 'ConnectTimeout=10',
                'pwd']
        custom_expect_and_input = {'Job has been submitted with JobID':'\x03','aaaaaa':'222222'}
        result = run_cmd_need_input(command=command, command_args=command_args, password='123456')

        :param command: [string], 执行的主命令，或者完整命令（带参数）
        :param command_args: [list], 命令参数
        :param custom_expect_and_input：[dict]，自定义交互指令。eg，{'Job has been submitted with JobID':'\x03'}dict中的key表示自定义交互指令要捕获的预期字符串，dict中的value表示收到预期字符串后输入的交互指令。比如捕获到'Job has been submitted with JobID'后，输入Ctrl+C（二进制为\x03）。
        :param password: [string], 需要交互输入的密码
        :param ensure_yes: [boolean], 提示确认，是否输入yes
        :param timeout: [int], 执行超时时间
        :return: [string or None]，命令执行成功，返回执行结果；命令执行失败，返回None
        '''
        import pty, select
        '''
        比如ssh root@192.168.1.1 -p 26222 -o NumberOfPasswordPrompts=2 -c 'pwd'，会拆成以下列表去执行
        commands = [
                    '/usr/bin/ssh',  # 命令第一个参数是command的路径和名称
                    self._username + '@' + self._host,
                    '-p', str(self._port),
                    '-o', 'NumberOfPasswordPrompts=2',
                    command,  # 举例中的pwd命令
         ]'''

        return_result = None
        commands = [
            '/usr/bin/bash',
            '-c',
        ]
        _args = ' '.join(command_args)
        commands.append(command + ' ' + _args)

        # 通过pty伪终端
        pid, child_fd = pty.fork()
        # 子进程才去执行命令
        try:
            if not pid:
                os.execv(commands[0],
                         commands)  # execv函数接受的参数是以一个list或者是一个tuple表示的参数表，os.execv()函数会取代当前进程并执行指定的命令，但是不会将命令的输出打印到标准输出流
        except Exception as e:
            logger.error(str(e))

        result = b''
        _start = time.time()
        self.error_code = ERROR_CODE_SUCCESS
        while time.time() - _start < timeout:
            try:
                ready, _, _ = select.select([child_fd], [], [],
                                            timeout)  # 通过select监听文件子进程文件描述符的读事件，并设置超时，防止os.read时间触发不了而卡死
                if child_fd not in ready:  # 当达到超时时间，还未触发读事件，则跳出循环
                    break
                output = os.read(child_fd, 10240)
            except (OSError, EOFError) as e:
                # self.error_code = e.errno
                self.error_msg = str(e)
                break
            except (Exception, BaseException) as e:
                # logger.error(str(e))
                self.error_msg = str(e)
                break

            _output_tmp = output.lower()
            # logger.critical(_output_tmp)
            # 提示输入密码，则写入密码
            if b'password:' in _output_tmp and password:
                if not isinstance(password, bytes):
                    password = password.encode()
                os.write(child_fd, password + b'\n')
            # 提示是否加入known host列表或者是否ok类，默认输入yes
            elif b'are you sure you want to continue connecting' in _output_tmp or b'is this ok' in _output_tmp:
                if ensure_yes:
                    os.write(child_fd, b'yes\n')
                else:
                    os.write(child_fd, b'no\n')
            # 自定义捕获expect后自定义输入字符串
            elif custom_expect_and_input:
                for expect, input_str in custom_expect_and_input.items():
                    if not isinstance(expect, bytes):
                        expect = expect.encode()
                    if expect in _output_tmp:
                        if not isinstance(input_str, bytes):
                            input_str = input_str.encode()
                        os.write(child_fd, input_str)
            # 提示带有：但是不在预期内，暂不处理，先break，跳出循环，避免卡死
            # elif b':' in _output_tmp:
            #     logger.error('Other input prompt shows: %s not expected, please check manually!' %str(output))
            #     break
            else:
                # 拼接多次获取到的数据
                result += output

        # 等待子进程退出
        _pid, _exit_code = os.waitpid(pid, 0)
        os.close(child_fd)
        if _exit_code != 0:
            self.error_code = ERROR_CODE_BASH_CMD

        return_result = None if not result else result.decode().strip()

        if need_log_result:
            logging.info("run [ %s ],result=%s,exit_code=%s,Ecode=%s,father=%s" % (str(command + ' ' + _args),str(return_result)[0:30], str(_exit_code),str(self.error_code), str(sys._getframe(1).f_code.co_name)))

        return return_result

    def get_iface_name_for_public(self):
        '''
        获取公网IP走的网卡的网卡名
        :return:
        '''
        # route -n中，取Destination是0.0.0.0这一行对应的Iface
        # Destination        Gateway        Genmask        Flags        Metric     Ref     Use     Iface
        # 0.0.0.0            192.168.200.1  0.0.0.0        UG           0          0       0       em1
        # 192.168.121.1      0.0.0.0        255.25.255.0   U            0          0       0       em2
        route_cmd = "route -n|awk '{print $1,$8}'|awk '{if($1==\"0.0.0.0\") print $2}'"
        _cmd = lo_cli.run_cmd(route_cmd)
        result = _cmd if _cmd else 'eth0'
        return result

    '''[2023.10.19] chfshan , 获取本机的整体资源使用率,获取失败返回默认值-1 ， 内存单位MB'''

    def _get_local_resource_data(self, _default_value=-1):
        _return_result = {'cpu_all': _default_value,
                          'mem_available': _default_value,
                          'mem_total': _default_value,
                          'io_util': _default_value,
                          'io_name': 'io',
                          'cpu_load_1': _default_value,
                          'disk_name': 'c',
                          'disk_use': _default_value,
                          }
        _data = self.get_cpu_usage().get('cpuall')
        if _data:
            _return_result.update({'cpu_all': float(_data)})

        _mem_data = self.get_memory_usage()
        if _mem_data.get('memtotal') and _mem_data.get('memfree'):
            _return_result.update({'mem_total': float(_mem_data.get('memtotal')) / 1024,
                                   'mem_available': float(_mem_data.get('memfree')) / 1024})
        _high_disk_use_percent = 0
        _high_disk_name = 'c'
        for _disk, _value in self.get_disk_usage().items():
            if str(_disk).endswith('use') and int(_value) > _high_disk_use_percent:
                _high_disk_use_percent = _value
                _high_disk_name = _disk
                _return_result.update({'disk_name': _high_disk_name, 'disk_use': _high_disk_use_percent})
                continue

        logger.critical(_return_result)
        return _return_result

    '''[2022.8.12] chfshan,获取本机python的版本号,如3.7.0'''

    def get_python_version(self):
        """
        获取本机python的版本号,如3.7.0
        :return: [string] python版本号3.7.0
        """
        try:
            return str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2])
        except:
            return platform.python_version()

    def get_os_system_version(self):
        '''
        获取操作系统系统版本，命令：head -n 1 /etc/issue或cat /etc/redhat-release
        :return:
        '''
        system_version = ''
        self.os_system_version_cmd_1 = "head -n 1 /etc/issue"
        self.os_system_version_cmd = "cat /etc/redhat-release"
        self.os_system_version_cmd_2 = "cat /etc/os-release"
        self.os_system_gcc_version_cmd = "cat /proc/version"
        try:
            result = self.run_cmd(self.os_system_version_cmd)
            "cat /etc/os-release"
            if '\S' in result:
                result = self.run_cmd(self.os_system_version_cmd_1)
                if 'No such file or directory' in result:
                    result = self.run_cmd(self.os_system_version_cmd_2)

            system_version = str(result).strip() + '\n' + str(self.run_cmd(self.os_system_gcc_version_cmd))
        except Exception as e:
            logger.error("get system version failed, the reason is %s" % (e))
        finally:
            return str(system_version).replace('=', '').replace('"', '')


lo_cli = LocalClient()


class NetWork(object):
    """
    :label [System&Monitor]:系统操作和性能监控相关
    """

    def __init__(self):
        self.local_ip = None
        self.local_ipv6_host = None

    """chfshan,返回本机可上网的ip地址,本机多个ip地址仅返回第一个"""

    def get_local_ip(self, ipv6=False):
        """获取本机的ip地址,多张网卡，返回能上网的第一张网卡
        :ipv6: [bool] 是否返回本机的ipv6地址
        :return: [string]本机的ip地址, 默认返回ipv4地址
        """

        s = None
        result = None
        if self.local_ip and not ipv6:  # 减少CPU开销，避免上层频繁调反复获取
            return self.local_ip
        if self.local_ipv6_host and ipv6:  # 减少CPU开销，避免上层频繁调反复获取
            return self.local_ipv6_host

        '''socket获取上公网的socket套,有多张取第一张'''
        try:
            if ipv6:
                s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                s.connect(('2002:0808:0808:0:0:0:0:0', 80))
                result = s.getsockname()[0]
                self.local_ipv6_host = result
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                result = s.getsockname()[0]
                self.local_ip = result
        except Exception:
            logger.debug(traceback.format_exc())
        '''关闭socket'''
        try:
            s.shutdown(2)
        except:
            pass
        try:
            s.close()
        except:
            pass

        return result

    '''[2023.2.1]chfshan 获取本机的公网地址,cmd=[curl ifconfig.me]'''

    def get_local_public_ip(self):
        """返回本机的公网地址
        :return:[string] 返回本机的公网地址,如: 101.71.248.138
        """
        cmd = "curl ifconfig.me"
        return lo_cli.run_cmd(cmd)


_network = NetWork()


def _get_python_execute_path(get_type='local', remote_server_client=None, client_dict_info=None):
    '''
    :param get_type: local=本机执行，remote=远程执行
    :return:
    '''
    cmd = 'which python'
    cmd1 = 'which python3'
    if get_type == 'remote':
        result = _run_cmd_in_remote(remote_server=remote_server_client, client_dict_info=client_dict_info, cmd=cmd, need_run_with_sudo=True, is_remote_support_sudo=remote_server_client.is_remote_support_sudo)
        if str(result).find('no python in') != -1 or not result:
            result = _run_cmd_in_remote(remote_server=remote_server_client, client_dict_info=client_dict_info, cmd=cmd1, need_run_with_sudo=True, is_remote_support_sudo=remote_server_client.is_remote_support_sudo)
            if str(result).find('no python in') != -1 or not result:
                logger.warning('get_python_execute_path failed')
                return False
    else:
        result = lo_cli.get_python_execute_path()

    return result


"""如果文件大于100MB, mv成_part1, 在写入新文件，已存在part1删除"""


def _write_to_file(file=None, data=None, as_cover=False, as_append=False, file_handle=None, file_size=5242880):
    """

    :param file:
    :param data:
    :param as_cover:
    :param as_append:
    :param file_handle:
    :param file_size: [文件大小] 默认5242880=5MB(ps文件26214400=25MB)
    :return:
    """
    _open_mode = 'a' if as_append else 'w'
    h_file = None
    try:
        h_file = open(file, mode=_open_mode) if (not file_handle) or (
                type(file_handle) != str and file_handle.closed) else file_handle

        _file = h_file.name
        # limit_file_size = file_size
        # if str(_file).find('top') != -1 and str(_file).find('org') != -1:
        #     limit_file_size = 200.00

        # if str(_file).find('iostat') != -1 and str(_file).find('org') != -1:
        #     limit_file_size = 25.00
        # if str(_file).find('ps') != -1 and str(_file).find('org') != -1:
        #     limit_file_size = 25.00
        # if str(_file).find('realtime') != -1:
        #     limit_file_size = 5.00

        if os.path.exists(_file) and os.path.getsize(_file) > file_size:  # >100MB就拆分， 同时删除之前拆分的文件
            # if os.path.exists(_file + '_part1'):
            #     import shutil
            #     shutil.rmtree(_file + '_part1', ignore_errors=True)
            #     lo_cli.run_cmd('rm -rf %s' % _file + '_part1')
            import shutil

            if str(_file).find('top') != -1 and str(_file).find('org') != -1:
                try:
                    shutil.move(_file + '_part3', _file + '_part4')  # shutil低概率失败但不抛错
                    lo_cli.run_cmd('mv %s %s' % (_file + '_part3', _file + '_part4'))  # mv低概率失败但不抛错
                except:
                    pass
                try:
                    shutil.move(_file + '_part2', _file + '_part3')  # shutil低概率失败但不抛错
                    lo_cli.run_cmd('mv %s %s' % (_file + '_part2', _file + '_part3'))  # mv低概率失败但不抛错
                except:
                    pass
                try:
                    shutil.move(_file + '_part1', _file + '_part2')  # shutil低概率失败但不抛错
                    lo_cli.run_cmd('mv %s %s' % (_file + '_part1', _file + '_part2'))  # mv低概率失败但不抛错
                except:
                    pass

            shutil.move(_file, _file + '_part1')
            lo_cli.run_cmd('mv %s %s' % (_file, _file + '_part1'))

        h_file.write(data)
        h_file.close()
    except Exception:
        logger.warning('failed=%s' % str(traceback.format_exc()))

    return h_file


def _read_file(file):
    result = ''
    try:
        h_file = open(file)
        result = h_file.read()
        h_file.close()
    except Exception:
        logger.warning('failed=%s,father=%s' % (str(traceback.format_exc()), str(sys._getframe(1).f_code.co_name)))

    return result


'''kliang, 字符的编解码(encode decode0,以及加解密(Encrypt|Decrypt)相关,以及压缩解压相关'''


class StringObject():
    '''[20230329] chfshan update,字符串解码,优先用本机编码类型解码
    :label [RegulationManager]:规范类(设计/输入输出等)
    '''

    def decode(self, byte_stream):
        result = byte_stream
        err_msg = ''
        if type(byte_stream) != bytes:  # py2中容易是string
            return byte_stream
        try:
            # result = byte_stream.decode(locale.getpreferredencoding())
            result = byte_stream.decode('utf-8')
            return result
        except (Exception, BaseException):
            pass
        try:
            result = byte_stream.decode(locale.getpreferredencoding())
            return result
        except (Exception, BaseException) as e:
            err_msg = e
            # logger.debug((traceback.format_exc(), byte_stream))

        try:
            if '0xb2' in str(err_msg):
                result = byte_stream.decode('gb2312')
                return result
        except (Exception, BaseException):
            logger.warning('fail = %s,return src byte=%s' % (traceback.format_exc(), str(byte_stream)[1:100]))

        # logger.critical(('23232', byte_stream,result))
        return result

    '''[2022-08-02],add by xlzhou, md5算法，支持字符串md5计算和文件内容md5计算'''

    def md5sum(self, string_or_file_path, file_read_buffsize=65536):
        _hash = None
        import hashlib
        try:
            _hash = hashlib.md5()
            '''[2024.05.08]kliang,解决部分情况将os.path.exists(字符串)返回为true的情况'''
            res = os.path.isfile(string_or_file_path)
            if res:
                with open(string_or_file_path, "rb") as f:
                    # 必须是rb形式打开的，否则的两次出来的结果不一致
                    # block = base64.b64encode(f.read())
                    for block in iter(lambda: f.read(file_read_buffsize), b""):
                        _hash.update(block)
                f.close()
            else:
                # list暂无用处，去掉
                # if isinstance(string_or_file_path, list):
                #     for i in string_or_file_path:
                #         _hash.update(i.encode('utf-8'))
                # else:
                _hash.update(string_or_file_path.encode('utf-8'))

        except Exception as e:
            logger.error("md5sum -> md5sum:fail [%s]" % (str(e)))
        # logger.error("md5sum result=%s" %(hash.hexdigest()))
        return _hash.hexdigest()

    '''压缩内存数据'''

    def compress(self, data):
        import zlib
        _result = data

        if type(data) is not bytes:
            _result = str(data).encode('utf-8')

        _result = zlib.compress(_result)

        return _result

    '''解压缩内存数据'''

    def decompress(self, data, need_decode=False):
        import zlib
        if type(data) is not bytes:
            return None

        _result = zlib.decompress(data)

        if need_decode:
            _result = self.decode(_result)
        return _result


_string_object = StringObject()

'''chfshan,安装第三方库并import'''


def import_third_module(module_name='requests', reason='', _need_print_log=True, install_module_name=None):
    """嘗試import,若失敗自動安装第三方库并import
    :label [FrameworkManager]:框架管理
    :param module_name: [string] 第三方库的名字(==版本号)
    :param reason: [string] 要安装的原因, 比如哪里需要依赖
    :param _need_print_log: [bool] 是否需要打印该方法产生的日志
    :param install_module_name: [string] 如果安装的库名和import的库名不同,则填入需安装的库名
    :return: [object] 第三方库的object,失败返回None
    :usage:
      paramiko = import_third_module('paramiko')
      paramiko.SSHClient()
      time_test = import_third_module('time')
      time_test.sleep(1)
      xlrd = import_third_module(module_name="xlrd=1.2.0")
      if xlrd is None:
        print('import xlrd failed')
      else:
      xlrd.open_workbook('chfshan.xlsx')
    """
    _import_module_name = str(module_name).split('=')[0]
    module_obj = None

    '''第一步,尝试导入第三方库,若成功return'''
    try:
        # from importlib import import_module
        # module_obj = import_module(_import_module_name)
        module_obj = __import__(_import_module_name)
        return module_obj
    except:
        pass

    import subprocess
    def popen_run_cmd(cmd):
        result = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        return result.communicate(), result.returncode

    # 如果安装的库名和import的库名,拼接安装库名+版本号
    _install_module_name = str(install_module_name) if install_module_name else _import_module_name
    if len(str(module_name).split('==')) > 1:
        _install_module_name += '==' + str(module_name).split('==')[1]

    if _need_print_log:
        logger.info(
            "*Need install third model[%s],cmd=[pip install %s], reason=%s" % (_install_module_name, _install_module_name, str(reason)))

    '''第二步,通过pip安装第三方库'''
    try:
        python_path = sys.executable
        pip_path = str(python_path) + ' -m pip '
        # pip_path = 'pip'
        # if sys.version_info > (3, 0):
        #     pip_path = 'pip3'
        # pip_path = str(python_path).replace('python','pip')
        # result = os.system('sudo pip install %s' % module_name) #256 Operation not permitted，用poen能成功
        result, pcode = popen_run_cmd(str(pip_path) + " install %s" % _install_module_name)
        logger.debug("[pip install %s] ret = %s, cmd=" % (_install_module_name, str(result)) + str(
            pip_path) + " install %s" % _install_module_name)
        if str(pcode).strip() == '127':  # popen=127命令不存在(即linux命令状态码,os.system返回32512), 状态码1：未知错误
            file_str = os.path.join(_get_current_code_py_path_and_name()[1], "get-pip.py").replace('\\', '/')
            py_ver = platform.python_version()[0:3]
            if not os.path.exists(file_str):
                if 'win32' in sys.platform:
                    result, pcode = popen_run_cmd(
                        'certutil -urlcache -split -f https://bootstrap.pypa.io/pip/%s/get-pip.py %s' % (
                        py_ver, file_str))
                else:
                    result = popen_run_cmd(
                        "curl -sSL https://bootstrap.pypa.io/pip/%s/get-pip.py -o %s" % (py_ver, file_str))
                    if str(result).strip() == '127':
                        result = popen_run_cmd(
                            "wget https://bootstrap.pypa.io/pip/%s/get-pip.py --no-check-certificate" % (py_ver))
            logger.info(
                "[pip install %s] - download get_pip.py ret = %s, cmd=[curl/wget -sSL https://bootstrap.pypa.io/pip/%s/get-pip.py -o get-pip.py ]" % (
                _install_module_name, str(result), py_ver))
            result = popen_run_cmd(str(python_path) + ' ' + str(file_str))
            logger.info("[pip install %s] - install get_pip.py ret = %s, cmd=[ python get-pip.py ]" % (
            _install_module_name, str(result)))
            result, pcode = popen_run_cmd('%s install %s' % (pip_path, _install_module_name))
            logger.info("[pip install %s] - ret = %s, cmd=[ pip install %s ]" % (_install_module_name, str(result), _install_module_name))
            if 'win32' not in sys.platform and str(pcode).strip() == '127':
                result = popen_run_cmd("sudo %s %s" % (python_path, file_str))  # os.system会返回256Operation not permitted
                result = popen_run_cmd('sudo %s install %s' % (pip_path, module_name))
    except Exception:
        logger.info("pip install [%s] fail=%s" % (_install_module_name, str(traceback.format_exc())))

    '''第三步,再次尝试导入'''
    try:
        # module_obj = import_module(_import_module_name)
        module_obj = __import__(_import_module_name)
        if _need_print_log:
            logger.info(
                "*Third model[{0}] install success,cmd=[pip install {0}], reason={1}".format(module_name, str(reason)))
    except Exception:
        logger.info("import[%s] fail=%s" % (_import_module_name, str(traceback.format_exc())))

    return module_obj


"""xlzhou&chfshan, ssh远程操作服务器, 获取/上传/执行命令"""


class _SSHConnection(object):
    """
    ssh连接，以及连接后的相关操作
    :label [System&Monitor]:系统操作和性能监控相关
    usage:
    connection = SSHConnection("192.168.121.88",26222,"ec2-user","ec2@gs.com")
    connection.put("client.py","client.py")
    connection.exec_command("python client.py")
    """
    # _NEED_START_MAINTANCE = []
    _CONN_DICT = {}  # [dict] 格式{(ip,port,username):ssh_conn_obj},用于各层多次实例化该类时,同一远程服务器只建1条链路并用于keepalive on time链路
    _CONN_ACTION_TIME = {}  # [dict] {(ip,port,username):aciton_time} 上层有动作的时间,用于判断和当前时间差是否超过_ssh_keep_alive_timeout，超过自动关闭链路并销毁socket
    _GLOBAL_THREAD_LOCK = []

    def __init__(self, host, port, username, password, timeout=5, need_print_log=True):
        self.paramiko = import_third_module("paramiko", _need_print_log=need_print_log)
        self.stop = False
        self._host = host
        try:
            self._port = int(port)
        except:
            self._port = -1
        self._username = username
        self._password = password
        self.ssh_conn = None  # ssh client object （paramilo或 linux自带的ssh实例）
        self._sftp = None

        self.error_msg = None  # 错误的消息内容
        self.exit_status_code = None  # 远程执行命令后的退出状态
        self.error_code = ERROR_CODE_UNKNOWN_ERROR
        self.is_remote_support_sudo = None  # 远程是否支持sudo的命令
        self.remote_current_dir = None  # 远程当前路径, 即pwd的值
        self._need_print_log = need_print_log
        self.timeout = timeout  # 超时时间,保活socket connect超时,账密校验超时、banner超时等
        self._thread_lock = threading.Lock()
        self._ssh_cmd_path = 'ssh'
        self._is_paramiko_support = False  # 第三方库是否成功,若失败通过系统ssh直接执行ssh命令
        self._is_remote_conneted = False  # 和远程的tcp链路是否正常
        self._ssh_keep_alive_timeout = 600  # 10分钟s无动作就关闭链路

        if len(self._GLOBAL_THREAD_LOCK) == 0:
            self._GLOBAL_THREAD_LOCK.append(threading.Lock())
            self._ssh_socket_maintaince()

        self._connect(timeout=self.timeout)  # 建立连接,【注意】该动作会生成1个socket并创一条tcp链路
        # self._NEED_START_MAINTANCE.append(True)
        # if len(self._GLOBAL_THREAD_LOCK) <= 1:  #仅仅上层首次实例化该类时，会启动链路的维护线程
        #     self._ssh_socket_maintaince()

    def _update_global_data(self, dict_object, key=None, value=None):
        if key is None:
            key = (self._host, self._port, self._username)
        self._GLOBAL_THREAD_LOCK[0].acquire()
        dict_object.update({key: value})
        self._GLOBAL_THREAD_LOCK[0].release()

    '''chfshan连接或重连远程服务器'''

    def _connect(self, timeout=10):
        self.error_code = ERROR_CODE_SUCCESS
        self.error_msg = ''
        _start_time = time.time()
        '''更新全局链路连接,未关闭时,不再连接,直接返回'''
        try:
            self._update_global_data(self._CONN_ACTION_TIME, value=_start_time)
            '''链路未关闭时,不再连接,直接返回'''
            if self.ssh_conn is not None and self.ssh_conn.get_transport().active and self._is_remote_conneted:
                return self.ssh_conn
        except Exception:
            pass

        self._thread_lock.acquire()
        '''创建sshclient并和远程连接,sshclient已创建不会进行二次创建'''
        try:
            '''未实例化ssh_conn,进行实例化,会创建1个socket'''
            if self.ssh_conn is None:
                '''实例化SSHClient'''
                self.ssh_conn = self.paramiko.SSHClient()
                self._is_paramiko_support = True  # 能识别到.SSHClient() 说明支持
                # 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接 ，此方法必须放在connect方法的前面
                self.ssh_conn.set_missing_host_key_policy(self.paramiko.AutoAddPolicy())
            '''跟远端建立tcp连接,概率出现connect立即抛异常timeout的情况，循环两次'''
            # logger.warning('connect [%s:%s] %s:%s ,timeout(%s)ms,remote_server=%s,conns=%s' %
            #                (self._host, self._port, self._username, self._password, str(timeout * 1000),
            #                 str(self.remote_server),str(self._CONN_DICT)))

            for i in range(0, 1):
                '''连接SSH服务端，以用户名和密码进行认证 ，调用connect方法连接服务器'''
                '''ssh.connect()的时候总会弹出异常 ‘No existing session’,使用allow_agent=False, look_for_keys=False解决'''
                self.ssh_conn.set_missing_host_key_policy(self.paramiko.AutoAddPolicy())
                try:
                    self.ssh_conn.connect(hostname=self._host,
                                          port=self._port,
                                          username=self._username,
                                          password=self._password,
                                          # timeout=10,  #太短第三方库startclient方法会启动失败
                                          allow_agent=True,
                                          # 不设置false第三方库报错No existing session  设置False遇到部分机子connect不上的会报该错并不可恢复
                                          look_for_keys=False,
                                          # compress=True, #第三方库概率报错No existing session
                                          # banner_timeout=timeout,
                                          # auth_timeout=timeout
                                          )
                except (Exception, BaseException, socket.error) as e:  # 此处 必须对self.remote_server.connect做except，不然第三方库卡死
                    self.error_code = ERROR_CODE_TCP_CONNECT  # 此处必须重写，不能用raise不然卡死... 太难了....
                    self.error_msg = str(e)
                    # logger.warning('connect [%s:%s] %s:%s ,timeout(%s)ms,remote_server=%s,conns=%s,%s' %
                    #                (self._host, self._port, self._username, self._password, str(timeout * 1000),
                    #                 str(self.remote_server), str(self._CONN_ACTION_TIME),self.error_msg))
                else:
                    self._is_remote_conneted = True
                    self._update_global_data(self._CONN_DICT, value=self.ssh_conn)
                    break
            '''更新重连/首次的连接object到全局,给首个实例维护使用'''
            # self._CONN_DICT.update({(self._host, self._port, self._username): self.remote_server})
            if self.error_code == ERROR_CODE_TCP_CONNECT:  # 此处必须重写，不能用raise不然卡死... 太难了....
                raise Exception(self.error_msg)
        except (Exception, BaseException, socket.error) as e:
            self.error_code = ERROR_CODE_TCP_CONNECT
            self.error_msg = str(e)
            self._is_remote_conneted = False
            self.close()
            # logger.warning((self._host,self._username,self._password,self._port,timeout,traceback.format_exc()))
        self._thread_lock.release()
        if self._need_print_log:
            _duration = str((time.time() - _start_time) * 1000 // 1)
            logger.info('ssh[127.0.0.1 <-> %s:%s] with connected,duration(%s)ms,timeout(%s)ms,error_code=%s' % (
            self._host, self._port, _duration, str(timeout * 1000), str(self.error_code)))
            if self.error_msg:
                logger.warning('connect [%s:%s] duration(%s)ms,timeout(%s)ms,failed=%s,conns=%s' %
                               (self._host, self._port, _duration, str(timeout * 1000),
                                str(self.error_msg), str(len(self._CONN_DICT))))

    def get(self, remotefile, localfile):
        '''
        从远程机器获取文件
        :param remotefile:远程机子的文件路径+文件名
        :param localfile: 下载到本机子的文件路径+文件名
        :return:
        '''
        '''2023-04-21,xlzhou,增加paramiko不支持情况下，采用本地scp远程执行命令方式下载文件'''
        if not self._is_paramiko_support:
            logger.warning('Paramiko is not support, execute command instead of bash command......')
            result = self._get_file_by_local_shell(remotefile=remotefile, localfile=localfile)
            return result

        self._update_global_data(self._CONN_ACTION_TIME, value=time.time())
        # self._CONN_ACTION_TIME.update({(self._host, self._port, self._username): time.time()})
        result = False
        # self.error_code = ERROR_CODE_SUCCESS
        # self.error_msg = ''
        try:
            self._connect()  # 目的: sshconn连接断开时会重连
            if self._sftp is None:
                self._sftp = self.ssh_conn.open_sftp()
            result = self._sftp.get(remotefile, localfile)
            self.error_code = 0
            result = True
        except Exception as e:
            logger.error("[%s] download [%s] failed, reason=[%s]" % (str(self._host), remotefile, e))
            self.error_msg = e
            self.error_code = ERROR_CODE_BASH_CMD
        if self._need_print_log:
            logger.info('get [%s] to (%s)[%s],result=%s' % (localfile, self._host, remotefile, result))

        return result

    def put(self, localfile, remotefile):
        '''
        本机上传文件到远程机器
        :param localfile: 本机的文件路径+文件名
        :param remotefile: 远程机子的文件路径+文件名
        :return:
        '''
        '''2023-04-21,xlzhou,增加paramiko不支持情况下，采用本地scp远程执行命令方式上传文件'''
        if not self._is_paramiko_support:
            logger.warning('Paramiko is not support, execute command instead of bash command......')
            result = self._put_file_by_local_shell(localfile=localfile, remotefile=remotefile)
            return result

        self._update_global_data(self._CONN_ACTION_TIME, value=time.time())
        # self._CONN_ACTION_TIME.update({(self._host, self._port, self._username): time.time()})
        result = False

        # self.error_msg = ''
        # self.error_code = ERROR_CODE_SUCCESS
        self._connect()  # 目的: sshconn连接断开时会重连
        self._thread_lock.acquire()
        try:

            if self._sftp is None:
                self._sftp = self.ssh_conn.open_sftp()
            self._sftp.put(localfile, remotefile)
            result = True
        except Exception as e:
            logger.warning(
                'put [%s] to (%s)[%s],result=%s' % (localfile, self._host, remotefile, str(traceback.format_exc())))
            self.error_msg = str(e)
            self.error_code = ERROR_CODE_BASH_CMD

        self._thread_lock.release()

        if self._need_print_log:
            logger.info('[%s:%s]put [%s] to [%s:%s],result=%s' % (
            self._host, str(self._port), localfile, self._host, remotefile, result))
        return result

    '''[2022.5.10] chfshan,远程机器上执行命令，返回命令console输出的所有结果, 以open_session的方式执行，远程不返回退出符，timeout秒后超时, 其他方式部分会概率出现卡死'''

    def exec_command(self, command, timeout=3, need_run_with_sudo=False, need_reconnect=True):
        """远程执行命令
        usage:
            _conn = SSHConnection('192.168.121.200',26222,'root','123456')
            result = _conn.exec_command('pwd')
            print(result)
        :param command: [string] 远程执行的完整命令
        :param timeout: [int] 默认超时时间
        :param need_reconnect: [int] 链路断开是否要重连链路
        :return: [string] 远程命令执行的的完整结果（跟console中输出一直）, 失败返回None
            命令执行失败, self.error_code=对应的错误码(即非0) 同时self.error_msg输出对应的错误文本
        """
        '''2023-04-21,xlzhou,增加paramiko不支持情况下，采用本地ssh远程执行命令方式获取结果'''
        result = ''

        if need_run_with_sudo:
            command = self.__get_sudo_cmd(command=command)
        if not self._is_paramiko_support:
            # logger.warning('Paramiko is not support, execute command instead of bash command......')
            result = self._exec_commond_by_local_shell(command=command, timeout=timeout)
            return result
        _start_time = time.time()

        self._update_global_data(self._CONN_ACTION_TIME, value=time.time())
        self.exit_status_code = None
        # self.error_msg = ''
        # self.error_code = ERROR_CODE_SUCCESS  #不需要,_conncect会重置
        if need_reconnect:
            self._connect(timeout=int(timeout) * 2)  # 目的: sshconn连接断开时会重连

        self._thread_lock.acquire()
        try:
            _timeout = 30
            if int(timeout) > 30:
                _timeout = timeout
            self._channel = self.ssh_conn.get_transport().open_session(timeout=_timeout)

            # self.channel.invoke_shell()
            '''pty虽然能解决部分机子报must have a tty to run,但不稳定有时无返回有时返回的结果会加\r有时返回不全等问题'''
            '''self._channel.get_pty()'''

            self._channel.settimeout(_timeout)
            if command == "" or command is None:
                raise Exception('wrong command')
            self._channel.exec_command(command + '\n')
            buff = ""
            _key = True
            _start_time = time.time()
            while (_key and time.time() - _start_time <= timeout):
                if self._channel.recv_ready():
                    for i in range(50):
                        _data = self._channel.recv(4096)
                        if not _data:
                            break
                        buff = str(buff) + str(_string_object.decode(_data))

                    # buff = str(buff) + str(_string_object.decode(self._channel.recv(4096*2)))
                    # logger.critical((self._host, buff, 'ready'))
                if self._channel.recv_stderr_ready():
                    self.error_msg = str(self.error_msg) + str(_string_object.decode(self._channel.recv_stderr(4096)))
                    # result = result + self.error_msg
                    self.error_code = 100
                    # logger.critical((self._host, buff, 'error'))
                if self._channel.exit_status_ready():
                    # logger.critical(('exit_status_ready',buff))
                    time.sleep(0.1)
                    if self._channel.recv_ready():
                        for i in range(100):
                            _data = self._channel.recv(4096)
                            if not _data:
                                break
                            buff = buff + str(_string_object.decode(_data))
                    exit_status = self._channel.exit_status_ready()
                    self.exit_status_code = self._channel.recv_exit_status()
                    _key = False
                    # logger.critical((self._host,buff))
                    self._channel.close()
                    result = buff + str(self.error_msg)
                    # logger.critical((buff,self.error_msg))
                    if exit_status != 0 and self.error_msg:
                        raise Exception(self.error_msg)
                time.sleep(0.01)
            self.error_code = ERROR_CODE_SUCCESS
            self._channel.close()
        except Exception as e:
            self.error_code = ERROR_CODE_BASH_CMD
            if str(e).find('SSH session not active') != -1:
                self._is_remote_conneted = False
            if not self.error_msg:
                self.error_code = ERROR_CODE_SCRIPT_SYNTAX_ERROR
            self.error_msg = e
        self._thread_lock.release()

        if self._need_print_log:
            _duration = str((time.time() - _start_time) * 1000 // 1)
            logger.info('[%s:%s] exec [%s],T=%s/%sms,exit_status=%s,father=[%s],result=%s' % (
            self._host, str(self._port), command, _duration, str(timeout * 1000), str(self.exit_status_code),
            str(sys._getframe(1).f_code.co_name), str(result)[:300]))
            if self.error_code != ERROR_CODE_SUCCESS:
                logger.warning(
                    '[%s:%s] exec [ %s ],T=%s/%sms, fail=%s,exit_status=%s,father=[%s],result=%s,remote_server=%s' % (
                    self._host, str(self._port), command, _duration, str(timeout * 1000), str(traceback.format_exc()),
                    str(self.exit_status_code), str(sys._getframe(1).f_code.co_name), str(result)[:300],
                    str(self.ssh_conn)))
        # 'pwd' 等命令返回有回车符，避免上层二次处理
        result = result[:-1] if str(result).endswith('\n') else result
        result = result[:-1] if str(result).endswith('\r') else result
        return result

    def __get_sudo_cmd(self, command, timeout=3):
        """远程执行命令
        :param command: [String],远程执行的完整命令
        :param is_remote_support_sudo: [bool or None] None:不确定是否支持;True:支持; False:远程服务器不支持sudo命令
        :param timeout: [int],默认超时时间,单位秒
        :return: [string],远程命令执行的结果
        :usage:
            _conn = SSHConnection('192.168.121.44',22,'root','123456')
            result = _conn.exec_sudo_cmd('pwd')
            print(result) #执行sudo pwd，返回  /root

        """
        pre_check_cmd = 'sudo pwd'
        if self.is_remote_support_sudo is None:
            try_sudo = self.exec_command(pre_check_cmd, need_run_with_sudo=False,
                                         timeout=timeout)  ## sudo部分机子 sudo + cmd 报错, ipvt10如121.247报"you must have a tty to run sudo", ucm报sudo不支持.另python远程执行sudo永远不会返回必须等超时
            if not try_sudo:  # 有时候pwd会执行失败，返回为空, 做保护
                try_sudo = self.exec_command(pre_check_cmd, need_run_with_sudo=False, timeout=timeout)
            if str(try_sudo).find('sudo: not found') != -1 or str(try_sudo).find('tty to run sudo') != -1:
                command = str(command).replace('sudo', '')
                self.is_remote_support_sudo = False
            else:
                if not str(command).strip().startswith('sudo ') and not str(command).strip().startswith('script '):
                    command = 'sudo ' + str(command)
                self.is_remote_support_sudo = True

        if self.is_remote_support_sudo is True and not str(command).strip().startswith('sudo'):
            command = 'sudo ' + str(command)
        if self.is_remote_support_sudo is False:
            command = str(command).replace('sudo ', ' ').strip()

        return command

    '''[2023-04-21], add by xlzhou, 兼容无法安装paramiko第三方库的系统环境，采用本地环境执行shell命令的方式'''

    def _exec_commond_by_local_shell(self, command, timeout=3):
        # linux平台采用pty伪终端实现ssh连接所需的password交互
        return_result = None
        if platform.system().lower() == 'linux':
            # 获取ssh的安装路径
            self.error_code = ERROR_CODE_SUCCESS
            # if not self._ssh_local_path:
            #     _ssh_local_path = lo_cli.run_cmd(command="which ssh")
            #     if not _ssh_local_path:
            #         logger.error('No ssh installed local, cannot execute command with ssh!')
            #         self.error_code = ERROR_CODE_BASH_CMD
            #         return None
            #
            #     self._ssh_local_path = _ssh_local_path

            # 兼容处理command为组装好的list结构情况，未组装好的commands，默认用ssh命令路径和username，password和传进来的command组装需要执行的完整命令
            # [chfshan] 2024.1.4, fix bug:  cmd需要用双引号,处理cmd中带有引号
            # [chfshan] 2024.1.19, fix bug: cmd含$时需转移,cmd含有双引号转义
            command = '"' + str(command).replace('"', '\\"') + '"'
            command = str(command).replace('$', '\$')

            commands = [
                self._username + '@' + self._host,
                '-p', str(self._port),
                '-o', 'NumberOfPasswordPrompts=2',
                '-o', 'ConnectTimeout=' + str(timeout),  # 设置ssh连接超时时间
                command,
            ]

            # 使用ssh命令本地执行远程commond操作，获取远端机器command执行结果
            return_result = lo_cli.run_cmd_need_input(command='ssh', command_args=commands, password=self._password)
            # lo_cli执行commond后，error_code被置位，则说明执行失败，置位自己的error_code和error_msg，并将返回结果result置为None
            if lo_cli.error_code != ERROR_CODE_SUCCESS:
                self.error_code = ERROR_CODE_BASH_CMD
                self.error_msg = return_result
                return_result = None
        # 非linux平台暂不支持
        else:
            logger.warning('Current system cannot support execute with ssh command!')
            self.error_code = ERROR_CODE_BASH_CMD
        return return_result

    '''[2023-04-24], add by xlzhou, 兼容无法安装paramiko第三方库的系统环境，采用本地环境执行shell命令的方式'''

    def _put_file_by_local_shell(self, localfile, remotefile=None, connect_timeout=10):
        # linux平台采用pty伪终端实现ssh连接所需的password交互

        if platform.system().lower() == 'linux':
            self.error_code = ERROR_CODE_SUCCESS
            # 获取scp的安装路径
            # if not self._scp_local_path:
            #     _scp_local_path = lo_cli.run_cmd(command="which ssh")
            #     if not _scp_local_path:
            #         logger.error('No scp installed local, cannot execute command with ssh!')
            #         return None
            #
            #     self._scp_local_path = _scp_local_path

            # 若未定义远端上传路径，则默认上传到登录账户的主目录下：非root用户是/home/[username]，root用户是/root
            if not remotefile:
                remotefile = '~'

            commands = [
                '-P', str(self._port), '-o', 'ConnectTimeout=' + str(connect_timeout),
                localfile,
                                             self._username + '@' + self._host + ':' + remotefile,
                # 设置连接超时时间
            ]

            # 使用scp命令执行上传文件操作
            result = lo_cli.run_cmd_need_input(command='scp', command_args=commands, password=self._password)
            # lo_cli执行commond后，error_code被置位，则说明执行失败，置位自己的error_code和error_msg，并将返回结果result置为None
            if lo_cli.error_code != ERROR_CODE_SUCCESS:
                self.error_code = ERROR_CODE_BASH_CMD
                self.error_msg = result
                result = None

            # 上传操作成功，且未定义remoteFile，文件上传到登录账户的主目录下，获取登录用户的主目录并返回
            if result and remotefile == '~':
                result = self._exec_commond_by_local_shell(command='pwd')
            # 上传成功，已定义remoteFile，返回定义的remoteFile
            elif result:
                result = remotefile
            # 上传失败，result=None（并置位了error_code和error msg）
            else:
                pass

            return result

        # 非linux平台暂不支持
        else:
            logger.warning('Current system cannot support execute with scp command!')
            self.error_code = ERROR_CODE_BASH_CMD
            return None

    '''[2023-04-24], add by xlzhou, 兼容无法安装paramiko第三方库的系统环境，采用本地环境执行shell命令的方式'''

    def _get_file_by_local_shell(self, remotefile, localfile=None, connect_timeout=None):
        # linux平台采用pty伪终端实现ssh连接所需的password交互
        if platform.system().lower() == 'linux':
            self.error_code = ERROR_CODE_SUCCESS

            # 获取scp的安装路径
            # _scp_local_path = lo_cli.run_cmd(command="which scp")
            # if not _scp_local_path:
            #     logger.error('No scp installed local, cannot upload file with scp!')
            #     self.error_code = ERROR_CODE_BASH_CMD
            #     return None

            # 若未执行下载到本地哪个目录下，则默认下载当前目录
            if not localfile:
                localfile = '.'

            commands = [
                '-P', str(self._port),
                self._username + '@' + self._host + ':' + remotefile,
                localfile,
                '-o', 'ConnectTimeout=' + str(connect_timeout),  # 设置连接超时时间
            ]

            # 使用scp命令执行下载文件操作
            result = lo_cli.run_cmd_need_input(command='scp', command_args=commands, password=self._password)
            if lo_cli.error_code != ERROR_CODE_SUCCESS:
                self.error_code = ERROR_CODE_BASH_CMD
                self.error_msg = result
                result = None

            # 下载操作成功，且未定义localfile，文件下载到当前目录，获取并返回当前目录
            if result and localfile == '.':
                result = lo_cli.run_cmd(command='pwd')
            elif result:
                result = localfile
            else:
                pass

            return result

        # 非linux平台暂不支持
        else:
            return False

    # 判断目录/文件是否存在
    def rexists(self, path):
        '''
        判断远程机器上的某个目录或者文件是否存在
        :param path: 远程目录或文件
        :return: 存在返回True，不存在返回False
        '''
        """os.path.exists for paramiko's SCP object
        """
        result = False
        if self._sftp is None:
            self._sftp = self.paramiko.SFTPClient.from_transport(self.ssh_conn.get_transport())
        try:
            self._sftp.stat(path)

        except IOError as e:
            if 'No such file' in str(e):
                result = False
            self.error_msg = e
        else:
            result = True

        return result

    '''[2023.4.18] chfshan 关闭ssh connect'''

    def close(self):
        self.stop = True
        # self._thread_lock.acquire()
        try:
            if self._sftp:
                self._sftp.close()
            if self.ssh_conn:
                # self.remote_server.get_transport().sock.close()
                # self.remote_server.get_transport().close()
                self.ssh_conn.close()
        except:
            logger.debug(traceback.format_exc())

        if self._CONN_DICT.get((self._host, self._port, self._username)):
            self._CONN_DICT.pop((self._host, self._port, self._username))
        if self._CONN_ACTION_TIME.get((self._host, self._port, self._username)):
            self._CONN_ACTION_TIME.pop((self._host, self._port, self._username))

        # self._thread_lock.release()
        # self.remote_server = None  #会导致反复创建实例第三方库的SSHClient实例，第三方库有bug,会报出No existing session 不可恢复
        self._is_remote_conneted = None
        self._sftp = None

    '''[2023.4.18] chfshan,链路维护'''

    def _ssh_socket_maintaince(self):

        def _do_ssh_socket_maintaince():
            while not GLOBAL_VAR.STOP:
                if self._need_print_log:
                    logger.info(('while loop start', self._host, self._username))
                time.sleep(int(self._ssh_keep_alive_timeout))
                _now_time = time.time()
                '''和当前时间差大于self._ssh_keep_alive_timeout,关闭ssh链路'''
                for ssh_info in list(self._CONN_DICT.keys()):
                    try:
                        ssh_conn = self._CONN_DICT[ssh_info]
                        if _now_time - int(self._CONN_ACTION_TIME[ssh_info]) > int(self._ssh_keep_alive_timeout):
                            ssh_conn.close()
                            self._update_global_data(self._CONN_DICT, key=ssh_info, value=ssh_conn)
                            time.sleep(0.1)
                            # logger.info((self._host,self._port,'timeout for maintaince, ssh closed'))
                            # self._CONN_DICT.update({ssh_info: remote_server})
                    except:
                        pass
            self.close()
            for ssh_info, ssh_conn in self._CONN_DICT.items():
                ssh_conn.close()
            logger.debug('[%s<->%s]maintain thread exit' % (self._host, self._username))

        T = threading.Thread(target=_do_ssh_socket_maintaince, args=(), name='%s_ssh_conn_maintain' % str(self._host))
        T.daemon = True
        T.start()
        if self._need_print_log:
            logger.info(('created thread,', self._host, self._username))

'''[2024-06-17], add by xunli, jump server超时等待装饰器'''
def _jump_server_wait_until_execute_pass(func):
    """
    jump server超时查询装饰器
    """
    def _wait_until_execute_pass(*args, **kwargs):
        timeout = kwargs.get('timeout', 30)
        min_interval = kwargs.get("min_interval", 0.05)
        max_interval = kwargs.get("max_interval", 0.1)
        switch_stage = kwargs.get("switch_stage", 5)
        query_interval = min_interval
        switch_interval = False
        error_flag = kwargs.get("error_flag", "error|")
        start_time = time.time()
        while True:
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    raise Exception(e)
                else:
                    if elapsed_time >= switch_stage and not switch_interval:
                        switch_interval = True
                        query_interval = max_interval
                    time.sleep(query_interval)
            else:
                if isinstance(result, str) and result.startswith(error_flag):
                    raise Exception(result)
                return result

    return _wait_until_execute_pass

"""[2024-06-12], add by xunli, jump server 相关操作类"""
class JumpServer(object):
    """
    :label [System&Monitor]:系统操作和性能监控相关
    """
    from collections import namedtuple
    JUMP_SERVER_CODE = namedtuple('JUMP_SERVER_CODE', ['error_code', 'error_msg', 'error_flag'])
    _ERROR_CODE_JUMP_ASSET_EXIST_MULTI = JUMP_SERVER_CODE(ERROR_CODE_JUMP_ASSET_EXIST_MULTI,
                                                          "remote host asset having multiple",
                                                          "remote host asset having multiple")
    _ERROR_CODE_JUMP_ASSET_IS_NONE = JUMP_SERVER_CODE(ERROR_CODE_JUMP_ASSET_IS_NONE, "remote host asset num is none",
                                                      "remote host asset num is none")
    _ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST = JUMP_SERVER_CODE(ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST,
                                                                 "remote host username not exist",
                                                                 "无可用账号")
    _ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE = JUMP_SERVER_CODE(ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE,
                                                                  "remote host python version not"
                                                                  " support jump server api",
                                                                  "requires a minimum of Python")
    _ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT = JUMP_SERVER_CODE(ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT,
                                                                 "remote host username password error",
                                                                 "shell: Invalid/incorrect password")
    _ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL = JUMP_SERVER_CODE(ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL,
                                                                "remote host system not support shell",
                                                                "Module shell is not suitable for this asset")
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(JumpServer, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, timeout=10):
        if not self._initialized:
            self._init_lock = threading.Lock()
            self._jump_host = "jumplocal.ipvideotalk.cn"
            self._jump_port = 443
            self._jump_username = _get_password_by_ini("jumpserver", "username")
            self._jump_password = _get_password_by_ini("jumpserver", "password")
            self._need_print_log = True
            self._timeout = timeout
            self._socket_lock = threading.Lock()
            self._socket = self._get_socket_connection_by_http_client()
            self._socket_time = time.time()
            self._token = self._get_jump_server_token()
            self._clean_interval = 600
            # (remote_host, remote_username):(error_code,asset_info,support_sudo,activity_time)
            self.remote_asset_info = {}
            self._default_username = ["ec2-user", "root"]
            self._custom_username = {}
            # python2没有daemon参数
            self._clean_thread = threading.Thread(target=self._clean_expired_assets)
            self._clean_thread.daemon = True
            self._clean_thread.start()
            self._initialized = True

    '''[2024-06-13], add by xunli, 更新jump server配置'''
    def _update_global_config(self, jump_host=None, jump_port=None, jump_username=None, jump_password=None,
                             need_print_log = None):
        """
        更新jump server全局配置
        :param jump_host: [string] jump server host地址
        :param jump_port: [int] jump server 端口
        :param jump_username: [string] jump server用户名
        :param jump_password: [string] jump server密码
        :param need_print_log: [bool] 是否需要打印日志，True-打印，False-不打印
        :return: None
        :usage:
            j=JumpServer()
            j.update_global_config("jump server host", "jump server host", "jump server用户名", "jump server密码", True)
        """
        self._jump_host = jump_host or self._jump_host
        self._jump_port = jump_port or self._jump_port
        self._jump_username = jump_username or self._jump_username
        self._jump_password = jump_password or self._jump_password
        if need_print_log is False:
            self._need_print_log = False
        if not all([jump_host, jump_port, jump_username, jump_password]):
            if self._socket:
                self._socket.close()
                self._socket = self._get_socket_connection_by_http_client()
            self._token = self._get_jump_server_token()
            self.remote_asset_info = {}

    '''[2024-06-19], add by xunli, 获取一个用于发送http请求的socket'''
    def _get_socket_connection_by_http_client(self):
        """
        获取http.client的连接
        :return: [object] http.client连接实例
        """
        self._check_system_python_version()
        try:
            import http.client as http_client
        except ImportError:
            import httplib as http_client
        if self._jump_port == 443:
            s = http_client.HTTPSConnection(self._jump_host, self._jump_port, timeout=self._timeout)
        else:
            s = http_client.HTTPConnection(self._jump_host, timeout=self._timeout)
        return s

    '''[2024-06-19], add by xunli, 组装重定向的url地址'''
    def _generate_url_api(self, api):
        """
        生成url请求api
        :param api:[string] api地址
        :return: [string] 组装的请求url
        """
        if self._jump_port == 80:
            request_url = "http://%s%s" % (self._jump_host, api)
        else:
            request_url = "https://%s%s" % (self._jump_host, api)
        return request_url

    '''[2024-06-19], add by xunli, 发送http请求'''
    def _send_request_by_http_client(self, method, api, header, data):
        """
        通过http.client发送http请求获取响应
        :param method: [string] 请求方法
        :param api: [string] api路径
        :param header: [dict] 请求头
        :param data: [dict] 请求体
        :return: [tuple] (响应对象，响应结果)
        """
        try:
            import http.client as http_client
        except ImportError:
            import httplib as http_client
        json_data = data
        if isinstance(data, dict):
            json_data = json.dumps(data)
        for i in range(2):
            with self._socket_lock:
                self._socket_time = time.time()
                if self._socket is None:
                    if self._need_print_log:
                        logging.info("JumpServer http client recreate")
                    self._socket = self._get_socket_connection_by_http_client()
                try:
                    self._socket.request(method, api, headers=header, body=json_data)
                    response = self._socket.getresponse()
                    resp_data = response.read()
                    return response, resp_data
                except http_client.HTTPException as e:
                    if i == 0:
                        self._socket.close()
                        self._socket = self._get_socket_connection_by_http_client()
                        if self._need_print_log:
                            logging.warning(
                                "JumpServer http client will reconnect, details: %s" % str(e))
                        continue
                    if self._need_print_log:
                        logging.warning("JumpServer http client reconnect error, details: %s" % str(e))
                    raise Exception(
                        "JumpServer Error, http client reconnect error, details: %s" % str(e))
                except:
                    raise Exception("JumpServer Error, http client send error, details: %s" % traceback.format_exc())

    '''[2024-06-19], add by xunli, 解析http请求'''
    def _parse_response_http_client(self, resp_obj, resp_data):
        """
        解析响应结果
        :param resp_obj: [object] 响应对象
        :param resp_data: [string] 响应数据
        :return: [dict] 响应结果
        """
        try:
            if 300 <= resp_obj.status < 400:
                resp = {"status_code": resp_obj.status, "location": resp_obj.getheader("Location")}
                return resp
            json_data = json.loads(resp_data)
            resp = {"status_code": resp_obj.status, "body": json_data}
            return resp
        except:
            raise Exception("JumpServer Error, api response cannot parse, details: %s" % resp_data)

    '''[2024-06-19], 发送http请求，获取响应'''
    def _send_request_parse_response(self, method, api, header, data=None):
        """
        发送请求并获取响应
        :param method: [string] 请求方法
        :param api: [string] api url
        :param header:[dict] 请求头
        :param data: [dict] 请求body
        :return: [dict] 响应结果
        """
        for i in range(2):
            resp_obj, resp_data = self._send_request_by_http_client(method, api, header, data)
            response = self._parse_response_http_client(resp_obj, resp_data)
            status_code = response.get("status_code")
            if 300 <= status_code < 400 and i == 0:
                new_api = response.get("location")
                api = self._generate_url_api(new_api)
                continue
            if status_code >= 400:
                error_msg = response.get("body", {}).get("detail")
                if error_msg:
                    if sys.version_info[0] < 3:
                        tmp_str = "刷新的令牌或缓存无效".decode("utf-8")
                    else:
                        tmp_str = "刷新的令牌或缓存无效"
                    if tmp_str in error_msg and i == 0:
                        self._token = self._get_jump_server_token()
                        header["Authorization"] = "Bearer %s" % self._token
                        continue
                else:
                    raise Exception("JumpServer error, api request error, response details: %s" % response)
            return response

    '''[2024-06-19], add by xunli, 生成jumpserver的请求头'''
    def _generate_header(self, token=None):
        """
        生成请求头
        :param token:[string] jump server的token
        :return: [dict] 请求头
        """
        header = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Connection": "keep-alive"
        }
        if token:
            header["Authorization"] = "Bearer %s" % token
        return header

    '''[2024-06-19], add by xunli, jump server 获取用户资产'''
    def _jump_api_perms_users_self_assets(self, remote_host):
        """
        jump server api 获取用户资产信息
        :param remote_host: [string] 服务器地址
        :return: [dict] 响应结果
        """
        api = "/api/v1/perms/users/self/assets/?address=%s" % remote_host
        header = self._generate_header(self._token)
        response_body = self._send_request_parse_response("GET", api, header)
        return response_body

    '''[2024-06-19], add by xunli, jump server 获取token'''
    def _jump_api_authentication_auth(self):
        """
        jump server api 获取token
        :return: [dict] 响应结果
        """
        api = "/api/v1/authentication/auth/"
        header = self._generate_header()
        data = {
            "username": self._jump_username,
            "password": self._jump_password
        }
        response_body = self._send_request_parse_response("POST", api, header, data)
        return response_body

    '''[2024-06-19], add by xunli, jump server 创建任务'''
    def _jump_api_ops_jobs_cmd_task(self, remote_username, cmd, asset_id):
        """
        jump server api 创建
        :param remote_username: [string] 远程服务器用户名
        :param cmd: [string] 待执行的指令
        :param asset_id: [string] 资产ID
        :return: [dict] 响应结果
        """
        api = "/api/v1/ops/jobs/"
        header = self._generate_header(self._token)
        data = {
            "type": "adhoc",
            "module": "shell",
            "args": cmd,
            "assets": [asset_id],
            "runas_policy": "skip",
            "runas": remote_username,
            "timeout": -1,
            "nodes": [],
            "instant": True,
            "is_periodic": False
        }
        response_body = self._send_request_parse_response("POST", api, header, data)
        return response_body

    '''[2024-06-19], add by xunli, jump server 获取任务执行状态'''
    def _jump_api_ops_job_execution_task_detail(self, task_id):
        """
        jump server api 获取任务执行状态
        :param task_id: [string] 任务ID
        :return: [dict] 响应结果
        """
        api = "/api/v1/ops/job-execution/task-detail/%s" % task_id
        header = self._generate_header(self._token)
        response_body = self._send_request_parse_response("GET", api, header)
        return response_body

    '''[2024-06-19], add by xunli, jump server 获取任务日志打印'''
    def _jump_api_ops_ansible_job_execution_log(self, task_id):
        """
        jump server api 获取ansible打印
        :param task_id: [string] 任务ID
        :return: [dict] 响应结果
        """
        api = "/api/v1/ops/ansible/job-execution/%s/log/" % task_id
        header = self._generate_header(self._token)
        response_body = self._send_request_parse_response("GET", api, header)
        return response_body

    '''[2024-06-19], add by xunli, jump server 创建文件任务'''
    def _jump_api_ops_jobs_file_task(self, remote_username, asset_id, remote_file):
        """
        jump server 创建文件上传的任务
        :param asset_id: [string]
        :param remote_file: [string] 远端文件路径
        :return: [dict] 响应结果
        """
        api = "/api/v1/ops/jobs/"
        header = self._generate_header(self._token)
        data = {
            "assets": [asset_id],
            "nodes": [],
            "module": "shell",
            "args": json.dumps({"dst_path": remote_file}),
            "type": "upload_file",
            "runas": remote_username,
            "runas_policy": "privileged_first",
            "instant": False,
            "is_periodic": False,
            "timeout": -1
        }
        response_body = self._send_request_parse_response("POST", api, header, data)
        return response_body

    '''[2024-07-04], add by xunli, jump server 获取资产的用户名'''
    def _jump_api_ops_username(self, asset_id):
        """
        获取资产的用户名
        :param asset_id: [string] 资产ID
        :return: [dict] 响应结果
        """
        api = "/api/v1/ops/username-hints/"
        header = self._generate_header(self._token)
        data = {"nodes": [], "assets": [asset_id], "query": ""}
        response_body = self._send_request_parse_response("POST", api, header, data)
        return response_body


    '''[2024-06-19], add by xunli, jump server 生成文件上传的body'''
    def _generate_http_multipart_body(self, boundary, job_id, local_file, remote_file):
        """
        生成文件上传的请求body
        :param boundary: [string] 唯一boundary ID
        :param job_id: [string] 工作ID
        :param local_file:[string] 本地文件路径
        :param remote_file: [string] 远端文件路径
        :return: [string] 请求body
        """
        body = []
        body.append("--%s" % boundary)
        body.append('Content-Disposition: form-data; name="job_id"')
        body.append('')
        body.append(job_id)
        body.append("--%s" % boundary)
        file_name = os.path.basename(remote_file)
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        body.append('Content-Disposition: form-data; name="files"; filename="%s"' % file_name)
        body.append('Content-Type: %s' % mime_type)
        body.append('')
        with open(local_file, 'rb') as f:
            body.append(f.read())
        body.append("--%s--" % boundary)
        body.append('')
        if sys.version_info[0] < 3:
            body_bytes = b"\r\n".join(b if isinstance(b, bytes) else b.encode('utf-8') for b in body)
        else:
            body_bytes = b"\r\n".join(b.encode('utf-8') if isinstance(b, str) else b for b in body)
        return body_bytes

    '''[2024-06-19], add by xunli, jump server 上传文件'''
    def _jump_api_ops_jobs_upload(self, job_id, local_file, remote_file):
        """
        jump server api 文件上传
        :param job_id: [string] 工作ID
        :param local_file: [string] 本地文件路径+文件名
        :param remote_file: [string] 远程文件名
        :return: [dict] 接口请求结果
        """
        api = "/api/v1/ops/jobs/upload/"
        header = self._generate_header(self._token)
        boundary_string = uuid.uuid4().hex
        header["Content-Type"] = "multipart/form-data; boundary=%s" % boundary_string
        body = self._generate_http_multipart_body(boundary_string, job_id, local_file, remote_file)
        header["Content-Length"] = str(len(body))
        response_body = self._send_request_parse_response("POST", api, header, data=body)
        return response_body

    '''[2024-06-19], add by xunli, 获取jump server的token'''
    def _get_jump_server_token(self):
        """
        获取jump server的token
        :return:[string] token值
        """
        resp = self._jump_api_authentication_auth()
        token = resp["body"]["token"]
        return token

    '''[2024-07-04], add by xunli, 获取活跃的用户名'''
    def _get_activity_remote_username_list(self):
        """
        获取活跃的用户名列表
        :return: [list] 用户名列表
        """
        custom_username = list(self._custom_username.keys())
        username_list = self._default_username + custom_username
        return username_list

    '''[2024-07-04], add by xunli, 获取资产ID下配置的用户名'''
    def _get_asset_remote_username_list(self, asset_id):
        """
        获取资产已配置的用户名列表
        :param asset_id: [string] 资产ID
        :return:[list] 用户名列表
        """
        resp_body = self._jump_api_ops_username(asset_id).get("body")
        username_list = [i.get("username") for i in resp_body]
        return username_list

    '''[2024-07-04], add by xunli, 返回可记录的用户名'''
    def _record_username(self, asset_id):
        """
        记录用户名
        :param asset_id:[string] 资产ID
        :return: [string] 用户名
        """
        activity_username = self._get_activity_remote_username_list()
        asset_username = self._get_asset_remote_username_list(asset_id)
        if not asset_username:
            return "error"
        for username in activity_username:
            if username in asset_username:
                return username
        return asset_username[0]

    '''[2024-06-19], add by xunli, jump server 获取用户资产api'''
    def _get_remote_host_statue_code(self, remote_host):
        """
        获取远程服务器状态码
        :param remote_host:[string] 服务器地址
        :return: [tuple] (状态码，资产信息)
        :usage:
            j=JumpServer()
            j.get_remote_host_statue_code("192.168.121.49", "root")
        """
        username_list = self._get_activity_remote_username_list()
        for name in username_list:
            asset_info = self.remote_asset_info.get((remote_host, name))
            if asset_info:
                return {"remote_username": name, "record_asset": asset_info}

    '''[2024-06-18], add by xunli, jump server 获取资产ID'''
    def _get_remote_host_asset_id(self, remote_host):
        """
        获取远程服务器资产ID
        :param remote_host:[string] 服务器地址
        :return: [string] 资产ID，是否支持sudo，True-支持，False-不支持，None-默认值
        """
        asset_info = self._get_remote_host_statue_code(remote_host)
        if asset_info is not None:
            with self._init_lock:
                asset_info = self._get_remote_host_statue_code(remote_host)
                if asset_info is not None:
                    remote_username = asset_info.get("remote_username")
                    record_asset = asset_info.get("record_asset")
                    self.remote_asset_info[(remote_host, remote_username)] = (record_asset[0], record_asset[1],
                                                                              record_asset[2], time.time())
                    if record_asset[0] == ERROR_CODE_SUCCESS:
                        return remote_username, record_asset[1], record_asset[2]
                    else:
                        raise Exception("JumpServer Error, asset in error records, details: %s" % record_asset[1])
        asset_list = self._jump_api_perms_users_self_assets(remote_host).get("body")
        if len(asset_list) > 1:
            self._update_asset_info(remote_host, "root", self._ERROR_CODE_JUMP_ASSET_EXIST_MULTI.error_code,
                                    self._ERROR_CODE_JUMP_ASSET_EXIST_MULTI.error_msg)
            raise Exception("JumpServer Error, %s remote host num error, id is not unique, details: %s" % (
                remote_host, asset_list))
        if len(asset_list) == 1:
            asset_id = asset_list[0].get("id")
            remote_username = self._record_username(asset_id)
            if remote_username == "error":
                self._update_asset_info(remote_host, "root", self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_code,
                                        self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_msg)
                raise Exception("JumpServer Error, %s remote host username not exist, details: no available username" % remote_host)
            else:
                self._update_asset_info(remote_host, remote_username, ERROR_CODE_SUCCESS, asset_id)
                return remote_username, asset_id, None
        else:
            self._update_asset_info(remote_host, "root", self._ERROR_CODE_JUMP_ASSET_IS_NONE.error_code,
                                    self._ERROR_CODE_JUMP_ASSET_IS_NONE.error_msg)
            raise Exception("JumpServer Error, %s, %s" % (remote_host,
                                                    self._ERROR_CODE_JUMP_ASSET_IS_NONE.error_msg))

    """[2024-07-03], add by xunli, 增加操作系统与python版本的校验"""
    def _check_system_python_version(self):
        """
        校验系统与版本
        """
        python_version = platform.python_version()
        system_type = platform.system()
        target_version = '2.7.9'
        if system_type == 'Windows' and python_version < target_version:
            raise Exception("JumpServer Error, please upgrade python to 2.7.9 or above")

    '''[2024-06-20], add by xunli, 解析cmd控制台的打印'''
    def _extract_command_output(self, remote_host, remote_username, raw_output):
        """
        提取命令输出结果
        :param raw_output:[string] 原始信息
        :param remote_host:[string] 服务器地址
        :param remote_username: [string] 服务器登录用户名
        :return: [string] 提取后的输出结果
        """
        ansi_escape = re.compile(r'\x1b\[([0-9;]*m|K)')
        clean_output = ansi_escape.sub('', raw_output)
        clean_output = clean_output.replace('\r\n', '\n')
        if self._need_print_log:
            if "Task ops.tasks.run_ops_job_execution" in clean_output:
                spend_time = clean_output.split("Task ops.tasks.")[-1].split(":")[0]
                logging.info("JumpServer task %s" % spend_time)
        if "non-zero return code" in clean_output:
            none_zero = clean_output.split(">>\n")[-1].split("non-zero return code")[0]
            return none_zero
        if "rc=0 >>" in clean_output:
            valid_output = clean_output.split(">>\n")[-1].split("Task ops.tasks.run_ops_job_execution")[0]
            if valid_output.endswith("\n"):
                valid_output = valid_output.rstrip("\n")
            return valid_output
        if self._ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL.error_flag in clean_output:
            self._update_asset_info(remote_host, remote_username, self._ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL.error_code,
                                    self._ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL.error_msg)
            raise Exception("JumpServer Error, %s, %s, %s, details:%s" % (remote_host, remote_username,
                                                                        self._ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL.error_msg,
                                                                        clean_output))
        else:
            raise Exception("JumpServer Error, cannot detect success flag, details: %s" % clean_output)

    '''[2024-06-21], add by xunli, 更新资产信息'''
    def _update_asset_info(self, remote_host, remote_username, status_code=None, status_msg=None, support_sudo=None):
        """
        更新资产信息
        :param remote_host: [string] 远程服务地址
        :param remote_username: [string] 远程服务用户名
        :param status_code: [int] 状态码
        :param status_msg: [string] 状态信息
        :param support_sudo: [bool] 是否支持sudo，True-支持，False-不支持，None-默认值，sudo只有在去执行时会更新参数
        :return: None
        """
        with self._init_lock:
            if remote_username not in self._default_username:
                self._custom_username[remote_username] = time.time()
            asset_key = (remote_host, remote_username)
            asset_info = self.remote_asset_info.get(asset_key)
            if support_sudo is None:
                if asset_info:
                    support_sudo = asset_info[2]
            else:
                if asset_info:
                    status_code = asset_info[0]
                    status_msg = asset_info[1]
            self.remote_asset_info[asset_key] = (status_code, status_msg, support_sudo, time.time())

    '''[2024-06-19], add by xunli, 等待任务执行完成'''
    @_jump_server_wait_until_execute_pass
    def _wait_until_task_execute_finished(self, task_id, remote_host, remote_username, timeout=20, min_interval=0.05,
                                          max_interval=0.1, error_flag="", switch_stage=5):
        """
        等待任务执行完成
        :param task_id:[string] 任务ID
        :param remote_host: [string] 远程服务器地址
        :param remote_username: [string] 远程服务用户名
        :param timeout: [int] 超时时间
        :param min_interval: [float] 最小查询间隔
        :param max_interval: [float] 最大查询间隔
        :param error_flag: [string] 错误标识，发生某个错误立即返回，不再超时查询
        :param switch_stage: [int] 间隔多少时间后切换为最大查询间隔
        :return: [string] 存在指定错误立即返回错误信息，若不存在等待超时后会抛出相关错误
        """
        resp_body = self._jump_api_ops_job_execution_task_detail(task_id).get("body")
        finish_status = resp_body.get("is_finished")
        summary = resp_body.get('summary', {})
        status = resp_body.get("status")
        excludes = summary.get('excludes', {})
        if sys.version_info[0] < 3:
            username_error = any(self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_flag.decode("utf-8") == value for value in excludes.values())
        else:
            username_error = self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_flag in excludes.values()
        if username_error:
            self._update_asset_info(remote_host, remote_username, self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_code,
                                    self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_msg)
            return "JumpServer Error| %s, %s: %s" % (remote_host, remote_username, self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_msg)
        if status == "failed":
            summary_str = json.dumps(summary)
            if self._ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE.error_flag in summary_str:
                self._update_asset_info(remote_host, remote_username, self._ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE.error_code,
                                        self._ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE.error_msg)
                return "JumpServer Error| %s, %s: %s, details: %s" % (remote_host, remote_username,
                                                                      self._ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE.error_msg, summary_str)
            elif self._ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT.error_flag in summary_str:
                self._update_asset_info(remote_host, remote_username, self._ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT.error_code,
                                        self._ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT.error_msg)
                return "JumpServer Error| %s, %s: %s, details: %s" % (remote_host, remote_username,
                                                                      self._ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT.error_msg,
                                                                      summary_str)
        if not finish_status:
            raise Exception("JumpServer Error, %s, %s: task %s is unfinished" % (remote_host, remote_username, task_id))

    '''[2024-06-20], add by xunli, 去除remote host中的特殊字符'''
    def _check_remote_host(self, remote_host):
        """
        检查远程服务器格式是否含有特殊字符
        如果存在特殊字符，则将其删除
        :param remote_host:[string] 远程服务器地址
        :return:[string] 去除特殊字符的远程服务器地址
        """
        control_chars = [' ', '\t', '\n', '\r']
        cleaned_host = ''.join(c for c in remote_host if c not in control_chars)
        return cleaned_host

    '''[2024-06-20], add by xunli, 从错误信息中获取错误码'''
    def _get_error_code_from_custom(self, error_details):
        """
        根据错误信息，返回指定错误码
        当前统一返回未知错误
        :param error_details: [string] 错误详情
        :return: [int] 错误码
        """
        error_code = ERROR_CODE_UNKNOWN_ERROR
        if self._ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT.error_msg in error_details:
            error_code = self._ERROR_CODE_JUMP_ASSET_PASSWORD_INCORRECT.error_code
        elif self._ERROR_CODE_JUMP_ASSET_EXIST_MULTI.error_msg in error_details:
            error_code = self._ERROR_CODE_JUMP_ASSET_EXIST_MULTI.error_code
        elif self._ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE.error_msg in error_details:
            error_code = self._ERROR_CODE_JUMP_ASSET_PYTHON_INCOMPATIBLE.error_code
        elif self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_msg in error_details:
            error_code = self._ERROR_CODE_JUMP_ASSET_USERNAME_NOT_EXIST.error_code
        elif self._ERROR_CODE_JUMP_ASSET_IS_NONE.error_msg in error_details:
            error_code = self._ERROR_CODE_JUMP_ASSET_IS_NONE.error_code
        elif self._ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL.error_msg in error_details:
            error_code = self._ERROR_CODE_JUMP_ASSET_NOT_SUPPORT_SHELL.error_code
        return error_code

    '''[2024-06-28], add by xunli, 获取sudo的执行指令'''
    def _get_sudo_cmd(self, remote_host, remote_username, cmd, support_sudo):
        """
        获取sudo执行指令
        :param remote_host: [string] 远程服务器地址
        :param remote_username: [string] 远程服务用户名
        :param cmd:[string] 待执行指令
        :param support_sudo: 当前机器是否支持sudo
        :return: 经过sudo格式化的指令
        """
        pre_check_cmd = 'sudo pwd'
        if support_sudo is None:
            code, output = self.run_cmd(remote_host, pre_check_cmd, need_run_with_sudo=False)
            if not output:
                output = self.run_cmd(remote_host, pre_check_cmd, need_run_with_sudo=False)
            if str(output).find('sudo: not found') != -1 or str(output).find('tty to run sudo') != -1:
                cmd = str(cmd).replace('sudo', '')
                support_sudo = False
            else:
                if not str(cmd).strip().startswith('sudo ') and not str(cmd).strip().startswith('script '):
                    cmd = 'sudo ' + str(cmd)
                support_sudo = True
            self._update_asset_info(remote_host, remote_username, support_sudo=support_sudo)
        if support_sudo is True and not str(cmd).strip().startswith("sudo"):
            cmd = 'sudo ' + str(cmd)
        if support_sudo is False:
            cmd = str(cmd).replace('sudo ', ' ').strip()
        return cmd

    '''[2024-06-18], add by xunli, 执行cmd指令'''
    def run_cmd(self, remote_host, cmd, timeout=30, need_run_with_sudo=False):
        """ 执行命令
        使用jump server在远端服务器上执行指令
        :param remote_host:[string] @notblink 远程服务地址 @example:192.168.121.49
        :param cmd:[string]  @notblink cmd指令 @example:ls
        :param timeout:[int] 超时时间 @default=30
        :param need_run_with_sudo: [bool] True-使用sudo，False-不使用sudo执行 @default=False
        :return: [tuple] (错误码, 执行结果)
        :usage:
            在192.168.121.49服务器上执行ls- l的指令
            j=JumpServer()
            j.execute_cmd("192.168.121.49", "root", "ls -l")
        """
        format_host = self._check_remote_host(remote_host)
        output_details = None
        error_code = ERROR_CODE_UNKNOWN_ERROR
        remote_username = None
        try:
            remote_username, asset_id, support_sudo = self._get_remote_host_asset_id(format_host)
            if need_run_with_sudo:
                cmd = self._get_sudo_cmd(remote_host, remote_username, cmd, support_sudo)
            task_id = self._jump_api_ops_jobs_cmd_task(remote_username, cmd, asset_id).get("body").get("task_id")
            self._wait_until_task_execute_finished(task_id, format_host, remote_username, timeout=timeout,
                                                   min_interval=0.5, max_interval=1, switch_stage=10,
                                                   error_flag="JumpServer Error|")
            raw_output = self._jump_api_ops_ansible_job_execution_log(task_id).get("body").get("data")
            output_details = self._extract_command_output(remote_host, remote_username, raw_output)
            error_code = ERROR_CODE_SUCCESS
            if self._need_print_log:
                logging.info("JumpServer execute cmd success======%s" % output_details)
        except Exception as e:
            output_details = traceback.format_exc()
            error_code = self._get_error_code_from_custom(output_details)
            if self._need_print_log:
                logging.info("%s, %s encountered an error executing %s, error code %s, error details: %s" % (
                    format_host, remote_username, cmd, error_code, str(e)))
        return error_code, output_details

    '''[2024-06-18], add by xunli, 上传文件'''
    def upload_file(self, remote_host, local_file, remote_file, timeout=180):
        """上传文件
        使用jump server将本地指定路径下的文件上传到远程服务器上的指定路径下
        :param remote_host: [string] @notblink 远程服务地址 @example:192.168.121.49
        :param local_file: [string] @notblink 本地文件路径+文件名 @example:D:\1.txt
        :param remote_file: [string] @notblink 远端文件路径+文件名 @example:/root/1.txt
        :param timeout: [int] 超时时间 @default=180
        :return: [tuple] (错误码，错误信息-如果是成功该值为None)
        :usage:
            上传本地文件D:\1.txt至远端服务器192.168.121.49中/root/1.txt
            j=JumpServer()
            j.upload_file("192.168.121.49", "root", r"D:\1.txt", "/root/1.txt")
        """
        format_host = self._check_remote_host(remote_host)
        output_details = None
        error_code = ERROR_CODE_UNKNOWN_ERROR
        remote_username = None
        try:
            tmp_file_name = remote_file.split("/")[-1]
            tmp_remote_file = "/tmp/%s" % tmp_file_name
            remote_username, asset_id, support_sudo = self._get_remote_host_asset_id(format_host)
            job_id = self._jump_api_ops_jobs_file_task(remote_username, asset_id, "/tmp").get("body").get("id")
            task_id = self._jump_api_ops_jobs_upload(job_id, local_file, tmp_file_name).get("body").get("task_id")
            self._wait_until_task_execute_finished(task_id, format_host, remote_username, timeout=timeout,
                                                   min_interval=2, max_interval=5, switch_stage=60,
                                                   error_flag="JumpServer Error|")
            if tmp_remote_file != remote_file:
                self.run_cmd(format_host, "mv %s %s" % (tmp_remote_file, remote_file))
            error_code = ERROR_CODE_SUCCESS
        except Exception as e:
            output_details = traceback.format_exc()
            error_code = self._get_error_code_from_custom(output_details)
            if self._need_print_log:
                logging.info("%s, %s upload file error, error code %s, error details: %s" % (
                    format_host, remote_username, error_code, str(e)))
        return error_code, output_details

    '''[2024-06-24], add by xunli, 清除不活跃的数据'''
    def _clean_expired_assets(self):
        """
        清除_clean_interval间隔内未访问过的资产
        :return: None
        """
        while not GLOBAL_VAR.STOP:
            time.sleep(int(self._clean_interval))
            current_time = time.time()
            assets_to_delete = []
            with self._init_lock:
                for del_asset in list(self.remote_asset_info.keys()):
                    asset_info = self.remote_asset_info[del_asset]
                    activity_time = asset_info[-1]
                    if current_time - activity_time > self._clean_interval:
                        assets_to_delete.append(del_asset)
                if assets_to_delete:
                    for asset in assets_to_delete:
                        del self.remote_asset_info[asset]
                        if self._need_print_log:
                            logging.info("%s has been removed due to inactivity" % str(asset))
            with self._socket_lock:
                socket_interval = current_time - self._socket_time
                if self._need_print_log:
                    logging.info(socket_interval)
                if socket_interval > self._clean_interval:
                    if self._socket:
                        self._socket.close()
                        self._socket = None
                        if self._need_print_log:
                            logging.info("http client socket has been reset due to inactivity")

class _RemoteServerManager(object):
    def __init__(self, remote_host=None,remote_port=None,need_print_log=True,retry_times=0,timeout=5,remote_username=None,remote_password=None):
        self.ssh_conn = None
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.remote_username = remote_username or _get_password_by_ini("jumpserver", "username")
        self.remote_password = remote_password or _get_password_by_ini("jumpserver", "password")
        self.need_print_log = need_print_log
        self.exit_status_code = None
        self.is_remote_support_sudo = None
        self.error_msg = None
        self.error_code = None
        self.retry_times = retry_times
        # 如果jump server连接失败，且ssh的paramiko不支持，将使用ssh执行命令
        self._jump_connect_error = False
        # 连接超时
        self.timeout = timeout

    '''@私有方法,不对外访问 获取ssh服务实体'''
    def _get_ssh_service_entity(self,ssh_conn_obj_or_remote_server_login_dict_info=None):
        """
            获取ssh服务实体
            :param ssh_conn_obj_or_remote_server_login_dict_info: [dict or object] SSHConnection实例化的类或远程客户端的信息(跟csv一致)
                  客户端dict中含有四个必填项即可:
                  {'platform': 'local',
                  'server_type': 'script_pc_in_lab_17',
                  'public_ip': '192.168.121.229', 【必填】
                  'local_ip': '192.168.121.229',
                  'ssh_user': 'test',   【必填】
                  'ssh_pwd': '123456',  【必填】
                  'ssh_port': '22',  【必填】
                  'domain': '',
                  'domain_port': '',
                  'dns': '',
                  'mac': '',
                  'pname_list': '',
                  'description': 'xxzhang pc-in lab'}
            :return: 返回ssh服务实体,失败返回None
            """
        _need_auto_close = False
        ssh_conn = None
        '''外面传入ssh登录信息,实例化ssh并自动关闭链路'''
        if isinstance(ssh_conn_obj_or_remote_server_login_dict_info, dict):
            ssh_conn = _SSHConnection(host=ssh_conn_obj_or_remote_server_login_dict_info['public_ip'], port=ssh_conn_obj_or_remote_server_login_dict_info['ssh_port'],
                                     username=ssh_conn_obj_or_remote_server_login_dict_info['ssh_user'],password=ssh_conn_obj_or_remote_server_login_dict_info['ssh_pwd'])
            _need_auto_close = True
        # None = nonetype object'''外面传入ssh_conn,不需要自动化关闭链路'''
        elif isinstance(ssh_conn_obj_or_remote_server_login_dict_info,object) and ssh_conn_obj_or_remote_server_login_dict_info != None:
            ssh_conn = ssh_conn_obj_or_remote_server_login_dict_info
            self.ssh_conn = ssh_conn_obj_or_remote_server_login_dict_info
            _need_auto_close = False
        #'''外面传入None,用self中的连接'''
        elif ssh_conn_obj_or_remote_server_login_dict_info is None:
            ssh_conn = _SSHConnection(host=self.remote_host, port=self.remote_port,username=self.remote_username,password=self.remote_password)
            if not ssh_conn._is_remote_conneted:
                ssh_conn = None
            else:
                self.ssh_conn = ssh_conn
        else:
            if self.ssh_conn != None:
                ssh_conn = self.ssh_conn
        return ssh_conn,_need_auto_close

    '''[2024-06-21], add by xunli, 创建远程连接'''
    def _creat_remote_connection(self):
        """
        创建远程连接
        :return: [object] 远程连接实例
        """
        ssh_conn = None
        if not self._jump_connect_error:
            try:
                jump_server = JumpServer(timeout=self.timeout)
                jump_result = jump_server._get_remote_host_statue_code(self.remote_host)
                if isinstance(jump_result, dict):
                    jump_code, jump_msg, support_sudo, last_time = jump_result.get("record_asset")
                    if jump_code == ERROR_CODE_SUCCESS:
                        ssh_conn = jump_server
                        self.error_code = ERROR_CODE_SUCCESS
                    else:
                        self.error_code = jump_code
                        self.error_msg = jump_msg
            except:
                self._jump_connect_error = True
                if self.need_print_log:
                    logging.info("jump server connect error")
        if not ssh_conn:
            ssh_conn = self._retry_remote_connect()
        return ssh_conn

    '''[2024-06-21], add by xunli, 重试ssh类型的连接'''
    def _retry_ssh_connect(self):
        """
        重试ssh连接
        :return: [object] ssh连接实例
        """
        ssh_conn = None
        retry_times = int(self.retry_times) or 1
        for i in range(retry_times):
            ssh_obj = _SSHConnection(host=self.remote_host, port=self.remote_port, username=self.remote_username,
                                      password=self.remote_password, timeout=self.timeout)
            self.error_code = ssh_obj.error_code
            self.error_msg = ssh_obj.error_msg
            if ssh_obj._is_paramiko_support is False and self._jump_connect_error is True:
                ssh_conn = ssh_obj
                break
            if ssh_obj.error_code == ERROR_CODE_SUCCESS:
                ssh_conn = ssh_obj
                break
            ssh_obj.close()
        return ssh_conn

    '''[2024-06-21], add by xunli, 重试远程连接'''
    def _retry_remote_connect(self):
        """
        重试远程连接
        :return: [object] 远程连接实例
        """
        ssh_conn = self._retry_ssh_connect()
        if ssh_conn is None and self._jump_connect_error is False:
            ssh_conn = JumpServer()
            self.error_code = ERROR_CODE_SUCCESS
        return ssh_conn

    '''[2024-06-21], add by xunli, 获取远程连接实例，并验证连接是否存在'''
    def _get_remote_server_active_entity(self, remote_host=None, remote_port=None,
                                   ssh_conn_obj_or_remote_server_login_dict_info=None):
        """
        获取远程连接实例
        验证实例active
        :param remote_host: [string] 远程服务地址
        :param remote_port: [int] 远程服务端口
        :param ssh_conn_obj_or_remote_server_login_dict_info: [dict or object] SSHConnection实例化的类或远程客户端的信息(跟csv一致)
        :return: [bool] True-使用后关闭连接，False-使用后不处理连接
        """
        _need_auto_close = False
        if self.ssh_conn:
            if isinstance(self.ssh_conn, _SSHConnection):
                if self.ssh_conn._is_paramiko_support is False:
                    return _need_auto_close
                if self.ssh_conn.ssh_conn.get_transport() and self.ssh_conn.ssh_conn.get_transport().active and self.ssh_conn._is_remote_conneted:
                    return _need_auto_close
                self.ssh_conn.close()
                self.ssh_conn = self._retry_remote_connect()
                return _need_auto_close
        if isinstance(ssh_conn_obj_or_remote_server_login_dict_info, JumpServer):
            self.ssh_conn = ssh_conn_obj_or_remote_server_login_dict_info
        elif isinstance(ssh_conn_obj_or_remote_server_login_dict_info, dict):
            self.remote_host = ssh_conn_obj_or_remote_server_login_dict_info['public_ip']
            self.remote_port = ssh_conn_obj_or_remote_server_login_dict_info['ssh_port']
            self.ssh_conn = self._creat_remote_connection()
            _need_auto_close = True
        elif isinstance(ssh_conn_obj_or_remote_server_login_dict_info, _RemoteServerManager):
            self._set_remote_host_info(ssh_conn_obj_or_remote_server_login_dict_info.remote_host,
                                       ssh_conn_obj_or_remote_server_login_dict_info.remote_port)
            self.ssh_conn = self._creat_remote_connection()
        else:
            self._set_remote_host_info(remote_host, remote_port)
            self.ssh_conn = self._creat_remote_connection()
        return _need_auto_close

    '''[2024-06-21], add by xunli, 设置远端服务信息'''
    def _set_remote_host_info(self, remote_host, remote_port):
        """
        设置远端服务信息
        :param remote_host:[string] 远程服务地址
        :param remote_port: [int] 远程服务端口
        :return: None
        """
        if self.remote_host is None:
            self.remote_host = remote_host
            self.remote_port = remote_port

    '''[2024-06-21], add by xunli, 关闭远程连接'''
    def close(self):
        """连接关闭
        关闭与远程服务器的连接
        :return: None
        """
        if isinstance(self.ssh_conn, _SSHConnection):
            self.ssh_conn.close()
        else:
            pass

    '''[2024-06-21], add by xunli, 下载文件'''
    def download_file(self, local_file, remote_file, remote_host=None, remote_port=None):
        """下载文件
        下载远程服务器上指定路径下的文件至本地指定路径
        :param local_file:[string] @notblink 本地文件地址 @example:D:\1.txt
        :param remote_file:[string] @notblink 远程文件地址 @example:/root/1.txt
        :param remote_host:[string] 远程服务地址 @default=None，为None时，实例化类时必传该参数
        :param remote_port: [int] 远程服务端口 @default=None，为None时，实例化类时必传该参数
        :return:[bool] 上传结果，True-成功，False-失败
        :usage:
            下载远端服务器192.168.121.49中的/root/1.txt的文件到D:\1.txt文件下
            r=remote_server("192.168.121.49",22,"root","xxxx")
            r.download_file(r"D:\1.txt", "/root/1.txt")
        """
        result = False
        if isinstance(self.ssh_conn, _SSHConnection):
            if self.ssh_conn.ssh_conn.get_transport().active and self.ssh_conn._is_remote_conneted:
                result = self.ssh_conn.get(remote_file, local_file)
                self.error_code = self.ssh_conn.error_code
                self.error_msg = self.ssh_conn.error_msg
            else:
                self.ssh_conn = self._retry_ssh_connect()
                if self.ssh_conn:
                    result = self.ssh_conn.get(remote_file, local_file)
                    self.error_code = self.ssh_conn.error_code
                    self.error_msg = self.ssh_conn.error_msg
        else:
            if isinstance(self.ssh_conn, JumpServer):
                self.error_msg = "jump server not support download file"
                self.error_code = ERROR_CODE_BASH_CMD
            else:
                self._set_remote_host_info(remote_host, remote_port)
                self.ssh_conn = self._retry_ssh_connect()
                result = self.ssh_conn.get(remote_file, local_file)
                self.error_code = self.ssh_conn.error_code
                self.error_msg = self.ssh_conn.error_msg
        if self.need_print_log:
            logging.info("remote host is %s" % self.remote_host)
        return result

    '''[2024-06-21], add by xunli, 上传文件'''
    def upload_file(self, local_file, remote_file, remote_host=None,remote_port=None, timeout=120):
        """上传文件
        上传本地指定路径下的文件至远程服务器上的指定路径下
        :param local_file:[string] @notblink 本地文件地址
        :param remote_file:[string] @notblink 远程文件地址
        :param remote_host:[string] 远程服务地址 @default=None，为None时，实例化类时必传该参数
        :param remote_port: [int] 远程服务端口 @default=None，为None时，实例化类时必传该参数
        :param timeout: [int]文件上传超时时间 @default=120，为None时，实例化类时必传该参数
        :return: [bool] 上传结果，True-上传成功，False-上传失败
        :usage:
            上传本地文件D:\1.txt至远端服务器192.168.121.49中/root/1.txt
            r=remote_server("192.168.121.49",22,"root","xxxx")
            r.upload_file(r"D:\1.txt", "/root/1.txt")
        """
        result = False
        self._get_remote_server_active_entity(remote_host, remote_port)
        if self.need_print_log:
            logging.info("remote host is %s" % self.remote_host)
        if isinstance(self.ssh_conn, _SSHConnection):
            result = self.ssh_conn.put(local_file, remote_file)
            self.error_code = self.ssh_conn.error_code
            self.error_msg = self.ssh_conn.error_msg
        elif isinstance(self.ssh_conn, JumpServer):
            self.error_code, self.error_msg = self.ssh_conn.upload_file(self.remote_host, local_file, remote_file, timeout)
            if self.error_code == ERROR_CODE_SUCCESS:
                result = True
        return result


    '''@私有方法，不对外访问 针对linux，命令是否要 sudo去执行'''
    def _execute_command_according_identity(self,ssh_conn_obj_or_remote_server_login_dict_info,need_run_with_sudo,cmd,timeout=3):
        result = ssh_conn_obj_or_remote_server_login_dict_info.exec_command(command=cmd,need_run_with_sudo=need_run_with_sudo, timeout=timeout)
        return result

    '''[2022.8.18] chfshan,在指定的远程服务器执行指定命令,多条命令可拼接如 cmd = "pwd && ls"  [2023.1.5]mrxu 修'''
    def run_cmd(self, cmd, timeout=10, ssh_conn_obj_or_remote_server_login_dict_info=None,need_run_with_sudo=False):
        """ 执行指令
        在指定的远程服务器执行指定命令,多条命令可拼接如 cmd = "pwd && ls"
        :param cmd: [string] @notblink 待执行命令行 @example:ls
        :param ssh_conn_obj_or_remote_server_login_dict_info: [dict or object] SSHConnection实例化的类或远程客户端的ssh信息
              dict时要求如下:
              {'public_ip': '192.168.121.229', 'ssh_port': '22'}
              ssh_info时要求为_RemoteServerManager的ssh_conn属性
        :param need_run_with_sudo: [bool] 仅针对linux，命令是否要 sudo去执行 @defalut=False
        :return: [string]命令结果,失败返回None
        :usage:
        方式一：
            remote_server = RemoteServerObject(remote_host='192.168.121.44',remote_port='22')
            print(remote_server.run_cmd('pwd'))   # '/root'
        方式二：
            print(run_cmd('pwd',{'public_ip':'192.168.121.44','ssh_port':22}))   # '/root'
        """
        result = None
        try:
            need_auto_close = self._get_remote_server_active_entity(
                ssh_conn_obj_or_remote_server_login_dict_info=ssh_conn_obj_or_remote_server_login_dict_info)
            if self.need_print_log:
                logging.info("remote host is %s, cmd is %s" % (self.remote_host,cmd))
            if isinstance(self.ssh_conn, _SSHConnection):
                result = self.ssh_conn.exec_command(command=cmd, need_run_with_sudo=need_run_with_sudo, timeout=timeout)
                self.error_code = self.ssh_conn.error_code
                self.error_msg = self.ssh_conn.error_msg
                self.is_remote_support_sudo = self.ssh_conn.is_remote_support_sudo
                self.exit_status_code = self.ssh_conn.exit_status_code
                if need_auto_close:
                    self.ssh_conn.close()
                    self.ssh_conn = None
            elif isinstance(self.ssh_conn, JumpServer):
                self.error_code, details = self.ssh_conn.run_cmd(self.remote_host, cmd, timeout, need_run_with_sudo)
                _, _, self.is_remote_support_sudo, _ = self.ssh_conn._get_remote_host_statue_code(self.remote_host).get("record_asset")
                if self.error_code == ERROR_CODE_SUCCESS:
                    self.exit_status_code = 0
                    result = details
                else:
                    self.error_msg = details
                    if "is unfinished" in self.error_msg:
                        self.error_code = ERROR_CODE_BASH_CMD
                        self.exit_status_code = -1
        except Exception as e:
            logger.warning('failed = %s' % str(e))
        return result

# class CsvOperate(object):
#     def csv_reader(self,path,line_num=''):
#         '''
#         读取csv文件的内容，并返回结果
#         :param path: csv文件的路径 ，如/home/ec2-user/test.csv
#         :param line_num: 要获取的数据的行的index，若为空，则返回整个csv的内容，每行为一个列表的方式，若csv中有title，则title也算一行，数据是从第二行开始，需要传2
#         :return: csv_content，列表格式，且csv中每行为一个列表，如[['time','cpu_load_1','cpu_load_5','cpu_load_15'],['20201125 10:06','1.0','2.9','2.0']]
#         '''
#         csv_content = []
#         # logger.info("path is %s, line_num is %s" % (path,line_num))
#         try:
#             with open(path, 'r+') as myFile:
#                 # logger.info("Now will read csv(%s)"%(path))
#                 lines = csv.reader(myFile)
#                 n = 0
#                 for line in lines:
#                     n = n + 1
#                     if len(line_num) == 0:
#                         csv_content.append(line)
#                     else:
#                         if int(line_num) == n:
#                             csv_content = line
#                         else:
#                             pass
#             return csv_content
#         except Exception as e:
#             logger.error("read csv failed, the reason is %s" %(e))
#     def csv_write(self,path,content=[],write_type='a+'):
#         '''
#         写csv文件,可追加行写入
#         :param path: csv文件的路径 ，如/home/ec2-user/test.csv
#         :param content: 列表格式，一行为一个列表，多行时，列表中包含多个列表，如，[1,2,3], [[1,2,3],[4,5,6]]
#         :return:
#         '''
#         try:
#             with open(path, write_type) as myFile:
#                 myWriter = csv.writer(myFile)  #无对应csv时，会自动创建csv再写入
#                 if len(content) != 0:
#                     if type(content) == list:
#                         if type(content[0]) == list:
#                             myWriter.writerows(content) #一次写入多行
#                             return True
#                         else:
#                             myWriter.writerow(content)  #写入一行
#                             # logger.info("Write 1 line success")
#                             return True
#                     else:
#                         logger.error("The type of input content is %s, it should be list"%(type(content)))
#                         return None
#                 else:
#                     logger.error("write content is empty, please check!")
#                     return None
#         except Exception as e:
#             logger.error("Write csv failed, the reason is %s" % (e))
#             return False
#     def csv_modify_write(self,path,line_num,col_name,modify_content):
#         '''
#         将文件中的所有信息读取出来，修改某一行某一列（列需要用列名，不能用index）的值，再将所有内容重新写入csv
#         :param path: csv文件路径+名称
#         :param line_num: 第line_num行，从1开始计数
#         :param col_name: 为str时，表示第一行中此名字的那一列，为int时，表示第col_name列，从1开始计数
#         :param modify_content:
#         :return:
#         '''
#         # 用pandas
#         # df = pd.read_csv(path, encoding='utf-8')
#         # df.loc[line_num,col_name] = modify_content
#         # # df[line_num].loc[col_num] = modify_content
#         # df.to_csv(path, encoding='utf-8')
#         #用csv库
#         #读csv中的内容
#         try:
#             csv_data = self.csv_reader(path)
#             # 判断col_name是否为str，若为str,则认为是列名
#             if type(col_name) == str:
#                 line1 = csv_data[0]
#                 col_num = line1.index(col_name)
#             elif type(col_name) == int:
#                 col_num = col_name -1
#             else:
#                 logger.error("The type of col_name is not str or int, it is %s"%(type(col_name)))
#             csv_data[line_num-1][col_num] = str(modify_content)
#             self.csv_write(path,csv_data,'wb')
#         except Exception as e:
#             logger.debug("csv_modify_write - failed=%s"%str(e))
#     def csv_combine_linux_cmd(self,csv_list,tar_csv,is_append=0):
#         '''
#         csv合并,linux上执行，用paste命令
#         :param csv_list: 需要合并的csv文件的名称，可带上路径
#         :param tar_csv: 合并后新的文件名
#         :param is_append: 是否追加写入，0：否，1:是
#         :return:
#         '''
#         csv_files = ''
#         for name in csv_list:
#             csv_files = csv_files + name + ' '
#         cmd_part1 = 'paste -d, %s '% csv_files
#         if is_append == 0:
#             cmd_part2 = '> %s'% tar_csv
#         elif is_append == 1:
#             cmd_part2 = '>> %s'% tar_csv
#         else:
#             logger.error("is_append is not 0 or 1,it is %s"%(is_append))
#         logger.error(cmd_part1 + cmd_part2)
#         lo_cli.run_cmd(cmd_part1+cmd_part2)

class _GetServerBasicData(object):
    '''
    性能稳定性测试前采集基础信息
    '''

    def __init__(self, client_params=None):
        '''
        :param client_ip: 执行脚本的本机IP
        :param filepath: basic信息的文件路径
        :param pname: 进程名（有些项需要进程名或进程号），可为str或list格式，多个进程时，str类型中可用,分隔
        '''
        self.monitor_commands()
        self.local_host = client_params.local_host
        self.client_params = client_params
        self.client_params.local_output_path = os.path.join(client_params.local_output_path,
                                                            client_params.local_host + '_monitor_output').replace(' ',
                                                                                                                  '').replace(
            '\\', '/')
        self.client_params.local_output_file = client_params.local_host + '_info.csv'
        if not os.path.exists(self.client_params.local_output_path):
            logger.warning("create dir=%s" % self.client_params.local_output_path)
            os.mkdir(self.client_params.local_output_path)
        self.file = os.path.join(self.client_params.local_output_path, self.client_params.local_output_file).replace(
            '\\', '/')
        self.client_params.pname_list = str(client_params.pname_list).replace('[', '').replace(']', '').replace('"',
                                                                                                                '').replace(
            "'", '').split(',')
        for i in self.client_params.pname_list:
            if not i:
                self.client_params.pname_list.remove(i)
        self.pname = self.client_params.pname_list

        self.csv_header = ['server_ip', 'device_type', 'kernel_version', 'system_version', 'drivers', 'cpu_model',
                           'cpu_cores', 'cpu_basic_freqency(MHz)', 'device_memory_size', 'device_swap_size',
                           'device_disk_size',
                           'device_disk_partition', 'application_version', 'user_process_limit', 'file_connection_num',
                           'proc_pid_connection_num', 'pid_max_allocated_mem',
                           'system_fs_file_max_num', 'default_tcp_recv_window_size', 'max_tcp_recv_window_size',
                           'default_tcp_send_window_size', 'max_tcp_send_window_size',
                           'tcp_recv_window_conf', 'tcp_send_window_conf', 'stack_size', 'network_bandwidth',
                           'network_pps', 'exception_description']
        self.info_list = []

    def monitor_commands(self):
        '''
        监控命令
        :return:
        '''

        self.thread_max = 'cat /proc/sys/kernel/threads-max'
        self.pid_max = 'cat /proc/sys/kernel/pid_max'

        self.product_name_cmd = "dmidecode | grep 'Product Name' |awk 'NR==1'"

        self.mcu_driver_cmd = "nvidia-smi|grep NVIDIA-SMI"
        self.swap_cmd = "free -m |grep Swap"

        self.cpu_model_cmd = "cat /proc/cpuinfo | grep 'model name' |awk 'NR==1' |awk -F ':' '{print$2}'"
        self.cpu_cores_cmd = "lscpu|grep CPU |grep -v ' CPU'|grep -v 'CPU '|awk '{print$2}'"
        self.cpu_basic_freqency_cmd = "lscpu|grep 'CPU MHz'|awk '{print $3}'"
        self.device_memory_size_cmd = "free -h|grep Mem |awk '{print $2}'"
        self.device_swap_size_cmd = "free -h|grep Swap |awk '{print $2}'"
        self.user_process_limit_cmd = 'ulimit -u'
        self.file_connection_num_cmd = 'ulimit -n'
        self.system_fs_file_max_num_cmd = 'cat /proc/sys/fs/file-max'
        self.default_tcp_recv_window_size_cmd = 'cat /proc/sys/net/core/rmem_default'
        self.max_tcp_recv_window_size_cmd = 'cat /proc/sys/net/core/rmem_max'
        self.default_tcp_send_window_size_cmd = 'cat /proc/sys/net/core/wmem_default'
        self.max_tcp_send_window_size_cmd = 'cat /proc/sys/net/core/wmem_max'
        self.max_allocated_mem_cmd = "ps aufx | grep %s|grep -v grep |awk '{print $5,$6}'"
        self.disk_size_cmd = "lsblk|awk '{if($6==\"disk\") print$4}'"
        self.disk_partition_cmd = "lsblk|grep -v MOUNTPOINT|awk '{print $NF}'|grep -v '^$'|awk '{for(i=1;i<=NF;i++){if($i~\"/\") print $i}}'"
        self.java_version_cmd = 'java -version'
        self.python_version_cmd = 'python -V'
        self.nginx_version_cmd = 'nginx -v'
        self.proc_pid_conn_num_cmd = 'cat /proc/%s/limits|grep "Max processes"'
        self.tcp_recv_window_conf_cmd = 'cat /proc/sys/net/ipv4/tcp_rmem'  # 为TCP socket预留用于接收缓冲的内存数量
        self.tcp_send_window_conf_cmd = 'cat /proc/sys/net/ipv4/tcp_wmem'
        self.stack_size_cmd = 'ulimit -s'
        self.os_kernel_version_cmd = 'uname -v'
        self.os_release_version = 'uname -r'
        # self.kernel_version_cmd = "uname -r"
        self.os_node_name_cmd = 'uname -n'
        self.cmd_uname_a = 'uname -a'
        self.cmd_lscpu = 'lscpu'
        self.cmd_get_kamailio_gs_version = "/opt/kamailio/sbin/kamcmd gs.version|grep 'gs.version'"  # sipproxy版本号
        self.cmd_dmidecode_serial_no = "dmidecode -t baseboard |grep Serial"
        self.cmd_get_gdms_version = "(echo 'gdms:'|tr '\\n' ' ' &&  cat /data/http/gdms/webapps/ROOT/version&& echo 'api:'|tr '\\n' ' ' && cat /data/http/gdms-api/webapps/ROOT/version && echo 'notification:'|tr '\\n' ' ' && cat /data/http/gdms-notification/webapps/ROOT/version)|tr ':' '#'"
        self.cmd_ulimit_info = "ulimit -a"  # openfiles 太小会影响socket的建立或者无法创建线程
        self.cmd_sysctl_buffer_info = "sysctl -a  2>/dev/null|grep -E 'rmem|wmem'"  # tcp缓冲区的大小,过小会导致netstat中能看到丢包

        # self.cmd_mysql_variables = 'mysql -h 127.0.0.1 -uadmin -padmin -e "show variables like \'%max%\';"'

    def run(self):

        for elem in self.csv_header:
            try:
                value = ''
                if elem == 'server_type':
                    value = ''
                elif elem == 'server_ip':
                    value = self.local_host + '(' + _network.get_local_ip() + ')'
                elif elem == 'device_type':
                    value = self.get_product_name()
                # elif elem == 'product_name':
                #     value = self.get_product_name()
                elif elem == 'kernel_version':
                    # value = self.get_cmd_result(self.kernel_version_cmd)
                    value = self.get_os_kernel_version()
                elif elem == 'drivers':
                    value = self.get_os_gpu_driver_info()
                elif elem == 'cpu_model':
                    value = self.get_cmd_result(self.cpu_model_cmd)
                elif elem == 'cpu_cores':
                    value = self.get_cmd_result(self.cpu_cores_cmd)
                elif elem == 'cpu_basic_freqency(MHz)':
                    value = self.get_cmd_result(self.cpu_basic_freqency_cmd)
                elif elem == 'device_memory_size':
                    value = self.get_cmd_result(self.device_memory_size_cmd)
                elif elem == 'device_swap_size':
                    value = self.get_cmd_result(self.device_swap_size_cmd)
                # elif elem == 'Total Memory':
                #     value = self.get_cmd_result("free -h|grep Mem |awk '{print $2}'")
                # value = self.get_mem_total()
                elif elem == 'pid_max_allocated_mem':
                    value = ''
                    for p_name in self.pname:
                        value_tmp = self.get_max_allocated_mem(p_name)
                        value = value + p_name + ': ' + value_tmp + '\n'
                elif elem == 'device_disk_size':
                    value = self.get_disk_size()
                elif elem == 'device_disk_partition':
                    value = self.get_cmd_result(self.disk_partition_cmd)
                elif elem == 'application_version':
                    value = value + 'java:' + self.get_java_version() + '\n'
                    value = value + 'python:' + self.get_python_version() + '\n'
                    value = value + 'nginx:' + self.get_nginx_version() + '\n'
                elif elem == 'user_process_limit':
                    value = self.get_cmd_result(self.user_process_limit_cmd)
                    # value = self.get_user_process_limit()
                elif elem == 'file_connection_num':
                    value = self.get_cmd_result(self.file_connection_num_cmd)
                    # value = self.get_file_conn_num()
                elif elem == 'proc_pid_connection_num':
                    value = ''
                    for p_name in self.pname:
                        value_tmp = self.get_proc_pid_conn_num(p_name)
                        value = value + p_name + ': ' + value_tmp + '\n'
                elif elem == 'system_fs_file_max_num':
                    value = self.get_cmd_result(self.system_fs_file_max_num_cmd)
                    # value = self.get_sys_fs_file_max_num()
                elif elem == 'default_tcp_recv_window_size':
                    value = self.get_cmd_result(self.default_tcp_recv_window_size_cmd)
                    # value = self.get_default_tcp_recv_window_size()
                elif elem == 'max_tcp_recv_window_size':
                    value = self.get_cmd_result(self.max_tcp_recv_window_size_cmd)
                    # self.get_max_tcp_recv_window_size()
                elif elem == 'default_tcp_send_window_size':
                    value = self.get_cmd_result(self.default_tcp_send_window_size_cmd)
                    # value = self.get_default_tcp_send_window_size()
                elif elem == 'max_tcp_send_window_size':
                    value = self.get_cmd_result(self.max_tcp_send_window_size_cmd)
                    # value = self.get_max_tcp_send_window_size()
                elif elem == 'tcp_recv_window_conf':
                    value = self.get_tcp_recv_window_conf()
                elif elem == 'tcp_send_window_conf':
                    value = self.get_tcp_send_window_conf()
                elif elem == 'stack_size':
                    value = self.get_cmd_result(self.stack_size_cmd)
                    # value = self.get_stack_size()
                elif elem == 'network_bandwidth':
                    value = self.get_network_bandwidth()
                elif elem == 'network_pps':
                    value = self.get_network_pps()
            except Exception as e:
                logger.error(e)
                continue
            self.info_list.append(value)
        # csv_operate = CsvOperate()
        # csv_operate.csv_write(self.file, self.csv_header, 'w+')
        # csv_operate.csv_write(self.file, self.info_list)

    def basic_func(self, cmd=None, need_run_with_sudo=False):

        return lo_cli.run_cmd(cmd, need_run_with_sudo=need_run_with_sudo)

    def get_os_kernel_version(self):
        # cmd = 'uname -v'
        return self.basic_func(self.os_kernel_version_cmd)

    def get_os_release_version(self):
        return self.basic_func(self.os_release_version)

    def get_product_name(self):
        '''
        获取机型（如，C5.4xlarge），命令：sudo dmidecode | grep 'Product Name' |awk 'NR==1',结果：Product Name: g4dn.4xlarge
        :return:
        '''
        result = self.basic_func([self.product_name_cmd, "sudo " + self.product_name_cmd])
        if 'dmidecode:' or 'denied' in result:
            result = self.basic_func(["sudo " + self.product_name_cmd])
        result = result.strip().split(':')[1].strip()
        return result

    "chfshan,cpu主频、核数、线程数"

    def get_lscpu_info(self):
        return self.basic_func('lscpu', True)

    def get_os_node_name(self):
        return self.basic_func(self.os_node_name_cmd)

    def get_os_gpu_driver_info(self):
        '''

        获取相关驱动信息,运维反馈，目前只有MCU有显卡驱动，其他服务器无任何驱动
        :return:
        '''
        driver_info = ''
        try:
            result = self.get_cmd_result(self.mcu_driver_cmd)
            if not result:
                return False
            if 'nvidia-smi:' not in result:
                nvidia_smi = result.split('NVIDIA-SMI')[1].strip().split(' ')[0]
                driver_version = result.split('Driver Version:')[1].strip().split(' ')[0]
                if 'CUDA Version' in result:
                    cuda_version = result.split('CUDA Version:')[1].strip().split(' ')[0]
                else:
                    cuda_version = ''
                driver_info = 'NVIDIA-SMI: ' + nvidia_smi + '\n' + 'Driver Version: ' + driver_version + '\n' + 'CUDA Version: ' + cuda_version
            else:
                pass

        except Exception as e:
            logger.error("get driver info failed, the reason is %s" % (e))
        finally:
            return driver_info

    def get_mem_swap(self):
        '''
        获取内存有无Swap，命令：free -m |grep 'Swap'|awk '{print $2}'（单位M）
        或swapon -s|grep -v 'Filename'|awk '{print $3}'（单位KB）
        或cat /proc/swaps|grep -v 'Filename'|awk '{print $3}'（单位KB）
        :return:
        '''
        mem_swap = ''
        try:
            result = lo_cli.run_cmd(self.swap_cmd)
            if result is False:
                logger.error("get free -m failed, the reason is %s" % (lo_cli.error_msg))
            else:
                swap_info = re.sub(' +', ' ', result).split(' ')
                if swap_info[1] == '0':
                    mem_swap = 'No Swap'
                else:
                    mem_swap = 'Swap Total: ' + swap_info[1] + '\n' + 'Swap Used: ' + swap_info[
                        2] + '\n' + 'Swap Free: ' + swap_info[3]
        except Exception as e:
            logger.error("get_mem_swap >> get mem swap failed, the reason is %s" % (e))
        finally:
            return mem_swap

    def get_max_allocated_mem(self, process_name):
        '''
        获取应用程序分配的最大内存，命令：ps aufx，看RSS（实际内存空间），VSZ（虚拟内存空间）？？？
        :return:
        '''
        max_allocated_mem = ''
        try:
            cmd = '"' + self.max_allocated_mem_cmd + '"%process_name'
            result = lo_cli.run_cmd(cmd)
            if result is False:
                logger.error("get_max_allocated_mem >>> get %s failed, the reason is %s" % (cmd, lo_cli.error_msg))
            else:
                max_allocated_mem = 'RSS: ' + result.split(' ')[0] + '\n' + 'VSZ: ' + result.split(' ')[1]
        except Exception as e:
            logger.error("get_max_allocated_mem >> get max allocated mem failed, the reason is %s" % (e))
        finally:
            return max_allocated_mem

    def get_disk_size(self):
        '''
        获取磁盘大小，命令：lsblk，得到的各磁盘的大小，再相加(要去除type为disk但没有下挂分区的磁盘，当type有两个)
        :return:
        '''
        disk_size = 0
        try:
            result = self.get_cmd_result(self.disk_size_cmd)
            disk_size_list = result.split('\n')
            for size_tmp in disk_size_list:
                if 'M' in size_tmp:
                    size_tmp = size_tmp[:-1] / 1024
                elif 'G' in size_tmp:
                    size_tmp = size_tmp[:-1]
                else:
                    pass
                disk_size = float(disk_size) + float(size_tmp)
            if '.' in str(disk_size) and str(disk_size)[-1] == '0':
                disk_size = str(disk_size).split('.')[0]
            disk_size = str(disk_size) + 'G'
        except Exception as e:
            logger.error("get_disk_size( >> get disk size failed, the reason is %s" % (e))
        finally:
            return disk_size

    def get_java_version(self):
        '''
        获取服务器上的java版本号，命令：java -version
        :return:
        '''
        java_version = ''
        if 'win32' in sys.platform:
            return java_version
        try:
            cmd1 = self.java_version_cmd + " 2>&1|awk 'NR==1'|awk -F '\"' '{print$2}'"
            cmd2 = '/usr/local/jdk/bin/' + self.java_version_cmd
            cmd3 = cmd2 + " -version 2>&1|awk 'NR==1'|awk -F '\"' '{print$2}'"
            result = lo_cli.run_cmd(self.java_version_cmd)
            if result != False:
                java_version = lo_cli.run_cmd(cmd1)
            else:
                result1 = lo_cli.run_cmd(cmd2)
                if result1 != False:
                    java_version = lo_cli.run_cmd(cmd3)
        except Exception as e:
            logger.warning("failed=%s" % (e))
        finally:
            return java_version

    def get_nginx_version(self):
        nginx_version = ''
        try:
            cmd1 = self.nginx_version_cmd + " 2>&1|awk -F '/' '{print$2}'"
            result = lo_cli.run_cmd(self.nginx_version_cmd)
            if result != False:
                nginx_version = lo_cli.run_cmd(cmd1)
            else:
                pass
        except Exception as e:
            logger.error("get nginx version failed, the reason is %s" % (e))
        finally:
            return nginx_version

    def get_jmeter_version(self):
        '''
        获取jmeter版本号，命令：
        :return:
        '''
        pass

    def get_software_version(self, cmd):
        version = ''
        try:
            result = lo_cli.run_cmd(self.nginx_version_cmd)
        except Exception as e:
            logger.error("failed=%s" % (e))
        finally:
            return version

    def get_proc_pid_conn_num(self, pid):
        '''
        获取某进程的最大连接数，命令：cat /proc/进程pid/limits
        :return:
        '''
        proc_conn_num = ''
        try:
            cmd = '"' + self.proc_pid_conn_num_cmd + '"%pid'
            result = lo_cli.run_cmd(cmd)
            if result is False:
                if 'cat:' in lo_cli.error_msg:
                    # 获取入参pid的进程号
                    # pid_1 = lo_cli.run_cmd('pidof %s' % pid)
                    # pid_1 = get_pid(pid)
                    cmd1 = '"' + self.proc_pid_conn_num_cmd + '"%pid1'
                    result_1 = lo_cli.run_cmd(cmd1)
                    if result_1:
                        process_limit_list = re.sub(' +', ' ', result_1).split(' ')
                        proc_conn_num = 'Soft Limit:' + process_limit_list[2] + '\n' + 'Hard Limit: ' + \
                                        process_limit_list[3]

            else:
                process_limit_list = re.sub(' +', ' ', result).split(' ')
                proc_conn_num = 'Soft Limit:' + process_limit_list[2] + '\n' + 'Hard Limit: ' + \
                                process_limit_list[3]
        except Exception as e:
            logger.error("failed=%s" % (e))
        finally:
            return proc_conn_num

    def get_tcp_recv_window_conf(self):
        '''
        【协议层】tcp接收缓冲区的配置，命令：cat /proc/sys/net/ipv4/tcp_rmem 或sysctl -a|grep tcp_wmem
        说明：为自动调优定义socket使用的内存。第一个值是为socket接收缓冲区分配的最少字节数；第二个值是默认值（该值会被rmem_default覆盖），缓冲区在系统负载不重的情况下可以增长到这个值；第三个值是接收缓冲区空间的最大字节数（该值会被rmem_max覆盖）。
        :return:
        '''
        tcp_recv_window_conf = ''
        try:
            result = lo_cli.run_cmd(self.tcp_recv_window_conf_cmd)
            if result is False:
                logger.error("get_tcp_recv_window_conf >>> get %s failed, the reason is %s" % (
                self.tcp_recv_window_conf_cmd, lo_cli.error_msg))
            else:
                tcp_recv_window_conf_list = re.sub(' +', ' ', result).split('\t')
                tcp_recv_window_conf = 'send_buf_min: ' + tcp_recv_window_conf_list[0] + '\n' + 'send_buf_default: ' + \
                                       tcp_recv_window_conf_list[1] + '\n' + 'send_buf_max: ' + \
                                       tcp_recv_window_conf_list[2]
            # self.info_list.append(tcp_recv_window_conf)
            # return tcp_recv_window_conf
        except Exception as e:
            logger.error("get_tcp_recv_window_conf >> get tcp recv window conf failed, the reason is %s" % (e))
        finally:
            return tcp_recv_window_conf

    def get_tcp_send_window_conf(self):
        '''
        【协议层】tcp发送缓冲区的配置,命令：cat /proc/sys/net/ipv4/tcp_wmem 或sysctl -a|grep tcp_rmem
        说明：为自动调优定义socket使用的内存。第一个值是为socket发送缓冲区分配的最少字节数；第二个值是默认值（该值会被wmem_default覆盖），缓冲区在系统负载不重的情况下可以增长到这个值；第三个值是发送缓冲区空间的最大字节数（该值会被wmem_max覆盖）。
        :return:
        '''
        tcp_send_window_conf = ''
        try:
            result = lo_cli.run_cmd(self.tcp_send_window_conf_cmd)
            if result is False:
                pass
            else:
                tcp_send_window_conf_list = re.sub(' +', ' ', result).split('\t')
                tcp_send_window_conf = 'send_buf_min: ' + tcp_send_window_conf_list[0] + '\n' + 'send_buf_default: ' + \
                                       tcp_send_window_conf_list[1] + '\n' + 'send_buf_max: ' + \
                                       tcp_send_window_conf_list[2]
        except Exception as e:
            logger.error("get tcp send window conf failed, the reason is %s" % (e))
        finally:
            return tcp_send_window_conf

    def get_network_bandwidth(self):
        '''
        当前网络带宽，刚才丢包情况，延迟情况
        :return:
        '''
        pass

    def get_network_pps(self):
        '''
        当前网络pps（出口pps上限，入口pps上限，既有出口又有入口pps上限）
        :return:
        '''
        pass

    def get_dmidecode_serial(self):
        return self.basic_func(self.cmd_dmidecode_serial_no)


# class Controller():
#     '''
#     控制机，负责向待监控服务器生成监控脚本、获取监控结果，并解析为指定格式（共generate_report使用）
#     '''
#
#     def __init__(self):
#         # self.client_record_file_path = client_record_file_path
#         # self.client_record_file_name = client_record_file_name
#         # self.local_record_file_name = local_record_file_name
#         self.python_file_name = PYTHON_FILE_NAME
#         self.remote_output_file_path = None
#         self.remote_output_file_name = None
#         self.remote_clients_with_dict_info = {}
#         self.local_output_path = None
#         self.local_output_file = None
#         self._remote_clients_param = {}
#         self.thread_id = None
#         self.need_print_datas = {
#             'headers': ['no', 'ip', 'service','monitor', 'status', 'user', 'ssh_pwd', 'port','pname',  'error'],
#             'datas': [],
#             'warn_datas': []}
#         self.__init_controller__()
#
#     def __init_controller__(self):
#         if not self.local_output_file:
#             self.local_output_file = PYTHON_FILE_NAME
#         if not self.local_output_path:
#             self.local_output_path = PYTHON_FILE_PATH
#         if not self.remote_output_file_path:
#             self.remote_output_file_path = REMOTE_WORK_PATH
#         if not self.remote_output_file_name:
#             self.remote_output_file_name = PYTHON_FILE_NAME
#
#     def start_python(self, ssh_connect_handle, remote_client_params=None):
#         '''
#         运行待监控服务器的脚本
#         :param client_list: 待执行脚本的服务器列表
#         :param script_path: 待监控服务器的脚本路径，若传入string类型，则client_list中所有服务器均使用此路径，若传入列表，且列表中多个值时，则与client_list中一一对应，若为1个值，则均使用此路径
#         :param script_name: 待监控服务器的脚本名称，若传入string类型，是client_list中所有服务器均执行此脚本，若传入列表，且列表中多个值时，则与client_list中一一对应，若为1个值，则均使用此脚本名
#         :param arg_dict: 运行脚本需要传入的参数，格式要求：{'11.0.208.81':[arg1,arg2],'11.0.32.114':[arg1,arg2]}，或所有服务器运行的脚本使用同一组参数，{'all':[arg1,arg2]}
#         :return:
#         '''
#         try:
#             # if remote_client_params.remote_output_file_path[-1] != '/':
#             #     remote_client_params.remote_output_file_path = remote_client_params.remote_output_file_path + '/'
#             # 将脚本路径和名称拼成一个字符串
#             python_file = os.path.join(remote_client_params.remote_output_file_path,remote_client_params.remote_output_file_name).replace('\\','/')
#
#             self.kill_old_python_process(ssh_connect_handle)
#             remote_client_params.pname_list = str(remote_client_params.pname_list).replace('[','').replace(']','').replace('"','').replace("'",'')
#             '''避免:  --needmonitorpname --servertype 会导致读进去的pname是 --servertype'''
#             if not remote_client_params.pname_list:
#                 remote_client_params.pname_list = '""' #
#             run_params = ' --runmode ' + str(remote_client_params.run_mode)+\
#                          ' --runtotaltime ' + str(remote_client_params.test_duration)+\
#                          ' --needmonitorpname ' + str(remote_client_params.pname_list).strip() +\
#                          ' --servertype ' + str(remote_client_params.server_type).strip() +\
#                          ' --logconsolelevel '+ str(GLOBAL_VAR.LOG_CONSOLE_LEVEL) +\
#                          ' --logfilelevel ' + str(GLOBAL_VAR.LOG_FILE_LEVEL)
#             python_path = get_python_execute_path(get_type='remote',ssh_connect_handle=ssh_connect_handle,client_dict_info=remote_client_params.remote_client_dict_info)
#             if not python_path:
#                 raise Exception('get python execute path failed')
#             # nice -20
#             command = 'sudo nohup ' + str(python_path).strip() + ' ' + python_file + ' ' + run_params + ' 2>/dev/null &'   #2>&1 在im上会导致日志太大,monitor和nohup.out有双份
#             logger.warning("Controller start python in [%s] exec cmd=[ %s ]" % (remote_client_params.thread_id,command))
#             remote_client_params.remote_python_start_cmd = command
#             result = ssh_connect_handle.exec_command(command,need_run_with_sudo=True)
#             logger.warning("[%s] exec cmd=[ %s ],result=###[ %s ]###\n" % (remote_client_params.thread_id, command,str(result)))
#         except Exception:
#             logger.error("[%s] run script failed, error=%s" % ( remote_client_params.thread_id,str(traceback.format_exc())))
#
#         return remote_client_params
#
#     def run_per_remote_client(self,remote_client_params,run_type='all'):
#         try:
#             remote_server = SSHConnection(remote_client_params.remote_client_dict_info['public_ip'], remote_client_params.remote_client_dict_info['ssh_port'],remote_client_params.remote_client_dict_info['ssh_user'], remote_client_params.remote_client_dict_info['ssh_pwd']) if not remote_client_params.remote_client_dict_info.get('remote_server') else remote_client_params.remote_client_dict_info.get('remote_server')
#             remote_client_params.remote_client_dict_info['remote_server'] = remote_server
#             if not remote_server:
#                 raise Exception('ssh connection failed')
#             if not str(remote_client_params.remote_output_file_path)[0].strip().replace('\\','/') == '/':
#                 remote_client_params.remote_output_file_path = os.path.join(remote_server.exec_command('pwd').strip().replace('\n',''),remote_client_params.remote_output_file_path).replace('\\','/')
#             if run_type == 'all':
#                 self.put_file_to_client(remote_server, remote_client_params)
#                 remote_client_params = self.start_python(remote_server,remote_client_params)
#                 self.check_and_add_crontab(remote_server,remote_client_params)
#             elif run_type == 'start':
#                 remote_client_params = self.start_python(remote_server, remote_client_params)
#             time.sleep(2)
#                 # if _need_close_ssh:
#                 #     remote_server.close()
#             #logger.error('[END][%s]\nparams=%s' % (str(remote_client_params.thread_id), str(remote_client_params.remote_client_dict_info)))
#         except Exception as e:
#             logger.error('error =%s' % (e))
#
#     def start_remote_clients(self,remote_clients_with_dict_info=None,remote_run_mode='p_client',run_type='all',thread_id='CHECK'):
#         """
#
#         :param remote_clients_with_dict_info:
#         :param run_type: [string] all/start/stop/check, all:上传脚本+启动
#         :return:
#         """
#         # 将此脚本上传到各client服务器指定路径下
#         task_list = []
#         if not remote_clients_with_dict_info:
#             remote_clients_with_dict_info = self.remote_clients_with_dict_info
#
#         remote_clients_with_dict_info = delete_duplicate_data_in_server_info(remote_clients_with_dict_info)
#         __print_log = "Controller[%s] will boot [%s] agents########\n"%(thread_id,len(remote_clients_with_dict_info))
#
#         for key,client_dict_info in remote_clients_with_dict_info.items():
#             __client_ip = ''
#             __client_ssh_user = ''
#             try:
#                 if not client_dict_info.get('no'):
#                     client_dict_info['no'] = 00
#                 client_dict_info['public_ip'] = str(client_dict_info['public_ip']).replace("'", '').replace('"','').strip()
#                 client_dict_info['ssh_user'] = str(client_dict_info['ssh_user']).replace("'", '').replace('"','').strip()
#                 client_dict_info['ssh_port'] = str(client_dict_info['ssh_port']).replace("'", '').replace('"','').strip()
#                 __client_ip = str(client_dict_info['public_ip'])
#                 __client_ssh_user = str(client_dict_info['ssh_user'])
#                 if not client_dict_info['ssh_user'] or len(client_dict_info) <= 1 or not __client_ip:
#                     raise Exception('no ssh_user or public_ip info')
#                 __print_log = __print_log + "[%s][STARTING] " % str(client_dict_info['no']) + "%s@%s -p %s -P %s -pname %s"%(__client_ssh_user,__client_ip, str(client_dict_info['ssh_pwd']),str(client_dict_info['ssh_port']),str(client_dict_info['pname_list'])) +'\n'
#                 remote_client_params = Params()
#                 remote_client_params.thread_id = thread_id + " Thread" + str(client_dict_info['no']) + "_%s" % str(client_dict_info['public_ip'])
#                 remote_client_params.remote_output_file_path = self.remote_output_file_path
#                 remote_client_params.run_mode = remote_run_mode
#                 remote_client_params.remote_client_dict_info = client_dict_info
#                 remote_client_params.remote_output_file_name = self.remote_output_file_name
#                 try:
#                     remote_client_params.pname_list = str(client_dict_info['pname_list']).replace(' ', '')
#                 except:
#                     remote_client_params.pname_list = []
#
#                 if not remote_client_params.pname_list:
#                     remote_client_params.pname_list = []
#
#                 remote_client_params.remote_host = client_dict_info['public_ip']
#                 try:
#                     remote_client_params.server_type = client_dict_info['product'].strip()+'_'+client_dict_info['service'].strip()
#                 except:
#                     remote_client_params.server_type = ''
#                 #logger.warning('[START][%s]\nparams=%s' % (remote_client_params.thread_id,str(client_dict_info)))
#                 # 开始执行Controller
#                 t = threading.Thread(target=self.run_per_remote_client, args=(remote_client_params,run_type,),name='T_'+str(remote_client_params.remote_host))
#                 t.start()
#                 task_list.append(t)
#             except Exception as e:
#                 __print_log = __print_log  + "[%s][SKIP] %s@%s, id=%s\n" % (str(client_dict_info['no']),__client_ssh_user, __client_ip, str(traceback.format_exc()))
#                 logger.warning('Controller.run - SUB_THREAD.CONTROLLER[%s] failed=[%s],params:%s '% (str(client_dict_info['public_ip']),str(traceback.format_exc()),str(client_dict_info)))
#         logger.error(__print_log)
#         for task in task_list:
#             task.join()
#
#     def check_and_start_every_client(self,client_dict_info,_agent_info,need_delete_remote_path=False,remote_client_run_mode='p_client',_check_loop=0):
#         _data_id = 0
#         try:
#             _data_id = client_dict_info['no']
#         except:pass
#         # _client_key_name = (client_dict_info.get('public_ip'),client_dict_info.get('ssh_port'))
#         _client_param = self._remote_clients_param.get((client_dict_info.get('public_ip'),client_dict_info.get('ssh_port')))
#         if not _client_param:
#             self._remote_clients_param[(client_dict_info.get('public_ip'),client_dict_info.get('ssh_port'))] = Params()
#
#         _client_param.remote_client_dict_info = client_dict_info
#
#         _data_node = [str(_data_id)[0:3],
#                       client_dict_info.get('public_ip'),
#                       str(str(client_dict_info.get('product')) + '_' + str(client_dict_info.get('service')))[0:15],
#                       'node_exporter',
#                       'RUNNING',
#                       client_dict_info.get('ssh_user'),
#                       client_dict_info.get('ssh_pwd'),client_dict_info.get('ssh_port'),
#                       str(client_dict_info.get('pname_list'))[0:35],]
#         _datas = [copy.deepcopy(_data_node),_data_node]
#         _datas[0][3] = 'python'#PYTHON_FILE_NAME
#         _warn_datas=[]
#
#         try:
#             _client_ip = str(client_dict_info.get('public_ip'))
#             _client_ssh_user = str(client_dict_info.get('ssh_user'))
#             _ssh_pwd = str(client_dict_info.get('ssh_pwd'))
#             _client_type = str(client_dict_info.get('product'))+'_'+str(client_dict_info.get('service'))
#             _ssh_port = str(client_dict_info.get('ssh_port'))
#             _pname = str(client_dict_info.get('pname_list'))
#
#             if not client_dict_info['ssh_user'] or len(client_dict_info) <= 1 or not client_dict_info['public_ip']:
#                 raise Exception('no ssh_user|public_ip info')
#             logger.error('[%s][%s/%s]START\nparams=%s' % (str(client_dict_info['public_ip']), str(_data_id), str(len(_agent_info)),str(client_dict_info)))
#
#
#             remote_server = SSHConnection(client_dict_info['public_ip'], client_dict_info['ssh_port'],client_dict_info['ssh_user'], client_dict_info['ssh_pwd'],timeout=5)
#             if remote_server.error_msg:
#                 raise Exception('connect[%s] %s' % (_client_ip,str(remote_server.error_msg)))
#             client_dict_info.update({'remote_server': remote_server})
#             _client_param.remote_server_object = remote_server
#
#             _local_file = os.path.join(PYTHON_FILE_PATH, PYTHON_FILE_NAME).replace('\\', '/')
#             _remote_py_file_path = os.path.join(str(remote_server.exec_command('pwd').strip().replace('\n', '')),
#                                                 REMOTE_WORK_PATH).replace('\\', '/')
#
#             if need_delete_remote_path:
#                 run_cmd_in_remote(remote_server, client_dict_info,"kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}')" %os.path.split(os.path.realpath(__file__))[1])
#                 run_cmd_in_remote(remote_server, client_dict_info,"kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep monitor_system_new.py|grep -v grep|awk '{print $2}')")
#                 run_cmd_in_remote(remote_server, client_dict_info,"kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}')" % 'node_exporter',is_remote_support_sudo=remote_server.is_remote_support_sudo)
#                 run_cmd_in_remote(remote_server,client_dict_info,"rm -rf %s" % (_remote_py_file_path+"*").replace('\\','/').replace('/*','*'),is_remote_support_sudo=remote_server.is_remote_support_sudo)
#
#                 return False
#
#             '''check并启动python脚本'''
#             _start_python_result = None
#             _remote_file_md5 = remote_server.exec_command('md5sum %s' % os.path.join(_remote_py_file_path,PYTHON_FILE_NAME).replace('\\','/'),need_run_with_sudo=True)
#             if _check_loop == 1 or remote_server.error_code != 0 or str(_remote_file_md5).find(str(_string_object.md5sum(_local_file))) == -1:  #对方和本地的文件不一致
#                 self.run_per_remote_client(remote_client_params=_client_param,run_type='all')
#                 # self.start_remote_clients({(_client_ip,_ssh_port):client_dict_info}, remote_run_mode=remote_client_run_mode,run_type='all', thread_id='ALL')  # 启动一台
#                 logger.info('waiting {0}s for clients[{1}:{2}] start......'.format('15',_client_ip,_ssh_port))
#                 time.sleep(15)
#                 logger.info('waiting {0}s for clients[{1}:{2}] start......,end'.format('15', _client_ip, _ssh_port))
#             for i in range(0,3):
#                 result = run_cmd_in_remote(remote_server, client_dict_info,
#                                            "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}'" % PYTHON_FILE_NAME,
#                                            is_remote_support_sudo=remote_server.is_remote_support_sudo)
#                 result = str(result).replace('\n', ' ')
#                 if result:
#                     break
#                 else:
#                     self.run_per_remote_client(remote_client_params=_client_param, run_type='start')
#
#                     # self.start_remote_clients({(_client_ip,_ssh_port):client_dict_info}, remote_run_mode=remote_client_run_mode,
#                     #                           run_type='start', thread_id='START')  # 启动一台
#                 if i==2 and not result:
#                     _datas[0][4] = 'STOP'
#                     _datas[0].append(str(result)[0:55])
#                     _warn_datas.append(_datas[0])
#             '''check并启动node_exporter'''
#             result = run_cmd_in_remote(remote_server, client_dict_info,"ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}'" % 'node_exporter',is_remote_support_sudo=remote_server.is_remote_support_sudo)
#             result = str(result).replace('\n', ' ')
#             if not result:
#                 result = remote_server.exec_command('uname -a')
#                 remote_path = os.path.join(_remote_py_file_path, 'node_exporter').replace('\\', '/')
#                 remote_file = os.path.join(remote_path, 'node_exporter-1.2.2.linux-amd64.tar.gz').replace('\\', '/')
#                 remote_untar_path = os.path.join(remote_path, 'node_exporter-1.2.2.linux-amd64').replace('\\', '/')
#                 local_file = os.path.join(os.path.dirname(PYTHON_FILE_PATH), 'tools', 'node_exporter','node_exporter-1.2.2.linux-amd64.tar.gz').replace('\\', '/')
#                 if result.find('aarch') != -1:
#                     remote_file = os.path.join(remote_path, 'node_exporter-1.2.2.linux-arm64.tar.gz').replace('\\','/')
#                     local_file = os.path.join(os.path.dirname(PYTHON_FILE_PATH), 'tools', 'node_exporter','node_exporter-1.2.2.linux-arm64.tar.gz').replace('\\', '/')
#                     remote_untar_path = os.path.join(remote_path, 'node_exporter-1.2.2.linux-arm64').replace('\\','/')
#                 remote_server.exec_command('mkdir -p %s' % remote_path)
#                 result = remote_server.exec_command('ls %s' % (remote_untar_path))
#                 if remote_server.error_msg:
#                     remote_server.put(local_file, remote_file)
#                     remote_server.exec_command('tar zxvf %s -C %s' % (remote_file, remote_path),timeout=10)
#                 remote_server.exec_command('nohup %s --collector.systemd --collector.processes 2>/dev/null &' % str(os.path.join(remote_untar_path, 'node_exporter').replace('\\', '/')),need_run_with_sudo=True)
#
#                 if remote_server.error_msg:
#                     _datas[1][4] = 'STOP'
#
#             remote_server.close()
#         except Exception as e:
#             logger.critical('check failed=%s' % str(traceback.format_exc()))
#             _datas[0][3] = 'all'
#             _datas[0][4] = 'DEAD'
#             _datas[0].append(str(e)[0:55])
#             _warn_datas.append(copy.deepcopy(_datas[0]))
#             _datas[0][3] = 'python'
#         print_table(datas=_datas,headers=self.need_print_datas['headers'],title=client_dict_info.get('public_ip'),description=str(client_dict_info))
#         self.need_print_datas['datas'] = self.need_print_datas['datas']+_datas
#         self.need_print_datas['warn_datas'] = self.need_print_datas['warn_datas']+_warn_datas
#
#
#     def do_run(self,need_delete_remote_path=None,test_platform=None,remote_client_run_mode='p_client',need_use_local_csv_servers=None,client_info=None,server_info=None):
#
#         check_interval = 60*10
#         _check_loop = 0
#         self._remote_client_params = {}
#         while True:
#             self.need_print_datas['datas'] = []
#             self.need_print_datas['warn_datas'] = []
#             _check_loop = _check_loop + 1
#             _agent_info = get_server_info_from_csv(test_platform=test_platform,csv_file_list=CSV_FILES)
#             if not need_use_local_csv_servers:
#                 _agent_info = {}
#                 _agent_info.update(client_info)
#                 _agent_info.update(server_info)
#
#             logger.warning('servers_infos=%s' % str(_agent_info))
#             _agent_info = delete_duplicate_data_in_server_info(_agent_info)
#             time.sleep(1)
#             _local_thread = []
#
#             for key, client_dict_info in _agent_info.items():
#                 T = threading.Thread(target=self.check_and_start_every_client,
#                                      args=(client_dict_info, _agent_info,need_delete_remote_path,remote_client_run_mode,_check_loop),
#                                      name='check_' + str(client_dict_info["public_ip"]))
#                 T.start()
#                 _local_thread.append(T)
#                 time.sleep(0.3)
#             for i in _local_thread:
#                 i.join()
#
#             print_table(datas=self.need_print_datas['datas'],headers=self.need_print_datas['headers'],title='[LOOP:%s]%s CHECK_RESULT_END'%(str(_check_loop),str(len(_agent_info))),tablefmt='grid')
#             print_table(datas=self.need_print_datas['warn_datas'],headers=self.need_print_datas['headers'],title='[FAILED]%s/%s'%(str(len(self.need_print_datas['warn_datas'])),str(len(_agent_info)*2)),tablefmt='grid')
#
#             logger.warning('do_run -- CHECK,time.sleep=%ss,for [check_interval=%ss]' % (str(check_interval), str(check_interval)))
#             time.sleep(int(check_interval))
#
#     def kill_old_python_process(self, ssh_connect_handle):
#         cmd = "kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}')" % self.python_file_name
#         # cmd = "kill $(ps -ef|grep %s|grep -v grep|awk '{print $2}')" % self.python_file_name
#         cmd_result = ssh_connect_handle.exec_command(cmd,need_run_with_sudo=True)
#     def put_file_to_client(self, ssh_connect_handle,remote_client_params):
#         '''
#         从本地传文件至remote服务器
#         :param client_list: 接收file的客户端服务器列表
#         :param local_file_path: 本地文件的路径（如/home/ec2-user/server_watchdog.py）
#         :param remote_file_path: 接收file的客户端该文件的存放路径,支持两种方式，一种是传入传路径（如/root/ec2-user/,不需要带文件名），
#                                   一种是传入非全路径，此种方式下，会获取当前登录用户的默认路径，再加上传入的路径（若登录进去为/home/ec2-user，传入的路径为test/script，则整个路径为/home/ec2-user/test/script）
#                                   说明：若remote_file_path首个字符为/时，则认为是全路径，若首个字符非/，则认为非全路径
#                                   若remote_file_path为str，或list且仅有一个元素，则所有client均使用此路径，若为lis且为多个元素，则与client_list中的client一一对应
#         :return:
#         '''
#         try:
#             create_cmd = 'mkdir -p %s' % remote_client_params.remote_output_file_path
#             create_result = ssh_connect_handle.exec_command(create_cmd)
#             self.kill_old_python_process(ssh_connect_handle)
#
#             remote_file = os.path.join(remote_client_params.remote_output_file_path,remote_client_params.remote_output_file_name).replace('\\','/')
#             local_file = os.path.join(self.local_output_path,self.local_output_file).replace('\\','/')
#             result = ssh_connect_handle.put(local_file,remote_file)
#             # 关闭ssh连接
#             # logger.critical('%s  %s'%(str(self.controller_param.thread_id),str(self.controller_param.remote_client_dict_info)))
#         except Exception as e:
#             logger.error("[%s]run script failed=%s" % (remote_client_params.thread_id,str(e)))
#
#     def check_and_add_crontab(self,remote_server,remote_client_params):
#         # remote_client_params = Params()
#         if not remote_client_params.remote_python_start_cmd or not remote_client_params.remote_output_file_name:
#             return False
#         cmd = "sudo sed -i '/{pyname}/d' crontab.bak && echo '@reboot {cmd}' >> crontab.bak".format(pyname=remote_client_params.remote_output_file_name,cmd=str(remote_client_params.remote_python_start_cmd))
#         # cmd1 = "sudo sed -i '/monitor_system_new/d' crontab.bak"
#         # cmd3 = "sudo sed -i '/@reboot None/d' crontab.bak"
#         cmd2 = 'sudo crontab -l > crontab.bak ; grep {pyname} crontab.bak'.format(pyname=remote_client_params.remote_output_file_name)
#         '''获取目前crontab中python的命令行'''
#         result = remote_server.exec_command(cmd2,need_run_with_sudo=True)
#         '''比较和即将写入的是否一样'''
#         #if str(result).replace(' ','').replace('\n','').replace('sudo','') != '@reboot {cmd}'.format(cmd=remote_client_params.remote_python_start_cmd).replace(' ','').replace('sudo',''):
#         if remote_client_params.remote_python_start_cmd and str(result).replace(' ','').replace('\n','').replace('sudo','') != '@reboot {cmd}'.format(cmd=remote_client_params.remote_python_start_cmd).replace(' ','').replace('sudo',''):
#             logger.info(('crontab changed','src=',result,'dst=','@reboot {cmd}'.format(cmd=remote_client_params.remote_python_start_cmd)))
#             """bak写入最新的python命令行，并替换crontab"""
#             remote_server.exec_command(cmd,need_run_with_sudo=True)
#             # remote_server.exec_sudo_cmd(cmd1,is_remote_support_sudo=remote_server.is_remote_support_sudo)
#             # remote_server.exec_sudo_cmd(cmd3,is_remote_support_sudo=remote_server.is_remote_support_sudo)
#
#             remote_server.exec_command("sudo crontab crontab.bak",need_run_with_sudo=True)

class _Controller_back():
    '''
    控制机，负责向待监控服务器生成监控脚本、获取监控结果，并解析为指定格式（共generate_report使用）
    '''

    def __init__(self):
        # self.client_record_file_path = client_record_file_path
        # self.client_record_file_name = client_record_file_name
        # self.local_record_file_name = local_record_file_name
        self.python_file_name = PYTHON_FILE_NAME
        self.remote_output_file_path = None
        self.remote_output_file_name = None
        self.remote_clients_with_dict_info = {}
        self.local_output_path = None
        self.local_output_file = None
        self._remote_clients_param = {}
        self.thread_id = None
        self.need_print_datas = {
            'headers': ['no', 'ip', 'service', 'monitor', 'status', 'user', 'ssh_pwd', 'port', 'pname', 'error'],
            'datas': [],
            'warn_datas': []}
        self.__init_controller__()

    def __init_controller__(self):
        if not self.local_output_file:
            self.local_output_file = PYTHON_FILE_NAME
        if not self.local_output_path:
            self.local_output_path = PYTHON_FILE_PATH
        if not self.remote_output_file_path:
            self.remote_output_file_path = REMOTE_WORK_PATH
        if not self.remote_output_file_name:
            self.remote_output_file_name = PYTHON_FILE_NAME

    def start_python(self, remote_server_client, remote_client_params=None):
        '''
        运行待监控服务器的脚本
        :param client_list: 待执行脚本的服务器列表
        :param script_path: 待监控服务器的脚本路径，若传入string类型，则client_list中所有服务器均使用此路径，若传入列表，且列表中多个值时，则与client_list中一一对应，若为1个值，则均使用此路径
        :param script_name: 待监控服务器的脚本名称，若传入string类型，是client_list中所有服务器均执行此脚本，若传入列表，且列表中多个值时，则与client_list中一一对应，若为1个值，则均使用此脚本名
        :param arg_dict: 运行脚本需要传入的参数，格式要求：{'11.0.208.81':[arg1,arg2],'11.0.32.114':[arg1,arg2]}，或所有服务器运行的脚本使用同一组参数，{'all':[arg1,arg2]}
        :return:
        '''
        start_result = True
        _run_python_cmd_result = ''
        try:
            # 将脚本路径和名称拼成一个字符串
            python_file = os.path.join(remote_client_params.remote_output_file_path,
                                       remote_client_params.remote_output_file_name).replace('\\', '/')

            self.kill_old_python_process(remote_server_client)
            remote_client_params.pname_list = str(remote_client_params.pname_list).replace('[', '').replace(']',
                                                                                                            '').replace(
                '"', '').replace("'", '')

            run_params = ' --runmode ' + str(remote_client_params.run_mode) + \
                         ' --logconsolelevel ' + str(GLOBAL_VAR.LOG_CONSOLE_LEVEL) + \
                         ' --logfilelevel ' + str(GLOBAL_VAR.LOG_FILE_LEVEL) + \
                         ' --monitorinterval ' + str(GLOBAL_VAR.MONITOR_INTERVAL)
            if str(remote_client_params.server_type).strip():
                run_params = run_params + ' --servertype ' + str(remote_client_params.server_type).strip()
            if str(remote_client_params.pname_list).strip():
                run_params = run_params + ' --needmonitorpname ' + str(remote_client_params.pname_list).strip()
            if str(remote_client_params.test_duration):
                run_params = run_params + ' --runtotaltime ' + str(remote_client_params.test_duration)

            python_path = _get_python_execute_path(get_type='remote', remote_server_client=remote_server_client, client_dict_info=remote_client_params.remote_client_dict_info)
            if not python_path:
                raise Exception('get python execute path failed' + str(traceback.format_exc()))
            # nice -20
            # command = 'sudo nohup ' + str(python_path).strip() + ' ' + python_file + ' ' + run_params + ' 2>/dev/null &'   #2>&1 在im上会导致日志太大,monitor和nohup.out有双份

            command = 'nohup ' + str(
                python_path).strip() + ' ' + python_file + ' ' + run_params + ' 2>/dev/null &'  # 2>&1 在im上会导致日志太大,monitor和nohup.out有双份

            logger.warning("Controller start python in [%s] exec cmd=[ %s ]" % (
            str(remote_client_params.remote_client_dict_info.get('public_ip')), command))
            remote_client_params.remote_python_start_cmd = command
            _run_python_cmd_result = remote_server_client.run_cmd(command, need_run_with_sudo=False)
            if remote_server_client.exit_status_code != 0:
                start_result = False
        except Exception:
            start_result = False
        logger.warning("[%s] START_PYTHON [%s][ %s ],result=#[\n%s\n]#,err=%s" % (
        remote_client_params.remote_client_dict_info.get('public_ip'), str(start_result),
        str(remote_client_params.remote_python_start_cmd), str(_run_python_cmd_result), str(traceback.format_exc())))

        return start_result

    # def run_per_remote_client(self,remote_client_params,run_type='all'):
    #     try:
    #         # remote_server = SSHConnection(remote_client_params.remote_client_dict_info['public_ip'], remote_client_params.remote_client_dict_info['ssh_port'],remote_client_params.remote_client_dict_info['ssh_user'], remote_client_params.remote_client_dict_info['ssh_pwd']) if not remote_client_params.remote_client_dict_info.get('remote_server') else remote_client_params.remote_client_dict_info.get('remote_server')
    #         # remote_client_params.remote_client_dict_info['remote_server'] = remote_server
    #         _need_close_ssh = False
    #         if remote_client_params.remote_client_dict_info.get('remote_server'):
    #             remote_server = remote_client_params.remote_client_dict_info['remote_server']
    #         else:
    #             remote_server = SSHConnection(remote_client_params.remote_client_dict_info['public_ip'], remote_client_params.remote_client_dict_info['ssh_port'],
    #                                      remote_client_params.remote_client_dict_info['ssh_user'], remote_client_params.remote_client_dict_info['ssh_pwd'])
    #             _need_close_ssh = True
    #         if not remote_server:
    #             raise Exception('ssh connection failed')
    #         if not str(remote_client_params.remote_output_file_path)[0].strip().replace('\\','/') == '/':
    #             remote_client_params.remote_output_file_path = os.path.join(remote_server.exec_command('pwd').strip().replace('\n',''),remote_client_params.remote_output_file_path).replace('\\','/')
    #         if run_type == 'all':
    #             self.put_file_to_client(remote_server, remote_client_params)
    #             if self.start_python(remote_server,remote_client_params):
    #                 self.check_and_add_crontab(remote_server,remote_client_params)
    #         elif run_type == 'start':
    #             remote_client_params = self.start_python(remote_server, remote_client_params)
    #         time.sleep(2)
    #         if _need_close_ssh:
    #             remote_server.close()
    #         #logger.error('[END][%s]\nparams=%s' % (str(remote_client_params.thread_id), str(remote_client_params.remote_client_dict_info)))
    #     except Exception as e:
    #         logger.error('error =%s' % (e))

    def run_per_remote_client_1(self, remote_client_params, run_type='all'):
        try:
            remote_server_client = _RemoteServerManager(remote_client_params.remote_client_dict_info['public_ip'],
                                                 remote_client_params.remote_client_dict_info['ssh_port']) if not remote_client_params.remote_server_object else remote_client_params.remote_server_object
            # remote_server_client = _RemoteServerManager(remote_client_params.remote_client_dict_info['public_ip'],
            #                                     remote_client_params.remote_client_dict_info['ssh_port'],
            #                                     remote_client_params.remote_client_dict_info['ssh_user'],
            #                                     remote_client_params.remote_client_dict_info[
            #                                     'ssh_pwd']) if not remote_client_params.remote_server_object else remote_client_params.remote_server_object
            remote_client_params.remote_server_object = remote_server_client
            if not remote_client_params.remote_output_file_path:
                remote_client_params.remote_current_path = remote_server_client.run_cmd('pwd').replace('\n', '').strip()
                remote_client_params.remote_output_file_path = os.path.join(
                    str(remote_client_params.remote_current_path),
                    REMOTE_WORK_PATH).replace('\\', '/')
            if not remote_client_params.remote_output_file_name:
                remote_client_params.remote_output_file_name = PYTHON_FILE_NAME
            if not remote_client_params.pname_list:
                remote_client_params.pname_list = remote_client_params.remote_client_dict_info.get(
                    'pname_list').replace(' ', '')
            if not remote_server_client:
                raise Exception('ssh connection failed')
            if not remote_client_params.server_type:
                remote_client_params.server_type = remote_client_params.remote_client_dict_info.get(
                    'product').strip() + '_' + remote_client_params.remote_client_dict_info.get('service').strip()
            if run_type == 'all':
                self._init_remote_path_and_file_info(remote_client_params=remote_client_params)
                self.put_file_to_client(remote_server_client, remote_client_params)
                self.start_python(remote_server_client, remote_client_params)
                self.check_and_add_crontab(remote_server_client, remote_client_params)
            elif run_type == 'start':
                remote_client_params = self.start_python(remote_server_client, remote_client_params)
            time.sleep(2)
        except Exception as e:
            logger.error('error =%s' % (e))

    def start_remote_clients(self, remote_clients_with_dict_info=None, remote_run_mode='p_client', run_type='all',
                             thread_id='CHECK'):
        """

        :param remote_clients_with_dict_info:
        :param run_type: [string] all/start/stop/check, all:上传脚本+启动
        :return:
        """
        # 将此脚本上传到各client服务器指定路径下
        task_list = []
        if not remote_clients_with_dict_info:
            remote_clients_with_dict_info = self.remote_clients_with_dict_info

        remote_clients_with_dict_info = _delete_duplicate_data_in_server_info(remote_clients_with_dict_info)
        __print_log = "Controller[%s] will boot [%s] agents########\n" % (thread_id, len(remote_clients_with_dict_info))

        for key, client_dict_info in remote_clients_with_dict_info.items():
            __client_ip = ''
            __client_ssh_user = ''
            try:
                if not client_dict_info.get('no'):
                    client_dict_info['no'] = 00
                client_dict_info['public_ip'] = str(client_dict_info['public_ip']).replace("'", '').replace('"',
                                                                                                            '').strip()
                client_dict_info['ssh_user'] = str(client_dict_info['ssh_user']).replace("'", '').replace('"',
                                                                                                          '').strip()
                client_dict_info['ssh_port'] = str(client_dict_info['ssh_port']).replace("'", '').replace('"',
                                                                                                          '').strip()
                __client_ip = str(client_dict_info['public_ip'])
                __client_ssh_user = str(client_dict_info['ssh_user'])
                if not client_dict_info['ssh_user'] or len(client_dict_info) <= 1 or not __client_ip:
                    raise Exception('no ssh_user or public_ip info')
                __print_log = __print_log + "[%s][STARTING] " % str(
                    client_dict_info['no']) + "%s@%s -p %s -P %s -pname %s" % (
                              __client_ssh_user, __client_ip, str(client_dict_info['ssh_pwd']),
                              str(client_dict_info['ssh_port']), str(client_dict_info['pname_list'])) + '\n'
                remote_client_params = _Params()
                remote_client_params.thread_id = thread_id + " Thread" + str(client_dict_info['no']) + "_%s" % str(
                    client_dict_info['public_ip'])
                remote_client_params.remote_output_file_path = self.remote_output_file_path
                remote_client_params.run_mode = remote_run_mode
                remote_client_params.remote_client_dict_info = client_dict_info
                remote_client_params.remote_output_file_name = self.remote_output_file_name

                remote_client_params.pname_list = str(
                    remote_client_params.remote_client_dict_info.get('pname_list')).replace(' ', '')

                # try:
                #     remote_client_params.pname_list = str(client_dict_info['pname_list']).replace(' ', '')
                # except:
                #     remote_client_params.pname_list = []
                #
                # if not remote_client_params.pname_list:
                #     remote_client_params.pname_list = []

                remote_client_params.remote_host = client_dict_info['public_ip']
                try:
                    remote_client_params.server_type = client_dict_info['product'].strip() + '_' + client_dict_info[
                        'service'].strip()
                except:
                    remote_client_params.server_type = ''
                # logger.warning('[START][%s]\nparams=%s' % (remote_client_params.thread_id,str(client_dict_info)))
                # 开始执行Controller
                t = threading.Thread(target=self.run_per_remote_client_1, args=(remote_client_params, run_type,),
                                     name='T_' + str(remote_client_params.remote_host))
                t.start()
                task_list.append(t)
            except Exception as e:
                __print_log = __print_log + "[%s][SKIP] %s@%s, id=%s\n" % (
                str(client_dict_info['no']), __client_ssh_user, __client_ip, str(traceback.format_exc()))
                logger.warning('Controller.run - SUB_THREAD.CONTROLLER[%s] failed=[%s],params:%s ' % (
                str(client_dict_info['public_ip']), str(traceback.format_exc()), str(client_dict_info)))
        logger.error(__print_log)
        for task in task_list:
            task.join()

    def check_and_start_every_client(self, client_dict_info, _agent_info, need_delete_remote_path=False,
                                     need_run_node_exporter=True, _check_loop=0):
        _data_id = 0
        try:
            _data_id = client_dict_info['no']
        except:
            pass
        # _client_key_name = (client_dict_info.get('public_ip'),client_dict_info.get('ssh_port'))
        _client_param = self._remote_clients_param.get(
            (client_dict_info.get('public_ip'), client_dict_info.get('ssh_port')))
        if not _client_param:
            _client_param = self._remote_clients_param[
                (client_dict_info.get('public_ip'), client_dict_info.get('ssh_port'))] = _Params(run_mode='p_client')

        _client_param.remote_client_dict_info = client_dict_info

        _data_node = [str(_data_id)[0:3],
                      client_dict_info.get('public_ip'),
                      str(str(client_dict_info.get('product')) + '_' + str(client_dict_info.get('service')))[0:15],
                      'node_exporter',
                      'RUNNING',
                      client_dict_info.get('ssh_user'),
                      client_dict_info.get('ssh_pwd'), client_dict_info.get('ssh_port'),
                      str(client_dict_info.get('pname_list'))[0:35], ]
        _datas = [copy.deepcopy(_data_node), _data_node]
        _datas[0][3] = 'python'  # PYTHON_FILE_NAME
        _warn_datas = []

        try:
            _client_ip = str(client_dict_info.get('public_ip'))
            _client_type = str(client_dict_info.get('product')) + '_' + str(client_dict_info.get('service'))
            _ssh_port = str(client_dict_info.get('ssh_port'))
            _pname = str(client_dict_info.get('pname_list'))

            if not client_dict_info['ssh_user'] or len(client_dict_info) <= 1 or not client_dict_info['public_ip']:
                raise Exception('no ssh_user|public_ip info')
            logger.error('[%s][%s/%s]START\nparams=%s' % (
            str(client_dict_info['public_ip']), str(_data_id), str(len(_agent_info)), str(client_dict_info)))

            remote_server = _RemoteServerManager(client_dict_info['public_ip'], client_dict_info['ssh_port'], timeout=5)
            if remote_server.error_msg:
                raise Exception('connect[%s] %s' % (str(client_dict_info.get('public_ip')), str(remote_server.error_msg)))
            # _client_param = Params()
            _client_param.remote_server_object = remote_server
            _client_param.remote_current_path = remote_server.run_cmd('pwd').replace('\n', '').strip()
            _client_param.remote_output_file_path = os.path.join(str(_client_param.remote_current_path),
                                                                 REMOTE_WORK_PATH).replace('\\', '/')
            _client_param.remote_output_file_name = PYTHON_FILE_NAME
            _local_file = os.path.join(PYTHON_FILE_PATH, PYTHON_FILE_NAME).replace('\\', '/')
            _remote_py_file_path = _client_param.remote_output_file_path

            if need_delete_remote_path:
                _run_cmd_in_remote(remote_server, client_dict_info, "kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}')" %
                                   os.path.split(os.path.realpath(__file__))[1])
                _run_cmd_in_remote(remote_server, client_dict_info, "kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep monitor_system_new.py|grep -v grep|awk '{print $2}')")
                _run_cmd_in_remote(remote_server, client_dict_info, "kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}')" % 'node_exporter', is_remote_support_sudo=remote_server.is_remote_support_sudo)
                _run_cmd_in_remote(remote_server, client_dict_info, "rm -rf %s" % (_remote_py_file_path + "*").replace('\\', '/').replace('/*', '*'), is_remote_support_sudo=remote_server.is_remote_support_sudo)

                return False

            '''check并启动python脚本'''
            _remote_file_md5 = remote_server.run_cmd(
                'md5sum %s' % os.path.join(_remote_py_file_path, PYTHON_FILE_NAME).replace('\\',
                                                                                           '/'))  # root文件也可用ec2-user执行
            if _check_loop == 1 or remote_server.error_code != 0 or str(_remote_file_md5).find(
                    str(_string_object.md5sum(_local_file))) == -1:  # 对方和本地的文件不一致
                self.run_per_remote_client_1(remote_client_params=_client_param, run_type='all')
                logger.info(
                    'waiting {0}s for clients[{1}:{2}] start......'.format('5', str(client_dict_info.get('public_ip')),
                                                                           str(client_dict_info.get('ssh_port'))))
                time.sleep(5)
                logger.info('waiting {0}s for clients[{1}:{2}] start......,end'.format('5', str(
                    client_dict_info.get('public_ip')), str(client_dict_info.get('ssh_port'))))
            _start_python_success = False
            _start_python_result = ''
            for i in range(0, 2):
                _start_python_success = True
                _start_python_result = remote_server.run_cmd(
                    cmd="ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}'" % PYTHON_FILE_NAME,
                    need_run_with_sudo=True)
                if str(remote_server.error_code) != "0" or not _start_python_result:
                    _start_python_success = False
                    self.run_per_remote_client_1(remote_client_params=_client_param, run_type='start')
                else:
                    break
                time.sleep(3)

            if _start_python_success is False:
                _datas[0][4] = 'STOP'
                _datas[0].append(str(_start_python_result)[0:55])
                _warn_datas.append(_datas[0])

            '''check并启动node_exporter'''
            if need_run_node_exporter:
                result = _run_cmd_in_remote(remote_server, client_dict_info, "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}'" % 'node_exporter', is_remote_support_sudo=remote_server.is_remote_support_sudo)
                result = str(result).replace('\n', ' ')
                if not result:
                    result = remote_server.run_cmd('uname -a')
                    remote_path = os.path.join(_remote_py_file_path, 'node_exporter').replace('\\', '/')
                    remote_file = os.path.join(remote_path, 'node_exporter-1.2.2.linux-amd64.tar.gz').replace('\\', '/')
                    remote_untar_path = os.path.join(remote_path, 'node_exporter-1.2.2.linux-amd64').replace('\\', '/')
                    local_file = os.path.join(os.path.dirname(PYTHON_FILE_PATH), 'tools', 'node_exporter',
                                              'node_exporter-1.2.2.linux-amd64.tar.gz').replace('\\', '/')
                    if result.find('aarch') != -1:
                        remote_file = os.path.join(remote_path, 'node_exporter-1.2.2.linux-arm64.tar.gz').replace('\\',
                                                                                                                  '/')
                        local_file = os.path.join(os.path.dirname(PYTHON_FILE_PATH), 'tools', 'node_exporter',
                                                  'node_exporter-1.2.2.linux-arm64.tar.gz').replace('\\', '/')
                        remote_untar_path = os.path.join(remote_path, 'node_exporter-1.2.2.linux-arm64').replace('\\',
                                                                                                                 '/')
                    remote_server.run_cmd('mkdir -p %s' % remote_path)
                    result = remote_server.run_cmd('ls %s' % (remote_untar_path))
                    if remote_server.error_msg:
                        remote_server.upload_file(local_file, remote_file)
                        remote_server.run_cmd('tar zxvf %s -C %s' % (remote_file, remote_path), timeout=10)
                    remote_server.run_cmd('nohup %s --collector.systemd --collector.processes 2>/dev/null &' % str(
                        os.path.join(remote_untar_path, 'node_exporter').replace('\\', '/')), need_run_with_sudo=True)

                    if remote_server.error_msg:
                        _datas[1][4] = 'STOP'

            remote_server.close()
        except Exception as e:
            logger.critical('check failed=%s' % str(traceback.format_exc()))
            _datas.pop(len(_datas) - 1)
            _datas[0][3] = 'all'
            _datas[0][4] = 'DEAD'
            _datas[0].append(str(e)[0:55])
            _warn_datas.append(copy.deepcopy(_datas[0]))
            # _datas[0][3] = 'python'
        print_table(datas=_datas, headers=self.need_print_datas['headers'], title=client_dict_info.get('public_ip'),
                    description=str(client_dict_info))
        self.need_print_datas['datas'] = self.need_print_datas['datas'] + _datas
        self.need_print_datas['warn_datas'] = self.need_print_datas['warn_datas'] + _warn_datas

    def do_run(self, test_platform=None, need_delete_remote_path=None, need_use_local_csv_servers=None,
               need_run_node_exporter=True, client_info=None, server_info=None):

        check_interval = 60 * 10
        _check_loop = 0

        while True:
            self._remote_client_params = {}
            self.need_print_datas['datas'] = []
            self.need_print_datas['warn_datas'] = []
            _check_loop = _check_loop + 1
            _agent_info = _get_server_info_from_csv(test_platform=test_platform, csv_file_list=CSV_FILES)
            if not need_use_local_csv_servers:
                _agent_info = {}
                _agent_info.update(client_info)
                _agent_info.update(server_info)

            logger.warning('servers_infos=%s' % str(_agent_info))
            _agent_info = _delete_duplicate_data_in_server_info(_agent_info)
            time.sleep(1)
            _local_thread = []

            for key, client_dict_info in _agent_info.items():
                T = threading.Thread(target=self.check_and_start_every_client,
                                     args=(
                                     client_dict_info, _agent_info, need_delete_remote_path, need_run_node_exporter,
                                     _check_loop),
                                     name='check_' + str(client_dict_info["public_ip"]))
                T.start()
                _local_thread.append(T)
                time.sleep(0.3)
            for i in _local_thread:
                i.join()

            print_table(datas=self.need_print_datas['datas'], headers=self.need_print_datas['headers'],
                        title='[LOOP:%s]%s CHECK_RESULT_END' % (str(_check_loop), str(len(_agent_info))),
                        tablefmt='grid')
            if self.need_print_datas['warn_datas']: # 2024.07.02 modify by jbzhu, 机器全成功后self.need_print_datas['warn_datas']为空, print_table异常
                print_table(datas=self.need_print_datas['warn_datas'], headers=self.need_print_datas['headers'],
                            title='[FAILED]%s/%s' % (
                            str(len(self.need_print_datas['warn_datas'])), str(len(_agent_info) * 2)), tablefmt='grid')
            else:
                logger.info('All machines executed successfully')

            logger.warning(
                'do_run -- CHECK,time.sleep=%ss,for [check_interval=%ss]' % (str(check_interval), str(check_interval)))
            time.sleep(int(check_interval))

    def kill_old_python_process(self, remote_server_client):
        cmd = "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v ' grep\| tail \| more \| vim \| vi \| less '|awk '{print $2}'|xargs sudo kill -9" % self.python_file_name
        # cmd = "kill $(ps -ef|grep %s|grep -v grep|awk '{print $2}')" % self.python_file_name
        cmd_result = remote_server_client.run_cmd(cmd, need_run_with_sudo=True)

    def put_file_to_client(self, remote_server_client, remote_client_params):
        '''
        从本地传文件至remote服务器
        :param client_list: 接收file的客户端服务器列表
        :param local_file_path: 本地文件的路径（如/home/ec2-user/server_watchdog.py）
        :param remote_file_path: 接收file的客户端该文件的存放路径,支持两种方式，一种是传入传路径（如/root/ec2-user/,不需要带文件名），
                                  一种是传入非全路径，此种方式下，会获取当前登录用户的默认路径，再加上传入的路径（若登录进去为/home/ec2-user，传入的路径为test/script，则整个路径为/home/ec2-user/test/script）
                                  说明：若remote_file_path首个字符为/时，则认为是全路径，若首个字符非/，则认为非全路径
                                  若remote_file_path为str，或list且仅有一个元素，则所有client均使用此路径，若为lis且为多个元素，则与client_list中的client一一对应
        :return:
        '''
        try:
            create_cmd = 'mkdir -p %s' % remote_client_params.remote_output_file_path
            create_result = remote_server_client.run_cmd(create_cmd)
            # self.kill_old_python_process(ssh_connect_handle)

            remote_file = os.path.join(remote_client_params.remote_output_file_path,
                                       remote_client_params.remote_output_file_name).replace('\\', '/')
            local_file = os.path.join(self.local_output_path, self.local_output_file).replace('\\', '/')
            result = remote_server_client.upload_file(local_file, remote_file)
            # 关闭ssh连接
            # logger.critical('%s  %s'%(str(self.controller_param.thread_id),str(self.controller_param.remote_client_dict_info)))
        except Exception as e:
            logger.error("[%s]run script failed=%s" % (remote_client_params.thread_id, str(e)))

    def check_and_add_crontab(self, remote_server, remote_client_params):
        # remote_client_params = Params()
        try:
            if not remote_client_params.remote_python_start_cmd or not remote_client_params.remote_output_file_name:
                raise Exception(('param fail', 'start_cmd=', remote_client_params.remote_python_start_cmd, 'file=',
                                 remote_client_params.remote_output_file_name))
            _modify_backup_crontab = "sudo sed -i '/{pyname}/d' crontab.bak && echo '@reboot {cmd}' >> crontab.bak".format(
                pyname=remote_client_params.remote_output_file_name,
                cmd=str(remote_client_params.remote_python_start_cmd))
            # cmd1 = "sudo sed -i '/monitor_system_new/d' crontab.bak"
            # cmd3 = "sudo sed -i '/@reboot None/d' crontab.bak"
            _backup_cmd = 'sudo crontab -l > crontab.bak ; stat -c %s crontab.bak'  # 备份并获取备份后的文件大小
            _get_old_cmd = 'grep {0} crontab.bak '.format(remote_client_params.remote_output_file_name)
            '''获取目前crontab中python的命令行'''
            _bak_size = remote_server.run_cmd(_backup_cmd, need_run_with_sudo=True)
            _rewrite_crontab = "sudo crontab crontab.bak"

            '''cpu 100%时, crontab -l > crontab.bak 内容为空,退出状态=None,备份后的文件大小是0不备份'''
            if remote_server.exit_status_code != 0 or remote_server.error_code != ERROR_CODE_SUCCESS or int(_bak_size) == 0:
                raise Exception('backup fail[%s]' % _backup_cmd)

            result = remote_server.run_cmd(_get_old_cmd, need_run_with_sudo=True)
            if remote_server.error_code != ERROR_CODE_SUCCESS:
                raise Exception('backup fail[%s]' % _backup_cmd)
            '''比较和即将写入的是否一样'''
            if str(result).replace(' ', '').replace('\n', '').replace('sudo', '') != '@reboot {cmd}'.format(
                    cmd=remote_client_params.remote_python_start_cmd).replace(' ', '').replace('sudo', ''):
                logger.info(('crontab src!=expect', 'src=', result, 'dst=',
                             '@reboot {cmd}'.format(cmd=remote_client_params.remote_python_start_cmd)))
                """bak写入最新的python命令行，并替换crontab"""
                remote_server.run_cmd(_modify_backup_crontab, need_run_with_sudo=True)
                # remote_server.exec_sudo_cmd(cmd1,is_remote_support_sudo=remote_server.is_remote_support_sudo)
                # remote_server.exec_sudo_cmd(cmd3,is_remote_support_sudo=remote_server.is_remote_support_sudo)
                if remote_server.exit_status_code != 0 or remote_server.error_code != ERROR_CODE_SUCCESS:
                    raise Exception('modify fail[%s]' % _modify_backup_crontab)
                remote_server.run_cmd(_rewrite_crontab, need_run_with_sudo=True)
            else:
                logger.info(
                    '[{0}]crontab src=expect,{1}'.format(remote_client_params.remote_client_dict_info.get('public_ip'),
                                                         result))

        except Exception as e:
            logger.info("failed=%s" % str(traceback.format_exc()))

    def _init_remote_path_and_file_info(self, remote_client_params):
        try:
            _remote_py = os.path.join(remote_client_params.remote_output_file_path,
                                      remote_client_params.remote_output_file_name).replace('\\', '/')
            _log = os.path.join(remote_client_params.remote_output_file_path, 'monitor.log').replace('\\', '/')
            # _now_user_cmd = 'stat -c "%U" ' + _remote_py
            # _now_user = remote_client_params.remote_server_object.exec_command(_now_user_cmd,need_run_with_sudo=True).replace('\n', '').strip()
            _expected_user = remote_client_params.remote_client_dict_info.get('ssh_user')
            _expected_user = 'root' if not _expected_user else _expected_user
            remote_client_params.remote_server_object.run_cmd(
                'chown -R {0}:{0} {1}'.format(_expected_user, remote_client_params.remote_output_file_path),
                need_run_with_sudo=True)
        except:
            pass


class _GetRealTimeData():
    def __init__(self, client_params=None, low_performance=False, need_print_log=True):
        self.client_params = client_params
        self.low_performance = low_performance
        if not client_params:
            client_params = _Params()
        self.local_ip = client_params.local_host
        self._local_py_path = client_params.local_output_path
        client_params.local_output_path = os.path.join(client_params.local_output_path,
                                                       client_params.local_host + '_monitor_output').replace(' ',
                                                                                                             '').replace(
            '\\', '/')
        client_params.local_output_file = client_params.local_host + '_monitor.csv'

        self._init_path_and_file_info()
        client_params.pname_list = str(client_params.pname_list).replace('[', '').replace(']', '').replace('"',
                                                                                                           '').replace(
            "'", '').split(',')
        self.pid_per_pname_dict = {}
        self.listen_port_per_pname_dict = {}
        self.pname = []
        self._need_print_log = need_print_log

        for n, i in enumerate(client_params.pname_list):
            if i and str(i).lower() != 'none' and (i not in client_params.pname_list[:n]):
                self.pname.append(str(i).strip())
                self.pid_per_pname_dict.update({i: []})
                self.listen_port_per_pname_dict.update({i: []})

        # '''pname去重去空'''
        # client_params.pname_list = self.pname = [i for n, i in enumerate(client_params.pname_list) if
        #                                          i and (i not in client_params.pname_list[:n])]
        self._pid_num_per_pname = 50
        self._listen_port_num_per_pname = 8
        self._display_pname_per_pid = {}  # 用于显示的pname,跟入参的pname不一样 {'pid':display_pname,'pid':display_pname} ext:{'3306':java#gwn_router}
        self.last_data = {'mysql': {}, 'redis': {}, 'podman': {}, 'p_cpu': {}, 'bw': {}, 'docker':{}}  # 上次获取的时间
        self.record_interval = int(client_params.monitor_interval)
        self.total_runtime = int(client_params.test_duration)
        self.iface_name = lo_cli.get_iface_name_for_public()

        self.__init_h_file()
        self._init_file_names(record_file_path=client_params.local_output_path)
        self._monitor_commands()
        try:
            self._genarate_check_monitor_bash_file()
        except:
            pass

        self._is_support_mysql = None
        self._cmd_mysql = None

        # 自动判断本机是否支持这些app,并记录app的可执行路径
        self._app_info = {}
        for _app in ['kamailio', 'rtpengine', 'jstat', 'podman', 'docker']:
            self._app_info.update({_app:{"state": None, 'cmd': None}})
        self._is_support_redis = None
        self._cmd_redis = None

        self._enable_ss = False

        self._bindwidth_data = {}  # 带宽启动线程时（默认）,存放获取到的最新数据
        self.cpu_data = {}  # 带宽启动线程时（默认）,存放获取到的最新数据
        self.cpu_times_static_data = {}
        self._vmstat_data = {}  # vmstat耗时1s所以线程启动,存放获取到的最新数据
        # self.all_datas = {
        #     'cpu': {}, 'cpu_load': {}, 'memory': {}, 'ss': {}, 'sockstat':{},
        #     'bindwidth': {},'io':{},
        #     'p_cpu': {}, 'p_memory': {}, 'p_thread_num': {}, 'p_pid': {},'p_num':{},
        #     'p_fd_num':{},'p_sockstat':{}, 'p_bindwidth':{},
        #     'app_java': {},
        #     'app_mysql': {}, 'app_redis': {},
        #     'app_kafka': {}, 'app_kamailio': {}, 'app_asterisk': {},
        #     'app_project': {}, }  #所有数据
        self.all_datas = {
            'cpu': {}, 'cpu_time': {}, 'cpu_load': {}, 'memory': {}, 'ss': {}, 'sockstat': {},
            'bw': {}, 'io': {}, 'vmstat': {}, 'storage': {}}
        if self.pname:
            self.all_datas.update({'p_cpu': {}, 'p_memory': {}, 'p_thread_num': {}, 'p_pid': {}, 'p_num': {},
                                   'p_fd_num': {}, 'p_sockstat': {}, 'p_bindwidth': {}, 'app_project': {}})
        if str(self.pname).find('java') != -1:
            self.all_datas.update({'app_java': {}})
        if str(self.pname).find('mysql') != -1:
            self.all_datas.update({'app_mysql': {}})
        if str(self.pname).find('redis') != -1:
            self.all_datas.update({'app_redis': {}})

        if str(self.pname).find('kafka') != -1:
            self.all_datas.update({'app_kafka': {}})
        if str(self.pname).find('asterisk') != -1:
            self.all_datas.update({'app_asterisk': {}})
        if str(self.pname).find('kamailio') != -1:
            self.all_datas.update({'app_kamailio': {}})
        self.all_datas.update({'app_podman': {}})
        self.all_datas.update({'app_docker': {}})

        logger.warning(('self.all_datas', self.all_datas))
        self._is_cpu_and_bindwidth_thread_start = False  # 判断线程是否已启动
        self._need_write_to_file = True
        # self._need_get_top = need_get_top
        logger.critical(('#################', sys.platform))
        if 'win32' not in sys.platform:
            threading.Thread(target=self.do_get_real_time_and_cpu_bw_vmstat_info,
                             args=(client_params.monitor_interval,),
                             kwargs={'need_write_to_file': self._need_write_to_file, 'top_interval': 15},
                             name='top_ps_cpu_bw').start()

    '''[chfshan] 2024.3.5 init文件目录结构,已有修改目录/文件的权限为登录用户'''

    def _init_path_and_file_info(self):
        try:
            if not os.path.exists(self.client_params.local_output_path):
                logger.warning("create dir=%s" % self.client_params.local_output_path)
                os.mkdir(self.client_params.local_output_path)

            # 定义需要修改的文件路径
            _log = os.path.join(self._local_py_path, 'monitor.log').replace('\\', '/')
            _py = os.path.join(PYTHON_FILE_PATH, PYTHON_FILE_NAME).replace('\\', '/')
            _expect_user = os.stat(_py).st_gid
            _new_user = None
            # for _file in (_log,_log+'.1',self.client_params.local_output_path):
            #     try:
            #         # 获取当前文件的所属组和所属用户信息
            #         _now_user = os.stat(_file).st_gid
            #         if str(_now_user) != str(_expect_user):
            #             os.chown(_file, -1, _now_user)
            #     except Exception as e:
            #         pass
            _new_user = _new_user if _new_user else lo_cli.run_cmd('stat -c "%U" ' + _py,
                                                                   need_run_with_sudo=True).strip()
            _new_user = os.getlogin()
            # lo_cli.run_cmd('chown -R {0}:{0} {1}'.format(_new_user,PYTHON_FILE_PATH),need_run_with_sudo=True)

        except:
            pass

    def _genarate_check_monitor_bash_file(self):
        _start_cmd = str(lo_cli.get_python_execute_path())
        for i in sys.argv:
            _start_cmd = _start_cmd + ' ' + str(i)

        logger.critical(_start_cmd)
        _start_cm_cmd = "/usr/bin/python3 /home/ec2-user/MONITOR_SYSTEM/monitor_system.py  --runmode p_client --runtotaltime 31536000 --needmonitorpname ,mysqld,sbin/asterisk,gs_avs,containermanager,lighttpd,comet,logic,business,cgi,pbxmid --servertype clouducm/clouducm_redis/master_container --logconsolelevel 20 --logfilelevel 20"
        _start_sbc_cmd = "/usr/bin/python /home/ec2-user/MONITOR_SYSTEM/monitor_system.py --runmode p_client --logconsolelevel 20 --logfilelevel 20 --monitorinterval 15 --servertype clouducm_proxy --needmonitorpname rtpengine,kamailio,nginx,sync_config --runtotaltime 31536000"
        _content = """#!/bin/bash
for i in $(seq 1 10000); do
 monitor_pid=$(ps -ef|grep monitor_system.py|grep -v grep|grep p_client|awk "{print $2}")
 echo "$monitor_pid"
 if [ $monitor_pid ];then
  echo "monitor process running, pid = $monitor_pid"
 else
  echo "monitor_system_pid= $monitor_pid,try start monitor_system [$i/600]..."
  monitor_pid=$(nohup %s 2>/dev/null &)
  echo "monitor command result=$monitor_cmd"
 fi
 sleep 30s
done
echo 'exit'
""" % str(_start_cmd)

        lo_cli.run_cmd("echo '%s' > '%s'" % (
        _content, os.path.join(self._local_py_path, "check_loal_monitor.sh").replace('\\', '/')))
        lo_cli.run_cmd("chmod 777 %s" % (os.path.join(self._local_py_path, "check_loal_monitor.sh").replace('\\', '/')))
        # lo_cli.run_cmd("rm -rf %s" % (os.path.join(self._local_py_path,"check_local_monitor.sh").replace('\\','/')))

    '''取监控相关数据的命令集,部分为backup未使用'''

    def _monitor_commands(self):
        '''
        监控命令
        :return:
        '''

        # 系统自带命令监控实现/proc内核为主,常用命令[/proc内核 free top vmstat pidof netstat ss]说明:
        '''
        vmstat - cpu&mem/io [vmstat -a -w -t -S K 1 2]/[vmstat -d -w -t -S K 1 2]无util
        free - mem [free -m]
        top - cpu&mem&pid-info [top -d 1]
        #netstat - socket [netstat -napt]
        ss - socket [ss -tuanps]
        '''

        # 依赖第三方库命令,需[yum install sysstat],常用命令[mpstat iostat pidstat tapstat sar sadf]说明:
        '''
        mpstat- cpu [ mpstat -P ALL 1 2 ]
        iostat- cpu [ iostat -c 1 10 ]
                io  [ iostat -x -d -k 1 2 ]
        sar   - cpu [ sar -u -P ALL 1 2 ]
                io  [ sar -d -p 1 2 ]
                net [ sar -n DEV 1 2 ]
                mem [ sar -r 1 2 ]
                load[ sar -q 1 2 ]
        pidstat-进程cpu[ pidstat -u -p $pid 1 2 ]
                进程mem[ pidstat -r -p pid 1 2 ]
                进程io [ pidstat -d -p $pid 1 2 ]   -p不带为全部
        '''

        # =========[监控命令][整机]【磁盘IO】 iostat/sar依赖sysstat-------------------
        self.cmd_disk_io = '/proc/diskstats'  # 内核数据
        self._cmd_disk_io_vmstat = 'vmstat -d -w -t -S K 1 2'  # 无ioutil
        ''' vmstat 输出示例 https://www.cnblogs.com/poloyy/p/13363123.html'''
        '''cs 列：上下文切换次数从之前 200 骤然上升到了 160w+...每秒上下文切换多少次才算正常？这个数值其实取决于系统本身的 CPU 性能,如果系统的上下文切换次数比较稳定，那么数百到一万以内，都是正常的,但当上下文切换次数超过一万次，或者切换次数出现数量级的增长时，就很可能已经出现了性能问题
        r 列：就绪队列的长度最大到 8了，大于我们的 CPU 个数 4，所以会存在大量的 CPU 竞争
        us、sy 列：两列的 CPU 使用率加起来上升到了 80-90，其中系统 CPU 使用率都是 60%+，说明 CPU 主要是被内核占用了
        in 列：中断次数已经达到 8w 了...说明中断处理也是个潜在的问题, 具体的终端类型看/proc/interrupts'''
        """
        [root@localhost csv]# vmstat -d -w -t -S K 1 2
        disk- -------------------reads------------------- -------------------writes------------------ ------IO------- -----timestamp-----
                  total    merged     sectors          ms     total    merged     sectors          ms     cur     sec                 CST
        sda       28942       414     2971655      328726   1138448     48119    72193163    11014038       0    1983 2023-11-02 11:09:43
        dm-0      28493         0     2883437      303524   1126278         0    72184424    34917006       0    1982 2023-11-02 11:09:43
        sda       28942       414     2971655      328726   1138473     48121    72193863    11014485       0    1983 2023-11-02 11:09:44
        dm-0      28493         0     2883437      303524   1126304         0    72185124    34917490       0    1982 2023-11-02 11:09:44

        Reads
           total: Total reads completed successfully
           merged: grouped reads (resulting in one I/O)
           sectors: Sectors read successfully
           ms: milliseconds spent reading

       Writes
           total: Total writes completed successfully
           merged: grouped writes (resulting in one I/O)
           sectors: Sectors written successfully
           ms: milliseconds spent writing

       IO
           cur: I/O in progress
           s: seconds spent for I/O
        """
        self._cmd_disk_io_iostat = 'iostat -x -d -k 1 2'  # 磁盘io使用率取util
        '''iostat 输出示例'''
        """
        [root@localhost csv]# iostat -x -d -k 1 2
        Linux 3.10.0-1127.19.1.el7.x86_64 (grandstream) 	11/02/2023 	_x86_64_	(40 CPU)

        Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
        sdb               0.00     1.64    5.05   85.24   150.62  3556.25    82.11     0.89    9.91    5.79   10.15   4.35  39.27
        sda               0.00     8.36    0.86   47.84    20.01  1999.35    82.94     0.14    2.85    3.86    2.83   3.31  16.10

        Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
        sdb               0.00     0.00    3.00   74.00    72.00   808.00    22.86     1.46   19.00    4.67   19.58   3.99  30.70
        sda               0.00     0.00    0.00   36.00     0.00   232.00    12.89     0.81   19.19    0.00   19.19   2.86  10.30
        await: 每个I/O请求的平均等待时间(毫秒)
        svctm: 处理I/O请求的平均服务时间(毫秒)【需<2ms】 =util/(iops)=util/(r/s+w/s), 1s的总服务时间除以总次数
        util:  设备的利用率百分比,1s中在服务的时间 【需<80%】
        """
        self._cmd_disk_io_sar = 'sar -d -p 1 2'  # 磁盘io使用率 util
        ''' sar 输出示例 '''
        """
        [root@localhost csv]# sar -d -p 1 2
        Linux 3.10.0-1127.19.1.el7.x86_64 (grandstream) 	11/02/2023 	_x86_64_	(40 CPU)

        06:05:18 AM       DEV       tps  rd_sec/s  wr_sec/s  avgrq-sz  avgqu-sz     await     svctm     %util
        06:05:19 AM       sdb    216.00      8.00  28208.00    130.63     12.56     58.70      3.29     71.00
        06:05:19 AM       sda      5.00      0.00    176.00     35.20      0.09      9.40      7.40      3.70

        06:05:19 AM       DEV       tps  rd_sec/s  wr_sec/s  avgrq-sz  avgqu-sz     await     svctm     %util
        06:05:20 AM       sdb     27.00      0.00    528.00     19.56      0.25      9.19      4.70     12.70
        06:05:20 AM       sda     31.00      0.00    552.00     17.81      0.65     22.42      3.39     10.50

        Average:          DEV       tps  rd_sec/s  wr_sec/s  avgrq-sz  avgqu-sz     await     svctm     %util
        Average:          sdb    121.50      4.00  14368.00    118.29      6.41     53.20      3.44     41.85
        Average:          sda     18.00      0.00    364.00     20.22      0.37     20.61      3.94      7.10
        """

        # =========[监控命令][整机]【磁盘存储】disk storage------------------
        self.cmd_disk_storage = 'df -Thm'

        # =========[监控命令][整机+进程]【top】定时保存日志仅用于问题定位----------------
        self.cmd_top_1 = "top -d 1 -n 2 -b -c -w 512 -o +%CPU"  # -o按MEM排序,-b输出文本可读格式,-c显示完整命令,-n执行次数 -d更新周期默认5s -w输出列宽 -i不显示闲置或者僵尸的进程信息
        self.cmd_top_2 = "top -d 1 -n 2 -b -c -w 512"  # 默认排序
        '''top输出示例'''
        """
        [root@manager]# top -d 1 -n 2 -b -c -w 512
        top - 06:48:57 up 17 days,  3:43,  8 users,  load average: 0.01, 0.07, 0.27
        Tasks: 350 total,   1 running, 337 sleeping,  12 stopped,   0 zombie
        %Cpu(s):  0.2 us,  0.5 sy,  0.0 ni, 99.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
        KiB Mem : 15684792 total,  6277888 free,  1372152 used,  8034752 buff/cache
        KiB Swap: 34815996 total, 34815996 free,        0 used. 13191372 avail Mem 

           PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
        129684 root      20   0  162284   2328   1620 R  12.5  0.0   0:00.03 top -d 1 -n 2 -b -c -w 512
             1 root      20   0 2108492   4904   2608 S   0.0  0.0 145:59.62 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
             2 root      20   0       0      0      0 S   0.0  0.0   0:02.22 [kthreadd]
             4 root       0 -20       0      0      0 S   0.0  0.0   0:00.00 [kworker/0:0H]
             6 root      20   0       0      0      0 S   0.0  0.0   0:17.37 [ksoftirqd/0]
             7 root      rt   0       0      0      0 S   0.0  0.0   0:00.19 [migration/0]

        """
        self.cmd_top_3 = 'top -d 1 -n 2 -b -c'
        self.cmd_top_4 = 'top -d 1 -n 2 -b '  # 真实ucm上仅这个命令能用

        # =========[监控命令][整机]【内存】------------------
        self.cmd_memory_by_proc = '/proc/meminfo'
        '''meminfo输出示例'''
        """
        $ cat /proc/meminfo 
        MemTotal:       329867012 kB
        MemFree:         1692348 kB
        MemAvailable:   88199952 kB
        Buffers:          615692 kB
        Cached:         84267056 kB
        SwapCached:            0 kB
        Active:         274521252 kB
        SwapTotal:             0 kB
        SwapFree:              0 kB
        """
        self.cmd_memory_by_free = 'free -m'
        '''free输出示例'''
        """
        $ free -m
              total        used        free      shared  buff/cache   available
        Mem:         322135      229499        1637         284       90998       86131
        Swap:             0           0           0
        """

        # =========[监控命令][整机]【cpu】 ------------------mpstat/sar需yum -y install sysstat
        self.cmd_cpu_usage_by_proc = '/proc/stat'  # 默认,失败用下面的几种，不同系统版本列数不一样
        self._cmd_cpu_usage_by_sar = 'sar -u -P ALL 1 2'  # 不同的机型列数不一样
        '''sar输出示例'''
        """
        [root@localhost ~]$ sar -u -P ALL 1 2
        Linux 3.10.0-1127.19.1.el7.x86_64 (grandstream) 	11/02/2023 	_x86_64_	(40 CPU)

        06:24:49 AM     CPU     %user     %nice   %system   %iowait    %steal     %idle
        06:24:50 AM     all     13.01      0.00      2.04      1.18      0.00     83.77
        06:24:50 AM       0     17.20      0.00      4.30      4.30      0.00     74.19
        06:24:50 AM       1     26.32      0.00      1.05      4.21      0.00     68.42

        06:24:50 AM     CPU     %user     %nice   %system   %iowait    %steal     %idle
        06:24:51 AM     all     16.30      0.00      2.84      1.89      0.00     78.97
        06:24:51 AM       0      7.69      0.00      5.49      0.00      0.00     86.81
        06:24:51 AM       1     17.17      0.00      3.03      2.02      0.00     77.78

        Average:        CPU     %user     %nice   %system   %iowait    %steal     %idle
        Average:        all     14.65      0.00      2.44      1.53      0.00     81.37
        Average:          0     12.50      0.00      4.89      2.17      0.00     80.43
        Average:          1     21.65      0.00      2.06      3.09      0.00     73.20
        """
        self._cmd_cpu_usage_by_mpstat = 'mpstat -P ALL 1 2'  # 显示所有cpu, 仅cpuall: mpstat 1 2
        '''mpstat输出示例'''
        """
        [root@localhost ~]$ mpstat -P ALL 1 2
        Linux 3.10.0-1127.19.1.el7.x86_64 (grandstream) 	11/02/2023 	_x86_64_	(40 CPU)

        06:26:58 AM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
        06:26:59 AM  all    0.08    0.00    2.27    1.23    0.00    0.08    0.00   14.97    0.00   81.38
        06:26:59 AM    0    0.00    0.00    5.38    1.08    0.00    2.15    0.00   17.20    0.00   74.19
        06:26:59 AM    1    0.00    0.00    2.13    2.13    0.00    0.00    0.00   12.77    0.00   82.98

        06:26:59 AM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
        06:27:00 AM  all    0.56    0.00    3.09    2.58    0.00    0.08    0.00   14.18    0.00   79.51
        06:27:00 AM    0    0.00    0.00    3.33    2.22    0.00    1.11    0.00   17.78    0.00   75.56
        06:27:00 AM    1    0.00    0.00    5.21    4.17    0.00    0.00    0.00   20.83    0.00   69.79

        Average:     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
        Average:     all    0.32    0.00    2.68    1.90    0.00    0.08    0.00   14.57    0.00   80.45
        Average:       0    0.00    0.00    4.37    1.64    0.00    1.64    0.00   17.49    0.00   74.86
        Average:       1    0.00    0.00    3.68    3.16    0.00    0.00    0.00   16.84    0.00   76.32
        """

        self._cmd_cpu_usage_by_vmstat = 'vmstat -a -w -t -S K 1 2'
        '''vmstat输出示例'''
        """
        [root@localhost ~]# vmstat -a -w -t -S K 1 2
        --procs-- -----------------------memory---------------------- ---swap-- -----io---- -system-- --------cpu-------- -----timestamp-----
           r    b         swpd         free        inact       active   si   so    bi    bo   in   cs  us  sy  id  wa  st                 UTC
           0    0       442352        43528       844576       498676  164  192 42172   280   81   80   4  23  72   1   0 2023-12-21 02:48:50
           0    0       442352        43528       843520       498612    0    0     0    64 3218 5763   2   6  92   0   0 2023-12-21 02:48:51
        """
        self._cmd_cpu_softirqs = 'cat /proc/softirqs'  # 软中断具体运行情况 调优:https://blog.csdn.net/m0_37383484/article/details/126973655
        '''输出示例TIMMER(定时终端)|NET_RX网络接收|SCHED内核调度|RCU锁'''
        """
        [root@localhost ~]# cat /proc/softirqs 
                        CPU0       CPU1       
              HI:          5         10
           TIMER:   10362138    9435146
          NET_TX:       2177       2185
          NET_RX:  195270482  246523284
           BLOCK:   16118547     124123
        IRQ_POLL:          0          0
         TASKLET:      61461      75135
           SCHED:   21273003   21380240
         HRTIMER:       3749       3489
             RCU:   39816056   42228609

        """

        # =========[监控命令][整机]【cpu load】 ------------------
        self.cmd_cpu_load_avg = "cat /proc/loadavg|awk -F' ' '{print $1,$2,$3}'"  # 默认，取失败时用cmd_cpu_load_avg_uptime等
        '''loadavg输出示例 [14.05 13.71 12.94 6/2406 9857]'''
        self.cmd_cpu_load_avg_uptime = "uptime|awk '{print $(NF-2),$(NF-1),$NF}'|awk -F',' '{print $1,$2,$3}'"
        '''uptime输出示例[ 06:39:52 up 34 days, 19:46,  2 users,  load average: 10.37, 12.84, 12.68]'''

        # =========[监控命令][整机]【网络流量】 ------------------
        self.cmd_network_info_by_proc = '/proc/net/dev'  # 默认,统计失败用下面的几种 # TCP_ESTABLISHED:1 TCP_SYN_SENT:2 TCP_SYN_RECV:3 TCP_FIN_WAIT1:4 TCP_FIN_WAIT2:5 TCP_TIME_WAIT:6 TCP_CLOSE:7 TCP_CLOSE_WAIT:8 TCP_LAST_ACL:9 TCP_LISTEN:10 TCP_CLOSING:11
        self.cmd_network_info_by_sar = 'sar -n DEV 1 2'
        '''sar输出示例'''
        """
        [root@manager-master P005_ucm]# sar -n DEV 1 2
        Linux 3.10.0-1127.19.1.el7.x86_64 (manager-master.ydmp) 	2023年11月02日 	_x86_64_	(24 CPU)

        06时50分11秒     IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s
        06时50分12秒        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00
        06时50分12秒       em1     18.00      5.00      1.56      0.62      0.00      0.00      0.00

        06时50分12秒     IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s
        06时50分13秒        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00
        06时50分13秒       em1     15.00      3.00      1.23      1.23      0.00      0.00      1.00

        平均时间:     IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s
        平均时间:        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00
        平均时间:       em1     16.50      4.00      1.40      0.92      0.00      0.00      0.50
        """
        self.__get_listen_port_count__ = "(cat /proc/net/tcp & cat /proc/net/tcp6)| awk '{if($4==\"0A\") print $0}'|wc -l"

        # =========[监控命令][整机]【链路】 ------------------
        self.cmd_ss = "ss -tuanps"  # -a所有状态的连接   antups
        '''ss输出示例'''
        """
        ss -tuanps
        Total: 5228 (kernel 9333)
        TCP:   539 (estab 4, closed 444, orphaned 0, synrecv 0, timewait 361/0), ports 0

        Transport Total     IP        IPv6
        *	  9333      -         -        
        RAW	  2         0         2        
        UDP	  12        7         5        
        TCP	  95        88        7        
        INET	  109       95        14       
        FRAG	  0         0         0        

        Netid State      Recv-Q Send-Q      Local Address:Port         Peer Address:Port              
        udp   UNCONN     0      0               11.0.0.1:53                  *:*                   users:(("dnsmasq",pid=4058,fd=5))
        tcp   LISTEN     0      1               127.0.0.1:5946                *:*                  users:(("qemu-kvm",pid=5953,fd=25))
        tcp   LISTEN     0      128             192.168.130.200:10050
        tcp   ESTAB      0      0               192.168.121.30:26222     192.168.121.230:47286     users:(("sshd",pid=15798,fd=3))*:*               
        """
        self._cmd_netstat = 'netstat -apn|grep -v STR|grep -v DGR'
        '''netstat示例,https://www.freesion.com/article/20011372008/）'''
        '''
        netstat -apn|grep -v STR|grep -v DGR
        Active Internet connections (servers and established)
        Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
        tcp        0      0 127.0.0.1:5946          0.0.0.0:*               LISTEN      5953/qemu-kvm       
        tcp        0      0 127.0.0.1:5914          0.0.0.0:*               LISTEN      5908/qemu-kvm       
        tcp        0      0 127.0.0.1:5947          0.0.0.0:*               LISTEN      6737/qemu-kvm  

        Established时netstat和ss都
        Recv-Q：OS持有的，尚未交付给应用的 数据的 字节数
        Send-Q：已经发送给对端应用,但对端应用尚未ack的字节数。此时这些数据依然要由OS持有
        Listen时
        ss的Recv-Q：“已建立成功（状态为ESTABLISHED），但尚未交付给应用的” tcp连接的数量。该值最大为：Send-Q+1，即：min(backlog, somaxconn)+1。https://segmentfault.com/a/1190000019252960
        ss的Send-Q：listen时，backlog的大小。其值为min(backlog, somaxconn)
        netstat的Recv-Q ：含义同ss的Recv-Q
        netstat的Send-Q： 尽管文档中说是"Since Kernel 2.6.18 this column contains the maximum size of the syn backlog"，但，实验中看不出来
        '''

        # =========[监控命令][整机+进程]【上下文切换】 ------------------
        self._cmd_pidstat = 'pidstat -wt -u 1 10'  # -w 输出进程切换指标,-t显示与选定任务关联的线程的统计信息,-u 输出 CPU 使用情况
        '''pidstat 输出示例'''
        """
        [ec2-user@ip-10-2-0-63 10.2.0.63_monitor_output]$ pidstat -wt -u 1 1
        Linux 6.1.61-85.141.amzn2023.aarch64 (ip-10-2-0-63.cn-north-1.compute.internal) 	12/25/23 	_aarch64_	(2 CPU)

        01:48:15      UID      TGID       TID    %usr %system  %guest   %wait    %CPU   CPU  Command
        01:48:16        0        59         -    0.00    1.74    0.00    0.00    1.74     0  kswapd0
        01:48:16        0         -        59    0.00    1.74    0.00    0.00    1.74     0  |__kswapd0
        01:48:16     1000   1159354         -    6.09    5.22    0.00    0.00   11.30     0  pidstat
        01:48:16     1000         -   1159354    6.09    5.22    0.00    0.00   11.30     0  |__pidstat
        01:48:16        0   1159362   1159362    0.00    0.87    0.00    0.00    0.87     1  (sudo)__sudo
        01:48:16        0   1159364         -    0.87    0.00    0.00    0.00    0.87     1  podman
        01:48:16        0         -   1159364    0.87    0.00    0.00    0.00    0.87     1  |__podman
        01:48:16        0   1212818         -    0.87    0.00    0.00    0.00    0.87     0  asterisk
        01:48:16        0   1215378   1215378    0.00    0.87    0.00    0.00    0.87     1  (redis-server)__redis-server
        01:48:16        0   1215988   1219083    0.00    0.87    0.00    0.87    0.87     0  (asterisk)__asterisk
        01:48:16        0   1216316         -    0.00    0.87    0.00    0.00    0.87     1  safe_mid.sh
        01:48:16        0   1218494         -    0.87    0.00    0.00    0.00    0.87     1  redis-server
        01:48:16        0   1218769         -    0.00    0.87    0.00    0.00    0.87     0  redis-server
        01:48:16        0   1219590         -    0.00    0.87    0.00    0.00    0.87     1  job
        01:48:16        0   1220161         -    0.87    0.00    0.00    0.00    0.87     0  logic
        01:48:16        0   1220184   1220979    0.00    0.87    0.00    0.00    0.87     0  (logic)__logic
        01:48:16        0   1220699         -    0.00    0.87    0.00    0.00    0.87     1  business
        01:48:16        0   1220732         -    0.87    0.00    0.00    0.00    0.87     1  comet
        01:48:16        0   1220783         -    0.00    0.87    0.00    0.00    0.87     1  comet
        01:48:16        0   1220814         -    0.87    0.00    0.00    0.00    0.87     1  comet
        01:48:16        0   1307162         -    0.00    0.87    0.00    0.00    0.87     0  python3
        01:48:16        0         -   1307196    0.00    0.87    0.00    0.00    0.87     1  |__python3
        01:48:16        0   1403057         -    0.87    0.00    0.00    0.00    0.87     1  python3

        01:48:15      UID      TGID       TID   cswch/s nvcswch/s  Command
        01:48:16        0         1         -      2.61      0.00  systemd
        01:48:16        0         -         1      2.61      0.00  |__systemd
        01:48:16        0        13         -      6.09      0.00  ksoftirqd/0
        01:48:16        0         -        13      6.09      0.00  |__ksoftirqd/0
        01:48:16        0        14         -     53.91      0.00  rcu_sched
        01:48:16        0         -        14     53.91      0.00  |__rcu_sched
        01:48:16        0        20         -      6.09      0.00  ksoftirqd/1
        01:48:16        0         -        20      6.09      0.00  |__ksoftirqd/1
        01:48:16        0        59         -      0.87      7.83  kswapd0
        01:48:16        0         -        59      0.87      7.83  |__kswapd0
        01:48:16        0       784         -     15.65      0.00  xfsaild/nvme0n1p1
        01:48:16        0         -       784     15.65      0.00  |__xfsaild/nvme0n1p1
        01:48:16        0       829         -     13.91      0.87  systemd-journal
        01:48:16        0         -       829     13.91      0.87  |__systemd-journal
        01:48:16        0      1416         -      2.61      0.00  systemd-homed
        01:48:16        0         -      1416      2.61      0.00  |__systemd-homed
        01:48:16       81      1428         -     10.43      0.00  dbus-broker
        01:48:16       81         -      1428     10.43      0.00  |__dbus-broker
        """

        # =========[监控命令][整机]【显卡】相关 ------------------
        self.cmd_nvidia_smi = "nvidia-smi"
        self.cmd_nvidia_dmon = 'nvidia-smi dmon -s pucmt -o T -c 1'

        # =========[监控命令][进程]【线程数】 ------------------
        self.cmd_process_thread_num = 'pstree -p {pid} | wc -l'  # .format(pid=22222)
        self.cmd_used_thread_num = 'pstree -p | wc -l'
        # =========[监控命令][进程]java-jvm ------------------
        # self.cmd_process_java_jstat = '/usr/local/jdk/bin/jstat -gc {pid}'  # .format(pid=22222)   获取gc full时间次数,内存等信息
        # self.cmd_process_java_jmap = '/usr/local/jdk/bin/jmap -heap {pid}'  # .format(pid=22222)   获取堆内存使用情况，执行时会block住线程
        '''jstat输出示例和说明'''
        '''
        [root@api ~]# jstat -gc 29541
         S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC     YGCT    FGC    FGCT     GCT   
        3584.0 3072.0  0.0   2656.8 54272.0  30379.3   219648.0   102022.2  70424.0 67327.4 8752.0 8106.2    399    3.330   3      0.444    3.774
        S0C、S1C、S0U、S1U：Survivor 0/1区容量（Capacity）和使用量（Used）
        EC、EU：Eden区(伊甸园区)容量和使用量
        OC、OU：年老代容量和使用量
        PC、PU：永久代容量和使用量
        YGC、YGT：年轻代GC次数和GC耗时
        FGC、FGCT：Full GC次数和Full GC耗时
        MC：方法区大小  
        MU：方法区使用大小 
        GCT：GC总耗时
        '''
        self.cmd_jmap_heap = '/usr/local/jdk/bin/jmap -heap {pid}'
        # =========[监控命令][整机]【ps】 ------------------
        self.ps_eo_cmd = "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,pcpu,pmem,etime,time,comm,args"
        self.ps_eo_cmd_2 = "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,rgroup,ruser,etime,time,comm,args"
        # pid在ps命令中的第几列
        # self._cmd_get_pid_col_num_in_ps = "ps -ef|head -1| awk -F ' ' '{for (i=1;i<=NF;i++) {if ($i==\"PID\") {print i}}}'"

        # --------[监控命令][过滤]cpu ------------------
        self.cmd_get_pid_from_pname_1 = "pidof %s|awk '{print $1}'"
        self.cmd_get_pid_from_pname_2 = "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,time,comm,args|grep -i %s|grep -vi 'grep\|" + str(
            PYTHON_FILE_NAME) + "\|vim \|more ' |awk '{print$%s}'|head -1"  # %s,PID在第几列, 一般在第二列
        self.cmd_process_mem_in_proc = "cat /proc/{pname_pid}/status | grep -E 'VmSize|VmRSS|Threads'"  # %s输入进程pid

        # =========[监控命令][进程]【mysql】 ------------------

        # self.cmd_mysql_variables = "mysql -h 127.0.0.1 -u%s -p%s -e \"show variables where Variable_name like '%%max%%' or Variable_name like '%%open%%' or Variable_name like '%%log_%%';\""

        # --------[监控命令][过滤cpu] ------------------
        '''top中过滤出cpu load,返回格式0.10,0.07,0.06'''
        self.cmd_filter_top_cpu_load = "(grep -i 'load average' %(file_name)s|awk 'NR %%2 == 0'|awk -F 'load average' '{IGNORECASE=1}{print $2}'|awk -F ': ' '{print $2}'|awk -F ',' '{print $1,$2,$3}'|awk -F ' ' '{OFS=\",\"}{print $1,$2,$3}')"
        # self.cmd_filter_proc_cpu_idle = "grep 'cpuall' %s |awk -vOFS= '{for(i=1;i<=NF;i+=2)$(i)=FS}1'|awk -vOFS=',' '{$1=$1+0; print $0}' > %s" % (self.file_proc_cpu_org, self.file_all_cpu_used_filter)
        self._cmd_merger_time_to_file = "grep %(time_line_keywords)s %(org_file)s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0'|paste -d ',' - %(merge_file)s > %(output_file)s"
        # self._cmd_get_cpuidle_column_no_in_sar = "sar|grep 'idle'| awk -F ' ' '{for (i=1;i<=NF;i++) {if ($i==\"%idle\") {print i}}}'"

        # self.cmd_filter_sar_cpu_idle = "grep -iv 'time\|cpu)' %s|awk '{print $NF}'|tr '\\n' ' '|tr '%%idle' '\\n'|grep -v '^\s*$'|awk -vOFS=',' '{$1=$1+0;print$0}' |awk 'NR%%3==2'|awk -F',' -vOFS=',' '{for(i=1;i<=NF;i++){$i=100-$i}}{print $0}' > %s" \
        #                                % (self.file_sar_cpu_org, self.file_all_cpu_used_filter)
        ''' --------[监控命令][过滤]内存 ------------------'''
        # self.cmd_filter_free_mem = "grep 'Mem:' %s|awk '{for(i=2;i<=NF;++i) printf $i \",\";printf \"\\n\"}' > %s" % \
        #                            (self.file_memory_org, self.file_memory_filtered)
        # self.cmd_filter_per_port_in_netstat = "grep -E '{port_id}|netstat_time|Recv-Q' %s|grep {port_id} -B 2 > %s" %(self.netstat_info_org,self._per_port_netstat_file)
        # self.cmd_filter_proc_network = "grep %(eth)s %(org_file)s |awk -vOFS=',' '{print $3,$4,$5,$6}' > %(out_file)s" % {
        #     'eth': self.iface_name, 'org_file': self.file_proc_network_org, 'out_file': self.file_filter_network}
        # self.cmd_filter_sar_network = "grep %(eth)s %(org_file)s |awk 'NR%%3 != 0'|awk 'NR%%2==0'|awk '{for(i=1;i<=NF;i++){{OFS=\",\"}if($i~\"%(eth)s\") print $(i+1),$(i+2),$(i+3),$(i+4)}}'"
        '''netstat中过滤出监控端口,多个时返回: 222 555 999 888 '''
        # self.cmd_get_listen_port_in_netstat = "netstat -nap|grep -vi 'estab\|stream\|CLOSE\|DGRAM'|grep -i %(pid_or_pname)s|awk '{print $4}'|awk -F':' '{print $NF}' | tr '\\n' ' '"
        # self.cmd_get_listen_port_in_ss = "ss -pltn|grep -i %(pid_or_pname)s|awk '{print $4}'|awk -F':' '{print $NF}' | tr '\\n' ' '"  # t:tcp p:使用套接字的进程 n:不解析服务如22不会显示成ssh l:listen s:显示套接字 u:udp
        '''过滤出netstat中recv或send-q非0的数据'''
        # self.cmd_filter_netstat_non_0 = "cat %(netstat_file)s|grep -vi 'SEQPACKET\|servers and established'| awk '$3>0 || $2>0 {print $0}'"
        # self.cmd_filter_ss_non_0 = "cat %(ss_file)s|grep -vi 'local address'| awk '$3>0 || $4>0 {print $0}'"
        '''其他过滤命令'''
        # self.cmd_get_im_online_users = "netstat -anp|grep ESTABLISHED|grep '443 ' |wc -l"
        # self.cmd_get_im_online_users = "ss -tunps|grep ':443 '|wc -l" #t:tcp u:udp p:使用套接字的进程 n:不解析服务如22不会显示成ssh e:显示详细的套接字 s:显示套接字

        # self.cmd_top_time = "grep 'top_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s" % (self.file_top_org, self.top_time_file)
        # self.cmd_get_top_available_mem = "grep 'avail Mem' %s|awk 'NR %%2 == 0'|awk '{print($9/1024)}' > %s"%(self.file_top_org,self.top_available_mem_file)
        # self.overall_cpu_idle_time_cmd = "grep 'sar_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s"%(self.file_sar_cpu_org,self.cpu_idle_time_file)
        # self.filter_proc_cpu_time_cmd = "grep 'proc_cpu_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s"%(self.file_proc_cpu_org,self.proc_cpu_time_file),
        # self._filter_per_sar_cpu_idle_in_sar_cmd = "grep ' {core_id} ' %s|awk 'NR%%3!=0' |awk 'NR%%2==0'|awk '{{print $NF}}' > %s"%(self.file_sar_cpu_org,self._per_cpu_idle_file)
        # self.filter_time_in_sar_cpu_cmd = "grep 'sar_cpu_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s"%(self.file_sar_cpu_org,self.sar_cpu_time_file),
        # self.cpu_cores_cmd = "lscpu|grep CPU |grep -v ' CPU'|grep -v 'CPU '|awk '{print$2}'"
        # self.filter_proc_network_time_cmd = "grep 'proc_network_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s" %(self.file_proc_network_org,self.proc_network_time_file)
        # 网络情况
        # self.sar_network_time_cmd = "grep 'sar_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s"%(self.file_sar_network_org,self.sar_network_time_file),
        # self.netstat_time_cmd = "grep 'netstat_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s"%(self.netstat_info_org,self.netstat_time_file),
        # self.netstat_rq_sum_cmd = "grep 'recv_q_buffer_sum' %s |awk '{print $2}' > %s"%(self.netstat_info_org,self.netstat_rq_sum_file),
        # self.netstat_sq_sum_cmd = "grep 'send_q_buffer_sum' %s |awk '{print $2}' > %s"%(self.netstat_info_org,self.netstat_sq_sum_file),
        # self.netstat_rq_port_sum_cmd = "grep 'recv_q_non' %s |awk '{print $2}' > %s"%(self.netstat_info_org,self.netstat_rq_port_sum_file),
        # self.netstat_sq_port_sum_cmd = "grep 'send_q_non' %s |awk '{print $2}' > %s"%(self.netstat_info_org,self.netstat_sq_port_sum_file)
        # self.cmd_filter_per_port_netstat_rs_q = "grep -i ':%(port_id)s '|grep -i 'listen'|head -1|awk -F' ' -vOFS=',' '{IGNORECASE=1;{print $2,$3}}'|awk 'END {print}'"
        # self.filter_cpu_all_idle_in_top_cmd = "grep \"%%Cpu(s)\" %s|awk 'NR %%2 == 0'|awk -F ',' '{print $4}'|awk -F ' ' '{print $1}' > %s" % (self.file_top_org, self.file_all_cpu_used_filter)
        # self.filter_cpu_all_idle_in_sar_cmd = "grep all %s|awk 'NR%%3!=0' |awk 'NR%%2==0'|awk '{print $NF}' > %s" % (self.file_sar_cpu_org, self.file_all_cpu_used_filter)

        # self.filter_cpu_all_idle_in_proc_cmd = "grep 'cpu_all' %s |awk -F 'cpu_all:' '{print $1}' > %s" % (self.file_proc_cpu_org, self.file_all_cpu_used_filter)
        # self._filter_per_cpu_idle_in_proc_cmd = "grep 'cpu{core_id}' %s|awk -F 'cpu{core_id}:' '{{print $1}}' > %s" %(self.file_proc_cpu_org,self._per_cpu_idle_file)

        # self.filter_sar_cpu_time_cmd = "grep 'sar_time' %s|awk '{for(i=1;i<=NF;i++){if($i~\":\") print $i}}'|awk 'NR %%2 == 0' > %s"%(self.file_sar_cpu_org,self.cpu_idle_time_file)

        # self._cmd_filter_per_pname_cpu_in_top = "grep '{pname}' %s|awk 'NR %%2 == 0'|awk '{{print %s}}'> %s" % (self.file_top_org,self.top_CPU_column_no, self._per_pname_cpu_usage_file)
        # self._cmd_filter_per_pname_res_in_top = "grep '{pname}' %s|awk 'NR %%2 == 0' |awk '{{{{print $6}}'|awk '{{for(i=1;i<=NF;i++){{if($i~\"g\"){{print$i*1024}} else {{print$i/1024}}}}}}}}' > %s" %(self.file_top_org,self._per_pname_res_top_file)
        # self._is_top_have_pname_res_cmd = "grep -i 'pid' %s|grep -i 'command' |grep -i 'res'" % self.file_top_org
        # self._cmd_filter_per_pname_VmRSS_in_proc = "grep 'VmRSS' %s|awk '{{print $2}}' > %s" % (self._file_proc_pid_mem_org,self._per_proc_pid_mem_file)
        # self._cmd_filter_proc_pid_mem_time_in_proc ="grep 'proc_mem_time' %s|awk '{{for(i=1;i<=NF;i++){{if($i~\":\") print $i}}}}'|awk 'NR %%2 == 0' > %s" %(self._file_proc_pid_mem_org,self._proc_pid_mem_time_file)

    '''chfshan,获取cpu load值,优先从/proc/loadavg取,返回字典'''

    def get_cpu_load_info(self, need_write_to_file=False):
        """获取cpu_load值,获取渠道uptime
        :param need_write_to_file: [bool] 是否写文件; Ture,写入org_file_uptime_cpu_load.txt
        :return: [dict], 内容如下:
            {'cpu_load_1':5.59,'cpu_load_5':3.45,'cpu_load_10':1.35}
        """
        return_result = collections.OrderedDict()
        time_str = 'cpu_load_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str.split('#')[1])})
        if 'win32' in sys.platform:
            return return_result

        with open('/proc/loadavg', 'r') as f:  # 0.39 0.34 0.63 3/832 13446
            datas = f.readlines()
            for line in datas:
                _data = line.split()
                if len(_data) < 3:
                    continue
                return_result.update({'cpu_load_1': float(_data[0])})
                return_result.update({'cpu_load_5': float(_data[1])})
                return_result.update({'cpu_load_15': float(_data[2])})
        f.close()

        if len(return_result) < 3:
            cmd_result = str(lo_cli.run_cmd(self.cmd_cpu_load_avg_uptime))
            tem = cmd_result.split()
            if len(tem) < 3:
                return return_result
            return_result.update({'cpu_load_1': float(tem[0])})
            return_result.update({'cpu_load_5': float(tem[1])})
            return_result.update({'cpu_load_15': float(tem[2])})

        if need_write_to_file:
            title_data = ",".join(map(str, return_result.keys())) + '\n'
            values_data = ",".join(map(str, return_result.values())) + '\n'
            self._h_file_cpu_load_filter = _write_to_file(self.record_file_path + 'filtered_load_average_realtime.csv',
                                                         data=title_data + values_data, as_append=True,
                                                         file_handle=self._h_file_cpu_load_filter)

        return return_result

    def get_disk_storage_info(self, need_write_to_file=False):
        return_result = collections.OrderedDict()
        time_str = 'df_Thm_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        if 'win32' in sys.platform:
            return return_result
        result = lo_cli.run_cmd(self.cmd_disk_storage, need_run_with_sudo=True)
        for no, _data in enumerate(result.split('\n')):
            if no > 50:
                break
            try:
                _available_index = 4
                _line_data = _data.split()
                if 'vailable' in _data:
                    _available_index = _line_data.index('Available')
                return_result.update({str(_line_data[-1][:100]): _line_data[_available_index]})
            except:
                pass
        if need_write_to_file:
            _write_to_file(self.record_file_path + 'org_file_df.txt', data=time_str + '\n' + str(result) + '\n',
                          as_cover=False, as_append=True)
        return return_result

    '''chfshan,获取cpu的使用率,获取渠道:/proc/stat，若失败从[sar cpu]获取,注意sar cpu存在每个cpu使用率超过100%问题'''

    def get_cpu_info(self, cpu_avg_interval=1, need_write_to_file=False):
        """ 获取整机、每个CPU的使用率, 获取渠道:/proc/stat，若失败从[sar cpu]获取
        :param need_write_to_file: [bool] 获取的结果是否写文件, True: 写入 org_file_proc_cpu.txt 或  org_file_sar_cpu.txt
            写入文件格式:
                proc_cpu_time#20230101 17:41:37
                cpuall 32.3; cpu0 23.0; cpu1 100.0; cpu2 3.0; cpu3 4.0;
        :param need_run_with_thread:[bool] 作为1个线程启动,会每隔interval时间获取一次，建议配合need_write_to_file=True一起使用起监控作用
        :param thread_get_data_interval: [bool] 线程获取数据的时间间隔 None:从self.record_interval取
        :return: [dict],示例如下:
            {'time':'20230106 10:02:59','cpuall':99,'cpu0':29,'cpu1':89}
        :其他说明: /proc/stat命令输出示例
            [hadoop@node031 ~]$ cat /proc/stat
            cpu  428285167 3121 324125720 2936765262 54942482 0 10855800 6885788 0 0
            cpu0 107910774 818 81598746 735132121 13547049 0 2013385 1743890 0 0
            cpu1 106141224 621 80125854 731988928 14054030 0 5486026 1716306 0 0
            cpu2 106501106 895 80912247 734774937 13769044 0 2671780 1704928 0 0
            cpu3 107732062 785 81488872 734869275 13572358 0 684608 1720663 0 0
            intr 15474248078 16 10 0 0 16498 0 0 0 0 1 0 34 86 0 0 9426894 0 0 0 0 0 0 0 0 0 32010457 0 0 1 44932803 0 2017389566 122490 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
            ctxt 99201334758
            btime 1664353287
            processes 897072053
            procs_running 6
            procs_blocked 0
            softirq 15498361391 2 4174145744 441032 2601041198 0 0 7586067 3028637879 0 1391542173

            /proc/stat中对应的每一位的含义:
            (cpu  428285167 3121 324125720 2936765262 54942482 0 10855800 6885788 0 0 )
            cpu指标	含义	时间单位	备注
            user	用户态时间	jiffies	一般/高优先级，仅统计nice<=0
            nice	nice用户态时间	jiffies	低优先级，仅统计nice>0
            system	内核态时间	jiffies
            idle	空闲时间	    jiffies	不包含IO等待时间
            iowait	I/O等待时间	jiffies	硬盘IO等待时间
            irq	    硬中断时间	jiffies
            softirq	软中断时间	jiffies
            steal	被盗时间	    jiffies	虚拟化环境中运行其他操作系统上花费的时间（since Linux 2.6.11）
            guest	来宾时间	    jiffies	操作系统运行虚拟CPU花费的时间(since Linux 2.6.24)
            guest_nice	nice来宾时间	jiffies	运行一个带nice值的guest花费的时间(since Linux 2.6.33)

        """
        result = -1
        try:
            # 优先从proc获取
            result = self._get_cpu_info_from_proc(cpu_avg_interval=cpu_avg_interval,
                                                  need_write_to_file=need_write_to_file)
            # logger.critical(result)

            if need_write_to_file:
                title_data = ",".join(map(str, result.keys())) + '\n'
                values_data = ",".join(map(str, result.values())) + '\n'
                self._h_file_cpu_filter = _write_to_file(self.record_file_path + 'filtered_cpu_used_realtime.csv',
                                                        data=title_data + values_data, as_append=True,
                                                        file_handle=self._h_file_cpu_filter)
            self.cpu_data = result
            # logger.critical(('self.cpu_data in cpu', self.cpu_data,result))
        except Exception:
            logger.warning('fail=%s' % str(traceback.format_exc()))
        return result

    def get_cpu_times_static_info(self):
        self.cpu_times_static_data = lo_cli.get_cpu_static_info()

    '''chfshan,获取每秒的pps和流量等网络信息,优先/proc/net/dev取,返回字典,流量单位bytes'''
    '''[2022.8.30] windows add by chfhsan,获取本机的网络情况,流量单位KB'''

    def get_bindwidth_info(self, need_write_to_file=False, interval='auto'):
        """获取每秒网络pps、带宽等情况,获取渠道'/proc/net/dev'
        :param need_write_to_file: [bool] 获取的结果是否写文件, True: 写入org_file_proc_network.txt
            写入文件内容示例如下:
                proc_network_time#20230106 12:10:59
                # Get current record
                # Inter-|   Receive                                                |  Transmit
                # face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
                # em1: 17482  141589    0  858    0     0          0    107916   1466      17    0    0    0     0       0          0
                # lo: 110161  275376    0    0    0     0          0         0 166571  275376    0    0    0     0       0          0
        :return:[dict], 示例如下:
            {'time':'20230106 10:02:59',iface:'em1',
            'em1_rxpck/s':1555,'em1_txpck/s','em1_rxkB/s':1555,'em1_txkB/s':1555,'em1_txerr/s':1555,'em1_rxerr/s':1555,'em1_rxdrop/s':1555,'em1_txdrop/s':1555,
            'lo_rxpck/s':1555,'lo_txpck/s','lo_rxkB/s':1555,'lo_txkB/s':1555,'lo_txerr/s':1555,'lo_rxerr/s':1555,'lo_rxdrop/s':1555,'lo_txdrop/s':1555}
        :其他说明: '/proc/net/dev'命令输出示例
            # Get current record
            # Inter-|   Receive                                                |  Transmit
            # face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
            # em1: 17482  141589    0  858    0     0          0    107916   1466      17    0    0    0     0       0          0
            # lo: 110161  275376    0    0    0     0          0         0 166571  275376    0    0    0     0       0          0
        """
        return_result = collections.OrderedDict()
        time_str = 'bindwidth_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str.split('#')[1])})
        if 'linux' in sys.platform:
            return_result = self._get_bindwidth_info_from_proc(need_one_time_org_data=False, process_pid='', process_display_name_flag='', interval=interval)
        elif 'win32' in sys.platform:
            self._psutil = import_third_module(module_name="psutil",
                                               reason='gather client sys data, if failed, only monitor no sys data, no other affect',
                                               _need_print_log=False)

            _s1 = self._psutil.net_io_counters(pernic=True)
            time.sleep(1)
            _s2 = self._psutil.net_io_counters(pernic=True)
            for iface_name in _s2.keys():
                # _iface_name_flag = iface_name.decode(locale.getpreferredencoding())

                _iface_data = round((_s2[iface_name].bytes_recv - _s1[iface_name].bytes_recv) / 1024, 3)
                return_result.update({iface_name + '_rxkB/s': _iface_data})
                _iface_data = round((_s2[iface_name].bytes_sent - _s1[iface_name].bytes_sent) / 1024, 3)
                return_result.update({iface_name + '_txkB/s': _iface_data})
                _iface_data = _s2[iface_name].packets_recv - _s1[iface_name].packets_recv
                return_result.update({iface_name + '_rxpck': _iface_data})
                _iface_data = _s2[iface_name].packets_sent - _s1[iface_name].packets_sent
                return_result.update({iface_name + '_txpck': _iface_data})

        if need_write_to_file:
            title_data = ",".join(map(str, return_result.keys())) + '\n'
            values_data = ",".join(map(str, return_result.values())) + '\n'
            self._h_file_network_filter = _write_to_file(self.record_file_path + 'filtered_network_file_realtime.csv',
                                                        data=title_data + values_data, as_append=True,
                                                        file_handle=self._h_file_network_filter)

        self._bindwidth_data = return_result

        return return_result

    '''chfshan,获取内存信息,优先从/proc/meminfo取,返回字典,单位KB'''

    def get_memory_info(self, get_in_remote=False, remote_server_client=None, need_write_to_file=False):
        """
        :param need_write_to_file: [bool] 获取的结果是否写文件, True: 写入org_file_free_m.txt
           写入文件内容示例如下:
               proc_memory_time#20230106 12:10:59
               命令输出结果,见其他说明
        :return:[dict], 示例如下:
           {'time':'20230106 10:02:59','memtotal':112322423,'memfree':54645,'memavailable':324234,'buffers':324,'cached':34234,'swapcached':32432,'active':343}

        :其他说明:  /proc/meminfo命令输出示例
           [hadoop@node031 ~]$ cat /proc/meminfo
           MemTotal:       32940244 kB     #所有内存(RAM)大小,减去预留空间和内核的大小。
           MemFree:         7919804 kB     #完全没有用到的物理内存，lowFree+highFree。
           MemAvailable:   12199912 kB     # MemFree只是尚未分配的内存，并不是所有可用的内存。有些已经分配掉的内存是可以回收再分配的。比如cache/buffer、slab都有一部分是可以回收的，这部分可回收的内存加上MemFree才是系统可用的内存，即MemAvailable(不精确)。
           Buffers:          182596 kB     #用来给块设备做缓存的内存，(文件系统的 metadata、pages)。包含已使用、未使用和可以回收的，块设备(block device)所占用的特殊file-backed pages，包括：直接读写块设备，以及文件系统元数据(metadata)比如superblock使用的缓存页。
           Cached:          4398424 kB     #分配给文件缓冲区的内存,例如vi一个文件，就会将未保存的内容写到该缓冲区。用户进程的内存页分为两种：file-backed pages（与文件对应的内存页），和anonymous pages（匿名页），比如进程的代码、映射的文件都是file-backed，而进程的堆、栈都是不与文件相对应的、就属于匿名页。file-backed pages在内存不足的时候可以直接写回对应的硬盘文件里，称为page-out，不需要用到交换区(swap)；而anonymous pages在内存不足时就只能写到硬盘上的交换区(swap)里，称为swap-out。
           SwapCached:            0 kB     #被高速缓冲存储用的交换空间（硬盘的swap）的大小,包含的是被确定要swapping换页，但是尚未写入物理交换区的匿名内存页。那些匿名内存页，比如用户进程malloc申请的内存页是没有关联任何文件的，如果发生swapping换页，这类内存会被写入到交换区。
           Active:         21412088 kB     #经常使用的高速缓冲存储器页面文件大小,active包含active anon和active file
           Inactive:        2882680 kB     #不经常使用的高速缓冲存储器文件大小,inactive包含inactive anon和inactive file。
           Active(anon):   19728148 kB     #活跃的匿名内存（进程中堆上分配的内存,是用malloc分配的内存），即匿名页，用户进程的内存页分为两种：与文件关联的内存页(比如程序文件,数据文件对应的内存页)和与内存无关的内存页（比如进程的堆栈，用malloc申请的内存），前者称为file pages或mapped pages,后者称为匿名页。
           Inactive(anon):    80836 kB     #见上。不活跃的匿名内存
           Active(file):    1683940 kB     #见上。活跃的文件使用内存
           Inactive(file):  2801844 kB     #见上。不活跃的文件使用内存
           Unevictable:       87012 kB     #不能被释放的内存页
           Mlocked:           87012 kB     #系统调用 mlock 家族允许程序在物理内存上锁住它的部分或全部地址空间。这将阻止Linux 将这个内存页调度到交换空间（swap space），即使该程序已有一段时间没有访问这段空间
           SwapTotal:             0 kB     #交换空间总内存(swap分区在物理内存不够的情况下，把硬盘空间的一部分释放出来，以供当前程序使用)。
           SwapFree:              0 kB     #当交换空间空闲内存
           Dirty:               944 kB     #等待被写回到磁盘的(需要写入磁盘的内存页的大小)
           Writeback:             0 kB     #正在被写回的内存区的大小。
           AnonPages:      19800792 kB     #未映射页的内存的大小。Anonymous pages(匿名页)数量 + AnonHugePages(透明大页)数量。
           Mapped:            88472 kB     #设备和文件等映射的大小。正被用户进程关联的file-backed pages。
           Shmem:             91324 kB     #已经被分配的共享内存大小.tmpfs所使用的内存.即利用物理内存来提供RAM磁盘的功能
           Slab:             351420 kB     #内核数据结构slab的大小。slab是linux内核的一种内存分配器。
           SReclaimable:     259036 kB     #可回收的slab的大小。
           SUnreclaim:        92384 kB     #不可回收的slab的大小。
           KernelStack:       49872 kB     #内核消耗的内存
           PageTables:        61996 kB     #管理内存分页的索引表的大小。Page Table的用途是翻译虚拟地址和物理地址，它是会动态变化的，要从MemTotal中消耗内存。
           NFS_Unstable:          0 kB     #不稳定页表的大小。发给NFS server但尚未写入硬盘的缓存页。
           Bounce:                0 kB     #在低端内存中分配一个临时buffer作为跳转，把位于高端内存的缓存数据复制到此处消耗的内存
           WritebackTmp:          0 kB     #FUSE用于临时写回缓冲区的内存
           CommitLimit:    16470120 kB     #系统实际可分配内存
           Committed_AS:   24598004 kB     #系统当前已分配的内存
           VmallocTotal:   34359738367 kB  #预留的虚拟内存总量，Vmalloc内存区的大小.可分配的虚拟内存总计.
           VmallocUsed:           0 kB     #已经被使用的虚拟内存
           VmallocChunk:          0 kB     #可分配的最大的逻辑连续的虚拟内存，vmalloc区可用的连续最大快的大小.通过vmalloc可分配的虚拟地址连续的最大内存
           HardwareCorrupted:     0 kB     #删除掉的内存页的总大小(当系统检测到内存的硬件故障时)
           AnonHugePages:         0 kB     #匿名 HugePages 数量
           ShmemHugePages:        0 kB     #表示用于shared memory或tmpfs的透明大页。
           ShmemPmdMapped:        0 kB     #表示用于用户态shared memory映射的透明大页。
           HugePages_Total:       0        #预留HugePages的总个数
           HugePages_Free:        0        #池中尚未分配的 HugePages 数量
           HugePages_Rsvd:        0        #表示池中已经被应用程序分配但尚未使用的 HugePages 数量
           HugePages_Surp:        0        #这个值得意思是当开始配置了20个大页，现在修改配置为16，那么这个参数就会显示为4，一般不修改配置，这个值都是0
           Hugepagesize:       2048 kB     #每个大页的大小
           DirectMap4k:     2099040 kB     #映射TLB为4kB的内存数量
           DirectMap2M:    31455232 kB
           DirectMap1G:     2097152 kB

           [root@chfshan_performance_for_sipproxy11 ~]# free -m
           total        used        free      shared  buff/cache   available
           Mem:           7820        1368         144         384        6308        5765
           Swap:             0           0           0

           used是已经使用的物理内存（不包括buff/cache）;
           free是指可用的物理内存，目前尚未分配，可以使用的大小，
           系统真正使用内存 =【Mem.total-Mem.free】 = 【Mem.used+Mem.buff/cache】;
           shared是指被共享使用的内存大小;
           buffer/cache是指系统分配的数量，注意这是总量，包含已使用、未使用和可以回收的buffer/cache；
           avaible是指可以被应用使用的内存大小 = 【Mem.free + 可回收的buffer/cache】，
           可回收的buffer/cache = 【Mem.avaible - Mem.free】
           正使用的buffer/cache = 【Mem.buffer/cache - 可回收的buffer/cache】；

       """
        return_result = collections.OrderedDict()
        # return_result = dict()

        time_str = '/proc/meminfo_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str.split('#')[1])})

        try:
            proc_meminfo_data = None
            if get_in_remote:
                proc_meminfo_data = remote_server_client.run_cmd(cmd='cat /proc/meminfo', need_run_with_sudo=True)

            return_result = lo_cli.get_memory_usage(proc_meminfo_data=proc_meminfo_data)
        except:
            pass

        if need_write_to_file:
            _write_to_file(self.record_file_path + 'org_file_memory.txt',
                          data=time_str + '\n' + '\n'.join(return_result) + '\n', as_append=True)

            filtered_data = ','.join(map(str, return_result.keys())) + '\n' + ','.join(
                map(str, return_result.values())) + '\n'

            self._h_file_mem_filter = _write_to_file(self.record_file_path + 'filtered_memory_realtime.csv',
                                                    data=filtered_data, as_append=True,
                                                    file_handle=self._h_file_mem_filter)

        return return_result

    '''chfshan,获取整机端口拥堵情况,每个进程的send-Q,recv-Q结果,优先ss -tuanps,返回字典'''

    def get_ss_info(self, process_port_id=443, need_write_to_file=True):

        """获取整机拥堵情况,每个进程的send-Q,recv-Q结果,优先ss -tuanps,返回字典
        :param need_write_to_file: [bool] 获取的结果是否写文件, True: 写入org_file_netstat.txt
            写入文件内容示例如下:
                ss_time#20230106 12:10:59
                命令输出结果,见[其他说明]
                返回的单位是B
        :return:[dict], self.pname=[coment,job]时,示例如下:
            {'time':'20230106 10:02:59','Recv_Q_sum/KB':112322423,'Recv_Q_non_0_sum/No':54645,'Send_Q_non_0_sum/No':324234,'Recv-Q_job3030/KB':324,'Send-Q_job3030/KB':34234,
            'connected_users_in_443':32432,'tcp_ESTAB_state_no':32432,'tcp_LISTEN_state_no':343,'tcp_TIME-WAIT_state_no':343}

        :其他说明:  ss -tuanps命令输出示例
            ~# ss -tuanps
            Total: 285 (kernel 494)
            TCP:   88 (estab 44, closed 15, orphaned 0, synrecv 0, timewait 15/0), ports 0

            Transport Total     IP        IPv6
            *	  494       -         -
            RAW	  0         0         0
            UDP	  5         5         0
            TCP	  73        59        14
            INET	  78        64        14
            FRAG	  0         0         0

            Netid  State      Recv-Q Send-Q     Local Address:Port        Peer Address:Port
            udp    ESTAB      0      0          192.168.126.240:38787     192.168.126.1:53     users:(("gs_cpe",pid=7659,fd=10))
            udp    UNCONN     0      0          0.0.0.0:6060              0.0.0.0:*            users:(("zero_config",pid=7437,fd=8))
            udp    UNCONN     0      0          0.0.0.0:6066              0.0.0.0:*            users:(("python",pid=6906,fd=3))
            udp    UNCONN     0      0          0.0.0.0:38896             0.0.0.0:*            users:(("gs_cpe",pid=7659,fd=9))
            udp    UNCONN     0      0          0.0.0.0:54320             0.0.0.0:*            users:(("gs_cpe",pid=7659,fd=8))
            tcp    ESTAB      0      0          127.0.0.1:32768           127.0.0.1:7171       users:(("business",pid=8378,fd=16))
            tcp    TIME-WAIT  0      0          127.0.0.1:34100           127.0.0.1:3510
            tcp    ESTAB      0      0          127.0.0.1:7171            127.0.0.1:49448
        """
        result = collections.OrderedDict()
        time_str = 'ss_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        result.update({'time': str(time_str.split('#')[1])})

        if 'win32' in sys.platform:
            return result
        self._h_file_ss_org_file = None
        _ss_result = self._analysis_ss_data()
        result.update(_ss_result)
        if need_write_to_file:
            title_data = ",".join(map(str, result.keys())) + '\n'
            values_data = ",".join(map(str, result.values())) + '\n'

            self._h_file_ss_filter = _write_to_file(self.record_file_path + 'filtered_netstat_realtime.csv',
                                                   title_data + values_data, as_append=True,
                                                   file_handle=self._h_file_ss_filter)

        return result

    '''chfshan,获取进程的cpu使用率,某个进程名对应的进程有多个时，会取ps中靠前的24个相加'''

    def get_process_cpu_info(self, need_write_to_file=True, interval='auto'):

        result = collections.OrderedDict()
        if len(self.pname) == 0:
            return result
        time_str = 'process_cpu_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        result.update({'time': str(time_str.split('#')[1])})

        _need_monitor_pname_pid_num = 60
        _pid_all_list = [','.join(_pid_list[0:_need_monitor_pname_pid_num]) for key, _pid_list in
                         self.pid_per_pname_dict.items()]
        _pid_all_list = ','.join(_pid_all_list).split(',')
        cpu_usage = lo_cli.get_process_cpu_usage(process_pid_list=_pid_all_list, interval=interval)

        for pname in self.pname:
            if not self.pid_per_pname_dict.get(pname):
                continue
            if len(self.pid_per_pname_dict.get(pname)) < 1:
                continue
            pname_cpu_usage = 0
            for no, _pid in enumerate(self.pid_per_pname_dict[pname][0:_need_monitor_pname_pid_num]):
                try:
                    pname_cpu_usage = pname_cpu_usage + float(cpu_usage[_pid])
                    if no < 6:
                        result.update(
                            {str(self._display_pname_per_pid[_pid]) + '_' + str(_pid): float(cpu_usage[_pid])})
                except:
                    logger.info((pname, _pid, cpu_usage, _pid_all_list, traceback.format_exc()))
                    continue

            result.update({str(pname) + '_all': pname_cpu_usage})
            # except:
            #     logger.info((pname,_pid,cpu_usage,_pid_all_list,traceback.format_exc()))

        if need_write_to_file:
            title_data = ",".join(map(str, result.keys())) + '\n'
            values_data = ",".join(map(str, result.values())) + '\n'

            self._h_file_process_cpu_filter = _write_to_file(
                self.record_file_path + 'filtered_process_cpu_info_realtime.csv', data=title_data + values_data,
                as_append=True, file_handle=self._h_file_process_cpu_filter)
        # logger.critical(('cpu',result))
        return result

    '''[2023.8.30]chfshan 进程的网络链路状态'''

    def get_process_sockstat_from_proc(self):
        return_result = {}
        for _pname, _pids in self.pid_per_pname_dict.items():
            _pids = _pids[0:3]
            for _pid in _pids:
                if not _pid:
                    continue
                _key_name_flag = self._display_pname_per_pid[str(_pid)] + '_' + str(_pid)
                _pid_result = self._get_socketstat_from_proc(process_pid=_pid, process_display_name_flag=_key_name_flag)
                if _pid_result:
                    return_result.update(_pid_result)
        return return_result

    '''[2023.8.30]chfshan 进程的文件描述符数量'''

    def get_process_fd_num(self):

        return_result = {}
        for _pname, _pids in self.pid_per_pname_dict.items():
            _pids = _pids[0:3]
            for _pid in _pids:
                try:
                    if not _pid:
                        continue
                    _num = lo_cli.run_cmd('ls /proc/%s/fd|wc -l' % str(_pid))

                    if int(_num) >= 0:
                        return_result.update({str(_pname) + '_' + str(_pid): int(_num)})
                except:
                    pass
        return return_result

    '''[2023.8.30]chfshan,带宽单位bytes 进程的带宽情况/proc/pid/net/dev'''

    def get_process_bindwidth_info_from_proc(self):
        return_result = {}
        for _pname, _pids in self.pid_per_pname_dict.items():
            _pids = _pids[0:3]
            for _pid in _pids:
                if not _pid:
                    continue
                _key_name_flag = self._display_pname_per_pid[str(_pid)]
                _pid_result = self._get_bindwidth_info_from_proc(need_one_time_org_data=True, process_pid=_pid, process_display_name_flag=_key_name_flag)
                if _pid_result:
                    return_result.update(_pid_result)
        logger.debug(return_result)
        return return_result

    '''chfshan,获取进程的内存和进程pid,某个进程名存在多个进程,mem-全部相加,线程数-取1个进程的pidof或ps中的第一个进程'''

    def get_process_mem_and_thread_info(self, need_write_to_file=False):
        """

        :param need_write_to_file:
        :return:
        """

        if len(self.pname) == 0:
            return ({}, {})
        _mem, _thread = self._get_process_mem_and_thread_from_proc(need_write_to_file=need_write_to_file)
        if need_write_to_file:
            title_data = ",".join(map(str, _mem.keys())) + '\n'
            values_data = ",".join(map(str, _mem.values())) + '\n'
            _write_to_file(self.record_file_path + 'filtered_process_mem_info_realtime.csv',
                          data=title_data + values_data, as_append=True)

        return (_mem, _thread)

    '''[2023]chfshan,根据特定的应用程序特殊支持,间隔时间特殊控制 目前支持java/kamailio/redis/gwn/mysql/mcu'''

    def get_project_app_info(self, app_interval=None, db_interval=60, need_write_to_file=True):

        result = collections.OrderedDict()

        if app_interval and self.last_data.get('application') and time.time() - (app_interval - 0.3) < int(
                self.last_data['application'].get('time')):
            return result

        if not self.last_data.get('application'):
            self.last_data.update({'application': {'time': time.time(), 'data': {}}})

        # result.update(self._get_kamailio_shmmem())
        if str(self.pname).lower().find('sshd') != -1:
            result.update(self._get_ucmrc_info())
        if str(self.pname).lower().find('asterisk') != -1:
            pass
        if str(self.pname).lower().find('mcu') != -1:
            self._get_mcu_nvidia_info()
            self._get_mcu_nvidia_dmon_info()
        if str(self.client_params.server_type).lower().find('gwn') != -1:
            result.update(self.get_establish_connections(port_id=10014, module_name='gwn_gateway_online_users'))
            if str(self.pname).lower().find('redis') != -1:
                result.update(self._get_gwn_redis_data(interval=db_interval))

        # result.update(self.get_mysql_data(mysql_username=mysql_username, mysql_pwd=mysql_pwd, interval=db_interval))

        result.update(self._get_clouducm_rtpEngine_info())
        # self.last_data.update({'application': {'time': time.time(), }})


        if need_write_to_file:
            title_data = ",".join(map(str, result.keys())) + '\n'
            values_data = ",".join(map(str, result.values())) + '\n'
            self._h_file_app_filter = _write_to_file(self.record_file_path + 'filtered_application_info_realtime.csv',
                                                    title_data + '\n' + values_data, as_append=True,
                                                    file_handle=self._h_file_app_filter)

        # del title_data, values_data
        # gc.collect()

        # logger.info(result)
        return result

    def _get_io_info_from_proc(self, interval=5, get_in_remote=False, remote_server_client=None):
        """
        :param get_in_remote:
        :return: [dict]

        {'time','20231102 18:17:46','vda_riops',0.0,'vda_wiops',0.0,'vda_util',0.0,'vda1_riops',0.0,'vda1_wiops',0.0,
        'vda1_util',0.0,'vda2_riops',0.0,'vda2_wiops',0.0,'vda2_util',0.0,'vda3_riops',0.0,
        'vda3_wiops',0.0,'vda3_util',0.0,'sr0_riops',0.0,'sr0_wiops',0.0,'sr0_util',0.0,'dm-0_riops',0.0,
        'dm-0_wiops',0.0,'dm-0_util',0.0,'dm-1_riops',0.0,'dm-1_wiops',0.0,'dm-1_util',0.0}
        """

        return_result = collections.OrderedDict()
        time_str = 'io_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str.split('#')[1])})

        _pre_io_data = None
        _after_io_data = None
        _cmd = '/proc/diskstats'
        if get_in_remote and remote_server_client:
            cmd = 'cat ' + _cmd + " ; sleep " + interval + " ; echo '###split###' ; " + 'cat ' + _cmd
            _data = remote_server_client.run_cmd(cmd=cmd, need_run_with_sudo=True)
            if remote_server_client.error_code != ERROR_CODE_SUCCESS:
                return return_result
            _data = str(_data).split('###split###')
            # logger.critical((_data[0],_data[-1]))
            _pre_io_data = _data[0]
            _after_io_data = _data[-1]
        global _len, _disk_tuple
        _disk_tuple = namedtuple('Disk',
                                 'major_number minor_number device_name read_count read_merged_count read_sections time_spent_reading write_count write_merged_count write_sections time_spent_write io_requests time_spent_doing_io weighted_time_spent_doing_do')
        _len = 14
        _disk_list = []

        def _get_disk_info(io_data=None):
            global _len, _disk_tuple

            _result_data = []
            try:
                _h_file = None
                if not io_data:
                    _h_file = open(_cmd, 'r')
                    io_data = _h_file.readlines()
                else:
                    io_data = io_data.split('\n')

                for _line in io_data:
                    if not _line:
                        continue
                    __data = _line.split()
                    # logger.critical(__data)
                    if _len < len(__data):
                        _disk_tuple = namedtuple('_disk_tuple',
                                                 'major_number minor_number \
                                                 device_name read_count \
                                                 read_merged_count read_sections time_spent_reading \
                                                 write_count write_merged_count write_sections time_spent_write io_requests \
                                                 time_spent_doing_io weighted_time_spent_doing_do ' + ' '.join('err_' + str(i) for i in range(len(__data) - _len)))
                        _len = len(__data)
                    _result_data.append(_disk_tuple(*__data))
                _h_file.close()
            except:
                pass
            return _result_data

        def _calculate_value_by_rate(after_value, before_value, rate):
            """
            公式为(float(int(after_value) - int(before_value)) / rate
            """
            _data = round(float(int(after_value) - int(before_value)) / rate, 2)
            # logger.info(('deal', after_value, before_value, rate, _data))
            _res = max(0, _data)
            return _res

        try:

            _st = time.time()
            _before = _get_disk_info(io_data=_pre_io_data)
            if not get_in_remote:
                time_sleep(interval - (time.time() - _st))
            _t2 = time.time()
            _after = _get_disk_info(io_data=_after_io_data)
            _ts = interval
            for (disk1), (disk2) in zip(_before, _after):
                # 读写次数/s
                return_result.update({str(disk1.device_name) + '_riops': _calculate_value_by_rate(disk2.read_count, disk1.read_count, _ts)})
                return_result.update({str(disk1.device_name) + '_wiops': _calculate_value_by_rate(disk2.write_count, disk1.write_count, _ts)})
                # 繁忙率
                return_result.update({str(disk1.device_name) + '_util': _calculate_value_by_rate(disk2.time_spent_doing_io, disk1.time_spent_doing_io, _ts * 10)})
                # 吞吐量
                return_result.update({str(disk1.device_name) + '_r': _calculate_value_by_rate(disk2.read_sections, disk1.read_sections, _ts * 2)})
                return_result.update({str(disk1.device_name) + '_w': _calculate_value_by_rate(disk2.write_sections, disk1.write_sections, _ts * 2)})
                # 单次吞吐量
                return_result.update({str(disk1.device_name) + '_rpt': _calculate_value_by_rate(disk2.read_sections, disk1.read_sections, max(1, 2 * (int(disk2.read_count) - int(disk1.read_count))))})
                return_result.update({str(disk1.device_name) + '_wpt': _calculate_value_by_rate(disk2.write_sections, disk1.write_sections, max(1, 2 * (int(disk2.write_count) - int(disk1.write_count))))})
                # 用于磁盘读/写的时间(ms)
                return_result.update({str(disk1.device_name) + '_rt': _calculate_value_by_rate(disk2.time_spent_reading, disk1.time_spent_reading, _ts)})
                return_result.update({str(disk1.device_name) + '_wt': _calculate_value_by_rate(disk2.time_spent_write, disk1.time_spent_write, _ts)})
                # 磁盘单次读/写的时间(ms)
                return_result.update({str(disk1.device_name) + '_prt': _calculate_value_by_rate(disk2.time_spent_reading, disk1.time_spent_reading, max(1, int(disk2.read_count) - int(disk1.read_count)))})
                return_result.update({str(disk1.device_name) + '_pwt': _calculate_value_by_rate(disk2.time_spent_write, disk1.time_spent_write, max(1, int(disk2.write_count) - int(disk1.write_count)))})
                # 进行I/O操作的时间(ms)
                return_result.update({str(disk1.device_name) + '_iot': _calculate_value_by_rate(disk2.weighted_time_spent_doing_do, disk1.weighted_time_spent_doing_do, _ts)})
        except Exception:
            logger.warning((traceback.format_exc()))
        return return_result

    def _get_iostat_info(self, need_write_to_file=True):
        result = ''
        time_str = 'iostat_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        if 'win32' in sys.platform:
            return result
        self._cmd_disk_io_iostat = 'iostat -x -d -k 1 2'
        result = lo_cli.run_cmd(self._cmd_disk_io_iostat, need_run_with_sudo=True)
        result = time_str + '\n' + str(result) + '\n'
        # write_to_file(self.file_real_time_temp_ss_data, data=result, as_cover=True)

        if need_write_to_file:
            _write_to_file(self.record_file_path + 'org_file_iostat.txt', data=result, file_size=10485760,
                          as_cover=False, as_append=True)

    def _get_vmstat_info(self, need_write_to_file=True):
        """
        cs进程上下文切换、线程上下文切换、中断上下文切换
        r正在运行和等待的CPU进程数,r多会引发cs多
        :param need_write_to_file:
        :return:
        """
        return_result = collections.OrderedDict()
        time_str = 'vmstat_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        if 'win32' in sys.platform:
            return return_result
        # self._cmd_disk_io_iostat = self._cmd_cpu_usage_by_vmstat
        result = lo_cli.run_cmd(self._cmd_cpu_usage_by_vmstat, need_run_with_sudo=True)
        # write_to_file(self.file_real_time_temp_ss_data, data=result, as_cover=True)
        # logger.info(result)
        try:
            _topic, _title, _data_1, _data_2 = result.split('\n')
            _data_2 = _data_2.split()
            for no, _name in enumerate(_title.split()):
                return_result.update({str(_name): int(_data_2[no])})
                if _name == 'st' or _name == 'UTC':
                    break
        except:
            pass
        if need_write_to_file:
            _write_to_file(self.record_file_path + 'org_file_vmstat.txt', data=time_str + '\n' + str(result) + '\n',
                          file_size=10485760, as_cover=False, as_append=True)
        self._vmstat_data = return_result
        return return_result

    '''软中断运行情况'''

    def _get_cpu_softirqs_info(self, need_write_to_file=True):
        result = ''
        time_str = 'cpu_softirqs_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        if 'win32' in sys.platform:
            return result
        result = lo_cli.run_cmd(self._cmd_cpu_softirqs, need_run_with_sudo=True)
        result = time_str + '\n' + str(result) + '\n'

        if need_write_to_file:
            _write_to_file(self.record_file_path + 'org_file_cpu_softirqs.txt', data=result, as_cover=False,
                          as_append=True)

    def get_io_info(self, interval=5):
        if 'win32' in sys.platform:
            return {}

        result = self._get_io_info_from_proc(interval=interval)

        logger.debug((result))

        return result

    def run_for_get_all_datas(self, interval=5, kafka_interval=60, db_interval=60, java_interval=60,
                              need_write_to_file=False):
        def _get_cpu_and_bindwidth(need_write_to_file=False):
            # self.get_cpu_times_static_info()
            self.get_cpu_info(need_write_to_file=False, cpu_avg_interval=1)
            self.get_bindwidth_info(need_write_to_file=False, interval='auto')
            self._get_vmstat_info(need_write_to_file=need_write_to_file)

        if not self._is_cpu_and_bindwidth_thread_start:
            threading.Thread(target=self._do_func,
                             args=(interval, _get_cpu_and_bindwidth, False,),
                             kwargs={
                                 'need_write_to_file': need_write_to_file,
                             },
                             name='cpu_bw_data').start()
            self._is_cpu_and_bindwidth_thread_start = True

        def _get_all_data(interval=5, kafka_interval=60, db_interval=60, need_write_to_file=False):

            result = {}
            try:
                result['cpu'] = self.cpu_data
                result['cpu_time'] = self.cpu_times_static_data
                result['cpu_load'] = self.get_cpu_load_info(need_write_to_file=need_write_to_file)
                result['memory'] = self.get_memory_info(need_write_to_file=need_write_to_file)
                result['io'] = self.get_io_info(interval=interval)
                result['ss'] = {}
                if self._enable_ss:
                    result['ss'] = self.get_ss_info(need_write_to_file=need_write_to_file)
                result['sockstat'] = self._get_socketstat_from_proc()
                result['bw'] = self._bindwidth_data
                result['vmstat'] = self._vmstat_data
                result['storage'] = self.get_disk_storage_info(need_write_to_file=True)
                if self.pname:
                    result['app_mysql'] = self.get_mysql_data(mysql_username='admin', mysql_pwd='admin',
                                                              interval=db_interval)  # 放在第一位
                    logger.info('app_mysql data getted')
                    _mem, _thread = self.get_process_mem_and_thread_info(need_write_to_file=need_write_to_file)
                    logger.info('_mem, _thread data getted')
                    result['p_cpu'] = self.get_process_cpu_info(need_write_to_file=need_write_to_file, interval='auto')
                    result['p_memory'] = _mem
                    result['p_thread_num'] = _thread
                    result['p_pid'] = self.pid_per_pname_dict
                    result['p_num'] = {}
                    for __pname, value in self.pid_per_pname_dict.items():
                        result['p_num'].update({__pname: len(value)})

                    result['app_project'] = self.get_project_app_info(app_interval=interval, db_interval=db_interval,
                                                                      need_write_to_file=need_write_to_file)
                    logger.info('app_project data getted')
                    result['app_kafka'] = self.get_kafka_data(server_type_keywords=['kafka_leader'],
                                                              interval=kafka_interval)
                    logger.info('app_kafka data getted')
                    if not self.low_performance:
                        result['app_podman'] = self._get_podman_data(app_interval=300)
                        result['app_docker'] = self._get_docker_data(app_interval=300)
                    result['app_kamailio'] = self._get_kamailio_shmmem()
                    result['app_java'] = self._get_process_java_info(interval=java_interval)
                    # result['p_bindwidth'] = self.get_process_bindwidth_info_from_proc()
                    # result['p_fd_num'] = self.get_process_fd_num()
                    result['p_fd_num'] = {}
                    # result['p_sockstat'] = self.get_process_sockstat_from_proc()
                    result['app_redis'] = {}

                self.all_datas = result

                logger.warning(('###updated all_datas', result))
                # logger.critical(('###self.last_data',self.last_data))

            except Exception:
                logger.warning((traceback.format_exc(), result))

            return result

        threading.Thread(target=self._do_func,
                         args=(interval, _get_all_data, True,),
                         kwargs={
                             "interval": interval,
                             "kafka_interval": kafka_interval,
                             "db_interval": db_interval,
                             'need_write_to_file': need_write_to_file,
                         },
                         name='all_data').start()
        logger.critical(("run_for_get_all_datas", 'exit'))
        # _get_all_data(result)

        return self.all_datas

    '''监控数据输出的文件名,部分为backup未使用'''

    def _init_file_names(self, record_file_path):
        # 原始信息保存的文件名
        # top原始信息文件名
        self.record_file_path = record_file_path
        if self.record_file_path[-1] != '/':
            self.record_file_path = self.record_file_path + '/'
        # self.file_top_org = self.record_file_path + 'org_file_top.txt'
        # self.file_ps_org = self.record_file_path + 'org_file_ps.txt'
        # free -m原始文件名
        # self.file_memory_org = self.record_file_path + 'org_file_memory.txt'
        # df -m原始文件名
        # self.df_m_info_org = self.record_file_path + 'org_file_df_m.txt'
        # updatime过滤cpuload信息
        # self.file_uptime_cpu_load_org = self.record_file_path + 'org_file_uptime_cpu_load.txt'
        # 磁盘原始信息文件名
        # self.disk_io_info_org = self.record_file_path + 'org_file_disk_io.txt'
        # sar的网络统计相关原始信息文件名
        # self.file_proc_network_org = self.record_file_path + 'org_file_proc_network.txt'
        # self.file_sar_network_org = self.record_file_path + 'org_file_sar_network.txt'
        # self.file_proc_cpu_org = self.record_file_path + 'org_file_proc_cpu.txt'
        # self.file_sar_cpu_org = self.record_file_path + 'org_file_sar_cpu.txt'
        # self.file_ss_info_org = self.record_file_path + 'org_file_ss.txt'
        # self.file_iostate_info_org = self.record_file_path + 'org_file_iostat.txt'
        # netstat原始信息文件名
        # self._file_proc_pid_mem_org = self.record_file_path + '{pname}_proc_mem_org.txt'

        # self.file_process_mem = self.record_file_path + 'filtered_process_mem_info.csv'
        # self.file_process_cpu_filter = self.record_file_path + 'filtered_process_cpu_info.txt'
        # self.file_all_cpu_used_filter = self.record_file_path + "filtered_cpu_used.csv"
        # self.file_netstat_filter = self.record_file_path + "filtered_netstat.csv"
        # self.file_process_java_org = self.record_file_path + 'process_java_info_org.txt'
        # self.file_application_filter = self.record_file_path + 'filtered_application_info.csv'
        # awk后，load average信息的csv文件名
        # self.file_filter_cpu_load_average = self.record_file_path + 'filtered_load_average.csv'
        # 过滤后，free -m或者/proc/meminfo
        # self.file_memory_filtered = self.record_file_path + 'filtered_memory.csv'
        # awk后，top文件中available mem信息的csv文件
        # self.file_filter_network = self.record_file_path + 'filtered_network_file.csv'
        # self.netstat_sum_file = self.record_file_path + 'netstat_sum.csv'
        # self._per_pname_cpu_usage_file = self.record_file_path + '{pname}_cpu_usage.csv'
        # self._per_proc_pid_mem_file = self.record_file_path+'{pname}_proc_mem_rss.csv'
        # self._per_pname_mem_file = ''
        # self._per_pname_res_top_file = self.record_file_path + '{pname}_top_res.csv'
        # self._per_port_netstat_file = self.record_file_path + 'netstat_port_{port_id}.csv'
        # self.file_netstat_non_0 = self.record_file_path + 'netstat_non_0.txt'
        self.file_real_time_temp_ss_data = self.record_file_path + 'temp_ss_file.txt'
        self.file_real_time_temp_top_data = self.record_file_path + 'temp_top_file.txt'
        self.file_real_time_temp_ps_data = self.record_file_path + 'temp_ps_file.txt'
        # self.top_available_mem_file = self.record_file_path + 'top_available_mem_file.csv'
        # self.sar_cpu_time_file = self.record_file_path + 'sar_cpu_time.csv'

        # awk后，top文件中的time信息的csv文件名
        # self.top_time_file = self.record_file_path + 'top_time.csv'
        # self.cpu_idle_time_file = self.top_time_file
        # awk后，free -m文件中time信息的csv文件名
        # self.free_m_time_file = self.record_file_path + 'free_m_time.csv'
        # self._proc_pid_mem_time_file = self.record_file_path + 'proc_process_mem_time.csv'
        # self.pname_res_time_file = ''
        # self.pname_status_org_info = self.record_file_path + 'pname_status_info_org.txt'
        # awk后 cpu idle信息的csv文件名
        # self.file_all_cpu_used_filter = self.record_file_path + 'cpu_all_idle.csv'
        # self.free_m_available_file = self.record_file_path + 'free_m_available_file.csv'
        # self._per_cpu_idle_file = None
        # self.cpu_pname_file = self.record_file_path + 'top_pname_cpu.csv'
        # awk后，sar文件中的time、rxpck，txpck，rxkB，txkB的csv文件名
        # self.sar_network_time_file = self.record_file_path + 'sar_network_time.csv'
        # self.sar_network_file = self.record_file_path + 'sar_network_file.csv'
        # awk后，netstat信息的csv文件名
        # self.netstat_time_file = self.record_file_path + 'netstat_time.csv'
        # self.proc_cpu_time_file = self.record_file_path + 'proc_cpu_time.csv'
        # self.cpu_idle_time_file = ''
        # self.proc_network_file = self.record_file_path + 'proc_network.csv'
        # self.proc_network_time_file = self.record_file_path + 'proc_network_time.csv'
        # self.netstat_rq_sum_file = self.record_file_path + 'netstat_rq_sum.csv'
        # self.filter_proc_cpu_time_cmd = None
        # self.netstat_sq_sum_file = self.record_file_path + 'netstat_sq_sum.csv'
        # self.netstat_rq_port_sum_file = self.record_file_path + 'netstat_rq_port_sum.csv'
        # self.netstat_sq_port_sum_file = self.record_file_path + 'netstat_sq_port_sum.csv'
        # self._per_cpu_idle_file = self.record_file_path+"cpu_{core_id}_idle.csv"
        # 提供给report的监控csv文件的title的定义

    def __init_h_file(self):
        self._h_file_ss_filter = None
        self._h_file_ss_org = None
        self._h_file_ps_org = None
        self._h_file_top_org = None
        self._h_file_iostat_org = None

        self._h_file_cpu_filter = None
        self._h_file_process_cpu_filter = None
        self._h_file_mem_filter = None
        self._h_file_process_mem_filter = None

        self._h_file_network_filter = None
        self._h_file_cpu_load_filter = None

        self._h_file_app_filter = None

    def _get_real_time_top_data(self, need_write_to_file=True):
        """
        VIRT：virtual memory usage 虚拟内存
        1）进程“需要的”虚拟内存大小，包括进程使用的库、代码、数据等；
        2）假如进程申请100m的内存，但实际只使用了10m，那么它会增长100m，而不是实际的使用量。
        RES：resident memory usage 常驻内存
        1）进程当前使用的内存大小，但不包括swap out；
        2）包含其他进程的共享；
        3）如果申请100m的内存，实际使用10m，它只增长10m，与VIRT相反；
        4）关于库占用内存的情况，它只统计加载的库文件所占内存大小。

        SHR：shared memory 共享内存
        1）除了自身进程的共享内存，也包括其他进程的共享内存；
        2）虽然进程只使用了几个共享库的函数，但它包含了整个共享库的大小；
        3）计算某个进程所占的物理内存大小公式：RES – SHR；
        4）swap out后，它将会降下来。
        """
        result = ''
        time_str = 'top_time#%s\n' % str(time.strftime("%Y%m%d %H:%M:%S"))
        if 'win32' in sys.platform:
            return result
        result = lo_cli.run_cmd(self.cmd_top_1)
        if result is False or "unknown argument" in str(result):
            result = lo_cli.run_cmd(self.cmd_top_2)
            if result is False:
                result = lo_cli.run_cmd(self.cmd_top_3)
            if result is False:
                result = lo_cli.run_cmd(self.cmd_top_4)

        result = time_str + '\n' + result + '\n'
        if need_write_to_file:
            self._h_file_top_org = _write_to_file(file=self.record_file_path + 'org_file_top.txt', data=result,
                                                 file_size=314572800, as_cover=False, as_append=True,
                                                 file_handle=self._h_file_top_org)
            _write_to_file(self.file_real_time_temp_top_data, data=result, as_cover=True)

        return result

    def _get_real_time_ss_data(self, need_write_to_file=True):
        result = ''
        time_str = 'ss_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        if 'win32' in sys.platform:
            return result
        result = lo_cli.run_cmd(self.cmd_ss, need_run_with_sudo=True)
        if not result:
            result = lo_cli.run_cmd(self.cmd_ss, need_run_with_sudo=True)
        result = time_str + '\n' + str(result) + '\n'
        _write_to_file(self.file_real_time_temp_ss_data, data=result, as_cover=True)

        if need_write_to_file:
            self._h_file_ss_org = _write_to_file(self.record_file_path + 'org_file_ss.txt', data=result, as_cover=False,
                                                as_append=True, file_handle=self._h_file_ss_org)

        # logger.critical(('write',self.file_real_time_temp_ss_data))

        return result

    def _get_real_time_ps_data(self, need_write_to_file=True):
        result = ''
        time_str = 'ps_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        _cmd_grep = "|grep -vi '%(py)s \| grep\| tail \| more \| vim \| vi \| less '" % {'py': PYTHON_FILE_NAME}
        cmd = self.ps_eo_cmd + _cmd_grep
        _ps_result = lo_cli.run_cmd(cmd)
        if _ps_result is False or "supported arguments" in cmd:
            _ps_result = lo_cli.run_cmd(self.ps_eo_cmd_2 + _cmd_grep)
        if 'win32' in sys.platform or lo_cli.error_code != ERROR_CODE_SUCCESS:
            return result
        result = time_str + '\n' + str(_ps_result) + '\n'
        _write_to_file(self.file_real_time_temp_ps_data, data=result, as_cover=True)

        if need_write_to_file:
            self._h_file_ps_org = _write_to_file(self.record_file_path + 'org_file_ps.txt', data=result, as_cover=False,
                                                as_append=True, file_handle=self._h_file_ps_org)

        return result

    def _update_pid_pname(self):

        pass

    def do_get_real_time_and_cpu_bw_vmstat_info(self, interval, top_interval=60, need_write_to_file=True):
        # if len(self.pname) == 0:
        #     return

        if not interval:
            interval = 10
        _et = _st = time.time()
        '''大循环,top'''
        while _et - _st <= self.total_runtime:
            _st = time.time()
            try:
                '''小循环,ps/cpu/bindwidth/vmstat/ss'''
                while _et - _st < top_interval:
                    _sst = time.time()
                    self._get_real_time_ps_data(need_write_to_file=need_write_to_file)
                    self._analysis_ps_data(need_return_process_mem_data=False)  # 更新self.pid_per_pname_dict
                    # self.get_bindwidth_info(need_write_to_file=False)
                    # self._get_vmstat_info(need_write_to_file=need_write_to_file)
                    # self.get_cpu_info(cpu_avg_interval=1, need_write_to_file=False)
                    if self._enable_ss:
                        self._get_real_time_ss_data(need_write_to_file=need_write_to_file)
                        self._analysis_ss_data(only_update_pname_port=True)  # 更新self.listen_port_per_pname_dict
                    time.sleep(int(interval) - (time.time() - _sst))
                    _et = time.time()
                    logger.debug(('###get and analysis ps/ss data', _et, _st, interval))

                if not self.low_performance:
                    self._get_real_time_top_data(need_write_to_file=need_write_to_file)
                    # self._get_iostat_info(need_write_to_file=need_write_to_file)
                    # self._get_cpu_softirqs_info(need_write_to_file=need_write_to_file)
                _et = time.time()
            except Exception:
                logger.critical(('#####,top/ss/ps failed=', traceback.format_exc()))
            try:
                time.sleep(int(interval) - (time.time() - _st))
            except:
                pass
        logger.warning('exit')

    def _do_func(self, do_interval, func, need_print_log=False, **kwargs):
        _et = st = time.time()
        while _et - st - 10 <= int(self.total_runtime):
            if self._need_print_log and need_print_log:
                logger.critical(('###[start]exce func', func, kwargs, self.total_runtime))
            _st = time.time()
            try:
                func(**kwargs)
                logger.critical(('###func exit,do_interval:%s' % str(do_interval), func, kwargs, self.total_runtime))

            except Exception:
                logger.critical((traceback.format_exc(), func, kwargs, self.total_runtime))
            _need_sleep_time = int(do_interval) - (time.time() - _st)
            if _need_sleep_time > 0:
                time_sleep(_need_sleep_time)
            if self._need_print_log and need_print_log:
                logger.critical(
                    ('###[end]exce func end,sleep_time:%s' % str(_need_sleep_time), func, kwargs, self.total_runtime))

            _et = time.time()
        logger.critical(('###[exit]exce func end,do_interval:%s' % str(do_interval), func, kwargs, self.total_runtime))

    def __get_pname_line_index_info_in_ps_top(self, _line_data, pname_list, _colunm_index_map, header_value_map):

        # _column_id = {'pid':-1,'cpu_percent':-1,'mem_percent':-1,'command':-1,'command_args':-1,'res':-1,'vss':-1}
        _column_id = _colunm_index_map
        _line_pname = ''
        __line_list = _line_data.split()

        if len(__line_list) < 3:
            return (_line_pname, _column_id)
        try:
            if 'PID ' in _line_data and 'USER ' in _line_data:

                _column_id['pid'] = list.index(__line_list, header_value_map['pid'])
                _column_id['res'] = list.index(__line_list, header_value_map['res'])
                _column_id['vss'] = list.index(__line_list, header_value_map['vss'])
                _column_id['cpu_percent'] = list.index(__line_list, header_value_map['cpu_percent'])
                _column_id['mem_percent'] = list.index(__line_list, header_value_map['mem_percent'])
                _column_id['command'] = list.index(__line_list, header_value_map['command'])
                _column_id['command_args'] = list.index(__line_list, header_value_map['command_args'],
                                                        len(__line_list) - 1)
                return (_line_pname, _column_id)

            elif 'monitor_system' in str(__line_list[_column_id['command_args']]) \
                    or 'vim ' in str(__line_list[_column_id['command_args']]) \
                    or 'cat ' in str(__line_list[_column_id['command_args']]) \
                    or 'tail ' in str(__line_list[_column_id['command_args']]):
                return (_line_pname, _column_id)
        except:
            logger.critical(('DATA INCOMPLETE', traceback.format_exc(), _line_data, pname_list))

        _line_pname = ''
        for _pname in pname_list:
            if not _pname:
                continue

            _pname_keywords = str(_pname).lower().split('#')
            result = [True for _pname_keyword in _pname_keywords if _pname_keyword in str(_line_data).lower()]
            # logger.critical((result,_pname_keywords,_line_data, _line_pname, _column_id))

            if len(_pname_keywords) == len(result):
                _line_pname = _pname
                break

        return (_line_pname, _column_id)

    '''获取pid列表/内存消耗'''

    def _analysis_ps_data(self, ps_data=None, need_return_process_mem_data=False):
        """

        :param need_return_process_mem_data: [bool] 统计ps中每个进程的内存数据,进程名出现多次时进行累加
        :return: {} 进程的内存单位是KB

        :param ps_data:[string]
        $ ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,pcpu,pmem,etime,time,comm,args
        USER       PID  PPID  NI    VSZ   RSS TT       STAT %CPU %MEM     ELAPSED     TIME COMMAND         COMMAND
        root         1     0   0 192236  5284 ?        Ss    0.0  0.0 35-19:48:33 00:14:27 systemd         /usr/lib/systemd/systemd --switched-root --system --deserialize 21
        root         2     0   0      0     0 ?        S     0.0  0.0 35-19:48:33 00:00:00 kthreadd        [kthreadd]
        root         4     2 -20      0     0 ?        S<    0.0  0.0 35-19:48:33 00:00:00 kworker/0:0H    [kworker/0:0H]
        root         6     2   0      0     0 ?        S     0.2  0.0 35-19:48:33 02:32:49 ksoftirqd/0     [ksoftirqd/0]
        root         7     2   -      0     0 ?        S     0.0  0.0 35-19:48:33 00:01:09 migration/0     [migration/0]
        root         8     2   0      0     0 ?        S     0.0  0.0 35-19:48:33 00:00:00 rcu_bh          [rcu_bh]


        """
        # "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args" rss vsize单位是kb

        if not ps_data:
            try:
                ps_data = str(_read_file(self.file_real_time_temp_ps_data)).split('\n')
            except:
                ps_data = []
        else:
            ps_data = str(ps_data).split('\n') if type(ps_data) != list else ps_data

        _pid_pname_dict = {}
        _display_pname_per_pid = {}
        _rss_pname_dict = {}
        _vss_pname_dict = {}
        header_value_map = {'pid': 'PID', 'res': 'RSS', 'vss': 'VSZ',
                            'cpu_percent': '%CPU', 'mem_percent': '%MEM',
                            'command': 'COMMAND', 'command_args': 'COMMAND'}

        _column_id = {'pid': -1, 'cpu_percent': -1, 'mem_percent': -1, 'command': -1, 'command_args': -1, 'res': -1,
                      'vss': -1}

        for _line_data in ps_data:
            if not self.pname:
                break
            (_line_pname, _column_id) = self.__get_pname_line_index_info_in_ps_top(_line_data=_line_data,
                                                                                   pname_list=self.pname,
                                                                                   _colunm_index_map=_column_id,
                                                                                   header_value_map=header_value_map)
            # logger.critical((_line_pname, _column_id, _line_data, self.pname))

            if not _line_pname:
                continue

            __line_list = _line_data.split()
            if not _pid_pname_dict.get(_line_pname):
                #     _pid_pname_dict.update({_line_pname: _pid_pname_dict.get(_line_pname)})
                # else:
                _pid_pname_dict.update({_line_pname: []})
                _vss_pname_dict.update({_line_pname: 0})
                _rss_pname_dict.update({_line_pname: 0})

            if int(__line_list[_column_id['pid']]) >= 0:
                _pid_pname_dict[_line_pname].append(__line_list[_column_id['pid']])

                if str(_line_pname).lower().find('yarntask') != -1:
                    _display_pname_per_pid.update({str(__line_list[_column_id['pid']]):
                                                       str(_line_data).split('/logs/')[-1].split('/taskmanager.')[0]})
                else:
                    _display_pname_per_pid.update({str(__line_list[_column_id['pid']]): _line_pname})

            if int(__line_list[_column_id['vss']]) >= 0 and need_return_process_mem_data:
                _vss_pname_dict[_line_pname] = _vss_pname_dict[_line_pname] + int(__line_list[_column_id['vss']])
            if int(__line_list[_column_id['res']]) >= 0 and need_return_process_mem_data:
                _rss_pname_dict[_line_pname] = _rss_pname_dict[_line_pname] + int(__line_list[_column_id['res']])

        self.pid_per_pname_dict = _pid_pname_dict
        self._display_pname_per_pid = _display_pname_per_pid

        logger.warning('self.pid_per_pname_dict=%s,len_ps_data=%s,pname=%s' % (
        str(self.pid_per_pname_dict), str(len(ps_data)), str(self.pname)))
        logger.warning('self._display_pname_per_pid=%s' % str(self._display_pname_per_pid))

        return _rss_pname_dict, _vss_pname_dict

    '''获取总的/某个进程的 端口拥堵，监听端口列表'''

    def _analysis_ss_data(self, ss_data=None, only_update_pname_port=False):
        """

        :return:

        :ex:
        [root@localhost MONITOR_SYSTEM]# ss -tuanps
        Total: 196 (kernel 375)
        TCP:   7 (estab 2, closed 0, orphaned 0, synrecv 0, timewait 0/0), ports 0

        Transport Total     IP        IPv6
        *	  375       -         -
        RAW	  1         0         1
        UDP	  3         1         2
        TCP	  7         3         4
        INET	  11        4         7
        FRAG	  0         0         0

        Netid State      Recv-Q Send-Q                    Local Address:Port                                   Peer Address:Port
        udp   UNCONN     0      0                             127.0.0.1:323                                               *:*                   users:(("chronyd",pid=1298,fd=5))
        udp   UNCONN     0      0                                 [::1]:323                                            [::]:*                   users:(("chronyd",pid=1298,fd=6))
        udp   UNCONN     0      0      [fe80::60da:f7b4:5168:3279]%enp2s0:546                                            [::]:*                   users:(("dhclient",pid=2231,fd=5))
        tcp   LISTEN     0      100                           127.0.0.1:25                                                *:*                   users:(("master",pid=2032,fd=13))
        tcp   LISTEN     0      128                                   *:22                                                *:*                   users:(("sshd",pid=1681,fd=3))
        tcp   ESTAB      0      1592                     192.168.121.50:22                                  192.168.126.169:56272               users:(("sshd",pid=21541,fd=3))
        tcp   LISTEN     0      100                               [::1]:25                                             [::]:*                   users:(("master",pid=2032,fd=14))
        tcp   LISTEN     0      128                                [::]:9100                                           [::]:*                   users:(("node_exporter",pid=3057,fd=3))
        tcp   LISTEN     0      128                                [::]:22                                             [::]:*                   users:(("sshd",pid=1681,fd=4))
        tcp   ESTAB      0      0               [::ffff:192.168.121.50]:9100                       [::ffff:192.168.121.200]:33846               users:(("node_exporter",pid=3057,fd=7))

        """
        return_result = {}
        if not ss_data:
            ss_data = str(_read_file(self.file_real_time_temp_ss_data)).split('\n')
        else:
            ss_data = ss_data.split('\n') if type(ss_data) != list else ss_data
        _recv_q = 2
        _send_q = 3
        _state = 1  # ESTABLISH/LISTEN
        _local_addr = 4
        _net_type = 0  # TCP/UDP

        _pname_recv_queue = {}
        _pname_send_queue = {}
        _pname_listen_port = {}
        _recv_queue_num = 0
        _send_queue_num = 0
        _recv_queue_sum = 0
        _send_queue_sum = 0

        _network_traffic = {}
        _online_users_in_443 = 0

        for _pname in self.pname:
            _pname_listen_port.update({_pname: []})
            # _pname_recv_queue.update({_pname: 0})
            # _pname_send_queue.update({_pname: 0})

        for _line_no, _line_data in enumerate(ss_data):
            # if _line_no > 2000:
            #     break
            _line_data_list = str(_line_data).split()
            # logger.critical(_line_data_list)
            if len(_line_data_list) < 6:
                continue
            __local_port = _line_data_list[_local_addr].split(':')[-1]

            try:  # 统计行,跳过
                __recv_data = int(_line_data_list[_recv_q])
                __send_data = int(_line_data_list[_send_q])
            except:
                continue
            try:
                if only_update_pname_port:
                    raise

                '''统计TCP状态数(estab/listen/time_wait等)'''
                __network_traffic = 0
                __network_traffic_key = _line_data_list[_net_type] + '_' + _line_data_list[_state]
                if _network_traffic.get(__network_traffic_key):
                    __network_traffic = _network_traffic[__network_traffic_key]
                _network_traffic[__network_traffic_key] = __network_traffic + 1

                '''统计端口拥堵总量和总个数'''
                if __recv_data > 0:
                    _recv_queue_num = _recv_queue_num + 1
                    _recv_queue_sum = _recv_queue_sum + __recv_data
                if __send_data > 0:
                    _send_queue_num = _send_queue_num + 1
                    _send_queue_sum = _send_queue_sum + __send_data

                '''443端口在线用户数'''
                if 'esta' in str(_line_data_list[_state]).lower() and int(__local_port) == 443:
                    _online_users_in_443 = _online_users_in_443 + 1

            except:
                pass
            if 'LISTEN' not in _line_data_list[_state]:
                continue

            for _pname in self.pname:
                try:
                    _find = False
                    if _pname in str(_line_data_list[-1]):
                        _find = True
                    if not _find:
                        _find_times = [True for _pid in self.pid_per_pname_dict.get(_pname) if
                                       _pid in _line_data_list[-1]]
                        if len(_find_times) > 0:
                            _find = True
                    if not _find:
                        continue
                    if len(_pname_listen_port[_pname]) <= self._listen_port_num_per_pname:
                        if __local_port not in _pname_listen_port[_pname]:
                            _pname_listen_port[_pname].append(__local_port)
                        __key_recv = 'Recv-Q_' + _pname + str(__local_port)
                        _old_recv = _pname_recv_queue.get(__key_recv) if _pname_recv_queue.get(__key_recv) else 0
                        _pname_recv_queue.update({__key_recv: __recv_data + _old_recv})
                        __key_send = 'Send-Q_' + _pname + str(__local_port)
                        _old_send = _pname_send_queue.get(__key_send) if _pname_send_queue.get(__key_send) else 0
                        _pname_send_queue.update({__key_send: __send_data + _old_send})
                        break
                    # logger.critical((_line_data_list,_pname,_send_queue_num,_send_queue_sum,_recv_queue_num,_recv_queue_sum,_pname_recv_queue))
                except Exception:
                    logger.critical((traceback.format_exc(), _line_data_list, self.pid_per_pname_dict))

        self.listen_port_per_pname_dict = _pname_listen_port
        logger.warning('self.listen_port_per_pname_dict=%s' % str(self.listen_port_per_pname_dict))
        if not only_update_pname_port:
            return_result.update(_pname_recv_queue)
            return_result.update(_pname_send_queue)
            return_result.update({'Recv_Q_sum': float(_recv_queue_sum)})
            return_result.update({'Send_Q_sum': float(_send_queue_sum)})
            return_result.update({'Recv_Q_non_0_no': int(_recv_queue_num)})
            return_result.update({'Send_Q_non_0_no': int(_send_queue_num)})
            return_result.update(_network_traffic)
            return_result.update({'online_in_443': _online_users_in_443})

        # logger.critical(('ss',return_result))
        return return_result

    def _analysis_top_data(self, top_data=None, analysis_pname_list=None):
        """
        top不支持取内存数据,因内存数值过大时显示不全,如
        KiB Mem : 32986700+total,  1474968 free, 23536641+used, 93025624 buff/cache
        KiB Swap:        0 total,        0 free,        0 used. 87837360 avail Mem

        :param top_data: [string] top的数据,如果是None从top的临时文件取
        :param analysis_pname_list: [list] 进程名, 用于匹配 COMMAND 列,匹配到就获取cpu和res输出
        :return: [dict]

        {'time':'20231102 18:17:49','cpu_load_15':0.0,'cpuall':3.9000000000000057,
        'mysql_1677643_cpu':'0.0','mysql_1677643_res':99952.0,'mysql_1677643_mem':'5.7',
        'asterisk_457692_cpu':'0.0','asterisk_457692_res':53660.0,'asterisk_457692_mem':'3.1',
        'asterisk_160643_cpu':'0.0','asterisk_160643_res':53456.0,'asterisk_160643_mem':'3.1',
        'asterisk_159537_cpu':'0.0'}

        """
        return_result = {}
        if not top_data:
            top_data = str(_read_file(self.file_real_time_temp_top_data)).split('top - ')[-1]
        else:
            top_data = top_data.split('top - ')[-1] if type(top_data) != list else top_data

        def _get_cpu_load(line_data):
            _result = {}
            _line_data = line_data.split(',')
            # logger.critical(_line_data)
            # logger.critical(_line_data[-3].split(':')[-1])
            try:
                _result.update({'cpu_load_15': float(_line_data[-1])})
                _result.update({'cpu_load_5': float(_line_data[-2])})
                _result.update({'cpu_load_1': float(_line_data[-3].split(':')[-1])})
            except:
                pass

            # logger.critical(_result)
            return _result

        def _get_cpu(line_data):
            _result = {}
            _line_data = line_data.split(',')
            _line_data = line_data.split(':')
            try:
                _name = _line_data[0].strip().lower().replace('%', '').replace('(s)', 'all')

                for _data in _line_data[-1].split(','):
                    if ' id' in _data:
                        _value = str(_data).replace('id', '')
                        _result.update({_name: round(100 - float(_value), 2)})
                        break
            except:
                pass
            return _result

        def _get_process_info(line_data, _line_pname, _column_id):
            _result = {}
            _line_data_list = line_data.split()
            try:
                _key_name = _line_pname + '_' + str(_line_data_list[_column_id['pid']])
                _cpu = _line_data_list[_column_id['cpu_percent']]
                _res = float(_line_data_list[_column_id['res']][0:-1]) * 1024 if 'g' in _line_data_list[
                    _column_id['res']] else float(
                    _line_data_list[_column_id['res']])
                _mem_percent = _line_data_list[_column_id['mem_percent']]
                _result.update({_key_name + '_cpu': _cpu, _key_name + '_res': _res, _key_name + '_mem': _mem_percent})
            except:
                pass

            return _result

        # _column_pid = -1
        # _column_res = -1
        # _column_cpu_percent = -1
        # _column_mem_percent = -1
        # _column_command = -1
        _pname_list = self.pname + analysis_pname_list if type(analysis_pname_list) == list else self.pname

        header_value_map = {'pid': 'PID', 'res': 'RES', 'vss': 'VIRT',
                            'cpu_percent': '%CPU', 'mem_percent': '%MEM',
                            'command': 'COMMAND', 'command_args': 'COMMAND'}

        _column_id = {'pid': -1, 'cpu_percent': -1, 'mem_percent': -1, 'command': -1, 'command_args': -1, 'res': -1,
                      'vss': -1}

        for _line_data in top_data.split('\n'):
            if not _line_data:
                continue
            if 'PID ' in _line_data and ' COMMAND' in _line_data and not _pname_list:
                break
            _line_data_list = _line_data.split()
            if 'load average' in _line_data:
                return_result.update(_get_cpu_load(_line_data))
            elif '%Cpu' in _line_data and ' id' in _line_data:
                return_result.update(_get_cpu(_line_data))

            elif 'KiB Mem' in _line_data and 'total' in _line_data:
                # not support for info not entire
                continue

            else:
                # logger.critical(_column_id)
                (_line_pname, _column_id) = self.__get_pname_line_index_info_in_ps_top(_line_data=_line_data,
                                                                                       pname_list=_pname_list,
                                                                                       _colunm_index_map=_column_id,
                                                                                       header_value_map=header_value_map)

                if not _line_pname:
                    continue
                # logger.critical((_column_command,_column_mem_percent,len(_line_data_list)))
                if _column_id['res'] != -1 and _column_id['cpu_percent'] != -1:
                    return_result.update(_get_process_info(_line_data, _line_pname=_line_pname, _column_id=_column_id))

        return return_result

    def get_top_info(self, get_in_remote=False, remote_server_client=None, analysis_pname_list=None):
        return_result = collections.OrderedDict()
        time_str = 'io_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str.split('#')[1])})

        _top_data = None
        if get_in_remote and remote_server_client:
            cmd = self.cmd_top_1
            _top_data = remote_server_client.run_cmd(cmd=cmd, need_run_with_sudo=True, timeout=8)
            if remote_server_client.error_code != ERROR_CODE_SUCCESS:
                return return_result

        return_result.update(self._analysis_top_data(top_data=_top_data, analysis_pname_list=analysis_pname_list))
        return return_result

    '''chfshan,有多个进程id时，mem全部相加,线程数取第一个进程'''

    def _get_process_mem_and_thread_from_proc(self, need_write_to_file=False):
        time_str = 'proc_mem_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        _mem_result = collections.OrderedDict()
        _mem_result.update({'time': str(time_str.split('#')[1])})
        _thread_result = copy.deepcopy(_mem_result)

        # return_result = collections.OrderedDict()
        # return_result.update({'time': str(time_str.split('#')[1])})
        _is_get_ps_mem = False
        _ps_data = {}

        def _get_process_mem_from_proc(pid):
            return_result = {}
            try:
                with open('/proc/%s/status' % str(pid), 'r') as f:
                    datas = f.readlines()
                    for _line in datas:
                        _data = _line.split()
                        if _line.startswith('VmRSS'):
                            return_result.update({'vm_rss': float(_data[1])})
                        if _line.startswith('VmSize'):
                            return_result.update({'vm_size': float(_data[1])})
                        if _line.startswith('VmSwap'):
                            return_result.update({'vm_swap': float(_data[1])})
                        if _line.startswith('Threads'):
                            return_result.update({'thread_no': float(_data[1])})
                            break
                f.close()
            except:
                pass

            return return_result

        for pname in self.pname:
            pid = None
            try:
                pid = self.pid_per_pname_dict[pname]
                _vm_size = 0
                _vm_rss = 0
                _thread_no = 0
                _vm_swap = 0
                # 取不到pid，继续循环下一个pname
                if len(pid) < 1:
                    continue
                # pname对应的pid超过2个，取ps的通过awk相加,不然逐个取proc
                if len(pid) > 50:
                    if not _is_get_ps_mem:
                        _ps_data = self._analysis_ps_data(need_return_process_mem_data=True)
                        _is_get_ps_mem = True
                    _vm_rss = _ps_data[0].get(pname)
                    _vm_size = _ps_data[1].get(pname)
                    _thread_no = lo_cli.run_cmd(
                        "cat /proc/%s/status | grep -E 'Threads'|awk '{print $2}'" % str(pid[0]), )
                else:
                    for no, pid in enumerate(pid[0:60]):
                        proc_mem = _get_process_mem_from_proc(pid)
                        if proc_mem.get('vm_rss') is not None:
                            _vm_rss = _vm_rss + float(proc_mem.get('vm_rss'))
                            _vm_size = _vm_size + float(proc_mem.get('vm_size'))
                            _thread_no = _thread_no + float(proc_mem.get('thread_no'))
                            _vm_swap = _vm_swap + float(proc_mem.get('vm_swap'))
                            if no < 6:
                                _mem_result.update({str(self._display_pname_per_pid[pid]) + '_' + str(
                                    pid) + '_vmsize': float(proc_mem.get('vm_size'))})
                                _mem_result.update({str(self._display_pname_per_pid[pid]) + '_' + str(
                                    pid) + '_res': float(proc_mem.get('vm_rss'))})
                                _mem_result.update({str(self._display_pname_per_pid[pid]) + '_' + str(
                                    pid) + '_TNO': float(proc_mem.get('thread_no'))})
                                _mem_result.update({str(self._display_pname_per_pid[pid]) + '_' + str(
                                    pid) + '_swap': float(proc_mem.get('vm_swap'))})

                _mem_result.update({str(pname) + '_all_vmsize': float(_vm_size)})
                _mem_result.update({str(pname) + '_all_res': float(_vm_rss)})
                _thread_result.update({str(pname) + '_all_TNO': float(_thread_no)})
                _mem_result.update({str(pname) + '_all_swap': float(_vm_swap)})
                _mem_result.update({str(pname) + '_all_res_swap': float(_vm_swap) + float(_vm_rss)})


            except Exception as e:
                logger.debug("pname=%s,result=%s,e=%s" % (pname, str(_mem_result), traceback.format_exc()))
                continue
        return (_mem_result, _thread_result)

    '''chfshan,有多个进程id时，mem全部相加,线程数取第一个进程'''

    def _get_process_mem_and_thread_from_proc_back(self, need_write_to_file=False):
        time_str = 'proc_mem_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        _mem_result = collections.OrderedDict()
        _mem_result.update({'time': str(time_str.split('#')[1])})
        _thread_result = copy.deepcopy(_mem_result)

        # return_result = collections.OrderedDict()
        # return_result.update({'time': str(time_str.split('#')[1])})
        _is_get_ps_mem = False
        _ps_data = {}

        def _get_process_mem_from_proc(pid):
            _vm_size = 0
            _vm_rss = 0
            _thread_no = 0
            with open('/proc/%s/status' % str(pid), 'r') as f:
                datas = f.readlines()
                for _line in datas:
                    # _line = str(_line).strip()
                    _data = _line.split()
                    # logger.critical(_data)
                    if _line.startswith('VmRSS'):
                        _vm_rss = float(_data[1])
                    if _line.startswith('VmSize'):
                        _vm_size = float(_data[1])
                    if _line.startswith('Threads'):
                        _thread_no = float(_data[1])
                        break
            f.close()
            return {'vm_rss': _vm_rss, 'vm_size': _vm_size, 'thread_no': _thread_no}

        for pname in self.pname:
            pid = None
            try:
                pid = self.pid_per_pname_dict[pname]
                _vm_size = 0
                _vm_rss = 0
                _thread_no = 0
                # 取不到pid，继续循环下一个pname
                if len(pid) < 1:
                    continue
                # pname对应的pid超过2个，取ps的通过awk相加,不然逐个取proc
                if len(pid) > 1:
                    if not _is_get_ps_mem:
                        _ps_data = self._analysis_ps_data(need_return_process_mem_data=True)
                        _is_get_ps_mem = True
                    _vm_rss = _ps_data[0].get(pname)
                    _vm_size = _ps_data[1].get(pname)
                    _thread_no = lo_cli.run_cmd(
                        "cat /proc/%s/status | grep -E 'Threads'|awk '{print $2}'" % str(pid[0]), )
                else:
                    with open('/proc/%s/status' % str(pid[0]), 'r') as f:
                        datas = f.readlines()
                        for _line in datas:
                            # _line = str(_line).strip()
                            _data = _line.split()
                            # logger.critical(_data)
                            if _line.startswith('VmRSS'):
                                _vm_rss = float(_data[1])
                            if _line.startswith('VmSize'):
                                _vm_size = float(_data[1])
                            if _line.startswith('Threads'):
                                _thread_no = float(_data[1])
                                break
                    f.close()

                    # for every_pid in pid:
                    #     try:
                    #         every_pid = int(every_pid)
                    #     except:
                    #         continue
                    #     cmd_result = lo_cli.run_cmd(self.cmd_process_mem_in_proc.format(pname_pid=str(every_pid)))
                    #     if not cmd_result:
                    #         continue
                    #     _temp = str(cmd_result).split('\n')
                    #     if len(_temp) < 2:
                    #         continue
                    #     __vm_size = _temp[0].split(':')[1].strip()
                    #     __vm_rss = _temp[1].split(':')[1].strip()
                    #     __thread_no = _temp[2].split(':')[1].strip()
                    #     if __vm_size[-2:].lower() == 'kb':
                    #         __vm_size = __vm_size[0:-2]
                    #     if __vm_rss[-2:].lower() == 'kb':
                    #         __vm_rss = __vm_rss[0:-2]
                    #     _vm_size = float(_vm_size) + float(__vm_size.strip())
                    #     _vm_rss = float(_vm_rss) + float(__vm_rss.strip())
                    #     _thread_no = float(_thread_no) + float(__thread_no.strip())

                # return_result.update({str(pname) + '_vmsize': float(_vm_size)})
                # return_result.update({str(pname) + '_res': float(_vm_rss)})
                # return_result.update({str(pname) + '_thread_num': float(_thread_no)})
                _mem_result.update({str(pname) + '_vmsize': float(_vm_size)})
                _mem_result.update({str(pname) + '_res': float(_vm_rss)})
                _thread_result.update({str(pname) + '_TNO': float(_thread_no)})

            except Exception as e:
                logger.debug("pname=%s,result=%s,e=%s" % (pname, str(_mem_result), traceback.format_exc()))
                continue
        return (_mem_result, _thread_result)

    def basic_func(self, cmd, module_name='basic'):
        return_result = collections.OrderedDict()
        time_str = '%s_time#%s' % (module_name, str(time.strftime("%Y%m%d %H:%M:%S")))
        return_result.update({'time': str(time_str).split('#')[1]})

        if 'win32' in sys.platform:
            return return_result
        cmd_result = str(lo_cli.run_cmd(cmd))
        try:
            return_result.update({str(module_name): round(float(cmd_result), 2)})
        except:
            pass
        del cmd_result, time_str
        gc.collect()
        return return_result

    '''chfshan,集成在get_cpu_info中,获取/proc/stat中获取整机的1s的CPU均值,返回dict'''

    def _get_cpu_info_from_proc(self, cpu_avg_interval=1, need_write_to_file=False):
        """
        :param need_write_to_file: [bool] 是否写文件; Ture将处理过的结果写文件，文件格式如下：
            写入文件格式:
                proc_cpu_time#20230101 17:41:37
                cpuall 32.3; cpu0 23.0; cpu1 100.0; cpu2 3.0; cpu3 4.0;
        :return: [dict 或 None] 失败返回None,  dict如：
            {'time':'20230106 10:02:59','cpuall':50,'cpu0':29,'cpu1':89}
        :其他说明: /proc/stat命令输出示例
            [hadoop@node031 ~]$ cat /proc/stat
            cpu  428285167 3121 324125720 2936765262 54942482 0 10855800 6885788 0 0
            cpu0 107910774 818 81598746 735132121 13547049 0 2013385 1743890 0 0
            cpu1 106141224 621 80125854 731988928 14054030 0 5486026 1716306 0 0
            cpu2 106501106 895 80912247 734774937 13769044 0 2671780 1704928 0 0
            cpu3 107732062 785 81488872 734869275 13572358 0 684608 1720663 0 0
            intr 15474248078 16 10 0 0 16498 0 0 0 0 1 0 34 86 0 0 9426894 0 0 0 0 0 0 0 0 0 32010457 0 0 1 44932803 0 2017389566 122490 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
            ctxt 99201334758
            btime 1664353287
            processes 897072053
            procs_running 6
            procs_blocked 0
            softirq 15498361391 2 4174145744 441032 2601041198 0 0 7586067 3028637879 0 1391542173

            /proc/stat中对应的每一位的含义:
            (cpu  428285167 3121 324125720 2936765262 54942482 0 10855800 6885788 0 0 )
            cpu指标	含义	时间单位	备注
            user	用户态时间	jiffies	一般/高优先级，仅统计nice<=0
            nice	nice用户态时间	jiffies	低优先级，仅统计nice>0
            system	内核态时间	jiffies
            idle	空闲时间	    jiffies	不包含IO等待时间
            iowait	I/O等待时间	jiffies	硬盘IO等待时间
            irq	    硬中断时间	jiffies
            softirq	软中断时间	jiffies
            steal	被盗时间	    jiffies	虚拟化环境中运行其他操作系统上花费的时间（since Linux 2.6.11）
            guest	来宾时间	    jiffies	操作系统运行虚拟CPU花费的时间(since Linux 2.6.24)
            guest_nice	nice来宾时间	jiffies	运行一个带nice值的guest花费的时间(since Linux 2.6.33)

        """
        return_result = collections.OrderedDict()
        time_str = 'proc_cpu_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))

        return_result.update({'time': str(time_str.split('#')[1])})

        result_dict = lo_cli.get_cpu_usage(interval=cpu_avg_interval)

        result = time_str + '\n'
        for (key, value) in result_dict.items():
            if str(key) == 'time':
                continue
            if float(value) > 100.00:  # cpu超过100时，处理成=100
                value = 100.00
            if float(value) < 0:
                value = 0.00
            result = str(result) + str(key) + " " + str(value) + '; '
            return_result.update({key: value})
        if need_write_to_file:
            _write_to_file(self.record_file_path + 'org_file_proc_cpu.txt', data=result + '\n', as_append=True)
        '''
        写入文件数据举例:
        proc_cpu_time: Mon Oct 18 03:01:54 UTC 2021 --------------------------->
        cpuall 0.5 ;cpu0 0.0 ;cpu1 0.0 ;
        返回数据举例:
        {'cpuall':0.5,'cpu0':0.0,'cpu1':0.0}
        '''
        # return_result = collections.OrderedDict()
        # return_result.update({'time': str(time_str.split('#')[1])})
        # result = self.parse_data_to_dict_format(result, data_type='proc_cpu')
        # return_result.update(result)

        return return_result

    '''chfshan,集成在get_network_info中,带宽单位byte,获取每秒的pps和流量等网络信息,获取渠道:/proc/net/dev,返回字典'''

    def _get_bindwidth_info_from_proc(self, get_in_remote=False, remote_server_client=None, need_one_time_org_data=False,
                                      process_pid='', process_display_name_flag='', interval=1):
        """从proc中获取每秒网络情况,获取渠道'/proc/net/dev'
        :param process_display_name_flag: [string] 进程带宽,key中的前缀
        :param need_one_time_org_data: [bool] 取一次原始的数据,进程时使用,上报到监控平台自行算出每秒的数据
        :param process_pid: [int] 进程id,某个进程带宽
        :param get_in_remote:[bool] 是否从远程获取带宽数据
        :param need_write_to_file: [bool] 获取的结果是否写文件, True: 写入org_file_proc_network.txt
            写入文件内容举例:
                proc_network_time#20230106 12:10:59
                # Get current record
                # Inter-|   Receive                                                |  Transmit
                # face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
                # em1: 17482  141589    0  858    0     0          0    107916   1466      17    0    0    0     0       0          0
                # lo: 110161  275376    0    0    0     0          0         0 166571  275376    0    0    0     0       0          0

        :return:[dict], 整机示例如下:
            {'time':'20230106 10:02:59','em1_rxpck':1555,'em1_txpck','em1_rxbw':1555,'em1_txbw':1555,'em1_txerr/s':1555,'em1_rxerr/s':1555,
            'em1_rxdrop/s':1555,'em1_txdrop/s':1555,
            'lo_rxpck':1555,'lo_txpck','lo_rxbw':1555,'lo_txbw':1555,'lo_txerr/s':1555,'lo_rxerr/s':1555,'lo_rxdrop/s':1555,'lo_txdrop/s':1555}


        :usage:
            print(_get_bindwidth_info_from_proc())

            remote_server = SSHConnection(host='192.168.130.113',port=22,username='root',password='grandstream.')
            print(_get_bindwidth_info_from_proc(get_in_remote=True,remote_ssh_conn=remote_server))
            print(_get_bindwidth_info_from_proc(get_in_remote=True,remote_ssh_conn=remote_server,process_pid=1234,process_display_name_flag='mysql'))

            {'time':'20231102 18:17:48','mysql_lo_rxbw':0,'mysql_lo_txbw':0,'mysql_lo_rxpck':0,'mysql_lo_txpck':0,'mysql_lo_rxerr':0,'mysql_lo_txerr':0,
            'mysql_lo_rxdrop':0,'mysql_lo_txdrop':0,'mysql_enp1s0_rxbw':392,'mysql_enp1s0_txbw':1180,'mysql_enp1s0_rxpck':2,'mysql_enp1s0_txpck':2,
            'mysql_enp1s0_rxerr':0,'mysql_enp1s0_txerr':0,'mysql_enp1s0_rxdrop':0,'mysql_enp1s0_txdrop':0}


        :其他说明: '/proc/net/dev'命令输出示例
            # Get current record
            # Inter-|   Receive                                                |  Transmit
            # face |bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
            # em1: 17482  141589    0  858    0     0          0    107916   1466      17    0    0    0     0       0          0
            # lo: 110161  275376    0    0    0     0          0         0 166571  275376    0    0    0     0       0          0
        """

        return_result = collections.OrderedDict()
        time_str = 'proc_bindwidth_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str.split('#')[1])})

        _cmd = '/proc%s/net/dev' % ('/' + str(process_pid))
        _pre_bw_data = None
        _after_bw_data = None

        if get_in_remote and remote_server_client:
            cmd = 'cat ' + _cmd + " ; sleep 1 ; echo '###split###' ; " + 'cat ' + _cmd
            _data = remote_server_client.run_cmd(cmd=cmd, need_run_with_sudo=True)
            if remote_server_client.error_code != ERROR_CODE_SUCCESS:
                return return_result
            _data = str(_data).split('###split###')
            # logger.critical((_data[0],_data[-1]))
            _pre_bw_data = _data[0]
            _after_bw_data = _data[-1]

        def _get_data(proc_data=None):
            result = {}
            iface_name = 0
            rx_bw = 1
            tx_bw = 9
            rx_pck = 2
            tx_pck = 10
            rx_err = 3
            tx_err = 11
            rx_drop = 4
            tx_drop = 12
            try:
                _h_file = None
                if not proc_data:
                    _h_file = open(_cmd, 'r')
                    proc_data = _h_file.readlines()
                else:
                    proc_data = proc_data.split('\n')
                for _lines in proc_data:
                    try:
                        _line = _lines.split()
                        # logger.critical(_line)
                        if len(_line) < 12:
                            continue
                        _pre_flag = process_display_name_flag + '_' + str(process_pid) + '_' + str(
                            _line[iface_name][0:-1]) if process_display_name_flag else str(_line[iface_name][0:-1])
                        result.update({_pre_flag + '_rxbw': int(_line[rx_bw])})
                        result.update({_pre_flag + '_txbw': int(_line[tx_bw])})
                        result.update({_pre_flag + '_rxpck': int(_line[rx_pck])})
                        result.update({_pre_flag + '_txpck': int(_line[tx_pck])})
                        result.update({_pre_flag + '_rxerr': int(_line[rx_err])})
                        result.update({_pre_flag + '_txerr': int(_line[tx_err])})
                        result.update({_pre_flag + '_rxdrop': int(_line[rx_drop])})
                        result.update({_pre_flag + '_txdrop': int(_line[tx_drop])})
                    except Exception:
                        logger.debug((_lines, process_display_name_flag, process_pid, traceback.format_exc()))
                _h_file.close()
            except:
                pass
            return result

        _et = _st = time.time()
        dictFirstRecord = None
        if interval != 'auto':
            dictFirstRecord = _get_data(proc_data=_pre_bw_data)
            if need_one_time_org_data:
                return dictFirstRecord
            if not get_in_remote:
                time_sleep(1 - (time.time() - _st))
        else:
            if len(self.last_data['bw']) == 2:
                dictFirstRecord = self.last_data['bw'][1]
                interval = _et - self.last_data['bw'][0]

        dictLastRecord = _get_data(proc_data=_after_bw_data)

        self.last_data['bw'] = (time.time(), dictLastRecord)

        for (key, value) in dictLastRecord.items():
            try:
                return_result.update({key: round((int(value) - int(dictFirstRecord[key])) / interval, 2)})
            except:
                pass

        # logger.critical(('#####Bindwidth,interval=%s' % str(interval), return_result))

        return return_result

    def get_establish_connections(self, port_id=443, module_name='online_users'):
        return self.basic_func("grep ':%s ' %s|grep -i 'esta'|wc -l" % (str(port_id), self.file_real_time_temp_ss_data),
                               module_name + '_in_' + str(port_id))

    def _get_socketstat_from_proc(self, process_pid='', process_display_name_flag=''):
        return_result = {}

        for _file in ['/proc%s/net/sockstat6' % ('/' + str(process_pid)),
                      '/proc%s/net/sockstat' % ('/' + str(process_pid))]:
            try:
                with open(_file, 'r') as f:
                    datas = f.readlines()
                    for _line in datas:
                        _datas = _line.split()
                        _pre = process_display_name_flag + '_' + str(
                            _datas[0][0:-1]) + '_' if process_display_name_flag else str(_datas[0][0:-1]) + '_'
                        # logger.critical((_datas,_pre))
                        try:
                            for no, _data in enumerate(_datas):
                                if 'used' in _data:
                                    return_result.update({_pre + 'used': int(_datas[no + 1])})
                                if 'inuse' in _data:
                                    return_result.update({_pre + 'inuse': int(_datas[no + 1])})
                                if 'orphan' in _data:
                                    return_result.update({_pre + 'fin_wait': int(_datas[no + 1])})
                                if 'tw' in _data:
                                    return_result.update({_pre + 'time_wait': int(_datas[no + 1])})
                                if 'alloc' in _data:
                                    return_result.update({_pre + 'alloc': int(_datas[no + 1])})
                                if 'mem' in _data:
                                    return_result.update({_pre + 'mem': int(_datas[no + 1])})
                        except:
                            pass
                f.close()
            except:
                pass

        logger.debug((return_result))

        return return_result

    '''特定应用程序的支持'''
    '''[20230301] chfshan, jstat -gc pid结果,jmap暂不支持因会暂定住java进程，获取java gc full 次数，gc full的时间，Eden等区内存使用量'''

    def _get_process_java_info(self, interval=60):
        """  jstat -gc pid的结果
        :return: [dict] {'进程名':值}  进程名规则: pname_java_jstatKeyName  如kafka_java_MC, 对yarntask进程做了特殊处理
        :usage:
            monitor = GetServerRealTimeData(Params())
            monitor.pname = ['java#YarnTaskExecutorRunner','kafka']
            print(monitor.get_process_java_info())

            输出结果为:  因大数据需要进程的细节对yarntask进程key做了特殊处理
            {'time':'20230330 07:02:11', 'kafka_java_EU':463872.0, 'kafka_java_YGC':33008.0, 'kafka_java_FGC':0.0,
            'kafka_java_OC:388096.0, 'kafka_java_S1C':1024.0, 'kafka_java_S0C':0.0, 'kafka_java_CCSC':7168.0,
            'kafka_java_MC':58624.0, 'kafka_java_CCSU':6411.6, 'kafka_java_OU':202008.3, 'kafka_java_FGCT':0.0,
            'kafka_java_EC':659456.0, 'kafka_java_GCT':856.719, 'kafka_java_YGCT':856.719, 'kafka_java_MU':51385.3,
            'kafka_java_S0U':0.0, 'kafka_java_S1U':1024.0,
            'java#yarntaskexecutorrunner_java_application_1679386548259_0063/container_e208_1679386548259_0063_01_000005_OC':3066880.0,
            'java#yarntaskexecutorrunner_java_application_1679386548259_0063/container_e208_1679386548259_0063_01_000005_S0U':0.0.......}

        :补充：
            hadoop@node032 ~]$ jstat -gc 32256
            S0C      S1C    S0U     S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC  YGCT    FGC   FGCT    GCT
            17152.0 17152.0 297.7   0.0   137728.0 112721.0  344064.0  11969.3  43964.0 43019.2  5112.0 4846.9  6   0.149   2    0.022   0.171

            名字解释:
            S0C	第一个幸存区的大小  Survivor Space0 capacity
            S1C	第二个幸存区的大小  Survivor Space1 capacity
            S0U	第一个幸存区的使用大小 Survivor Space0 used
            S1U	第二个幸存区的使用大小 Survivor Space1 used
            EC	伊甸园区的大小  Eden Space capacity
            EU	伊甸园区的使用大小  Eden Space used
            OC	老年代大小  Old Space capacity
            OU	老年代使用大小 Old Space used
            MC	方法区大小   永久代Meta Space capacity
            MU	方法区使用大小 永久代Meta Space used
            CCSC	压缩类空间大小  永久代Class Space capacity
            CCSU	压缩类空间使用大小  永久代Class Space capacity
            YGC	年轻代垃圾回收次数  Young GC
            YGCT	年轻代垃圾回收消耗时间  Young GC Time
            FGC	老年代垃圾回收次数  Full GC
            FGCT	老年代垃圾回收消耗时间  Full GC Time
            GCT	垃圾回收消耗总时间


        """
        return_result = {}

        '''本机不支持mysql'''
        if str(self.client_params.pname_list).lower().find('java') == -1 or self._app_info['jstat']['state'] is False:
            return return_result

        '''无上一次的数据,添加'''
        if not self.last_data.get('java'):
            self.last_data.update({'java': {'time': time.time(), 'data': {}}})

        '''设了interval但时间未到'''
        if interval and self.last_data.get('java') and time.time() - interval < int(
                self.last_data['java'].get('time')):
            # logger.critical(('waiting......'))
            return self.last_data['java'].get('data')

        '''首次调, 初始化jstat命令行'''
        if self._app_info['jstat']['state'] is None:
            self._app_info['jstat']['state'] = False
            _jstat_cmd = lo_cli.run_cmd("su - `whoami` -c 'which jstat'", need_run_with_sudo=True)
            if lo_cli.error_code == ERROR_CODE_SUCCESS:
                self._app_info['jstat']['state'] = True
                self._app_info['jstat']['cmd'] = _jstat_cmd.strip() + ' '
            else:
                lo_cli.run_cmd('/usr/local/jdk/bin/jstat -help')
                if lo_cli.error_code == ERROR_CODE_SUCCESS:
                    self._app_info['jstat']['state'] = True
                    self._app_info['jstat']['cmd'] = "/usr/local/jdk/bin/jstat "

            self._app_info['jstat']['cmd'] = str(self._app_info['jstat']['cmd']) + ' -gc {pid}'
            _cmd_process_java_jmap = str(self._app_info['jstat']['cmd']).replace('jstat', 'jmap')


            # if lo_cli.error_code != ERROR_CODE_SUCCESS or not _jstat_cmd:
            #     lo_cli.run_cmd('/usr/local/jdk/bin/jstat -help')
            #     self._app_info['jstat']['cmd'] = '/usr/local/jdk/bin/jstat '
            # if lo_cli.error_code == ERROR_CODE_SUCCESS:
            #     self._app_info['jstat']['state'] = True
            #     self._app_info['jstat']['cmd'] = _jstat_cmd.strip()
            #     self.cmd_process_java_jstat = _jstat_cmd + ' -gc {pid}'
            #     self.cmd_process_java_jmap = str(self.cmd_process_java_jstat).replace('jstat', 'jmap')

        time_str = 'java_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str).split('#')[1]})

        '''chfshan,暂未使用，jmap会暂停住进程,改为使用jstat'''
        # def get_jmap_by_pid(pname, pid):
        #     return_value = {}
        #     cmd_result = str(lo_cli.run_cmd(_cmd_process_java_jmap.format(pid=str(pid)), need_run_with_sudo=True,
        #                                      ))
        #     if lo_cli.error_code != 0:
        #         return False
        #     else:
        #         cmd_result = str(cmd_result).lower().strip().replace(' ', '')
        #         _young_old_space_flag = cmd_result.split('younggeneration')[-1].split('\n')
        #         _label_flag = '_edenspace'
        #         for _line in _young_old_space_flag:
        #             _value_flag = ''
        #             key_name = ''
        #             try:
        #                 _line = str(_line).lower().strip().replace(' ', '')
        #                 if _line.find('space:') != -1 and _line.find('=') == -1 and _line.find('used') == -1:
        #                     _label_flag = '_' + _line.replace(':', '') + '_'
        #                 _value_flag = _line.split('=')
        #                 if len(_value_flag) != 2:
        #                     continue
        #                 key_name = pname + _label_flag + _value_flag[0]
        #                 if str(pname).lower().find('yarntask') != -1:
        #                     # logger.critical((self._display_pname_per_pid,_label_flag,_value_flag,pid))
        #                     key_name = pname + '_java_jmap_' + self._display_pname_per_pid[pid] + _label_flag + _value_flag[0]
        #                 return_value.update({key_name: round(int(_value_flag[-1].split('(')[0]) / 1024 / 1024, 2)})
        #             except Exception:
        #                 logger.critical((pid, pname, _value_flag, key_name, _line, traceback.format_exc()))
        #                 continue
        #
        #         return return_value
        '''chfshan, jstat -gc pid获取单个进程的信息'''

        def get_jstat_by_pid(pname, pid):
            '''
            每个进程的jstat -gc 的结果
            :param pname: [string] 进程名
            :param pid: [int] 进程id
            :return: [dict] {'经过处理的进程名':值}
            '''
            return_value = {}
            cmd_result = str(
                lo_cli.run_cmd(str(self._app_info['jstat']['cmd']).format(pid=str(pid)), need_run_with_sudo=True, ))
            if lo_cli.error_code != 0:
                return False
            else:
                cmd_result = str(cmd_result).strip()
                _jstat_value_flag = cmd_result.split('\n')
                if len(_jstat_value_flag) < 2:
                    return False
                _temp_title = _jstat_value_flag[0].split()
                _temp_value = _jstat_value_flag[1].split()
                for i, data in enumerate(_temp_title):
                    _value_flag = ''
                    key_name = ''
                    try:
                        key_name = pname + '_java_' + data.strip()
                        if str(pname).lower().find('yarntask') != -1:
                            # logger.critical((self._display_pname_per_pid,_label_flag,_value_flag,pid))
                            key_name = pname + '_java_' + str(
                                self._display_pname_per_pid[str(pid)]) + '_' + data.strip()
                        return_value.update({key_name: float(_temp_value[i])})
                    except Exception:
                        logger.warning((pid, self._display_pname_per_pid, pname, _value_flag, key_name, data,
                                        traceback.format_exc()))
                        continue
                del cmd_result, _jstat_value_flag, _temp_title, _temp_value

            return return_value

        for pname in self.pname:
            pid = None
            try:
                pid = self.pid_per_pname_dict[pname][0]
                pid = int(pid)
            except:
                continue
            pid = [pid]
            if str(pname).lower().find('yarntask') != -1:
                pid = self.pid_per_pname_dict[pname]
            for _pid in pid:
                _result = get_jstat_by_pid(pname=pname, pid=_pid)
                # logger.critical((_result,_pid,pid,pname,self._display_pname_per_pid))
                if _result:
                    return_result.update(_result)
                else:
                    continue

        self.last_data.update({'java': {'time': time.time(), 'data': return_result}})
        return return_result

    '''kamailio共享内存大小(单位MB)，连接数信息'''
    def _get_kamailio_shmmem(self, ):
        """

        :return:
        :cmd_result_readme:
             [ec2-user@ip-10-2-254-237 ~]$ /opt/kamailio/sbin/kamcmd core.tcp_info
            {
                readers: 5
                max_connections: 102400
                max_tls_connections: 102400
                opened_connections: 151
                opened_tls_connections: 130
                write_queued_bytes: 0
            }

            opened_connections 表达：tcp/tls/wss 连接总数
            opened_tls_connections 表达：tls/wss 连接总数

            细分连接：
            sbc 查看客户端的tls 客户端 & cloudUCM TLS trunk)
            ss -tn sport = :5061 | tail -n +2 | wc -l

            sbc 查看客户端的tcp 客户端 & cloudUCM TCP trunk)
            ss -tn sport = :5060 | tail -n +2 | wc -l

            sbc 查看客户端的wss 客户端
            ss -tn sport = :3000 | tail -n +2 | wc -l
        """
        return_result = collections.OrderedDict()

        if self._app_info['kamailio']['state'] is None:
            lo_cli.run_cmd("/opt/kamailio/sbin/kamcmd -V",need_run_with_sudo=True)

            if lo_cli.error_code == ERROR_CODE_SUCCESS:
                self._app_info['kamailio']['state'] = True
                self._app_info['kamailio']['cmd'] = '/opt/kamailio/sbin/kamcmd '
            else:
                self._app_info['kamailio']['state'] = False
        # logger.critical(self._app_info)
        if str(self.pname).lower().find('kamailio') == -1 or self._app_info['kamailio']['state'] is False:
            return return_result


        time_str = 'kamailio_shmmem_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str).split('#')[1]})

        # 获取连接数信息
        _kam_tcp_info_cmd = self._app_info['kamailio']['cmd'] + " core.tcp_info"
        _kam_tcp_info = lo_cli.run_cmd(_kam_tcp_info_cmd)

        for _datas in _kam_tcp_info.split('\n'):
            try:
                _name,_data = _datas.strip().split(':')
                _name = _name.strip().replace(' ','_')
                return_result.update({'kam_tcp_'+_name:int(_data)})
            except Exception as e:
                logger.critical((traceback.format_exc(),_datas))

        _kam_shmmem_cmd = self._app_info['kamailio']['cmd'] + " core.shmmem m|grep -vi '{\|}'|awk -F ':' '{print $1,$2}'"
        _kam_shmmem = str(lo_cli.run_cmd(_kam_shmmem_cmd, need_run_with_sudo=True))

        # 获取共享内存信息
        for i in _kam_shmmem.split('\n'):
            try:
                _name,_data = str(i).split()
                return_result.update({"kam_shmmem_" + _name: float(_data)})
            except Exception:
                logger.warning(traceback.format_exc())

        del time_str
        gc.collect()
        return return_result

    def _get_redis_data(self, cmd=None, module_name='redis', interval=60):
        return_result = {}

        if self._is_support_redis is False:
            return return_result

        _time = time.time()
        '''无上一次的数据,添加'''
        if not self.last_data.get('redis'):
            self.last_data.update({'redis': {'time': _time, 'data': {}}})

        if interval and _time - interval < int(self.last_data['redis'].get('time')) and _time != self.last_data[
            'redis'].get('time'):
            # return return_result
            return self.last_data.get('redis').get('data')
        logger.critical((self.last_data['redis'].get('time'), time, '##################afwefwefwaef'))
        '''首次调, 初始化redis命令行'''
        if self._is_support_redis is None:
            self._is_support_redis = False
            _reids_cmd = lo_cli.run_cmd("su - `whoami` -c 'which redis-cli'", need_run_with_sudo=True)
            if lo_cli.error_code != ERROR_CODE_SUCCESS or not _reids_cmd:
                lo_cli.run_cmd('/usr/local/redis/bin/redis-cli -v')
                _reids_cmd = '/usr/local/redis/bin/redis-cli '
            if lo_cli.error_code != ERROR_CODE_SUCCESS or not _reids_cmd:
                lo_cli.run_cmd('/usr/local/redis/src/redis-cli -v')
                _reids_cmd = '/usr/local/redis/src/redis-cli '
            if lo_cli.error_code != ERROR_CODE_SUCCESS or not _reids_cmd:
                lo_cli.run_cmd('/gwn/bin/redis/bin/redis-cli -v')
                _reids_cmd = '/gwn/bin/redis/bin/redis-cli '
            if lo_cli.error_code == ERROR_CODE_SUCCESS:
                self._is_support_redis = True
                self._cmd_redis = _reids_cmd.strip()
        if cmd:
            # return_result = self.basic_func(cmd=cmd, module_name=module_name)
            _cmd_result = lo_cli.run_cmd(command=cmd)
            try:
                _conn_num = [line for line in _cmd_result.split("\n") if line.isdigit()][0]
                return_result.update({str(module_name): round(float(_conn_num), 2)})
            except Exception:
                pass
            self.last_data.update({'redis': {'time': time.time()}})

        self.last_data.update({'redis': {'time': time.time(), 'data': return_result}})
        logger.critical((return_result, self._is_support_redis))
        return return_result

    def _get_gwn_redis_data(self, interval=60):
        result = {}
        # ap = '/usr/local/redis/src/redis-cli -n 2 keys node:isOnline:*_online|wc -l'
        # client = '/usr/local/redis/src/redis-cli -n 12 keys client:*|wc -l'    --- 不准,改成dbsize（也可用 info keyspace）

        _ap_online = self._get_redis_data(cmd='%s -n 2 -a gwn_local keys node:isOnline:*_online|wc -l' % str(self._cmd_redis),
                                          module_name='gwn_ap_online', interval=interval)
        result.update(_ap_online)
        # _client_online = self._get_redis_data(cmd='%s -n 12 keys client:*|wc -l' % str(self._cmd_redis), module_name='gwn_client_online',interval=0)
        # result.update(_client_online)

        self.last_data['redis']['data'].update(result)

        # self.last_data.update({'redis': {'time':time.time()}})
        return result

    def get_kafka_data(self, kafka_public_ip=None, kafka_ssh_user='hadoop', kafka_ssh_pwd='123456',
                       server_type_keywords=None, interval=None):
        """

        :param kafka_public_ip:
        :param kafka_ssh_user:
        :param kafka_ssh_pwd:
        :param server_type_keywords: [list] server_type的要求, server_type 要求含有list中的所有keywords
        :param interval: [int] 多久获取一次
        :return: [dict]

        """
        return_result = collections.OrderedDict()

        '''还未到监控间隔时间/无要求的关键字/无kafka进程,直接返回'''
        if str(self.pname).lower().find('kafka') == -1:
            return return_result

        if server_type_keywords:
            for keyword in server_type_keywords:
                if str(self.client_params.server_type).find(keyword) == -1:
                    return return_result

        '''无上一次的数据,添加'''
        if not self.last_data.get('kafka'):
            self.last_data.update({'kafka': {'time': time.time(), 'data': {}}})

        '''时间未到，返回上一次的数据'''
        if interval and time.time() - interval < int(self.last_data['kafka'].get('time')):
            # logger.critical(('### not get return',self.last_data.get('kafka'),time.time(),interval))
            return self.last_data.get('kafka').get('data')

        _local_ip = _network.get_local_ip()
        if kafka_public_ip is not None:
            _local_ip = kafka_public_ip
        # kafka_cmd = "sh /usr/local/kafka/bin/kafka-consumer-groups.sh --bootstrap-server %s:9092 --describe --all-groups 2>/dev/null |awk '{if ($4~/^[0-9]/) print $0}'" % str(_local_ip)
        # kafka_cmd = "echo 123456| su - hadoop -c \"sh /usr/local/kafka/bin/kafka-consumer-groups.sh --bootstrap-server %s:9092 --describe --all-groups 2>/dev/null | grep -v TOPIC \"" % str(_local_ip)
        kafka_cmd = 'su - %s -c "/usr/local/kafka/bin/kafka-consumer-groups.sh --bootstrap-server %s:9092 --describe --all-groups 2>/dev/null | grep -v TOPIC"' % (
        kafka_ssh_user, str(_local_ip))

        time_str = 'kafka_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
        return_result.update({'time': str(time_str).split('#')[1]})
        cmd_result = str(lo_cli.run_cmd(kafka_cmd, need_run_with_sudo=True))
        cmd_result = cmd_result.split('\n')
        for i in cmd_result:
            try:
                part = str(i).split()
                if len(part) < 8:
                    continue
                key_name = part[0] + '-' + part[1] + '-' + part[2]
                _cur_key = key_name + '_CURRENT-OFFSET'
                _end_key = key_name + '_LOG-END-OFFSET'
                return_result.update({_cur_key: int(part[3])})
                return_result.update({_end_key: int(part[4])})
                return_result.update({key_name + '_lag': int(part[5])})

                if self.last_data['kafka']['data'].get(_cur_key):
                    return_result.update(
                        {_cur_key + '_offset': int(part[3]) - int(self.last_data['kafka']['data'].get(_cur_key))})
                if self.last_data['kafka']['data'].get(_end_key):
                    return_result.update(
                        {_end_key + '_offset': int(part[4]) - int(self.last_data['kafka']['data'].get(_end_key))})
            except Exception:
                logger.warning("[%s]failed=%s" % (str(i), str(traceback.format_exc())))

        self.last_data.update({'kafka': {'time': time.time(), 'data': return_result}})

        # logger.critical(('### kafka_data',return_result,'#####',self.last_data.get('kafka')))

        return return_result

    def _get_clouducm_mysql_data(self, mysql_username='admin', mysql_pwd='admin', interval=None):
        return_result = {}
        _ucm_mac_list = self.last_data.get('podman').get('name_list')
        if not _ucm_mac_list:
            return return_result
        for _ucm_mac in _ucm_mac_list:
            _cmd = str(self._cmd_mysql) + \
                   ' -h 127.0.0.1 -D%s -e ' % (str(_ucm_mac) + '_master') + \
                   '"select count(1),action_type   from cdr GROUP BY  action_type ;"'
            cmd_result = str(lo_cli.run_cmd(_cmd, need_run_with_sudo=True))
            for data in cmd_result.split('\n'):
                try:
                    _data, _name = data.split()
                    return_result.update({'cdr_' + _ucm_mac + '_' + _name: int(_data)})
                except:
                    pass

        return return_result

    def get_mysql_data(self, mysql_username='admin', mysql_pwd='admin', interval=None):
        """

        :param mysql_username:
        :param mysql_pwd:
        :param interval:
        :return:
        :usage:

        :btw:
        MySQL关键性能指标:连接情况,缓冲池使用情况,每秒查询数,每秒事务数
        thread_cmd 返回结果
        Threadpool_idle_threads	0\nThreadpool_threads	0\nThreads_cached	0\nThreads_connected	237\nThreads_created	80013\nThreads_running	2

        """

        return_result = collections.OrderedDict()
        _time = time.time()

        '''本机不支持mysql'''
        if str(self.client_params.pname_list).lower().find('mysql') == -1 or self._is_support_mysql is False:
            return return_result

        '''首次调, 初始化mysql命令行'''
        if self._is_support_mysql is None:
            _msql_cmd = lo_cli.run_cmd("su - `whoami` -c 'which mysql'", need_run_with_sudo=True)
            if lo_cli.error_code == ERROR_CODE_SUCCESS and _msql_cmd:
                self._is_support_mysql = True
                self._cmd_mysql = _msql_cmd.strip()
            else:
                self._is_support_mysql = False
                return return_result
        '''max_connections:最大连接数'''
        '''innodb_buffer_pool_size:缓冲池大小/B(最多应为物理内存的80%),innodb_buffer_pool_chunk_size块大小,size/chunk_size应<1000'''
        '''innodb_buffer_pool_instance:设置有多少个缓存池,建议为CPU个数'''
        '''slow_query_log:是否开启慢查询日志，1表示开启，0表示关闭'''
        '''thread_cache_size:当客户端断开之后，服务器处理此客户的线程将会缓存起来以响应下一个客户而不是销毁(前提是缓存数未达上限)'''
        '''table_open_cache:缓存下来的表的数量， =最大连接数*表的个数（因为每个连接线程都会创建一个）'''
        '''table_definition_cache:table_share对象(fmr表结构文件)=表的个数（因为所有线程共享）'''
        '''open_files_limit:mysqld可用的最大文件描述符数目,Open_files/open_files_limit<=75,如果你遇到“Too many open files”的错误,应加大它'''
        '''innodb_open_files:InnoDB存储引擎有效，它指定了mysql可以同时打开的最大.ibd文件的数目'''
        '''max_connections*你的表数目 = table_open_cache <=open_files_limit< ulimit -n   innodb_open_files<ulimit -n'''
        '''锁超时 innodb_lock_wait_timeout 事务1持有锁，事务2等待一定时间后返回执行失败'''
        '''事务空闲超时：idle_transaction_timeout事务1开始执行，事务1不干活一段时间后断开连接（客户端代码需要自己重新建立连接）'''
        ''''''
        _cmd_mysql_variables = str(self._cmd_mysql) + \
                               ' -h 127.0.0.1 -e ' + \
                               '"show variables where ' + \
                               "Variable_name like '%max_c%' or " + \
                               "Variable_name like '%innodb_buffer_pool_%size' or " + \
                               "Variable_name like '%open%' or " + \
                               "Variable_name like '%log_bin' or " + \
                               "Variable_name like '%slow_query%' or " + \
                               "Variable_name like '%thread_%' or " + \
                               "Variable_name like '%table_%'" + \
                               ';"'

        '''无上一次的数据,添加'''
        if not self.last_data.get('mysql'):
            # _time = time.time()
            self.last_data.update({'mysql': {'time': _time, 'time_static_config': _time, 'static_data': str(
                lo_cli.run_cmd(_cmd_mysql_variables, need_run_with_sudo=True)), 'static_dict_data': {}, 'data': {}}})

        '''mysql配置,每隔24小时更新发一次'''
        if _time - 21600 >= int(self.last_data['mysql'].get('time_static_config')) or _time == self.last_data[
            'mysql'].get('time_static_config'):
            _result = {}
            logger.info('6Hours,update mysql variables')
            cmd_result = str(lo_cli.run_cmd(_cmd_mysql_variables, need_run_with_sudo=True))
            # self.last_data['mysql']['static_data'] = cmd_result
            for _line_data in cmd_result.split('\n'):
                try:
                    _name, _data = str(_line_data).split()
                    if 'table_' in _name or 'open_files' in _name or 'max_connections' in _name or 'thread_ca' in _name:
                        _result.update({str(_name): round(float(_data), 2)})
                    # _item = str(i).split()
                    # # logger.critical(_item)
                    # if len(_item) == 2 and ('table_open_cache' in _item[0] or 'open_files' in _item[0]):
                    #     return_result.update({str(_item[0]): round(float(_item[1]), 2)})
                    # if len(_item) == 2 and (_item[0] == 'log_bin'):
                    #     log_bin_open = 1
                    #     if _item[1] == 'OFF':
                    #         log_bin_open = 0
                    #     return_result.update({str(_item[0] + '_is_open'): log_bin_open})
                    if _name == 'log_bin':
                        log_bin_open = 0 if _data == 'OFF' else 1
                        _result.update({'log_bin_is_open': log_bin_open})
                    if _name == 'slow_query_log':
                        slow_query_log_is_open = 0 if _data == 'OFF' else 1
                        _result.update({'slow_query_log_is_open': slow_query_log_is_open})
                except:
                    pass

            self.last_data['mysql'].update(
                {'static_data': cmd_result, 'time_static_config': _time, 'data': _result, 'static_dict_data': _result})

        '''设了interval但时间未到'''
        if interval and time.time() - interval < int(self.last_data['mysql'].get('time')):
            # return return_result
            return self.last_data.get('mysql').get('data')

        _processlist_cmd = str(
            self._cmd_mysql) + ' -h 127.0.0.1 -e "select count(*) from information_schema.processlist where COMMAND not like \'%%Sleep%%\' and INFO not like \'%%information_schema.processlist%%\';" |awk "{print $2}"|awk "NR==2 {print}"'

        '''Innodb_buffer_pool缓冲池满会读磁盘,Innodb_buffer_pool_reads的值较大,可能缓冲池的大小不足或者热数据没有被缓存到缓冲池'''
        '''Innodb_buffer_pool_wait_free: >0，缓冲池设置过小'''
        '''inddb缓冲池命中率应>99:Innodb_buffer_pool_read_requests/(pool_read_requests+pool_reads+pool_read_ahead)'''
        '''slow_qu慢查询的次数,慢查询的时间看show variables'''
        '''Com_sele等select/update/delete/update的总次数,可用于计算QPS-query查询率'''
        '''Com_commit等commit/rollback的总次数,可用于计算TPS-事务数'''
        '''Max_used_connections:过去的最大连接数应<max_connections,不然有1040-Too many connections,理想设置:Max_used_connections/max_connections ≈ 85'''
        '''Opened_tables:打开过的表数量,过大,说明配置的table_[open]_cache值可能太小'''
        '''Open_tables:打开表的数量,Open_tables/Opened_tables=85,Open_tables/table_open_cache=95'''
        '''Open_files:打开文件数,Open_files/open_files_limit<=75'''
        '''Table_locks_waited：表级等待争用发生等待的次数，高说明存在较严重表级锁争取问题，应优化(如减少锁、加索引等)，Table_locks_immediate/Table_locks_waited应趋向于0,>5000采用InnoDB引擎，因InnoDB是行锁而MyISAM是表锁，对于高并发写入的应用InnoDB效果会好些。示例中的服务器Table_locks_immediate / Table_locks_waited = 235，MyISAM就足够了。'''
        '''Innodb_row_lock_waits/times/time_avg:等待总次数/总时长/平均时长,次数高时长长要优化'''
        '''Threads_created表示创建过的线程数,如Threads_created值过大,MySQL服务器一直在创线程,耗资源,可适当增加配置:thread_cache_size如65'''
        '''Handler_read_rnd_next:在数据文件中读下一行的请求数。表扫描率=Handler_read_rnd_next/Com_select>4000,说明进行了太多表扫描，很有可能索引没有建好，增加read_buffer_size值会有一些好处，但最好不要超过8MB,如果你正进行大量的表扫描，该值较高。通常说明你的表索引不正确或写入的查询没有利用索引。'''
        '''Handler_read_key:走索引的次数，如果这个值比较大，说明索引使用良好'''

        _status_cmd = str(self._cmd_mysql) + \
                      ' -h 127.0.0.1 -e ' + \
                      '"show status where ' + \
                      "Variable_name like 'thread%' or " + \
                      "Variable_name like 'Innodb_buffer_pool%' or " + \
                      "Variable_name like 'Innodb_row_lock%' or " + \
                      "Variable_name like '%slow_qu%' or " + \
                      "Variable_name like '%slow_qu%' or " + \
                      "Variable_name like '%Handler_read%' or " + \
                      "Variable_name like '%max_use%' or " + \
                      "Variable_name like 'Que%' or " + \
                      "Variable_name like 'open%_tables' or " + \
                      "Variable_name like '%table_locks%' or " + \
                      "Variable_name like 'Com_sele%' or Variable_name like 'Com_up%' or Variable_name like 'Com_in%' or Variable_name like 'Com_comm%' or Variable_name like 'Com_del%' or Variable_name like 'Com_rol%' " + \
                      ';"'  # "|awk '{print $1 $2}'|awk 'NR!=1{print}'"

        try:
            time_str = 'mysql_time#%s' % str(time.strftime("%Y%m%d %H:%M:%S"))
            return_result.update({'time': str(time_str).split('#')[1]})
            if 'win32' in sys.platform:
                raise Exception('not support')
            cmd_result = str(lo_cli.run_cmd(_processlist_cmd, need_run_with_sudo=True))
            return_result.update({str("mysql_process_list"): round(float(cmd_result), 2)})

            cmd_result = str(lo_cli.run_cmd(_status_cmd, need_run_with_sudo=True))
            cmd_result = cmd_result.split('\n')
            for _line_data in cmd_result:
                try:
                    __name, __data = str(_line_data).split()
                    return_result.update({__name: round(float(__data), 2)})
                except:
                    pass
            _app_data = self._get_clouducm_mysql_data(mysql_username=mysql_username, mysql_pwd=mysql_pwd,
                                                      interval=interval)
            return_result.update(_app_data)
        except Exception:
            logger.warning(("failed=%s" % str(traceback.format_exc()), self._is_support_mysql))

        self.last_data['mysql'].update({'time': _time, 'data': return_result})
        return_result.update(self.last_data['mysql'].get("static_dict_data"))  # 叠入6个小时一轮询的静态数据

        return return_result

    def _get_ucmrc_info(self):

        _cmd_kami_ssh_conn = "grep 'kamailio' %s|grep -i 'estab'|grep -v ':6380 \|:5061 '|wc -l" % (
            self.file_real_time_temp_ss_data)
        _cmd_turnnel_num = "grep sshd %s | grep -v ':%s ' |grep -i 'listen'|wc -l" % (
        self.file_real_time_temp_ss_data, str(self.client_params.local_ssh_port))
        _cmd_tls_client = "grep ':5061 ' %s|grep -i 'esta'|wc -l" % (self.file_real_time_temp_ss_data)
        _cmd_websocket_client = "grep ':443 ' %s|grep -i 'esta'|wc -l" % (self.file_real_time_temp_ss_data)

        websocket_client = lo_cli.run_cmd(_cmd_websocket_client)
        tls_client = lo_cli.run_cmd(_cmd_tls_client)
        turnnel_num = lo_cli.run_cmd(_cmd_turnnel_num)
        kami_ssh_conn = lo_cli.run_cmd(_cmd_kami_ssh_conn)

        try:
            turnnel_num = float(turnnel_num) / 2
        except:
            logger.warning('get turnnel num failed')
            turnnel_num = 0
        try:
            websocket_client = float(websocket_client)
        except:
            logger.warning('get websocket_client num failed')
            websocket_client = -1
        try:
            tls_client = float(tls_client)
        except:
            tls_client = -1
        try:
            kami_ssh_conn = float(kami_ssh_conn)
        except:
            kami_ssh_conn = -1

        return {'ucmrc_tls_online': tls_client, 'ucmrc_websocket_online': websocket_client,
                'ucmrc_turnnel_online': turnnel_num, 'ucmrc_kamai_ssh_conn': kami_ssh_conn}

    def _get_mcu_nvidia_info(self):
        self._execute_cmd_and_write_file(self.cmd_nvidia_smi, self.nvidia_smi_org)

    def _get_mcu_nvidia_dmon_info(self):
        self._execute_cmd_and_write_file(self.cmd_nvidia_dmon, self.nvidia_dmon_org)

    def _get_docker_data(self, app_interval=300):
        _res = self._get_podman_data(need_asterisk=False, app_interval=app_interval, sevice='docker')
        # logger.warning(('get_docker', _res))
        return _res

    # [chfshan]2023.12.15
    def _get_podman_data(self, need_asterisk=True, app_interval=300, sevice='podman'):
        """
        podman指标获取:资源消耗,podman容器数,podman中应用程序的情况
        :param need_asterisk:[bool] 是否需要获取容器中ak应用程序的指标
        :param app_interval:
        :return:
        :usage:
        :podman常用命令:
            podman ps -a  #查看运行中的容器情况,如容器id 容器占用端口
            podman stats  #查看运行中容器的资源消耗
            podman exec -it 619bdfa816a4 /bin/bash  #进入容器
            podman exec -it 619bdfa816a4 /app/asterisk/sbin/asterisk -rx 'pjsip show contacts' #容器中ak的在线用户数
            podman exec -it 619bdfa816a4 /app/asterisk/sbin/asterisk -rx 'core show channels'     #容器中ak的线路数
            会议:1个会议2个用户
            [root@localhost ~]# podman  exec -it 000B85000020 /app/asterisk/sbin/asterisk -rx 'core show channels'
            Channel                        Location             State   Application(Data)
            CBAnn/90706051-00000000;2      s@default:1          Up      (None)
            CBAnn/90706051-00000000;1      s@default:1          Up      (None)
            PJSIP/1000-00000000            s@sub-dial-conferenc Up      ConfBridge(90706051,,,sfu_admi
            PJSIP/1001-00000001            s@sub-dial-conferenc Up      ConfBridge(90706051,,,sfu_user
            4 active channels
            2 of 500 max active calls ( 0.40% of capacity)
            3 calls processed
            Asterisk ending (0).
            p2p时,caller+callee算1个channel
        """

        return_result = {}
        if str(self.client_params.pname_list).lower().find(
                'containermanager') == -1 or self._app_info[sevice]['state'] is False:
            return return_result
        if self._app_info[sevice]['state'] is None:
            self._app_info[sevice]['state'] = False
            _cmd = lo_cli.run_cmd("%s -v" % sevice, need_run_with_sudo=True)
            if lo_cli.error_code == ERROR_CODE_SUCCESS:
                self._app_info[sevice]['state'] = True
                self._app_info[sevice]['cmd'] = sevice + ' '

        _time = time.time()
        '''无上一次的数据,添加'''
        if not self.last_data.get(sevice):
            # _time = time.time()
            self.last_data.update({sevice: {'time': _time, 'data': {}, 'name_list': []}})

        '''设了interval但时间未到'''
        if app_interval and time.time() - app_interval < int(self.last_data[sevice].get('time')):
            # return return_result
            return self.last_data.get(sevice).get('data')

        _container_id_list = []

        def _get_container_info_from_ps():
            __container_id_list = []
            _get_container_cmd = '%s ps -a' % sevice

            _containers = lo_cli.run_cmd(command=_get_container_cmd, need_run_with_sudo=True)
            if lo_cli.error_code != ERROR_CODE_SUCCESS:
                return __container_id_list

            for _data in _containers.split('\n'):
                _data_line = _data.split()
                if len(_data_line) > 2 and len(_data_line[0]) == 12:
                    __container_id_list.append(_data_line[0])
            return __container_id_list

        def _change_bw_to_MB(data):

            # units = {
            #     'bit': 1,
            #     'B': 8,
            #     'Byte': 8,
            #     'kb': 8 * 1024,
            #     'KB': 8 * 1024,
            #     'kB': 8 * 1024,
            #     'mb': 8 * 1024 * 1024,
            #     'MB': 8 * 1024 * 1024,
            #     'GB': 8 * 1024 * 1024 * 1024
            # }
            return_result = 0
            data = data.lower()
            result = re.findall('\d+\s*.\d+', data)  # \d数字+1个或多个\s空白*0个或多个
            if len(result) > 0:
                return_result = float(result[0])
            if 'g' in data:
                return_result = return_result * 1024  # *1024*1024*1024
            elif 'm' in data:
                return_result = return_result  # *1024*1024
            elif 'k' in data:
                return_result = return_result / 1024
            else:
                return_result = return_result / 1024 / 1024
            return round(return_result, 2)

        # 单位MB
        def _get_container_info_from_stats():
            __id_list = []
            __stats_data = {}
            __name_list = []
            # _get_container_cmd = 'podman stats --no-stream --format json'
            # if lo_cli.error_code != ERROR_CODE_SUCCESS:
            #     return __id_list,__stats_data
            # if _containers.startswith('['):
            #     _containers = _containers[1:-1]
            # _containers = json.loads(_containers)
            # logger.critical(list(_containers))
            # for _data in list(_containers):
            #     try:
            #         _container_id = str(_data.get('id'))
            #         if len(_container_id) == 12:
            #             __id_list.append(_container_id)
            #         else:
            #             continue
            #
            #         __stats_data.update({_container_id+'_cpu_percent':_data.get('cpu_percent')[:-1]})
            #         __stats_data.update({_container_id+'_mem_percent':_data.get('mem_percent')[:-1]})
            #         __stats_data.update({_container_id+'_avg_cpu':_data.get('avg_cpu')[:-1]})
            #         net_rx,net_tx = (_data.get('net_io')).split('/')
            #         __stats_data.update({_container_id + '_net_rx':_change_bw_to_MB(net_rx),_container_id + '_net_tx':_change_bw_to_MB(net_tx)})
            #         mem_use, mem_total = (_data.get('mem_usage')).split('/')
            #         __stats_data.update({_container_id + '_mem_used': _change_bw_to_MB(mem_use),
            #                              _container_id + '_mem_total': _change_bw_to_MB(mem_total)})
            #
            #         block_io_read, block_io_write = (_data.get('block_io')).split('/')
            #         __stats_data.update({_container_id + '_block_io_read': _change_bw_to_MB(block_io_read),
            #                              _container_id + '_block_io_write': _change_bw_to_MB(block_io_write)})
            #     except:pass

            """
            [
                 {
                  "id": "021ee94c7462",
                  "name": "000B85000010",
                  "cpu_time": "12m47.901722s",
                  "cpu_percent": "1.01%",
                  "avg_cpu": "1.01%",
                  "mem_usage": "113MB / 1.787GB",
                  "mem_percent": "6.33%",
                  "net_io": "33.16MB / 27.42MB",
                  "block_io": "19.67GB / 532.9MB",
                  "pids": "263"
                 },
                 {
                  "id": "42193e418c6d",
                  "name": "000B33333333",
                  "cpu_time": "16m22.095179s",
                  "cpu_percent": "1.16%",
                  "avg_cpu": "1.16%",
                  "mem_usage": "147.5MB / 1.787GB",
                  "mem_percent": "8.25%",
                  "net_io": "81.29MB / 155.8MB",
                  "block_io": "30.15GB / 575.1MB",
                  "pids": "267"
                 },
            ]

            """

            _get_container_cmd = self._app_info[sevice]['cmd'] + ' stats --no-stream --format "table {{.ID}},{{.Name}},{{.CPUPerc}},{{.MemPerc}},{{.MemUsage}},{{.BlockIO}},{{.NetIO}}"'
            """
            ID,NAME,CPU %,MEM %,MEM USAGE / LIMIT,BLOCK IO,NET IO
            021ee94c7462,000B85000010,1.01%,6.44%,115.1MB / 1.787GB,33.1GB / 543.1MB,38.05MB / 31.27MB
            42193e418c6d,000B33333333,1.16%,8.31%,148.5MB / 1.787GB,47.12GB / 585.1MB,86.54MB / 159.9MB
            63e292d909cb,000B85000053,1.01%,6.28%,112.2MB / 1.787GB,39.86GB / 534.1MB,33.58MB / 27.74MB
            c114fe4a3971,000B85000069,1.11%,12.20%,217.9MB / 1.787GB,72.86GB / 681.3MB,204.9MB / 338.8MB
            d49c03b3eb07,000B22222222,1.02%,7.76%,138.7MB / 1.787GB,35.65GB / 625.9MB,55.56MB / 76.77MB
            d7dea0a43ae3,000B11111111,1.09%,12.56%,224.5MB / 1.787GB,73.88GB / 1.067GB,84.04MB / 197.3MB
            """

            _containers = str(lo_cli.run_cmd(command=_get_container_cmd, need_run_with_sudo=True)).strip()
            # if lo_cli.error_code != ERROR_CODE_SUCCESS:
            #     return __id_list,__stats_data
            logger.critical(_containers)
            for _data in _containers.split('\n'):
                try:
                    _data_line = _data.split(',')
                    if len(_data_line) > 6 and len(_data_line[0]) == 12 and not str(_data_line[0]).startswith('CONTAINER'): # 兼容docker
                        __id_list.append(_data_line[0])
                        __name_list.append(_data_line[1])

                    else:
                        continue
                    _flag = _data_line[1]
                    __stats_data.update({_flag + '_cpu_percent': _data_line[2][:-1]})
                    __stats_data.update({_flag + '_mem_percent': _data_line[3][:-1]})
                    # __stats_data.update({_container_id+'_avg_cpu':_data.get('avg_cpu')[:-1]})
                    net_rx, net_tx = str(_data_line[6]).split('/')
                    __stats_data.update(
                        {_flag + '_net_rx': _change_bw_to_MB(net_rx), _flag + '_net_tx': _change_bw_to_MB(net_tx)})
                    mem_use, mem_total = str(_data_line[4]).split('/')
                    __stats_data.update({_flag + '_mem_used': _change_bw_to_MB(mem_use),
                                         _flag + '_mem_total': _change_bw_to_MB(mem_total)})

                    block_io_read, block_io_write = str(_data_line[5]).split('/')
                    __stats_data.update({_flag + '_block_io_read': _change_bw_to_MB(block_io_read),
                                         _flag + '_block_io_write': _change_bw_to_MB(block_io_write)})
                except:
                    pass
            return __id_list, __stats_data, __name_list

        _container_id_list, podman_perf_data, _container_name_list = _get_container_info_from_stats()
        return_result.update({'container_no': len(_container_id_list)})
        return_result.update(podman_perf_data)
        logger.critical(('#####', 'container_name_list', _container_name_list, _container_id_list, podman_perf_data))

        def _get_asterisk_call_data(data):
            _return_data_active_channel = 0
            _return_data_call_process = 0
            _return_data_calls = 0
            _data = data.split('\n')
            for _data_line in _data:
                if 'active channel' in _data_line:
                    _return_data_active_channel = _data_line.split()[0]
                if 'call proce' in _data_line or 'calls proce' in _data_line:
                    _return_data_call_process = _data_line.split()[0]
                if 'active call' in _data_line:
                    _return_data_calls = _data_line.split()[0]

            return _return_data_active_channel, _return_data_calls, _return_data_call_process

        def _get_asterisk_online_data(data):
            _return_data_users = 0
            _data = data[-80:].split('\n')
            for _data_line in _data:
                if 'Objects found' in _data_line:
                    _return_data_users = _data_line.split()[-1]

            return _return_data_users

        _online_user_cmd = self._app_info[sevice]['cmd'] + " exec -it %s /app/asterisk/sbin/asterisk -rx 'pjsip show contacts'"
        _calls_cmd = self._app_info[sevice]['cmd'] + " exec -it %s /app/asterisk/sbin/asterisk -rx 'core show channels'"

        if str(self.client_params.pname_list).lower().find('asterisk') != -1 and need_asterisk is True:
            for _index, _container_id in enumerate(_container_id_list):
                try:
                    _flag = _container_name_list[_index]
                    _calls_result = lo_cli.run_cmd(_calls_cmd % str(_container_id), need_run_with_sudo=True)
                    (channels, calls, last_calls) = _get_asterisk_call_data(_calls_result)
                    return_result.update({_flag + '_ak_channels': int(channels)})
                    # return_result.update({_container_id+'_ak_last_calls':int(last_calls)})
                    return_result.update({_flag + '_ak_calls': int(calls)})
                    _user_result = lo_cli.run_cmd(_online_user_cmd % str(_container_id), need_run_with_sudo=True)
                    result = _get_asterisk_online_data(_user_result)
                    return_result.update({_flag + '_ak_online_user': int(result)})
                except:
                    pass

        self.last_data.update(
            {sevice: {'time': time.time(), 'data': return_result, 'name_list': _container_name_list}})
        logger.critical(('#####', 'return_result', return_result))

        return return_result

    def _get_clouducm_rtpEngine_info(self):
        """

        :return:
        :cmd result readme:
        [ec2-user@ip-10-2-254-237 ~]$ /opt/rtpengine/bin/rtpengine-ctl -ip 127.0.0.1:2224 list numsessions
        Current sessions own: 5
        Current sessions foreign: 0
        Current sessions total: 5
        Current transcoded media: 0
        Current sessions ipv4 only media: 4
        Current sessions ipv6 only media: 0
        Current sessions ip mixed  media: 0
            /*------查看sbc 呼叫情况-------*/
            /opt/rtpengine/bin/rtpengine-ctl -ip 127.0.0.1:2224 list numsessions
            Current sessions total 呼叫总数（注意挂断后，会延后30s还在统计）
        """
        return_result = {}

        if self._app_info['rtpengine']['state'] is None:
            lo_cli.run_cmd("/opt/rtpengine/bin/rtpengine-ctl -h",need_run_with_sudo=True)

            if lo_cli.error_code == ERROR_CODE_SUCCESS:
                self._app_info['rtpengine']['state'] = True
                self._app_info['rtpengine']['cmd'] = '/opt/rtpengine/bin/rtpengine-ctl '
            else:
                self._app_info['rtpengine']['state'] = False

        _rtpe_numsessions_cmd = "/opt/rtpengine/bin/rtpengine-ctl -ip 127.0.0.1:2224 list numsessions"


        if str(self.client_params.pname_list).lower().find('rtpe') != -1:
            _rtpe_numsessions = lo_cli.run_cmd(_rtpe_numsessions_cmd)
            for _datas in _rtpe_numsessions.split('\n'):
                try:
                    _name,_data =  _datas.strip().split(':')
                    _name = _name.strip().replace(' ','_')
                    return_result.update({'rtpe_'+_name:int(_data)})
                except Exception:
                    logger.critical((_datas,traceback.format_exc()))

        return return_result

class _Params():
    '''
    usage:
    params = params()
    params.client_user_pwd = P@ssword1234
    params.set_params()

    set_params: 尝试读取ini文件中配对的初始化参数，无ini文件，设定默认值
    '''

    def __init__(self, test_duration=3600 * 24 * 365, monitor_interval=5, local_listen_port=9101,
                 platform=['local', 'aws', 'vps'], run_mode='p_client'):
        self.test_duration = test_duration
        self.monitor_interval = monitor_interval
        self.local_listen_port = local_listen_port

        # self.monitor_server_info = []
        # self.remote_client_dict_info = []
        self.pname_list = []
        self.server_type = ''
        self.platform = platform
        self.thread_id = ''
        self.run_mode = run_mode
        self.remote_server_object = None

        self.local_host = _network.get_local_ip()
        # self.local_ssh_pwd = None
        # self.local_ssh_user = None
        self.local_ssh_port = None
        self.local_output_path = PYTHON_FILE_PATH
        self.local_output_file = PYTHON_FILE_NAME

        self.remote_host = None
        self.remote_output_file_name = None
        self.remote_output_file_path = None
        self.remote_python_start_cmd = None
        self.remote_client_dict_info = None
        self.remote_client_run_mode = None
        self.remote_current_path = None


def _init_global_var_and_options():
    GLOBAL_VAR.SERVER_TYPE = ''  # 服务器的类型
    GLOBAL_VAR.pname_list = []  # 监控的进程列表['comet', 'logic', 'business', 'discovery', 'job', 'mysqld','redis-server','ssh']  #监控的进程名,若外面未传，使用该默认值
    GLOBAL_VAR.MONITOR_INTERVAL = 15  # 监控取数据的间隔
    GLOBAL_VAR.TEST_TOTAL_TIME = 3600 * 24 * 365  # 监控脚本运行时长，单位s,若外面未传，使用该默认值,1年
    GLOBAL_VAR.RUN_MODE = 'p_client'
    GLOBAL_VAR.PLATFORM = ['local', 'aws', 'vps', 'pre_online']

    parser = OptionParser()
    # parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
    #                   help="have or not have,make lots of noise")
    parser.add_option("-l", "--lowperformance", action="store_true", dest="low_performance",
                      help="have or not have,make lots of noise")
    parser.add_option('-L', '--logconsolelevel', action="store", dest='log_console_level',
                      help='log in console level, 0/critical/fatal - CRITICAL,1/error --- ERROR,2/warning,3/info --INFO,4 debug,5 notset')
    parser.add_option('-F', '--logfilelevel', action="store", dest='log_file_level',
                      help='log in file level, 0/critical/fatal - CRITICAL,1/error --- ERROR,2/warning,3/info --INFO,4 debug,5 notset')

    parser.add_option('-M', '--runmode', action="store", dest='run_mode',
                      help='run mode, client/server/controller/p_client client mode ,server mode')
    parser.add_option('-T', '--runtotaltime', action="store", dest='run_time', help='run total time, seconds')
    # parser.add_option('-t','--servicetype', action="store", dest='service_type',help='server_type, asterisk/ucm')
    # parser.add_option('-P', '--needmonitorport', action="store", dest='need_monitor_port', help='monitor port list')
    parser.add_option('-p', '--needmonitorpname', action="store", dest='need_monitor_pname', help='monitor pname list')
    parser.add_option('-t', '--servertype', action="store", dest='server_type', help='server type')
    parser.add_option('-i', '--monitorinterval', action="store", dest='monitor_interval', help='server type')

    try:
        (options, args) = parser.parse_args()

        if options.log_console_level:
            _log_console_level = str(options.log_console_level).lower()
            if _log_console_level == '0' or _log_console_level == 'critical' or _log_console_level == 'fatal' or _log_console_level == str(
                    logging.CRITICAL):
                GLOBAL_VAR.LOG_CONSOLE_LEVEL = 'CRITICAL'
                # LOG_FILE_LEVEL = 'CRITICAL'
            if _log_console_level == '1' or _log_console_level == 'error' or _log_console_level == str(logging.ERROR):
                GLOBAL_VAR.LOG_CONSOLE_LEVEL = 'ERROR'
                # LOG_FILE_LEVEL = 'ERROR'
            if _log_console_level == '2' or _log_console_level == 'warning' or _log_console_level == str(
                    logging.WARNING):
                GLOBAL_VAR.LOG_CONSOLE_LEVEL = 'WARNING'
                # LOG_FILE_LEVEL = 'WARNING'
            if _log_console_level == '3' or _log_console_level == 'info' or _log_console_level == str(logging.INFO):
                GLOBAL_VAR.LOG_CONSOLE_LEVEL = 'INFO'
            if _log_console_level == '4' or _log_console_level == 'debug' or _log_console_level == str(logging.DEBUG):
                GLOBAL_VAR.LOG_CONSOLE_LEVEL = 'DEBUG'
            if _log_console_level == '5' or _log_console_level == 'notset' or _log_console_level == str(logging.NOTSET):
                GLOBAL_VAR.LOG_CONSOLE_LEVEL = 'NOTSET'
            GLOBAL_VAR.console_handler.setLevel(GLOBAL_VAR.LOG_CONSOLE_LEVEL)
        if options.log_file_level:
            _log_file_level = str(options.log_file_level).lower()
            if _log_file_level == '0' or _log_file_level == 'critical' or _log_file_level == 'fatal':
                GLOBAL_VAR.LOG_FILE_LEVEL = 'CRITICAL'
            if _log_file_level == '1' or _log_file_level == 'error':
                # LOG_CONSOLE_LEVEL = 'ERROR'
                GLOBAL_VAR.LOG_FILE_LEVEL = 'ERROR'
            if _log_file_level == '2' or _log_file_level == 'warning':
                # LOG_CONSOLE_LEVEL = 'WARNING'
                GLOBAL_VAR.LOG_FILE_LEVEL = 'WARNING'
            if _log_file_level == '3' or _log_file_level == 'info':
                # LOG_CONSOLE_LEVEL = 'INFO'
                GLOBAL_VAR.LOG_FILE_LEVEL = 'INFO'
            if _log_file_level == '4' or _log_file_level == 'debug':
                # LOG_CONSOLE_LEVEL = 'DEBUG'
                GLOBAL_VAR.LOG_FILE_LEVEL = 'DEBUG'
            if _log_file_level == '5' or _log_file_level == 'notset':
                # LOG_CONSOLE_LEVEL = 'NOTSET'
                GLOBAL_VAR.LOG_FILE_LEVEL = 'NOTSET'
            file_handler.setLevel(GLOBAL_VAR.LOG_FILE_LEVEL)
        if options.run_mode:
            GLOBAL_VAR.RUN_MODE = str(options.run_mode).lower()
            if str(options.run_mode)[0] == "'" or str(options.run_mode)[0] == '"':
                GLOBAL_VAR.RUN_MODE = str(options.run_mode)[1:-1].strip().lower()
        if options.run_time:

            GLOBAL_VAR.TEST_TOTAL_TIME = options.run_time
            if str(options.run_time)[0] == "'" or str(options.run_time)[0] == '"':
                GLOBAL_VAR.TEST_TOTAL_TIME = str(options.run_time)[1:-1].strip().lower()
        if options.need_monitor_pname or str(options.need_monitor_pname).strip() == '':
            GLOBAL_VAR.pname_list = str(options.need_monitor_pname).lower()
            if len(GLOBAL_VAR.pname_list) > 0 and (
                    str(options.need_monitor_pname)[0] == "'" or str(options.need_monitor_pname)[0] == '"'):
                GLOBAL_VAR.pname_list = str(options.need_monitor_pname)[1:-1].strip().lower()
        if options.server_type:
            GLOBAL_VAR.SERVER_TYPE = str(options.server_type).lower()
            if str(options.server_type)[0] == "'" or str(options.server_type)[0] == '"':
                GLOBAL_VAR.SERVER_TYPE = str(options.server_type)[1:-1].strip().lower()
        if options.low_performance:
            GLOBAL_VAR.LOW_PERFORMANCE = True
        if options.monitor_interval:
            GLOBAL_VAR.MONITOR_INTERVAL = int(options.monitor_interval)

        # if options.need_monitor_port:
        #     MONITOR_LISTEN_PORT_LIST = str(options.need_monitor_port).lower()
        #     if str(options.need_monitor_port)[0] == "'" or str(options.need_monitor_port)[0] == '"':
        #         MONITOR_LISTEN_PORT_LIST = str(options.need_monitor_port)[1:-1].strip().lower()
        # if options.service_type:
        #     MONITOR_SERVICE_TYPE_LIST = str(options.service_type).lower()
        #     if str(options.service_type)[0] == "'" or str(options.service_type)[0] == '"':
        #         MONITOR_SERVICE_TYPE_LIST = str(options.service_type)[1:-1].strip().lower()
    except Exception as e:
        logger.error('deal_option - failed=%s' % str(traceback.format_exc()))


'''会过滤掉没有publib_ip以及ssh_port的服务器'''


def _get_server_info_from_csv(test_platform=['local'],
                             csv_file_list=[os.path.join(DATA_FILE_PATH, 'test_server_info.csv'),
                                            os.path.join(DATA_FILE_PATH, 'server_info.csv')]):
    """

    :param test_platform:
    :param server_info_csv_file_path:
    :param server_info_csv_file:
    :return: 返回字典，key为元组 (ip,ssh_port,'pnamelist')  #pnamelist为解决csv中重复问题,通过pname解决key一致导致被覆盖问题
    {('139.180.186.253', '22', ''): {'owner': 'xlzhou', 'platform': 'vps', 'product': 'vps_script', 'region': 'singapore', 'service': 'T_1', 'public_ip': '139.180.186.253', 'local_ip': '139.180.186.253', 'ipv6': '', 'ssh_user': 'root', 'ssh_pwd': 'qN[8S!p#*+XQGx5(', 'ssh_port': '22', 'domain': '', 'domain_port': '', 'dns': '', 'mac': '', 'pname_list': '', 'description': 'VPS_ucmrc_perf*', 'no': 1},

    """

    if type(test_platform) == 'string':
        test_platform = [test_platform]
    result = {}
    # 从csv中过滤信息
    _no = 0
    _csv_map = {
        'public_ip': 'public_ip',
        'ssh_port': 'ssh_port',
        'ssh_user': 'ssh_user',
        'ssh_pwd': 'ssh_pwd',
        'pname_list': 'pname_list',
        'service': 'service',
        'product': 'product',
        'platform': 'platform',
    }
    for csv_file in csv_file_list:
        try:
            h_file = open(csv_file, 'r')
            f = h_file.readlines()
            import csv
            common_datas = csv.DictReader(f,
                                          fieldnames=None,
                                          restkey=None,
                                          restval=None,
                                          dialect='excel')
            h_file.close()
            for data in common_datas:
                if str(data.get(_csv_map['platform'])).lower().strip() not in test_platform or not data.get(
                        _csv_map['public_ip']) or not data.get(_csv_map['ssh_port']):
                    continue
                _no = _no + 1
                data.update({'no': _no})
                # result.append(dict(data))
                result.update({(str(data[_csv_map['public_ip']]), str(data[_csv_map['ssh_port']]),
                                str(data[_csv_map['pname_list']])): dict(data)})

        except Exception as e:
            logger.warning("read csv data failed=%s" % str(e))
    return result


def _run_cmd_in_remote(remote_server=None, client_dict_info=None, cmd=None, need_run_with_sudo=True,
                      is_remote_support_sudo=None):
    """
    cmd_kill_monitor = "kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}')" % PYTHON_FILE_NAME
    cmd_check_monitor = "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}'" % PYTHON_FILE_NAME
    cmd_check_node_exporter = "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}'" % 'node_exporter'
    cmd_kill_node_exporter = "kill -9 $(ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep %s|grep -v grep|awk '{print $2}')" % 'node_exporter'
    cmd_rm_all_file = "rm -rf %s" % (os.path.join(str(remote_server.exec_command('pwd')).strip(),REMOTE_WORK_PATH)+"*").replace('\\','/').replace('/*','*')
    """
    result = None
    try:
        if len(client_dict_info) <= 1:
            return False
        if not remote_server:
            remote_server = _RemoteServerManager(client_dict_info['public_ip'], client_dict_info['ssh_port'])
        if need_run_with_sudo:
            result = remote_server.run_cmd(cmd, need_run_with_sudo=True)
        else:
            result = remote_server.run_cmd(cmd)
    except Exception as e:
        logger.critical('run_cmd_in_remote - falied=%s' % str(e))

    return result


def _run_cmd_after_exit_handle(signum, frame):
    # signal.signal(signal.SIGTERM, run_cmd_after_exit_handle)  # 请求中止进程，kill命令缺省发送   # 信号捕捉程序必须在循环之前设置
    # signal.signal(signal.SIGINT, run_cmd_after_exit_handle)  # 由Interrupt Key产生，通常是CTRL+C或者DELETE产生的中断
    # # signal.signal(signal.SIGKILL, run_cmd_after_exit_handle) # 由kill  -9 产生，这个信号无法被捕捉或忽略，不能使用
    logger.error("I will dead for be killed or ctrl+c, signum=[%s]" % (str(signum)))
    sys.exit(0)


class _PromethusSimulator():
    REGISTRY = {}

    def __init__(self, registry=None, name=None, label_name=None, p_type='Gauge'):
        self.doc_lable_name = '#doc#'
        if not registry:
            self.registry = self.REGISTRY
        self.name = name
        self.label_name = label_name
        self._type = p_type

    def generate_latest(self):
        document = ''
        title_line = "# HELP {0} {1}\n# TYPE {0} {2}\n"
        content = '%(name)s%(label)s %(label_vaule)s\n'  # PYTHON_CPU_LOAD{cpu_load="cpu_load_5"} 1.35
        for name, name_value in self.REGISTRY.items():
            # logger.critical((name,name_value))
            document += title_line.format(name, self.REGISTRY[name][self.doc_lable_name],
                                          str(self.REGISTRY[name]['p_type']).lower())
            for label_name, label_value in name_value.items():
                if label_name == self.doc_lable_name or label_name == 'p_type':
                    continue
                document += content % {'name': name, 'label': label_name, 'label_vaule': label_value}
        return document

    def labels(self, **kargs):
        a = '%(label)s="%(label_vaule)s"'
        label_value = '{'
        for key, value in dict(**kargs).items():
            label_value = label_value + a % {'label': key, 'label_vaule': value} + ','
        label_value = label_value[0:-1] + '}'
        self.__class__.REGISTRY[self.name].update({label_value: None})
        l1 = self.__class__(name=self.name, label_name=label_value)
        return l1

    def set(self, value):
        self.__class__.REGISTRY[self.name][self.label_name] = value

    def Gauge(self, name, document, labelnames, p_type='Gauge'):
        self.__class__.REGISTRY.update({name: {}})
        self.REGISTRY[name].update({self.doc_lable_name: document})
        self.REGISTRY[name].update({'p_type': p_type})
        # logger.critical(self.REGISTRY[name])
        self._type = p_type
        return self.__class__(name=name, label_name=labelnames, p_type=p_type)

    def Counter(self, name, document, labelnames):
        return self.Gauge(name=name, document=document, labelnames=labelnames, p_type='Counter')

    def CollectorRegistry(self):
        return True

    def clear(self):
        # try:
        #     for i in self.label_name:
        #         logger.critical(self.REGISTRY[self.name])
        #         self.REGISTRY[self.name].pop[i]
        # except Exception as e:
        #     logger.critical(e)
        try:
            self.REGISTRY.update({self.name: {self.doc_lable_name: '', 'p_type': self.REGISTRY[self.name]['p_type']}})
        except Exception as e:
            logger.critical((e, self.REGISTRY))


class _RunMonitor():
    PROME_OBJECT = None

    def __init__(self):
        # threading.Thread.__init__(self)
        # self.monitor_args = monitor_args
        self._need_print_log = True

    def run_client(self):
        logger.info('monitor.StartMonitor - start')

        params_realtime = _Params()
        params_realtime.pname_list = GLOBAL_VAR.pname_list
        params_realtime.server_type = GLOBAL_VAR.SERVER_TYPE
        # params_realtime.port_list = MONITOR_LISTEN_PORT_LIST
        # params_realtime.client_service_type = MONITOR_SERVICE_TYPE_LIST

        params_basic = _Params()  # 必须初始化类，不然类的属性会混乱，python类传的是地址
        params_basic.pname_list = GLOBAL_VAR.pname_list
        params_basic.server_type = GLOBAL_VAR.SERVER_TYPE
        # params_basic.port_list = MONITOR_LISTEN_PORT_LIST
        # params_basic.client_service_type = MONITOR_SERVICE_TYPE_LIST
        out_put = os.path.join(params_basic.local_output_path, params_basic.local_host + '_monitor_output').replace(' ',
                                                                                                                    '').replace(
            '\\', '/')
        if os.path.exists(out_put + '_old'):
            import shutil
            shutil.rmtree(out_put + '_old', ignore_errors=True)
            os.system('rm -rf %s' % out_put + '_old')
        if os.path.exists(out_put):
            os.rename(out_put, out_put + '_old')
        logger.critical('RunMonitor.run_client - create path %s' % str(out_put))
        os.mkdir(out_put)
        lo_cli.run_cmd('service firewalld stop & service iptables stop', need_run_with_sudo=True)
        lo_cli.run_cmd('firewall-cmd --add-port=9100/tcp --permanent & firewall-cmd --add-port=9101/tcp --permanent',
                       need_run_with_sudo=True)
        client = _GetServerBasicData(client_params=params_basic)
        client.run()
        client_1 = _GetRealTimeData(client_params=params_realtime)
        # client_1.do_run()

    def run_prometheus_client(self, monitor_interval=5, LOCAL_LISTEN_PORT=9101, ):
        logger.info('[run as prometheus_python_client mode')
        _prome_result = {}
        server_real_data = None
        client_basic_info = None
        p_basic = None

        try:
            self._init_promethus_client()
            self._start_http_server(listen_port=LOCAL_LISTEN_PORT)

            prome_params_realtime = _Params()
            prome_params_realtime.pname_list = GLOBAL_VAR.pname_list
            prome_params_realtime.server_type = GLOBAL_VAR.SERVER_TYPE
            prome_params_realtime.monitor_interval = GLOBAL_VAR.MONITOR_INTERVAL
            server_real_data = _GetRealTimeData(prome_params_realtime, low_performance=GLOBAL_VAR.LOW_PERFORMANCE)
            server_real_data._enable_ss = False
            # client_basic_info = GetServerBasicData(client_params=copy.deepcopy(prome_params_realtime))
            server_real_data.run_for_get_all_datas(kafka_interval=60, db_interval=60, interval=monitor_interval,
                                                   need_write_to_file=False)
            # _prome_realtime_key_map = {
            #     'cpu':"PYTHON_ALL_CPU",
            #     'cpu_load':'PYTHON_CPU_LOAD',
            #     'memory':'PYTHON_MEMORY',
            #     'ss':'PYTHON_NETSTAT',  #含process的
            #     'io':'PYTHON_IO',
            #     'sockstat':'PYTHON_SOCKSTAT',
            #     'bindwidth':'PYTHON_BINDWIDTH',
            #     'p_cpu':'PYTHON_PROCESS_CPU',
            #     'p_memory':'PYTHON_PROCESS_MEMORY',
            #     'p_thread_num':'PYTHON_PROCESS_THREAD_NUM',
            #     'p_pid':'PYTHON_PROCESS_PID',
            #     'p_num':'PYTHON_PROCESS_NUM',
            #     'app_java':'PYTHON_APP_JAVA',
            #     'app_mysql':'PYTHON_APP_MYSQL',
            #     'app_redis':'PYTHON_APP_REDIS',
            #     'app_kafka':'PYTHON_APP_KAFKA',
            #     'app_asterisk':'PYTHON_APP_ASTERSIK',
            #     'app_kamailio':'PYTHON_APP_KAMAILIO',
            #     'app_project':'PYTHON_APP_project',
            #
            #     # 'PYTHON_APP_UCMRC': None,
            #     # 'PYTHON_APP_GWN': None,
            # }

            # p_basic = self.PROME_OBJECT.Gauge('node_basic_info', 'SERVER_BASIC_INFO',
            #                                   ['python_version', 'java_version', 'lscpu', 'os_version',
            #                                    'im_version', 'gdms_version', 'uname_a', 'kamailio_gs_version', 'ulimit',
            #                                    'sysctl', 'mysql_var'])  # 'nodename', 'sysname',
            p_basic = self.PROME_OBJECT.Gauge('node_basic_info', 'BASIC', ['mysql'])
            for realtime_key in server_real_data.all_datas.keys():
                _key_map = 'PY_' + 'P_' + str(realtime_key[2:]).upper() if realtime_key.startswith(
                    'p_') else 'PY_' + str(realtime_key).upper()
                _prome_object = self.PROME_OBJECT.Gauge(str(_key_map), _key_map, [realtime_key])
                _prome_result.update({realtime_key: _prome_object})

            # for realtime_key,prome_key in _prome_realtime_key_map.items():
            #     value = self.PROME_OBJECT.Gauge(str(prome_key), prome_key, [realtime_key])
            #     _prome_result.update({realtime_key:value})
        except Exception:
            logger.critical(traceback.format_exc())

        _start_time = _et = time.time()
        __report_info = {}
        _loop = 0

        while _et - _start_time - 10 < int(GLOBAL_VAR.TEST_TOTAL_TIME):

            # import linecache
            # import tracemalloc
            # tracemalloc.start()
            if _loop % int(720 / monitor_interval) == 0:  # 12小时后更新一次,0次时更新
                try:
                    time.sleep(2)
                    # p_basic.labels(python_version=lo_cli.get_python_version(),
                    #                java_version='',
                    #                uname_a=str(lo_cli.run_cmd('uname -a')),
                    #                lscpu=str(lo_cli.run_cmd('lscpu')),
                    #                im_version='',
                    #                gdms_version='',
                    #                os_version=lo_cli.get_os_system_version(),
                    #                kamailio_gs_version='',
                    #                ulimit=str(lo_cli.run_cmd("ulimit -a")),
                    #                sysctl=str(lo_cli.run_cmd("sysctl -a  2>/dev/null|grep -E 'rmem|wmem'")),
                    #                mysql_var=server_real_data.last_data.get('mysql').get('static_data'), ).set(1.0)
                    p_basic.labels(mysql='').set(1.0)
                except:
                    pass

            _loop = _loop + 1
            __st = time.time()
            logger.critical(('###all_datas=', server_real_data.all_datas))
            for realtime_key, realtime_value in server_real_data.all_datas.items():
                try:
                    if realtime_value.get('time'):
                        realtime_value.pop('time')
                    if not realtime_value:
                        continue
                    prome_object = _prome_result.get(realtime_key)

                    # logger.critical((prome_object.__class__.__name__,prome_object._type,realtime_key,type(realtime_value[list(realtime_value.keys())[0]]),list(realtime_value.keys())[0],realtime_value))
                    if prome_object is None or \
                            (prome_object and (
                                    prome_object.__class__.__name__ == "Gauge" or prome_object._type == 'Gauge') and type(
                                realtime_value[list(realtime_value.keys())[0]]) == dict):
                        # logger.critical('aaaaaaaaaa')
                        _key_map = 'PY_' + 'P_' + str(realtime_key[2:]).upper() if realtime_key.startswith(
                            'p_') else 'PY_' + str(realtime_key).upper()
                        if type(realtime_value[list(realtime_value.keys())[0]]) == dict:
                            _prome_object = self.PROME_OBJECT.Counter(str(_key_map), _key_map, [realtime_key, "mode"])
                        else:
                            _prome_object = self.PROME_OBJECT.Gauge(str(_key_map), _key_map, [realtime_key])
                        _prome_result.update({realtime_key: _prome_object})

                    prome_object.clear()  # 清理缓存
                    # if 'app_' not in str(realtime_key):
                    #     prome_object.clear()

                    for (key, _data) in realtime_value.items():
                        if type(_data) == dict:
                            # if prome_object.__class__.__name__ == "Gauge":
                            #     prome_object.clear()
                            #     _key_map = 'PY_' + 'P_' + str(realtime_key[2:]).upper() if realtime_key.startswith(
                            #         'p_') else 'PY_' + str(realtime_key).upper()
                            #     _prome_object = self.PROME_OBJECT.Counter(str(_key_map), _key_map, [realtime_key,"mode"])
                            #     _prome_result.update({realtime_key: _prome_object})
                            _data = _data.items()
                        else:
                            _data = [_data]
                        # logger.critical(('#####', type(_data),_data))
                        # logger.critical((_data,realtime_key,realtime_value))
                        _key = repr(str(key).encode('utf-8')).strip('b')[1:-1] # 兼容python2中不存在b''格式
                        for _per_data in _data:
                            try:
                                __data = _per_data[1] if type(_per_data) == tuple and len(_per_data) == 2 else _per_data
                                __data = __data[0] if type(__data) == list and len(__data) > 0 else __data
                                # logger.critical((key, realtime_key,_data,__data,type(_per_data)))
                                if type(__data) == list or not bool(
                                        re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$').match(
                                                str(__data))):  # or not str(__data).isdigit():
                                    continue
                                # __report_info.update({str(key): __data})
                                # logger.critical(('prome_object.labels(%s="%s").set(round(float(%s),2))' % (realtime_key,key,str(__data))))
                                # logger.critical((type(realtime_value[key])))
                                if type(realtime_value[key]) == dict:
                                    eval('prome_object.labels(%s="%s",mode="%s").set(round(float(%s),2))' % (
                                        realtime_key, _key, _per_data[0], str(__data)))
                                else:
                                    eval('prome_object.labels(%s="%s").set(round(float(%s),2))' % (
                                    realtime_key, _key, str(__data)))
                            except Exception:
                                logger.critical((traceback.format_exc()))
                except (BaseException, Exception):
                    logger.critical(('error', traceback.format_exc()))
            _et = time.time()
            _sleep_time = monitor_interval - (_et - __st)

            if _sleep_time > 0:
                logger.warning('monitor will sleep(%ss).......' % str(_sleep_time))
                time.sleep(_sleep_time)
            gc.collect()
            logger.warning('monitor sleep(%ss) end.......' % str(_sleep_time))
            os.nice(0)
            # snapshot = tracemalloc.take_snapshot()
            # display_top(snapshot)

        logger.critical(('prome exit,MONITOR_SYSTEM exit', GLOBAL_VAR.TEST_TOTAL_TIME))

        __report_info = {}

    def _init_promethus_client(self):

        for i in range(0, 2):
            try:
                prometheus_client = import_third_module('prometheus_client')
                self.PROME_OBJECT = prometheus_client
                import prometheus_client
                # from prometheus_client import start_http_server, CollectorRegistry, Gauge
                break
            except:
                pass
        # os.system('wget https://github.com/prometheus/node_exporter/releases/download/v0.17.0/node_exporter-0.17.0.linux-amd64.tar.gz')
        # basic = Gauge('node_uname_info', 'SERVER_BASIC_INFO',['nodename', 'sysname'], registry=reg) #grafana自带的格式
        # basic.labels(nodename="localhost.localdomain", sysname="Linux").set(1.0)  # grafana 默认图表使用
        try:
            self.PROME_OBJECT.CollectorRegistry()
        except Exception as e:
            logging.debug(
                'import third monitor - prometheus_client failed,start run with local simulator promethus client')
            self.PROME_OBJECT = _PromethusSimulator(registry={})
            self.PROME_OBJECT_PERF_INDEX = _PromethusSimulator(registry={})

    '''[2022.7.19] add by chfshan, 在本机启动一个http服务器,监听prome的http请求'''

    def _start_http_server(self, listen_port=9101, _need_init_env=True):
        """在本机启动一个http服务器,监听prome的http请求,响应存储在prome中的所有数据
        :param listen_port: [int]本地监听端口
        :return: 无
        """
        start_result_flag = False
        start_error_msg = ''
        try:
            from BaseHTTPServer import HTTPServer
            from BaseHTTPServer import BaseHTTPRequestHandler
            from urlparse import parse_qs, urlparse
            from SocketServer import ThreadingMixIn, ThreadingTCPServer, StreamRequestHandler, BaseRequestHandler

        except ImportError:
            # Python 3
            from http.server import HTTPServer
            from http.server import BaseHTTPRequestHandler
            from urllib.parse import parse_qs, quote_plus, urlparse
            from socketserver import ThreadingMixIn, ThreadingTCPServer, StreamRequestHandler, BaseRequestHandler

        # prometheus_client = cls.PROME_OBJECT

        '''因ThreadedHTTPServer存在问题，暂时未用'''

        class PromeHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    request_url = urlparse(self.path).path
                    _output = ''
                    if str(request_url).endswith('etrics'):
                        # self.send_response(200) #会不断的打印日志
                        # self.send_response_only(200)  # python2不支持，替换下面的方法
                        if self.request_version != 'HTTP/0.9':
                            self.wfile.write(
                                ("%s %d %s\r\n" % (self.protocol_version, 200, '')).encode('latin-1', 'strict'))
                        self.send_header('Server', self.version_string())
                        self.send_header('Date', self.date_time_string())
                        hearder = (str('Content-Type'), str('text/plain; version=0.0.4; charset=utf-8'))
                        self.send_header(*hearder)
                        self.end_headers()
                        _output = _RunMonitor.PROME_OBJECT.generate_latest()

                        if not _output:
                            _output = '# HELP PYTHON_KAMAILIO_INFO SERVER_BASIC_INFO(MB) '.encode()
                        else:
                            if type(_output) != bytes:
                                _output = _output.encode()
                        self.wfile.write(_output)
                        del _output, hearder
                        gc.collect()

                    else:
                        self.send_error(404, 'Path Not Found: %s' % self.path)
                    # logging.critical('http_server - Recv {0}{1} - 200 - {3}'.format(self.address_string(), str(request_url), _output))
                    del request_url
                    gc.collect()
                except Exception as e:
                    logging.warning('PromeHandler failed = %s' % str(e))

        '''暂时未用，python自带的ThreadedHTTPServer库有问题，个别机子处理很慢，导致netstat端口堵到超时,虽第二个请求会再起一个线程，但端口仍然堵, 复现客户端wwchen-vps压力机139.180.186.253'''

        class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
            """Handle requests in a separate thread."""

        PROME_OBJECT = self.PROME_OBJECT

        class MyTCPServer(BaseRequestHandler):
            def handle(self):
                # print self.request,self.client_address,self.server
                # logger.critical(('****',self.client_address,'start'))
                while True:
                    data = self.request.recv(4096)
                    if not data:
                        break

                    reply_data = "HTTP/1.0 200\r\n"
                    reply_data += "Server: BaseHTTP/0.1 Python/%s\r\n" % str(sys.version.split()[0])
                    reply_data += "Date: %s GMT\r\n" % str(
                        datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S"))  # Mon, 07 Nov 2022 10:43:03
                    reply_data += "Content-Type: text/plain; version=0.0.1; charset=utf-8\r\n"
                    _body = '\r\n'

                    try:
                        _promethus_data = PROME_OBJECT.generate_latest()
                        _promethus_data = _promethus_data.decode() if type(
                            _promethus_data) == bytes else _promethus_data
                        _body = str(str(_promethus_data) + _body).replace('\r', '')
                    except:
                        _body = '# HELP PYTHON_KAMAILIO_INFO SERVER_BASIC_INFO(MB)'
                        logger.critical(traceback.format_exc())
                    reply_data += "Content-Length: %s\r\n\r\n" % str(len(_body))
                    reply_data += _body

                    if sys.version_info >= (3, 0):
                        reply_data = reply_data.encode('utf-8')

                    # logger.critical(('****',self.client_address,data))
                    self.request.sendall(reply_data)
                    try:
                        # self.request.close() # 2024.07.01 modify by jbzhu, reason is: MyTCPServer instance has no attribute 'request'
                        del data, reply_data # , self.request 2024.07.01 modify by jbzhu, reason is: MyTCPServer instance has no attribute 'request'
                        gc.collect()
                    except:
                        pass

                    # logger.critical(('****',self.client_address,'sent', reply_data[0:150]))
                logger.info((self.client_address, 'exit'))

        for i in range(1, 100):
            # if not GLOBAL_VAR._is_main_process:
            #     break
            _monitor = None
            try:
                if self._need_print_log:
                    logging.info('[%s/100]try starting http server, port = %s' % (str(i), str(listen_port)))
                '''promethus第三方库自带服务器，端口会堵死不可恢复，改用python自带库HTTPServer'''
                '''prometheus_client.start_http_server(int(prome_params_basic.local_listen_port),registry=reg)'''
                '''python自带的HTTPServer库有问题，netstat端口仍会堵死不可恢复，改用ThreadedHTTPServer，堵死时会再拉起一个线程处理终端请求'''
                '''prome_httpserver = HTTPServer(('', prome_params_basic.local_listen_port),PromeHandler)'''
                ''' python自带的ThreadedHTTPServer库有问题，个别机子处理很慢，导致netstat端口堵到超时,虽第二个请求会再起一个线程，但端口仍然堵, 复现客户端wwchen-vps压力机139.180.186.253'''
                '''运维反馈ThreadedHTTPServer存在内存泄漏(我处未出现)'''
                '''prome_httpserver = ThreadedHTTPServer(('', listen_port), PromeHandler)
                # t = threading.Thread(target=prome_httpserver.serve_forever)
                # t.daemon = True
                # t.start()'''

                '''研发测试自研的Tcp服务器, 短链路性能问题待优化'''
                # _monitor = TcpServer(local_addr='0.0.0.0', local_listen_port=listen_port,
                #                      need_print_log=self._need_print_log)
                # if int(_monitor.error_code) != 0:
                #     raise Exception(_monitor.error_msg)
                # _monitor.thread_reply_msg(thread_name='MONITOR_%s' % str(listen_port),
                #                           for_what='MONITOR_%s' % str(listen_port), need_print_log=self._need_print_log,
                #                           object_for_reply_data_self_defined=prometheus_client)

                _monitor = ThreadingTCPServer(('0.0.0.0', listen_port), MyTCPServer)
                t = threading.Thread(target=_monitor.serve_forever)
                t.daemon = True
                t.start()

                start_result_flag = True
                if self._need_print_log:
                    logging.info('[%s]HTTP server STARTED, port = %s' % (str(i), str(listen_port)))
                break
            except (socket.timeout, BaseException, socket.error, Exception) as e:
                start_error_msg = str(e)
                time.sleep(8)
                logging.debug('[%s] starting http server[port=%s] failed=%s' % (str(i), str(listen_port), e))
                try:
                    _monitor.close_socket()
                except:
                    pass

        if not start_result_flag:
            if self._need_print_log:
                logging.info('start http server failed, port = %s,error=%s' % (str(listen_port), str(start_error_msg)))
                os._exit(0)
                sys.exit()
            return False

        if 'win32' not in sys.platform:
            lo_cli.run_cmd('service firewalld stop && service iptables stop', need_run_with_sudo=True)
            lo_cli.run_cmd(
                'firewall-cmd --add-port=9100/tcp --permanent && firewall-cmd --add-port={0}/tcp --permanent && iptables -I INPUT -p TCP --dport 9100 -j ACCEPT && iptables -I INPUT -p TCP --dport {0} -j ACCEPT'.format(
                    str(listen_port)), need_run_with_sudo=True)
        elif _need_init_env:
            logging.info(
                '###YOU ARE WINDOWS, PLEASE manually CLOSE YOUR FIREWALL(firewall->advance->public profile->off) , otherwise monitor server connect you failed' * 1)
        return True


def _delete_duplicate_data_in_server_info(agents_info, need_print_log=True):
    if len(agents_info) <= 0:
        return agents_info
    _dict_data = {'public_ip': '', 'ssh_pwd': ''}
    return_data = {}  # {(publicip,sshport):完整信息,(publicip,sshport):完整信息}

    for key, data in agents_info.items():
        data = dict(data)
        try:
            if not data.get('public_ip') or not data.get('ssh_port'):
                raise Exception('NO SSH INFO IP[%s]' % str(data))

            if str(data['ssh_pwd']).strip().startswith('"'):
                data['ssh_pwd'] = data['ssh_pwd'][1:-1]

            if not return_data.get(key[0:2]):
                return_data.update({key[0:2]: data})

            else:
                old_value = return_data[key[0:2]]
                new_value = old_value
                new_value['pname_list'] = str(data['pname_list'] + old_value['pname_list']).replace("][", ",")
                new_value['service'] = str(data['service']) + '/' + str(old_value['service'])
                new_value['product'] = str(data['product']) + '/' + str(old_value['product'])
                if old_value.get('no'):
                    new_value['no'] = str(old_value['no']) + '/' + str(data['no'])
                return_data.update({key[0:2]: dict(new_value)})
                # logger.info(('Duplicated %s'%str(key),'new_data=%s'%str(new_value)))
        except Exception as e:
            if need_print_log:
                logger.warning('delete_duplicate_data_in_server_info - remove=%s' % str(e))
    if need_print_log:
        logger.warning('after delete_duplicate_data_in_server_info=%s' % str(return_data))
    return return_data


def _display_top(snapshot, key_type='lineno', limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    logger.critical("Top %s lines" % limit)
    import linecache
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        logger.critical("#%s: %s:%s: %.1f KiB"
                        % (index, frame.filename, frame.lineno, stat.size / 1024))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            logger.critical('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        logger.critical("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    logger.critical("Total allocated size: %.1f KiB" % (total / 1024))

'''chfshan,读取/配置ini配置文件'''
class _Config(object):
    '''
    读取/设置ini配置文件
    Usage:
        from config import Config
        cf = Config(PROJECT_CONFIG_FILE)
        BROWSER_TYPE = cf.get("browser","browser_type")
    Param:
      config_file: the .ini file you want to get, default is BASE_CONFIG_FILE
    '''

    def __init__(self, config_file_or_file_obj=None):
        self.config_file = config_file_or_file_obj
        self._config = cf.ConfigParser()
        self.__read__(config_file_or_file_obj)

    '''2024.07.03, xlzhou, 读取文件内容，加载到configparser内存中（兼容未打开的文件和已打开的文件）'''
    def __read__(self, config_file_or_file_obj):
        if not config_file_or_file_obj:
            return False
        try:
            # 如果是已经打开的文件，则直接调用ConfigParser的read_file方法读取内容(不会打开关闭文件)，否则调用read读取内容（会自动打开和关闭文件）
            if hasattr(config_file_or_file_obj, 'read'):  # 是打开的文件
                self._config.read_file(config_file_or_file_obj)
            else:
                self._config.read(config_file_or_file_obj)
        except Exception as e:
            if e:
                logger.error(
                    "common.Config.init - config file read error=%s,config file=%s" % (e, config_file_or_file_obj))

    def get_config_option_value(self, section, option_name, config_file_or_file_obj=None):
        if config_file_or_file_obj:
            self.__read__(config_file_or_file_obj)

        if self._config.has_section(section) and self._config.has_option(section, option_name):
            return self._config.get(section, option_name)
        else:
            logger.warning('No section as %s or no option_name as %s' % (str(section), str(option_name)))
            return None

    def set_config_option_value(self, section, option_name, option_value, config_file_or_file_obj=None, auto_add_section=False):
        if not self._config.has_section(section) and auto_add_section:
            logger.info('No section name as: %s, auto add section...' % str(section))
            self._config.add_section(section=section)
        elif not self._config.has_section(section):
            logger.warning('No section name as: %s, please check' % str(section))
            return False

        # config内存数据设置
        self._config.set(section, option_name, str(option_value))

        if not config_file_or_file_obj:
            config_file_or_file_obj = self.config_file

        _file = config_file_or_file_obj
        if not hasattr(_file, 'read'):
            _file = open(_file, "w+")

        # config内存数据写入文件
        self._config.write(config_file_or_file_obj)
        # 若文件属于方法内打开的，则写入后关闭文件
        if config_file_or_file_obj and not hasattr(config_file_or_file_obj, 'read') and hasattr(_file, 'read'):
            _file.close()

'''2024.07.03, xlzhou, 获取common_lib/password.ini的密码配置信息'''
def _get_password_by_ini(section, option_name):
    _config = _Config()
    _password_ini_encrypted = os.path.join(GLOBAL_VAR.COMMON_CONFIG_PATH,
                                           'encrypted_config/password_with_crypto.ini').replace('\\', '/')    
    _password_ini = os.path.join(GLOBAL_VAR.COMMON_CONFIG_PATH, 'password.ini').replace('\\', '/')
    result = _config.get_config_option_value(section, option_name, config_file_or_file_obj=_password_ini_encrypted)
    if not result:
        result = _config.get_config_option_value(section, option_name, config_file_or_file_obj=_password_ini)

    # 从password_with_crypto.ini中读取的配置为加密数据，需要解密（未实现）
    else:
        try:
            auto_test_decrpto_password = import_pyc_by_running_version(module_name='common_lib.protect_lib.auto_test_password_crypto', multiple_class_or_func='auto_test_decrpto_password')
            result = auto_test_decrpto_password(result, key=None)
        except Exception as e:
            logger.warning('Get encrypted configuration but decrypted failed...')

    if not result:
        logger.warning('Password of [%s]:%s not exist or not filled, please check!' % (str(section), str(option_name)))

    return result


if __name__ == '__main__':
    _cmd = 'stat -c "%U" MONITOR_SYSTEM/monitor.log'
    signal.signal(signal.SIGTERM, _run_cmd_after_exit_handle)  # 请求中止进程，kill命令缺省发送   # 信号捕捉程序必须在循环之前设置
    signal.signal(signal.SIGINT, _run_cmd_after_exit_handle)  # 由Interrupt Key产生，通常是CTRL+C或者DELETE产生的中断
    # signal.signal(signal.SIGKILL, run_cmd_after_exit_handle) # 由kill  -9 产生，这个信号无法被捕捉或忽略，不能使用

    CSV_FILES = [os.path.join(DATA_FILE_PATH, 'test_server_info.csv'),
                 os.path.join(DATA_FILE_PATH, 'server_info.csv'),
                 os.path.join(os.path.dirname(PYTHON_FILE_PATH), 'external_support', 'data', 'hz_test_server.csv'),
                 os.path.join(os.path.dirname(PYTHON_FILE_PATH), 'external_support', 'data', 'sz_test_server.csv'),
                 ]
    client_info = {}
    server_info = {
        ('54.222.202.188',26222):
            {'owner': '', 'platform': 'local', 'product': 'fawefwef', 'region': 'us', 'service': 'fawefwef', 'public_ip': '54.222.202.188', 'local_ip': '54.222.202.188', 'ipv6': '', 'ssh_user': 'ec2-user', 'ssh_pwd': 'grandstream.', 'ssh_port': '26222', 'domain': 'gateway.gwn.cloud', 'domain_port': '10014', 'dns': '192.168.130.24', 'pname_list': "rtpengine,kamailio,nginx,sync_config", 'description': ''},
        # ('192.168.130.223',22):
        #     {'owner': '', 'platform': 'local', 'product': 'clouducm', 'region': 'us', 'service': 'gateway_4','public_ip': '192.168.130.223', 'local_ip': '192.168.80.24', 'ipv6': '', 'ssh_user': 'root','ssh_pwd': 'grandstream.', 'ssh_port': '22', 'domain': 'gateway.gwn.cloud', 'domain_port': '10014','dns': '192.168.130.24', 'pname_list': '','description': ''},
        # ('192.168.130.24',22):
        #     {'owner': '', 'platform': 'local', 'product': 'gwn_cloud&gwn_cloud&gwn_cloud&gwn_cloud', 'region': 'us', 'service': 'api&admin&gateway_1&server_1','public_ip': '192.168.130.24', 'local_ip': '192.168.30.24', 'ipv6': '', 'ssh_user': 'root','ssh_pwd': 'grandstream.', 'ssh_port': '22', 'domain': 'gateway.gwn.cloud', 'domain_port': '10014','dns': '192.168.130.24', 'pname_list':  '[java#gwn_api,java#gwn_admin,nginx,gateway,node,java#gwn_api,java#gwn/conf,java#gwn_router,java#gwn_api,java#gwn/conf,nginx,gateway,node]','description': ''},
    }

    _init_global_var_and_options()
    monitor_run = _RunMonitor()

    USE_CSV_SERVER_INFO = True  # 服务器列表是否从csv读取，False，列表取client_info+server_info，True取server_info.csv+test_server_info.csv
    ONLY_FOR_DELETE_REMOTE_FILES = False  # 是否清理每个服务器由监控产生的所有文件，True，全删。[仅为需要清理时使用]
    need_run_node_exporter = False

    if GLOBAL_VAR.RUN_MODE == 'controller':
        contorller = _Controller_back()
        contorller.do_run(need_delete_remote_path=ONLY_FOR_DELETE_REMOTE_FILES, client_info=client_info,
                          server_info=server_info, test_platform=GLOBAL_VAR.PLATFORM,
                          need_use_local_csv_servers=USE_CSV_SERVER_INFO, need_run_node_exporter=need_run_node_exporter)
    elif GLOBAL_VAR.RUN_MODE == 'client':
        t1 = threading.Thread(target=monitor_run.run_client, args=())
        t1.start()
    elif GLOBAL_VAR.RUN_MODE == 'p_client':
        monitor_run.run_prometheus_client(monitor_interval=GLOBAL_VAR.MONITOR_INTERVAL)
        # t1 = threading.Thread(target=monitor_run.run_prometheus_client,args=(GLOBAL_VAR.MONITOR_INTERVAL,))
        # t1.start()
    elif GLOBAL_VAR.RUN_MODE == 'chfshan':  # chfshan专属，调试使用
        logger.critical(os.path.abspath(__file__))
        start_cmd = str(lo_cli.get_python_execute_path())
        for i in sys.argv:
            start_cmd = start_cmd + ' ' + str(i)

        logger.critical(start_cmd)
    elif GLOBAL_VAR.RUN_MODE == 'update':
        remote_cm_server_list = ['10.2.0.63', '10.2.0.172', '10.2.0.101', '10.2.0.13', '10.2.0.228']
        remote_sbc_list = ["54.222.202.188", "140.179.37.83", "54.223.153.204", '54.223.60.230', '54.223.63.188']

        server_accout = ['ec2-user', 'grandstream.', 22]
        # server_accout = ['ec2-user', 'grandstream.', 26222]
        for _host in remote_cm_server_list:
            remote_server = _RemoteServerManager(remote_host=_host, remote_port=server_accout[2])
            cmd = 'cat /opt/containerManager/version'
            _ver = remote_server.run_cmd(cmd, need_run_with_sudo=True)
            logger.critical(('########', _host, _ver))
            remote_server.run_cmd('mkdir -p /home/ec2-user/MONITOR_SYSTEM')
            # remote_server.put('/home/ec2-user/MONITOR_SYSTEM/check_monitor.sh','/home/ec2-user/MONITOR_SYSTEM/check_monitor.sh')
            # remote_server.exec_command('chmod 777 /home/ec2-user/MONITOR_SYSTEM/check_monitor.sh')
            _local = str(os.path.abspath(__file__)).replace('\\', '/')
            remote_server.put(_local,
                         '/home/ec2-user/MONITOR_SYSTEM/monitor_system.py')
            remote_server.run_cmd(
                "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep monitor_system.py|grep -v  'grep\|tail \|more \|vim \|vi '|awk '{print $2}'|xargs sudo kill -9",
                need_run_with_sudo=True)
            time.sleep(0.5)
            remote_server.run_cmd(
                "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep monitor_system.py|grep -v  'grep\|tail \|more \|vim \|vi '|awk '{print $2}'|xargs sudo kill -9",
                need_run_with_sudo=True)
            time.sleep(0.5)
            result = remote_server.run_cmd(
                "ps -eo user,pid,ppid,nice,vsz,rss,tty,stat,etime,time,comm,args|grep check_local_monitor|grep -v  'grep\|tail \|more \|vim \|vi '|awk '{print $2}'",
                need_run_with_sudo=True)
            if not str(result).replace('\n', '').strip():
                remote_server.run_cmd('nohup /home/ec2-user/MONITOR_SYSTEM/check_local_monitor.sh  2>/dev/null &')

    else:
        logger.error("--run_mode %s [error],  should be controller/client/p_client !" % GLOBAL_VAR.RUN_MODE)

    logger.info("MONITOR_SYSTEM main thread,normal exit")

    # /usr/bin/python /root/MONITOR_SYSTEM/monitor_system_backup.py --runmode p_client --runtotaltime 31536000 --needmonitorpname [asterisk,kamailio,gs_avs,conference] --logconsolelevel INFO --logfilelevel INFO