from Tetris import *
import threading
import time
import cv2
import numpy as np

KEY_UP = 2490368
KEY_DOWN = 2621440
KEY_LEFT = 2424832
KEY_RIGHT = 2555904
KEY_ENTER = 13
KEY_W = 119
KEY_A = 97
KEY_S = 115
KEY_D = 100
KEY_SPACE = 32
KEY_ESC = 27
KEY_G = 103
KEY_R = 114

class TetrisPainter:
	def __init__(self, tetrises, winSize):
		self.tetrises = tetrises
		self.tnum = len(tetrises)
		self.size = (int(winSize[0] / self.tnum), winSize[1])
		self.winSize = (self.tnum * self.size[0], self.size[1])
		self.frameWidth = 2
		self.font = cv2.FONT_HERSHEY_PLAIN
		self.fontConst = 10
		self.sizeRate = winSize[1] / 700
		self.scoreFontHeight = int(20 * self.sizeRate)
		self.scoreColor = randomColor()
		self.blockSizes = [0 for t in tetrises]
		self.mapSP = [(0, 0) for t in tetrises]
		self.nextSP = [(0, 0) for t in tetrises]
		self.scoreSP = [(0, 0) for t in tetrises]
		self.frameColor = randomColor()
		self.setBG()
	
	def setBG(self):
		self.bg = np.zeros((self.winSize[1], self.winSize[0], 3), dtype = np.uint8)
		b = int(self.size[1] * 0.02)
		trb = 2#block to frame border blank
		hfw = int(self.frameWidth / 2)
		log("Setting background, size%s"%str(self.winSize))
		for tn in range(0, self.tnum):
			bx = tn * self.size[0]
			by = 0
			cv2.rectangle(self.bg, (bx + hfw, by + hfw),
							(bx + self.size[0] - hfw, by + self.size[1] - hfw)
						, self.frameColor, self.frameWidth)
			self.blockSizes[tn] = int((self.size[1] - 4 * self.frameWidth - 2 * b - 4) / self.tetrises[tn].size[1])
			mapfsp = (bx + self.frameWidth + b + hfw, by + self.frameWidth + b + hfw)
			mapfep = (mapfsp[0] + self.blockSizes[tn] * self.tetrises[tn].size[0] + self.frameWidth + 2 * trb
							, self.size[1] - self.frameWidth - b - hfw)
			self.drawFrame(mapfsp, mapfep)
			self.mapSP[tn] = (mapfsp[0] + trb + hfw, mapfep[1] - trb - self.blockSizes[tn] * self.tetrises[tn].size[1] - hfw)
			
			nextofsp = (mapfep[0] + b + 2 * hfw, mapfsp[1])
			nextifsp = (nextofsp[0] + trb + self.frameWidth, nextofsp[1] + trb + self.frameWidth)
			nextifep = (nextifsp[0] + 4 * self.blockSizes[tn] + 2 * trb, nextifsp[1] + 4 * self.blockSizes[tn] + 2 * trb)
			nextofep = (nextifep[0] + trb + self.frameWidth, nextifep[1] + trb + self.frameWidth)
			self.drawFrame(nextofsp, nextofep)
			self.drawFrame(nextifsp, nextifep)
			self.nextSP[tn] = (nextifsp[0] + trb, nextifsp[1] + trb)
			scoretsp = (nextofsp[0] - hfw, nextofep[1] + hfw + 2 * b)
			self.drawText(self.bg, "SCORE:", scoretsp, self.scoreFontHeight, self.scoreColor, 2)
			self.scoreSP[tn] = (scoretsp[0], scoretsp[1] + b + self.scoreFontHeight)
			
		log("Background setted, size = %d"%self.bg.size)
	
	def getImg(self):
		img = self.bg.copy()
		for tn in range(0, self.tnum):
			map = self.tetrises[tn].colorMap
			bs = self.blockSizes[tn]
			t = self.tetrises[tn]
			for y in range(0, t.size[1]):
				for x in range(0, t.size[0]):
					drawBlock(img, self.mapSpTransform(tn, (x, y)), bs, map[y][x])
			item = t.item
			if item != None:
				for dy in range(0, item.size):
					for dx in range(0, item.size):
						#log("Drawing falling Item(corlor = %s)"%str(item.color))
						if item[dy][dx]:
							drawBlock(img, self.mapSpTransform(tn, (item.x + dx, item.y + dy)), bs, item.color)
			next = t.nextItem
			if next != None:
				db = int(bs * (4 - next.size) / 2)
				bx = self.nextSP[tn][0] + db
				by = self.nextSP[tn][1] + db
				for dy in range(0, next.size):
					for dx in range(0, next.size):
						if next[dy][dx]:
							drawBlock(img, (bx + dx * bs, by + dy * bs), bs, next.color)
				self.drawText(img, "%9d"%t.score, self.scoreSP[tn], self.scoreFontHeight, self.scoreColor, 2)
			
			if not t.running:
				if not t.dead:
					continue
				else:
					continue
			
			
		#log("getImg() img.size = %d"%img.size)
		return img
	
	def drawText(self, img, str, lt, height, color, thickness):
		lt = (lt[0], lt[1] + height)
		cv2.putText(img, str, lt, self.font, height / self.fontConst, color, thickness, cv2.LINE_AA)
	
	def drawFrame(self, fsp, fep):
		cv2.rectangle(self.bg, fsp, fep, self.frameColor, self.frameWidth)
	
	def mapSpTransform(self, tn, bpt):
		return (self.mapSP[tn][0] + bpt[0] * self.blockSizes[tn], self.mapSP[tn][1] + bpt[1] * self.blockSizes[tn])

def drawBlock(img, sp, size, color):
	b = 3
	s = (sp[0] + b, sp[1] + b)
	e = (sp[0] + size - b, sp[1] + size - b)
	pts = np.array([[s[0],s[1]], [s[0],e[1]], [e[0], e[1]], [e[0], s[1]]], np.int32)
	pts = pts.reshape((-1,1,2))
	cv2.fillPoly(img, [pts], color)
	
def main():
	mapSize = (10, 20)
	winSize = (1200, 700)
	tetrises = [Tetris(mapSize), Tetris(mapSize)]
	win = cv2.namedWindow("Tetris")
	cv2.moveWindow("Tetris", 0, 0)
	mutex = threading.Lock()
	
	def draw(maxFPS = 0):
		painters = TetrisPainter(tetrises, winSize)
		while True:
			cv2.imshow("Tetris", painters.getImg())
			if maxFPS != 0:
				time.sleep(1 / maxFPS)
				
	def clock(step = 0):
		while True:
			for t in tetrises:
				mutex.acquire()
				t.clock()
				mutex.release()
			time.sleep(step)
	#up 	2490368
	#down	2621440
	#left 	2424832
	#right 	2555904
	#enter	13
	#w 		119
	#a		97
	#s		115
	#d		100
	#space	32
	#esc	27
	#g		103
	#r		114
	def go():
		for t in tetrises:
			t.go()
			
	def init():
		for t in tetrises:
			t.reset()
	
	def control():
		keyMap = {
			KEY_W: 		tetrises[0].drop,
			KEY_S:		tetrises[0].down,
			KEY_A: 		tetrises[0].left,
			KEY_D: 		tetrises[0].right,
			KEY_SPACE: 	tetrises[0].rotate,
			KEY_UP:		tetrises[1].drop,
			KEY_DOWN:	tetrises[1].down,
			KEY_LEFT: 	tetrises[1].left,
			KEY_RIGHT:	tetrises[1].right,
			KEY_ENTER:	tetrises[1].rotate,
			KEY_R:		init,
			KEY_G:		go
		}
		while True:
			k = cv2.waitKeyEx(1)
			if k in range(ord("A"), ord("Z") + 1):
				k += ord("a") - ord("A")
				
			if k in keyMap:
				mutex.acquire()
				keyMap[k]()
				mutex.release()
			elif k == KEY_ESC:
				break
			elif k != -1:
				log("Unknow key(%d)"%k)
	threads = []
	threads.append(threading.Thread(target = draw))
	threads.append(threading.Thread(target = clock))
	#threads.append(threading.Thread(target = control))
	
	for t in threads:
		t.setDaemon(True)
		t.start()
	
	control()
	
	print("end")
	cv2.destroyAllWindows()

def log(obj):
	if DebugMode:
		print("TetrisWin:",str(obj))
	
if __name__ == "__main__":
	main()
