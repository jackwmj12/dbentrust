
def install(name="txredisapi"):
	redisModule.install(name)

def installRedis():
	redisModule.install("redis")

def installTxRedis():
	redisModule.install("txredisapi")

def installAioRedis():
	redisModule.install("aioredis")

class redisModule():
	name = "txredisapi"

	@classmethod
	def install(cls,name= "txredisapi"):
		cls.name = name