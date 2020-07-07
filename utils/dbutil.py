# coding:utf8
'''
Created on 2013-5-8

@author: lan (www.9miao.com)
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

from numbers import Number

def forEachPlusInsertProps(tablename, props):
    '''
    生成插入语句
    :param tablename:
    :param props: type dict
    :return:
    '''
    assert type(props) == dict
    pkeysstr = str(tuple(props.keys())).replace('\'', '`')
    pvaluesstr = ["%s," % val if isinstance(val, Number) else
                  "'%s'," % str(val).replace("'", "\\'") for val in props.values()]
    pvaluesstr = ''.join(pvaluesstr)[:-1]
    sqlstr = """INSERT INTO `%s` %s values (%s);""" % (tablename, pkeysstr, pvaluesstr)
    return sqlstr

def FormatCondition(props):
    '''
    生成查询条件(where)字符串
    :param props:
    :return:
    '''
    items = props.items()
    itemstrlist = []
    for _item in items:
        if isinstance(_item[1], Number):
            sqlstr = " `%s`=%s AND" % _item
        else:
            sqlstr = " `%s`='%s' AND " % (_item[0], str(_item[1]).replace("'", "\\'"))
        itemstrlist.append(sqlstr)
    sqlstr = ''.join(itemstrlist)
    return sqlstr[:-4]

def FormatUpdateStr(props):
    '''
    生成更新语句
    :param props:
    :return:
    '''
    items = props.items()
    itemstrlist = []
    for _item in items:
        if isinstance(_item[1], Number):
            sqlstr = " `%s`=%s," % _item
        else:
            sqlstr = " `%s`='%s'," % (_item[0], str(_item[1]).replace("'", "\\'"))
        itemstrlist.append(sqlstr)
    sqlstr = ''.join(itemstrlist)
    return sqlstr[:-1]

def forEachUpdateProps(tablename, props, prere):
    '''
    遍历所要修改的属性，以生成sql语句
    :param tablename: 表名称
    :param props: set
    :param prere: where
    :return:
    '''
    assert type(props) == dict
    pro = FormatUpdateStr(props)
    pre = FormatCondition(prere)
    sqlstr = """UPDATE `%s` SET %s WHERE %s;""" % (tablename, pro, pre)
    return sqlstr

def EachQueryProps(props):
    '''
    遍历字段列表生成sql语句
    :param props:
    :return:
    '''
    sqlstr = ""
    if props == '*':
        return '*'
    elif type(props) == type([0]):
        for prop in props:
            sqlstr = sqlstr + prop + ','
        sqlstr = sqlstr[:-1]
        return sqlstr
    else:
        raise Exception('props to query must be dict')
        return

def forEachQueryProps(sqlstr, props):
    '''
    遍历所要查询属性，以生成sql语句
    :param sqlstr:
    :param props:
    :return:
    '''
    if props == '*':
        sqlstr += ' *'
    elif type(props) == type([0]):
        i = 0
        for prop in props:
            if (i == 0):
                sqlstr += ' ' + prop
            else:
                sqlstr += ', ' + prop
            i += 1
    else:
        raise Exception('props to query must be list')
        return
    return sqlstr

def GetTableIncrValue(database,tablename):
    """
    获数据表最大ID
    :param database:
    :param tablename:
    :return:
    """
    sql = """SELECT AUTO_INCREMENT FROM information_schema.`TABLES` \
    WHERE TABLE_SCHEMA='%s' AND TABLE_NAME='%s';""" % (database, tablename)
    return sql

def ReadDataFromDB(tablename):
    """
    从数据库读取
    :param tablename:
    :return:
    """
    sql = """select * from %s""" % tablename
    return sql

def DeleteFromDB(tablename, props):
    """
    从数据库中删除
    :param tablename:
    :param props: type dict
    :return:
    """
    prers = FormatCondition(props)
    sql = """DELETE FROM %s WHERE %s ;""" % (tablename, prers)
    return sql

def InsertIntoDB(tablename, data):
    """
    写入数据库
    :param tablename:
    :param data: type dict
    :return:
    """
    sql = forEachPlusInsertProps(tablename, data)
    return sql

def UpdateWithDict(tablename, props, prere):
    """
    更新记录
    :param tablename:
    :param props: update
    :param prere: where
    :return:
    """
    sql = forEachUpdateProps(tablename, props, prere)
    return sql

def getAllPkByFkInDB(tablename, pkname, props):
    """
    根据所有的外键获取主键ID
    :param tablename:
    :param pkname:
    :param props:
    :return:
    """
    props = FormatCondition(props)
    sql = """Select `%s` from `%s` where %s""" % (pkname, tablename, props)
    return sql

def GetOneRecordInfo(tablename, props):
    """
    获取单条数据的信息
    :param tablename:
    :param props:
    :return:
    """
    props = FormatCondition(props)
    sql = """Select * from `%s` where %s""" % (tablename, props)
    return sql
    # conn = dbpool.connection()
    # cursor = conn.cursor(cursorclass=DictCursor)
    # cursor.execute(sql)
    # result = cursor.fetchone()
    # cursor.close()
    # conn.close()
    # return result

def GetRecordList(tablename, pkname, pklist):
    """
    """
    pkliststr = ""
    for pkid in pklist:
        pkliststr += "%s," % pkid
    pkliststr = "(%s)" % pkliststr[:-1]
    sql = """SELECT * FROM `%s` WHERE `%s` IN %s;""" % (tablename, pkname, pkliststr)
    return sql

# class UnknownParamstyle(Exception):
#     """
#     raised for unsupported db paramstyles
#
#     (currently supported: qmark, numeric, format, pyformat)
#     """
#     pass
#
# class _ItplError(ValueError):
#     def __init__(self, text, pos):
#         ValueError.__init__(self)
#         self.text = text
#         self.pos = pos
#
#     def __str__(self):
#         return "unfinished expression in %s at char %d" % (
#             repr(self.text), self.pos)
#
# class SQLProducer:
#     """
#      Database
#     """
#
#     @classmethod
#     def query(cls, sql_query, svars=None):
#         """
#         Execute SQL query `sql_query` using dictionary `vars` to interpolate it.
#         If `processed=True`, `vars` is a `reparam`-style list to use
#         instead of interpolating.
#             # >>> SQLProducer.query("SELECT * FROM foo", _test=True)
#             <sql: 'SELECT * FROM foo'>
#             # >>> SQLProducer.query("SELECT * FROM foo WHERE x = $x", vars=dict(x='f'), _test=True)
#             <sql: "SELECT * FROM foo WHERE x = 'f'">
#             # >>> SQLProducer.query("SELECT * FROM foo WHERE x = " + sqlquote('f'), _test=True)
#             <sql: "SELECT * FROM foo WHERE x = 'f'">
#         """
#         if svars is None:
#             svars = {}
#
#         if isinstance(sql_query, SQLQuery):
#             sql_query = cls.reparam(sql_query, svars)
#
#         return sql_query
#
#     @classmethod
#     def select(cls, tables, query='*', filter=None, order=None, group=None,
#                limit=None, offset=None, svars=None, _test=False):
#         """
#         Selects `what` from `tables` with clauses `where`, `order`,
#         `group`, `limit`, and `offset`. Uses vars to interpolate.
#         Otherwise, each clause can be a SQLQuery.
#         """
#         if svars is None:
#             svars = {}
#         # 加入关键字，并提取参数
#         sql_clauses = cls.sql_clauses(query, tables, filter, group, order, limit, offset)
#         #
#         clauses = [cls.gen_sclause(sql, val, svars) for sql, val in sql_clauses if val is not None]
#         #s
#         qout = SQLQuery.sjoin(clauses)
#         return qout
#
#     @classmethod
#     def sql_clauses(cls, query, tables, filter, group, order, limit, offset):
#         return (
#             ('SELECT', query),
#             ('FROM', sqllist(tables)),
#             ('WHERE', filter),
#             ('GROUP BY', group),
#             ('ORDER BY', order),
#             ('LIMIT', limit),
#             ('OFFSET', offset)
#         )
#
#     @classmethod
#     def gen_sclause(cls, sql, val, svars):
#         '''
#         生成
#         :param sql: sql关键字 如 select update where ...
#         :param val: 关键字对应值
#         :param svars: 传入值
#         :return:
#         '''
#         # string ，进行参数重写
#         nout = cls.sreparam(val, svars)
#
#         # 返回 关键字 + SQLQuery
#         if sql and nout:
#             ret = sql + " " + nout
#         else:
#             ret = sql or nout
#         return ret
#
#     @classmethod
#     def gen_clause(cls, sql, val, svars):
#         '''
#         生成
#         :param sql: sql关键字
#         :param val: 关键字对应值
#         :param svars: 传入值
#         :return:
#         '''
#         if isinstance(val, int):
#             if sql == 'WHERE':
#                 nout = 'id = ' + sqlquote(val)
#             else:
#                 # 查询内，若不是where就是select
#                 nout = SQLQuery(val)
#
#         elif isinstance(val, (list, tuple)) and len(val) == 2:
#             #
#             nout = SQLQuery(val[0], val[1])  # backwards-compatibility
#
#         elif isinstance(val, SQLQuery):
#             #
#             nout = val
#         else:
#
#             nout = cls.reparam(val, svars)
#
#         def xjoin(a, b):
#             '''
#
#             :param a:
#             :param b:
#             :return:
#             '''
#             if a and b:
#                 return a + ' ' + b
#             else:
#                 return a or b
#
#         ret = xjoin(sql, nout)
#         return ret
#
#     @classmethod
#     def reparam(cls, string_, dictionary):
#         """
#         Takes a string and a dictionary and interpolates the string
#         using values from the dictionary. Returns an `SQLQuery` for the result.
#         :param string_:
#         :param dictionary:
#         :return: SQLQuery
#         """
#         result = []
#         interpolate = cls._interpolate(string_)
#         for live, chunk in interpolate:
#             if live:
#                 dictionary = dictionary.copy()  # eval mucks with it
#                 v = eval(chunk, dictionary)
#                 result.append(sqlquote(v))
#             else:
#                 result.append(chunk)
#         ret = SQLQuery.join(result, '')
#         return ret
#
#     @classmethod
#     def sreparam(cls, string_, dictionary):
#         """
#         将变量插入字符串
#           input : string = "set name = $name "
#           input : dictionary = dict(name="joe")
#           output : "set name = 'joe'"
#         :param string_:
#         :param dictionary:
#         :return: str
#         """
#         result = []
#         interpolate = cls._interpolate(string_)
#         for live, chunk in interpolate:
#             if live:
#                 dictionary = dictionary.copy()  # eval mucks with it
#                 chunk = ssqlquote(eval(chunk, dictionary))
#             result.append(chunk)
#         ret = SQLQuery.sjoin(result, '')
#         return ret
#
#     @classmethod
#     def sqlwhere(cls, dictionary, grouping=' AND '):
#         """
#         Converts a `dictionary` to an SQL WHERE clause `SQLQuery`.
#         """
#         return SQLQuery.join([k + ' = ' + SQLParam(v) for k, v in dictionary.items()], grouping)
#
#     @classmethod
#     def _interpolate(cls, sformat):
#
#         def matchorfail(text, pos):
#             s = tokenize.generate_tokens(StringIO(text[pos:]).readline)
#             match = next(s)
#             if match is None:
#                 raise _ItplError(text, pos)
#             return match.string, match.end[1] + pos
#
#         # 变量命名规则
#         namechars = "abcdefghijklmnopqrstuvwxyz" \
#                     "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_";
#         # 代码块
#         chunks = []
#         # 游标位置
#         pos = 0
#
#         while 1:
#             # 查找 dollar 符号位置，该符号后一个单词将会被同名变量替换
#             # 如 $xxx 将被换成 dict["xxx"]
#             # 所以第一步需要找到dollar
#             dollar = sformat.find("$", pos)
#             if dollar < 0:
#                 # 若未找到，则证明无需进行变量替换，直接break就可以
#                 break
#             # 获得 dollar 下一个字节的游标
#             nextchar = sformat[dollar + 1]
#             # 如果下一个游标为 {
#             if nextchar == "{":
#                 # 找到数据块增加至列表 chunks
#                 chunks.append((0, sformat[pos:dollar]))
#                 pos, level = dollar + 2, 1
#                 while level:
#                     match, pos = matchorfail(sformat, pos)
#                     # print(match, pos)
#                     tstart, tend = match.regs[3]
#                     token = sformat[tstart:tend]
#                     if token == "{":
#                         level = level + 1
#                     elif token == "}":
#                         level = level - 1
#                 chunks.append((1, sformat[dollar + 2:pos - 1]))
#
#             # 如果下一个游标符合变量命名规则的首位
#             elif nextchar in namechars:
#                 # 提前提取dollar前的代码块，加入到chunks
#                 chunks.append((0, sformat[pos:dollar]))
#                 # 获取$后的单词，以及单词所在位置
#                 match, pos = matchorfail(sformat, dollar + 1)
#
#                 while pos < len(sformat):
#                     # 若游标未到底
#                     if sformat[pos] == "." and \
#                             pos + 1 < len(sformat) and sformat[pos + 1] in namechars:
#                         match, pos = matchorfail(sformat, pos + 1)
#                     elif sformat[pos] in "([":
#                         pos, level = pos + 1, 1
#                         while level:
#                             match, pos = matchorfail(sformat, pos)
#                             tstart, tend = match.regs[3]
#                             token = sformat[tstart:tend]
#                             if token[0] in "([":
#                                 level = level + 1
#                             elif token[0] in ")]":
#                                 level = level - 1
#                     else:
#                         break
#                 chunks.append((1, sformat[dollar + 1:pos]))
#             else:
#                 chunks.append((0, sformat[pos:dollar + 1]))
#                 pos = dollar + 1 + (nextchar == "$")
#
#         if pos < len(sformat):
#             chunks.append((0, sformat[pos:].replace("%","%%")))
#         return chunks
#
#     @classmethod
#     def _where(cls, where, svars):
#         # print(where)
#         # print(svars)
#         if isinstance(where, int):
#             where = "id = " + cls.sqlparam(where)
#         elif isinstance(where, (list, tuple)) and len(where) == 2:
#             where = SQLQuery(where[0], where[1])
#         elif isinstance(where, SQLQuery):
#             pass
#         else:
#             where = cls.reparam(where, svars)
#         return where
#
#     def _get_insert_default_values_query(self, table):
#         return "INSERT INTO %s DEFAULT VALUES" % table
#
#     @classmethod
#     def insert(cls, tablename, seqname=None, _test=False, **values):
#         """
#         Inserts `values` into `tablename`. Returns current sequence ID.
#         Set `seqname` to the ID if it's not the default, or to `False`
#         if there isn't one.
#         """
#
#         def q(x):
#             return "(" + x + ")"
#
#         if values:
#             # 用 SQLQuery.join 的方法
#             _keys = SQLQuery.join(values.keys(), ', ')
#             _values = SQLQuery.join([SQLParam(v) for v in values.values()], ', ')
#             sql_query = "INSERT INTO %s " % tablename + q(_keys) + ' VALUES ' + q(_values)
#         else:
#             sql_query = SQLQuery(cls._get_insert_default_values_query(tablename))
#
#         return str(sql_query)
#
#     @classmethod
#     def multiple_insert(cls, tablename, values, seqname=None, _test=False):
#         """
#         Inserts multiple rows into `tablename`. The `values` must be a list of dictioanries,
#         one for each row to be inserted, each with the same set of keys.
#         Returns the list of ids of the inserted rows.
#         Set `seqname` to the ID if it's not the default, or to `False`
#         if there isn't one.
#         """
#         if not values:
#             return []
#
#         # if not self.supports_multiple_insert:
#         #     out = [self.insert(tablename, seqname=seqname, _test=_test, **v) for v in values]
#         #     if seqname is False:
#         #         return None
#         #     else:
#         #         return out
#
#         keys = values[0].keys()
#         # @@ make sure all keys are valid
#
#         # make sure all rows have same keys.
#         for v in values:
#             if v.keys() != keys:
#                 raise ValueError('Bad data')
#
#         sql_query = SQLQuery('INSERT INTO %s (%s) VALUES ' % (tablename, ', '.join(keys)))
#
#         for i, row in enumerate(values):
#             if i != 0:
#                 sql_query.append(", ")
#             SQLQuery.join([SQLParam(row[k]) for k in keys], sep=", ", target=sql_query, prefix="(", suffix=")")
#
#         return str(sql_query)
#
#     @classmethod
#     def update(cls, tables, filter, svars=None, _test=False, **values):
#         """
#         Update `tables` with clause `where` (interpolated using `vars`)
#         and setting `values`.
#         """
#         if svars is None: svars = {}
#         where = cls._where(filter, svars)
#
#         query = (
#                 "UPDATE " + sqllist(tables) +
#                 " SET " + cls.sqlwhere(values, ', ') +
#                 " WHERE " + where)
#
#         return str(query)
#
#         # if _test: return query
#         #
#         # db_cursor = self._db_cursor()
#         # self._db_execute(db_cursor, query)
#         # if not self.ctx.transactions:
#         #     self.ctx.commit()
#         # return db_cursor.rowcount
#
#     @classmethod
#     def delete(cls, table, filter, using=None, svars=None, _test=False):
#         """
#         Deletes from `table` with clauses `where` and `using`.
#
#             # >>> db = DB(None, {})
#             # >>> name = 'Joe'
#             # >>> db.delete('foo', where='name = $name', vars=locals(), _test=True)
#             <sql: "DELETE FROM foo WHERE name = 'Joe'">
#         """
#         if svars is None:
#             svars = {}
#         where = cls._where(filter, svars)
#
#         q = 'DELETE FROM ' + table
#         if using:
#             q += ' USING ' + sqllist(using)
#         if where:
#             q += ' WHERE ' + where
#
#         return str(q)
#
# class SQLQuery(object):
#     """
#     You can pass this sort of thing as a clause in any db function.
#     Otherwise, you can pass a dictionary to the keyword argument `vars`
#     and the function will call reparam for you.
#
#     Internally, consists of `items`, which is a list of strings and
#     SQLParams, which get concatenated to produce the actual query.
#     """
#     __slots__ = ["items"]
#
#     # tested in sqlquote's docstring
#     def __init__(self, items=None):
#         """
#         Creates a new SQLQuery.
#             SQLQuery("x") => <sql: 'x'>
#             q = SQLQuery(['SELECT * FROM ', 'test', ' WHERE x=', SQLParam(1)]) => <sql: 'SELECT * FROM test WHERE x=1'>
#             q.query(), q.values() => ('SELECT * FROM test WHERE x=%s', [1])
#             SQLQuery(SQLParam(1)) => <sql: '1'>
#         :param items:
#         """
#         if items is None:
#             self.items = []
#         elif isinstance(items, list):
#             self.items = items
#         elif isinstance(items, SQLParam):
#             self.items = [items]
#         elif isinstance(items, SQLQuery):
#             self.items = list(items.items)
#         else:
#             self.items = [items]
#
#         # Take care of SQLLiterals
#         for i, item in enumerate(self.items):
#             # print(item)
#             if isinstance(item, SQLParam) and isinstance(item.value, SQLLiteral):
#                 self.items[i] = item.value.v
#
#     def append(self, value):
#         '''
#         列表的添加功能
#         :param value:
#         :return:
#         '''
#         self.items.append(value)
#
#     def __add__(self, other):
#         '''
#         :param other:
#         :return:
#         '''
#         if isinstance(other, str):
#             items = [other]
#         elif isinstance(other, SQLQuery):
#             items = other.items
#         else:
#             return NotImplemented
#         return SQLQuery(self.items + items)
#
#     def __radd__(self, other):
#         '''
#
#         :param other:
#         :return:
#         '''
#         if isinstance(other, str):
#             items = [other]
#         else:
#             return NotImplemented
#
#         return SQLQuery(items + self.items)
#
#     def __iadd__(self, other):
#         '''
#
#         :param other:
#         :return:
#         '''
#         if isinstance(other, (str, SQLParam)):
#             self.items.append(other)
#         elif isinstance(other, SQLQuery):
#             self.items.extend(other.items)
#         else:
#             return NotImplemented
#         return self
#
#     def __len__(self):
#         '''
#
#         :return:
#         '''
#         return len(self.query())
#
#     def query(self, paramstyle=None):
#         """
#         Returns the query part of the sql query.
#             # >>> q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam('joe')])
#             # >>> q.query()
#             'SELECT * FROM test WHERE name=%s'
#             # >>> q.query(paramstyle='qmark')
#             'SELECT * FROM test WHERE name=?'
#         """
#         s = []
#         for x in self.items:
#             if isinstance(x, SQLParam):
#                 # 获取数值占位符 s%
#                 x = x.get_marker(paramstyle)
#                 # 变量转成 str 并添加进入 list
#                 s.append(safestr(x))
#             else:
#                 # 若传入值非sqlparam对象，则直接转成 str
#                 x = safestr(x)
#                 # automatically escape % characters in the query
#                 # For backward compatability, ignore escaping when the query looks already escaped
#                 # 将 % 转化成 %% 否则将报错
#                 if paramstyle in ['format', 'pyformat']:
#                     if '%' in x and '%%' not in x:
#                         x = x.replace('%', '%%')
#                 # 变量转成 str 并添加进入 list
#                 s.append(x)
#         # list 转 str
#         ret = "".join(s)
#         return ret
#
#     def values(self):
#         """
#         Returns the values of the parameters used in the sql query.
#             # >>> q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam('joe')])
#             # >>> q.values()
#             ['joe']
#         """
#         return [i.value for i in self.items if isinstance(i, SQLParam)]
#
#     @staticmethod
#     def join(items, sep=' ', prefix=None, suffix=None, target=None):
#         """
#         字符串，SQLQuery 拼接函数
#             SQLQuery.join(['a', 'b'], ', ') =》 <sql: 'a, b'>
#             SQLQuery.join(['a', 'b'], ', ', prefix='(', suffix=')') =》 <sql: '(a, b)'>
#         :param items: str，SQLQuery
#         :param sep:  间隔符 如 .
#         :param prefix: 头符号 如 (
#         :param suffix: 尾符号 如 )
#         :param target: 目标对象
#         :return: SQLQuery
#         """
#         if target is None:
#             target = SQLQuery()
#         target_items = target.items
#
#         if prefix:
#             target_items.append(prefix)
#
#         for i, item in enumerate(items):
#             if i != 0:
#                 target_items.append(sep)
#             if isinstance(item, SQLQuery):
#                 target_items.extend(item.items)
#             else:
#                 target_items.append(item)
#
#         if suffix:
#             target_items.append(suffix)
#
#         return target
#
#     @staticmethod
#     def sjoin(items, sep=' ', prefix=None, suffix=None, target=None):
#         """
#         字符串，SQLQuery 拼接函数
#             SQLQuery.join(['a', 'b'], ', ') =》 <sql: 'a, b'>
#             SQLQuery.join(['a', 'b'], ', ', prefix='(', suffix=')') =》 <sql: '(a, b)'>
#         :param items: str，SQLQuery
#         :param sep:  间隔符 如 .
#         :param prefix: 头符号 如 (
#         :param suffix: 尾符号 如 )
#         :param target: 目标对象
#         :return: str
#         """
#         if not target:
#             target = ""
#
#         if prefix:
#             target += prefix
#
#         for i, item in enumerate(items):
#             if i != 0:
#                 target += sep
#             target += item
#
#         if suffix:
#             target += suffix
#
#         return target
#
#     def _str(self):
#         try:
#             return self.query() % tuple([sqlify(x) for x in self.values()])
#         except (ValueError, TypeError):
#             return self.query()
#
#     def __str__(self):
#         return safestr(self._str())
#
#     def __unicode__(self):
#         return safeunicode(self._str())
#
#     def __repr__(self):
#         return '<sql: %s>' % repr(str(self))
#
#     # def sql(self):
#     #     return "".join(self.items)
#
# class SQLParam(object):
#     """
#     Parameter in SQLQuery , 植入sql的参数，需要通过这个类包装，提供SQLQuery调用所需要的函数
#         q = SQLQuery(["SELECT * FROM test WHERE name=", SQLParam("joe")])
#         q.query()
#         'SELECT * FROM test WHERE name=%s'
#         q.values()
#         ['joe']
#     """
#     __slots__ = ["value"]
#
#     def __init__(self, value):
#         self.value = value
#
#     def get_marker(self, paramstyle='pyformat'):
#         if paramstyle == 'qmark':
#             return '?'
#         elif paramstyle == 'numeric':
#             return ':1'
#         elif paramstyle is None or paramstyle in ['format', 'pyformat']:
#             return '%s'
#         raise UnknownParamstyle(paramstyle)
#
#     def sqlquery(self):
#         return SQLQuery([self])
#
#     def __add__(self, other):
#         return self.sqlquery() + other
#
#     def __radd__(self, other):
#         return other + self.sqlquery()
#
#     def __str__(self):
#         return str(self.value)
#
#     def __repr__(self):
#         # return '<param: %s>' % repr(self.value)
#         return str(self.value)
#
# class SQLLiteral:
#     """
#     Protects a string from `sqlquote`.
#         sqlquote('NOW()') =》 <sql: "'NOW()'">
#         sqlquote(SQLLiteral('NOW()')) =》 <sql: 'NOW()'>
#     """
#
#     def __init__(self, v):
#         self.v = v
#
#     def __repr__(self):
#         return self.v
#
# def safeunicode(obj, encoding='utf-8'):
#     """
#     Converts any given object to unicode string.
#     :param obj:
#     :param encoding:
#     :return:
#     """
#     t = type(obj)
#     if t is str:
#         return obj.encode(encoding)
#     elif t in [bytes, int, float, bool]:
#         return obj
#     else:
#         return str(obj).encode(encoding)
#
# def safestr(obj, encoding='utf-8'):
#     """
#     Converts any given object to utf-8 encoded string.
#     :param obj:
#     :param encoding:
#     :return:
#     """
#     if isinstance(obj, bytes):
#         return obj.decode(encoding)
#     elif isinstance(obj, str):
#         return obj
#     elif isinstance(obj, Iterable):  # iterator
#         return [safestr(item) for item in obj]
#     else:
#         return str(obj)
#
# def sqlify(obj):
#     """
#     converts `obj` to its proper SQL version
#     :param obj:
#     :return:
#     """
#     if obj is None:
#         return 'NULL'
#     elif obj is True:
#         return "1"
#     elif obj is False:
#         return "0"
#     elif datetime and isinstance(obj, datetime.datetime):
#         return repr(obj.isoformat())
#     else:
#         if isinstance(obj, bytes):
#             obj = obj.decode()
#         return repr(obj)
#
# def sqllist(lst):
#     """
#     Converts the arguments for use in something like a WHERE clause.
#     ["a","b","c"] => "a,b,c"
#     "a,b,c" => "a,b,c"
#     :param lst:
#     :return:
#     """
#     if isinstance(lst, str):
#         return lst
#     else:
#         return ', '.join(lst)
#
# def _sqllist(values):
#     """
#     list => SQLParam
#     ["a","b","c"] => <sql: '(1, 2, 3)'>
#     :param values:
#     :return: SQLQuery
#     """
#     items = []
#     items.append('(')
#     for i, v in enumerate(values):
#         if i != 0:
#             items.append(', ')
#         items.append(SQLParam(v))
#     items.append(')')
#     return SQLQuery(items)
#
# def _ssqllist(values):
#     """
#     list => SQLParam
#     ["a","b","c"] => '(1, 2, 3)'
#     :param values:
#     :return: str
#     """
#     items = []
#     items.append('(')
#     for i, v in enumerate(values):
#         if i != 0:
#             items.append(', ')
#         items.append(SQLParam(v))
#     items.append(')')
#     return str(SQLQuery(items))
#
# def sqlquote(a):
#     """
#     确保 a 可以被 SQL query 引用
#         sqlquote(True) =》 '1'
#         sqlquote(3) => 3
#         sqlquote([2, 3]) => (2, 3)
#     :param a:
#     :return: SQLQuery
#     """
#     if isinstance(a, list):
#         return _sqllist(a)
#     else:
#         return SQLParam(a).sqlquery()
#
# def ssqlquote(a):
#     """
#     确保 a 可以被 SQL query 引用
#         sqlquote(True) =》 '1'
#         sqlquote(3) => 3
#         sqlquote([2, 3]) => (2, 3)
#     :param a:
#     :return: SQLQuery
#     """
#     if isinstance(a, list):
#         return _ssqllist(a)
#     else:
#         # return SQLParam(a).sqlquery().query(paramstyle="pyformat")
#         return str(SQLParam(a).sqlquery())