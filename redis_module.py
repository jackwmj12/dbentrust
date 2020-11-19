
def installRedis(name):
	redisModule.install(name)

class redisModule():
	name = "txredisapi"

	@classmethod
	def install(cls,name= "txredisapi"):
		cls.name = name