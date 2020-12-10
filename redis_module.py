
def installRedis(name):
	redisModule.install(name)

class redisModule():
	name = "redis"

	@classmethod
	def install(cls,name= "txredisapi"):
		cls.name = name