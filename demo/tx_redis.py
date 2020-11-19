import os,sys

from utils import defer

sys.path.append("../../")

from twisted.internet import reactor

from redis_module import installRedis

installRedis("txredisapi")

from memobject import *

class User(MemAdmin):
    _tablename_ = "user"
    
    def __init__(self, pk=None):
        super(User, self).__init__(pk)
        
        self.username = ""
    
    def keys(self):
        return ("username",)


class Book(MemObject):
    _tablename_ = "books:book"
    
    def __init__(self, pk=None):
        super(Book, self).__init__(pk)
        
        self.bookname = ""
    
    def keys(self):
        return ("bookname",)


class UserBooks(MemRelation):
    _tablename_ = "books"
    
    _root_ = User
    _leafs_ = [Book]


@defer.inlineCallbacks
def process():
    user = User(1)
    user.username = "joe"
    yield user.insert_without_sync()
    book = Book(1)
    book.bookname = "joe's first book"
    yield book.insert_without_sync()
    books = user.build_empty_relation(UserBooks)
    yield books.append(book)
    ret = yield user.get_all()
    print(ret)
    defer.returnValue(True)
    # print(user.get_all())

def run():
    process().addCallback(lambda ign: reactor.stop())


if __name__ == '__main__':
    config = {
        "REDIS_HOST": os.environ.get("TEST_REDIS_HOST"),
        "REDIS_PASSWORD": os.environ.get("TEST_REDIS_PASSWORD"),
    }
    MemConnectionManager.initConnection(config)
    
    reactor.callWhenRunning(run)
    
    reactor.run()