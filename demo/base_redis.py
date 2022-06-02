
import os

from dbentrust.main import installRedis

installRedis()

from dbentrust.memobject import *

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
    _leafs_ =[Book]


if __name__ == '__main__':
    config = {
        "REDIS_HOST": os.environ.get("HOST_OF_TEST"),
        "REDIS_PASSWORD": os.environ.get("PASSWORD_OF_ALI_REDIS"),
    }
    MemConnectionManager.initConnection(config)
    user = User(1)
    user.username = "joe"
    user.insert_without_sync()
    book = Book(1)
    book.bookname = "joe's first book"
    book.insert_without_sync()
    books = user.build_empty_relation(UserBooks)
    books.append(book)
    print(user.get_all())