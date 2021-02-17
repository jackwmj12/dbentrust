
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dbentrust.memobject.memobject import *

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
        "REDIS_HOST": os.environ.get("TEST_REDIS_HOST"),
        "REDIS_PASSWORD": os.environ.get("TEST_REDIS_PASSWORD"),
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