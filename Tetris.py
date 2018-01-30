import random
import time
import math

DebugMode = True

class Model:
	def __init__(self, name, list):#list is a tuple
		self.list = list
		self.size = len(list)
		self.name = name
		flag = False
		c = 0
		for r in list:
			for p in r:
				flag = flag or p
			if flag:
				break;
			else:
				c += 1
		self.sy = -c
		
		
class Item:
	def __init__(self, model, x , y = None, color = None):
		self.model = model
		self.list = [list(r) for r in model.list]
		self.plist = model.list
		self.size = model.size
		self.x = x
		self.px = x
		self.y = model.sy if y == None else y
		self.py = self.y
		self.color = randomColor() if color == None else color
	
	def __getitem__(self, index):
		return self.list[index]
	
	def move(self):
		self.list = self.plist
		self.y = self.py
		self.x = self.px
	
	def unmove(self):
		self.plist = self.list
		self.py = self.y
		self.px = self.x
		#self.log("unmoved, x = %d, y = %d"%(self.x, self.y))
	
	def down(self):
		self.py += 1
	
	def left(self):
		self.px -= 1
	
	def right(self):
		self.px += 1
	
	def rotate(self):
		self.plist = [[self.list[self.size - x - 1][y] for x in range(0, self.size)] for y in range(0, self.size)]
		
	def log(self, obj):
		print("Item(M-%s):%s"%(self.model.name, str(obj)))
	
	
class Tetris:
	def_model_set = [Model("J", ((1, 0, 0), (1, 1, 1), (0, 0, 0)))
					,Model("L", ((0, 1, 0), (0, 1, 0), (0, 1, 1)))
					,Model("Z", ((1, 1, 0), (0, 1, 1), (0, 0, 0)))
					,Model("S", ((0, 1, 1), (1, 1, 0), (0, 0, 0)))
					,Model("O", ((1, 1), (1, 1)))
					,Model("I", ((0, 0, 0, 0), (1, 1, 1, 1), (0, 0, 0, 0), (0, 0, 0, 0)))]
	tetris_num = 0
	
	def __init__(self, size, bgColor = (0, 0, 0), reward = 10, modelSet = def_model_set):
		self.id = Tetris.tetris_num + 1
		Tetris.tetris_num += 1
		
		self.size = size
		self.width = size[0]
		self.height = size[1]
		self.modelSet = modelSet
		self.bgColor = bgColor
		self.map = [[0 for x in range(0, size[0])] for y in range(0, size[1])]
		self.colorMap = [[bgColor for x in range(0, size[0])] for y in range(0, size[1])]
		self.running = False
		self.dead = False
		self.item = None
		self.score = 0
		self.reward = reward
		self.lastTime = 0
		self.setStepTime()
		self.setNextItem()
		
	def reset(self):
		self.__init__(self.size, self.bgColor, self.reward, self.modelSet)
	
	def setStepTime(self):
		#self.stepTime = (- math.atan(0.01 * self.score - 10) + math.pi / 2) / math.pi
		self.stepTime = 0.4
		
	def setNextItem(self, model = None):
		if model == None:
			model = random.choice(self.modelSet)
		
		self.nextItem = Item(model, int((self.width - model.size)/ 2))
	 
	def go(self):
		if not self.running:
			self.log("GO!!")
			self.createItem()
			self.running = True
		
	def fail(self):
		self.dead = True
	
	def createItem(self):
		if self.crashCheck(self.nextItem):
			self.log("createItemFail-%s"%self.nextItem.model.name)
			self.fail()
		else:
			self.log("createItemSuccess-%s"%self.nextItem.model.name)
			self.item = self.nextItem
			self.setNextItem()
		
	def crashCheck(self, item = None):
		if item == None:
			item = self.item
		for by in range(0, item.size):	
			for bx in range(0, item.size):
				x = item.px + bx
				y = item.py + by
				if item.plist[by][bx]:
					if x < 0 or x >= self.width or y < 0 or y >= self.height:
						return True
					elif self.map[y][x]:
						return True
		return False
					
	
	def moveCheck(self):
		if self.crashCheck():
			self.item.unmove()
			return False
		else:
			self.item.move()
			return True
	
	def fix(self):
		for by in range(0, self.item.size):	
			for bx in range(0, self.item.size):
				x = self.item.x + bx
				y = self.item.y + by
				if self.item[by][bx]:
					#self.log("Fixing Item, x = %d, y = %d"%(x, y))
					self.map[y][x] = 1
					self.colorMap[y][x] = self.item.color
		self.item = None
		self.clear()
		self.createItem()
		
	def clear(self):
		y = self.height - 1
		while y >= 0:
			flag = True
			for bx in self.map[y]:
				flag = flag and bx
			if flag:
				del self.map[y]
				del self.colorMap[y]
				self.map.insert(0, [0 for x in range(0, self.width)])
				self.colorMap.insert(0, [self.bgColor for x in range(0, self.width)])
				self.score += self.reward
				self.setStepTime()
			else:
				y -= 1
				
				
	def down(self):
		if not self.dead and self.running:
			self.item.down()
			if not self.moveCheck():
				self.fix()
				return False
			return True
	
	def left(self):
		if not self.dead and self.running:
			self.item.left()
			self.moveCheck()
		
	def right(self):
		if not self.dead and self.running:
			self.item.right()
			self.moveCheck()
	
	def rotate(self):
		if not self.dead and self.running:
			self.item.rotate()
			self.moveCheck()
	
	def drop(self):
		if not self.dead and self.running:
			while self.down():
				continue
	
	def clock(self):
		nowTime = time.time()
		if nowTime - self.lastTime >= self.stepTime:
			if self.running and not self.dead:
				self.down()
			self.lastTime = time.time()
		return self.stepTime
		
	def log(self, obj):
		if DebugMode:
			print("Tetris-%d:%s"%(self.id, str(obj)))
		
		
def randomColor():
	#return (0, 255, 0)
	return (random.randint(100,255), random.randint(100,255), random.randint(100,255))
	