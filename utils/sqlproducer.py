# coding:utf8
'''
Created on 2013-5-8

@author: joe lin
            ┏┓　　　┏┓
          ┏┛┻━━━┛┻┓
          ┃　　　━　　　┃
          ┃　┳┛　┗┳　┃
          ┃　　　　　　　┃
          ┃　　　┻　　　┃
          ┗━┓　　　┏━┛
              ┃　　　┃
              ┃　　　┗━━━┓
              ┃　　　　　　　┣┓
              ┃　　　　　　　┏┛
              ┗┓┓┏━┳┓┏┛
                ┃┫┫　┃┫┫
                ┗┻┛　┗┻┛
                 神兽保佑，代码无BUG!
@desc：

'''

import datetime
import tokenize
from collections import Iterable
from io import StringIO
from twisted.internet import reactor, defer

from firefly3.exts import tx_sql

INSERT = 1
DELETE = 2
UPDATE = 3
SELECT = 4


class UnknownParamstyle(Exception):
    """
    raised for unsupported db paramstyles

    (currently supported: qmark, numeric, format, pyformat)
    """
    pass

class _ItplError(ValueError):
    def __init__(self, text, pos):
        ValueError.__init__(self)
        self.text = text
        self.pos = pos
    
    def __str__(self):
        return "unfinished expression in %s at char %d" % (
            repr(self.text), self.pos)

class UnknownCommand(Exception):
    """
    raised for unsupported db paramstyles

    (currently supported: qmark, numeric, format, pyformat)
    """
    pass

class SQLProducer:
    """
     Database
    """
    
    def __init__(self, tables=None):
        self._command = None
        self._tables = tables
        self._query = None
        self._filter = None
        self._order = None
        self._group = None
        self._limit = None
        self._offset = None
        self._using = None
        self._svars = {}
    
    def query(self, _query=None):
        """
        Execute SQL query `sql_query` using dictionary `vars` to interpolate it.
        If `processed=True`, `vars` is a `reparam`-style list to use
        instead of interpolating.
        """
        if _query is None:
            self._query = "*"
        if type(_query) in [list,tuple, SQLQuery]:
            self._query = sqllist(_query)
        else:
            self._query = safestr(_query)
        return self
    
    def filter(self, filter, svars=None):
        self._filter = safestr(filter)
        if svars:
            self._svars.update(svars)
        return self
    
    def order(self, order, svars=None):
        self._order = safestr(order)
        if svars:
            self._svars.update(svars)
        return self
    
    def group(self, group, svars=None):
        self._group = safestr(group)
        if svars:
            self._svars.update(svars)
        return self
    
    def limit(self, limit, svars=None):
        self._limit = safestr(limit)
        if svars:
            self._svars.update(svars)
        return self
    
    def offset(self, offset, svars=None):
        self._offset = safestr(offset)
        if svars:
            self._svars.update(svars)
        return self
    
    def using(self,using,svars=None):
        self._using = safestr(using)
        if svars:
            self._svars.update(svars)
        return self
    
    @property
    def sql_clauses(self):
        return (
            ('SELECT', self._query),
            ('FROM', sqllist(self._tables)),
            ('WHERE', self._filter),
            ('GROUP BY', self._group),
            ('ORDER BY', self._order),
            ('LIMIT', self._limit),
            ('OFFSET', self._offset)
        )

    def gen_clause(self, sql, val):
        '''
        生成
        :param sql: sql关键字
        :param val: 关键字对应值
        :return:
        '''
        if isinstance(val, int):
            if sql == 'WHERE':
                nout = 'id = ' + sqlquote(val)
            else:
                # 查询内，若不是where就是select
                nout = SQLQuery(val)

        elif isinstance(val, (list, tuple)) and len(val) == 2:
            #
            nout = SQLQuery(val[0], val[1])  # backwards-compatibility

        elif isinstance(val, SQLQuery):
            #
            nout = val
        else:

            nout = reparam(val, self._svars)

        def xjoin(a, b):
            '''

            :param a:
            :param b:
            :return:
            '''
            if a and b:
                return a + ' ' + b
            else:
                return a or b

        ret = xjoin(sql, nout)
        return ret
    
    def sqlwhere(self, dictionary, grouping=' AND '):
        """
        Converts a `dictionary` to an SQL WHERE clause `SQLQuery`.
        """
        return SQLQuery.join([k + ' = ' + SQLParam(v) for k, v in dictionary.items()], grouping)
    
    def _where(self, where, svars):
        # print(where)
        # print(svars)
        if isinstance(where, int):
            where = "id = " + SQLParam(where)
        elif isinstance(where, (list, tuple)) and len(where) == 2:
            where = SQLQuery(where[0], where[1])
        elif isinstance(where, SQLQuery):
            pass
        else:
            where = reparam(where, svars)
        return where
    
    def _get_insert_default_values_query(self, table):
        return """
            INSERT INTO %s DEFAULT VALUES
        """ % table

    @defer.inlineCallbacks
    def one(self):
        """
        Selects `what` from `tables` with clauses `where`, `order`,
        `group`, `limit`, and `offset`. Uses vars to interpolate.
        Otherwise, each clause can be a SQLQuery.
        """
        self.limit(1)
        clauses = [self.gen_clause(sql, val) for sql, val in self.sql_clauses if val is not None]
        query = SQLQuery.join(clauses)
        sql = query.query("pyformat")
        ret = yield tx_sql.runQuery(sql, query.values())
        defer.returnValue(ret[0])

    @defer.inlineCallbacks
    def all(self):
        """

        :return:
        """
        # 加入关键字，并提取参数
        clauses = [self.gen_clause(sql, val) for sql, val in self.sql_clauses if val is not None]
        query = SQLQuery.join(clauses)
        sql = query.query("pyformat")
        ret = yield tx_sql.runQuery(sql, query.values())
        defer.returnValue(ret)
    
    def insert(self, svars):
        """
        Inserts `values` into `tablename`. Returns current sequence ID.
        Set `seqname` to the ID if it's not the default, or to `False`
        if there isn't one.
        """
        self._command = INSERT
        self._svars = svars
        
        return self
    
    def update(self,**svars):
        """
        Update `tables` with clause `where` (interpolated using `vars`)
        and setting `values`.
        """
        self._command = UPDATE
        if svars is None:
            self._svars = {}
        else:
            self._svars = svars
        return self

    def delete(self,**svars):
        """
        Deletes from `table` with clauses `where` and `using`.
        """
        self._command = DELETE
        if svars is None:
            self._svars = {}
        else:
            self._svars = svars
        return self
    
    def commit(self):
        query = None
        if self._command == UPDATE:
            query = (
                " UPDATE " + sqllist(self._tables) +
                " SET " + self.sqlwhere(self._svars, ', ') +
                " WHERE " + self._where(self._filter, self._svars))
        elif self._command == INSERT:
            if self._svars:
                if isinstance(self._svars,dict):
                    # 用 SQLQuery.join 的方法
                    _keys = SQLQuery.join(self._svars.keys(), ', ')
                    _values = SQLQuery.join([SQLParam(v) for v in self._svars.values()], ', ')
                    query = "INSERT INTO %s " % self._tables + q(_keys) + ' VALUES ' + q(_values)
                elif isinstance(self._svars,list):
                    if not self._svars:
                        return []
    
                    keys = self._svars[0].keys()
                    # @@ make sure all keys are valid
    
                    # make sure all rows have same keys.
                    for v in self._svars:
                        if v.keys() != keys:
                            raise ValueError('Bad data')
    
                    query = SQLQuery('INSERT INTO %s (%s) VALUES ' % (self._tables, ', '.join(keys)))
    
                    for i, row in enumerate(self._svars):
                        if i != 0:
                            query.append(", ")
                        SQLQuery.join([SQLParam(row[k]) for k in keys], sep=", ", target=query, prefix="(",suffix=")")
            else:
                query = SQLQuery(self._get_insert_default_values_query(self._tables))
        elif self._command == DELETE:
            query = 'DELETE FROM ' + self._tables
            if self._using:
                query += ' USING ' + sqllist(self._using)
            if self._filter:
                query += ' WHERE ' + self._where(self._filter, self._svars)
        if query:
            sql = str(query)
            return tx_sql.runOperation(sql)
    
    @staticmethod
    def runQuery(sql, svars):
        
        '''
        数据库的查
        :param sql: sql语句
        :param args: sql内部参数
        :return:
        '''
        query = reparam(sql,dictionary=svars)
        sql = str(query.query("format"))
        return tx_sql.runQuery(sql=sql, args=(query.values()))
   
    @staticmethod
    def runOperation(sql, svars):
        '''
        数据库的增删改
        :param sql: sql语句
        :param args: sql内部参数
        :return:
        '''
        query = reparam(sql, dictionary=svars)
        sql = str(query.query("format"))
        return tx_sql.runQuery(sql=sql, args=(query.values()))
        
class SQLQuery(object):
    """
    You can pass this sort of thing as a clause in any db function.
    Otherwise, you can pass a dictionary to the keyword argument `vars`
    and the function will call reparam for you.

    Internally, consists of `items`, which is a list of strings and
    SQLParams, which get concatenated to produce the actual query.
    """
    __slots__ = ["items"]
    
    # tested in sqlquote's docstring
    def __init__(self, items=None):
        """
        Creates a new SQLQuery.
            SQLQuery("x") => <sql: 'x'>
            q = SQLQuery(['SELECT * FROM ', 'test', ' WHERE x=', SQLParam(1)]) => <sql: 'SELECT * FROM test WHERE x=1'>
            q.query(), q.values() => ('SELECT * FROM test WHERE x=%s', [1])
            SQLQuery(SQLParam(1)) => <sql: '1'>
        :param items:
        """
        if items is None:
            self.items = []
        elif isinstance(items, list):
            self.items = items
        elif isinstance(items, SQLParam):
            self.items = [items]
        elif isinstance(items, SQLQuery):
            self.items = list(items.items)
        else:
            self.items = [items]
        
        # Take care of SQLLiterals
        for i, item in enumerate(self.items):
            if isinstance(item, SQLParam) and isinstance(item.value, SQLLiteral):
                self.items[i] = item.value.v
    
    def append(self, value):
        '''
        列表的添加功能
        :param value:
        :return:
        '''
        self.items.append(value)
    
    def __add__(self, other):
        '''
        :param other:
        :return:
        '''
        if isinstance(other, str):
            items = [other]
        elif isinstance(other, SQLQuery):
            items = other.items
        else:
            return NotImplemented
        return SQLQuery(self.items + items)
    
    def __radd__(self, other):
        '''

        :param other:
        :return:
        '''
        if isinstance(other, str):
            items = [other]
        else:
            return NotImplemented
        
        return SQLQuery(items + self.items)
    
    def __iadd__(self, other):
        '''

        :param other:
        :return:
        '''
        if isinstance(other, (str, SQLParam)):
            self.items.append(other)
        elif isinstance(other, SQLQuery):
            self.items.extend(other.items)
        else:
            return NotImplemented
        return self
    
    def __len__(self):
        '''

        :return:
        '''
        return len(self.query())
    
    def query(self, paramstyle=None):
        """
        Returns the query part of the sql query.
            # >>> q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam('joe')])
            # >>> q.query()
            'SELECT * FROM test WHERE name=%s'
            # >>> q.query(paramstyle='qmark')
            'SELECT * FROM test WHERE name=?'
        """
        s = []
        for x in self.items:
            if isinstance(x, SQLParam):
                # 获取数值占位符 s%
                x = x.get_marker(paramstyle)
                # 变量转成 str 并添加进入 list
                s.append(safestr(x))
            else:
                # 若传入值非sqlparam对象，则直接转成 str
                x = safestr(x)
                # automatically escape % characters in the query
                # For backward compatability, ignore escaping when the query looks already escaped
                # 将 % 转化成 %% 否则将报错
                if paramstyle in ['format', 'pyformat']:
                    if '%' in x and '%%' not in x:
                        x = x.replace('%', '%%')
                # 变量转成 str 并添加进入 list
                s.append(x)
        # list 转 str
        ret = "".join(s)
        return ret
    
    def values(self):
        """
        Returns the values of the parameters used in the sql query.
            # >>> q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam('joe')])
            # >>> q.values()
            ['joe']
        """
        return [i.value for i in self.items if isinstance(i, SQLParam)]
    
    @staticmethod
    def join(items, sep=' ', prefix=None, suffix=None, target=None):
        """
        字符串，SQLQuery 拼接函数
            SQLQuery.join(['a', 'b'], ', ') =》 <sql: 'a, b'>
            SQLQuery.join(['a', 'b'], ', ', prefix='(', suffix=')') =》 <sql: '(a, b)'>
        :param items: str，SQLQuery
        :param sep:  间隔符 如 .
        :param prefix: 头符号 如 (
        :param suffix: 尾符号 如 )
        :param target: 目标对象
        :return: SQLQuery
        """
        if target is None:
            target = SQLQuery()
            
        target_items = target.items
        
        if prefix:
            target_items.append(prefix)
        
        for i, item in enumerate(items):
            if i != 0:
                target_items.append(sep)
            if isinstance(item, SQLQuery):
                target_items.extend(item.items)
            else:
                target_items.append(item)
        
        if suffix:
            target_items.append(suffix)
        
        return target
    
    def _str(self):
        try:
            return self.query() % tuple([sqlify(x) for x in self.values()])
        except (ValueError, TypeError):
            return self.query()
    
    def __str__(self):
        return safestr(self._str())
    
    def __unicode__(self):
        return safeunicode(self._str())
    
    def __repr__(self):
        return '<sql: %s>' % repr(str(self))

class SQLParam(object):
    """
    Parameter in SQLQuery , 植入sql的参数，需要通过这个类包装，提供SQLQuery调用所需要的函数
        q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam("joe")])
        q.query()
        'SELECT * FROM test WHERE name=%s'
        q.values()
        ['joe']
    """
    __slots__ = ["value"]
    
    def __init__(self, value):
        self.value = value
    
    def get_marker(self, paramstyle='pyformat'):
        if paramstyle == 'qmark':
            return '?'
        elif paramstyle == 'numeric':
            return ':1'
        elif paramstyle is None or paramstyle in ['format', 'pyformat']:
            return '%s'
        raise UnknownParamstyle(paramstyle)
    
    def sqlquery(self):
        return SQLQuery([self])
    
    def __add__(self, other):
        return self.sqlquery() + other
    
    def __radd__(self, other):
        return other + self.sqlquery()
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        # return '<param: %s>' % repr(self.value)
        return str(self.value)

class SQLLiteral:
    """
    Protects a string from `sqlquote`.
        sqlquote('NOW()') =》 <sql: "'NOW()'">
        sqlquote(SQLLiteral('NOW()')) =》 <sql: 'NOW()'>
    """
    
    def __init__(self, v):
        self.v = v
    
    def __repr__(self):
        return self.v

def safeunicode(obj, encoding='utf-8'):
    """
    Converts any given object to unicode string.
    :param obj:
    :param encoding:
    :return:
    """
    t = type(obj)
    if t is str:
        return obj.encode(encoding)
    elif t in [bytes, int, float, bool]:
        return obj
    else:
        return str(obj).encode(encoding)

def safestr(obj, encoding='utf-8'):
    """
    Converts any given object to utf-8 encoded string.
    :param obj:
    :param encoding:
    :return:
    """
    if isinstance(obj, bytes):
        return obj.decode(encoding)
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, Iterable):  # iterator
        return [safestr(item) for item in obj]
    else:
        return str(obj)

def sqlify(obj):
    """
    converts `obj` to its proper SQL version
    :param obj:
    :return:
    """
    if obj is None:
        return 'NULL'
    elif obj is True:
        return "1"
    elif obj is False:
        return "0"
    elif datetime and isinstance(obj, datetime.datetime):
        return repr(obj.isoformat())
    else:
        if isinstance(obj, bytes):
            obj = obj.decode()
        return repr(obj)

def sqllist(lst):
    """
    Converts the arguments for use in something like a WHERE clause.
    ["a","b","c"] => "a,b,c"
    "a,b,c" => "a,b,c"
    :param lst:
    :return:
    """
    if isinstance(lst, str):
        return lst
    else:
        return ', '.join(lst)

def _sqllist(values):
    """
        <sql: '(1, 2, 3)'>
    """
    items = []
    items.append('(')
    for i, v in enumerate(values):
        if i != 0:
            items.append(', ')
        items.append(SQLParam(v))
    items.append(')')
    ret = SQLQuery(items)
    return ret

def sqlquote(a):
    """
    确保 a 可以被 SQL query 引用
        sqlquote(True) =》 '1'
        sqlquote(3) => 3
        sqlquote([2, 3]) => (2, 3)
    :param a:
    :return: SQLQuery
    """
    if isinstance(a, list):
        return _sqllist(a)
    else:
        return SQLParam(a).sqlquery()

def reparam(string_, dictionary):
    """
    Takes a string and a dictionary and interpolates the string
    using values from the dictionary. Returns an `SQLQuery` for the result.
    :param string_:
    :param dictionary:
    :return: SQLQuery
    """
    dictionary = dictionary.copy()  # eval mucks with it
    result = []
    interpolate = _interpolate(string_)
    for live, chunk in interpolate:
        if live:
            v = eval(chunk, dictionary)
            result.append(sqlquote(v))
        else:
            result.append(chunk)
    ret = SQLQuery.join(result, '')
    return ret

def q(x):
    return "(" + x + ")"

def _interpolate(sformat):
    
        def matchorfail(text, pos):
            s = tokenize.generate_tokens(StringIO(text[pos:]).readline)
            match = next(s)
            if match is None:
                raise _ItplError(text, pos)
            return match.string, match.end[1] + pos
    
        # 变量命名规则
        namechars = "abcdefghijklmnopqrstuvwxyz" \
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_";
        # 代码块
        chunks = []
        # 游标位置
        pos = 0
    
        while 1:
            # 查找 dollar 符号位置，该符号后一个单词将会被同名变量替换
            # 如 $xxx 将被换成 dict["xxx"]
            # 所以第一步需要找到dollar
            dollar = sformat.find("$", pos)
            if dollar < 0:
                # 若未找到，则证明无需进行变量替换，直接break就可以
                break
            # 获得 dollar 下一个字节的游标
            nextchar = sformat[dollar + 1]
            # 如果下一个游标为 {
            if nextchar == "{":
                # 找到数据块增加至列表 chunks
                chunks.append((0, sformat[pos:dollar]))
                pos, level = dollar + 2, 1
                while level:
                    match, pos = matchorfail(sformat, pos)
                    # print(match, pos)
                    tstart, tend = match.regs[3]
                    token = sformat[tstart:tend]
                    if token == "{":
                        level = level + 1
                    elif token == "}":
                        level = level - 1
                chunks.append((1, sformat[dollar + 2:pos - 1]))
        
            # 如果下一个游标符合变量命名规则的首位
            elif nextchar in namechars:
                # 提前提取dollar前的代码块，加入到chunks
                chunks.append((0, sformat[pos:dollar]))
                # 获取$后的单词，以及单词所在位置
                match, pos = matchorfail(sformat, dollar + 1)
            
                while pos < len(sformat):
                    # 若游标未到底
                    if sformat[pos] == "." and \
                            pos + 1 < len(sformat) and sformat[pos + 1] in namechars:
                        match, pos = matchorfail(sformat, pos + 1)
                    elif sformat[pos] in "([":
                        pos, level = pos + 1, 1
                        while level:
                            match, pos = matchorfail(sformat, pos)
                            tstart, tend = match.regs[3]
                            token = sformat[tstart:tend]
                            if token[0] in "([":
                                level = level + 1
                            elif token[0] in ")]":
                                level = level - 1
                    else:
                        break
                chunks.append((1, sformat[dollar + 1:pos]))
            else:
                chunks.append((0, sformat[pos:dollar + 1]))
                pos = dollar + 1 + (nextchar == "$")
    
        if pos < len(sformat):
            chunks.append((0, sformat[pos:].replace("%", "%%")))
        return chunks

if __name__ == '__main__':
    # sql = SQLProducer.insert("user", **dict(id=0, user_name="joe"))
    # sql = SQLProducer.delete("user", filter="user.id=$id", svars=dict(id=1))
    # sql = SQLProducer.update(tables="user", filter="id = $id and age > $age_l and major = $major",
    #                          svars=dict(id=1, age_l=28, major="教师"), **dict(user_name="joe"))
    
    
    from twisted.internet import reactor, defer
    from firefly3.utils import DefferedErrorHandle
    
    tx_sql.init_app({
        "DB_HOST": "",
        "DB_PASSWORD": "",
        "DB_NAME": ""
    })
    
    @defer.inlineCallbacks
    def get():
        ret = yield SQLProducer(["gateway","gateway_idtk"]).query(
            """DATE_FORMAT(CONCAT(DATE(gateway_idtk.time), ' ', HOUR(gateway_idtk.time),':00'),'%Y-%m-%d %H:%i') AS `time`,FORMAT(SUM(gateway_idtk.rate),0) AS `rate`"""
        ).filter(
            """(gateway_idtk.time BETWEEN $time_start  AND $time_end ) AND gateway_idtk.equipment_id IN $equipments""",
            svars = dict(time_start="2019-10-20 00:00:00", time_end="2020-02-20 23:59:59",equipments=[i for i in range(1, 5)])
        ).group(
            """DATE_FORMAT(CONCAT(DATE(gateway_idtk.time),' ',HOUR(gateway_idtk.time),':00'),'%Y-%m-%d %H:%i')""",
        ).limit(100).all()
        
        print(ret)

    @defer.inlineCallbacks
    def update():
        db = SQLProducer("banner").update(link_url="https://1121").filter("id = $id",dict(id=1))
        yield db.commit()

    @defer.inlineCallbacks
    def insert():
        db = SQLProducer("banner").insert(dict(name="医用款",link_url="https://",image_url="https://"))
        yield db.commit()

    @defer.inlineCallbacks
    def multiple_insert():
        values = [dict(name="医用款{}".format(i), link_url="https://{}".format(i), image_url="https://{}".format(i)) for i in range(10)]

        db = SQLProducer("banner").insert(values)
        yield db.commit()

    @defer.inlineCallbacks
    def delete():
        db = SQLProducer("banner").delete().filter("id > $id",dict(id=5))
        yield db.commit()
    
    @defer.inlineCallbacks
    def query():
        # ret = yield SQLProducer.runQuery(sql = """
        #     SELECT DATE_FORMAT(DATE(gateway_idtk.time),"%Y-%m-%d") as `time` ,
        #             FORMAT(SUM(gateway_idtk.rate),0) AS `rate`,
        #      FROM gateway_idtk
        #      WHERE (gateway_idtk.time BETWEEN %s AND %s )
        #         AND gateway_idtk.equipment_id = %s
        #      GROUP BY
        #          DATE_FORMAT(DATE(gateway_idtk.time),"%Y-%m-%d");
        # """)
        ret = yield SQLProducer.runQuery(sql="""
            select * from gateway_parameter where gateway_parameter.parameter_desc in $desc;
        """,svars=dict(desc = ["测试应用","写字楼应用","3"]))
        print(ret)
    
    
    # get().addCallback(update).addCallback(insert).addCallback()
    # delete().addErrback(DefferedErrorHandle)
    
    reactor.run()
    
    # sql = sqlproducer.text("""
    #     SELECT
    # 	device.id,
    # 	device.ser_num,
    # 	device.config_version,
    # 	device.parameter_version,
    # 	device.version,
    # 	ISNULL(device.location) AS location
    #     FROM
    #         device
    #     WHERE
    #         device.ser_num = $ser_num
    # """,dict(ser_num = "50-0A-0814D1077"))