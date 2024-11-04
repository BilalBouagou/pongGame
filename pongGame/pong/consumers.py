from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import json
import random
import string

# todo : implement "sides" logic and game scoring

class GameConsumer(AsyncWebsocketConsumer):
	gameStates = {}
	SCREEN_WIDTH = 800
	SCREEN_HEIGHT = 400
	PADDLE_WIDTH = 10
	PADDLE_HEIGHT = 100
	PADDLE_SPEED = 5

	async def generatePlayerID(self): # generate random player ID if user is not authenticated idk wach nkhlih il3b aslan warever
		return ''.join(random.choice(string.ascii_letters) for _ in range(10))

	async def connect(self):
		self.gameID = self.scope['url_route']['kwargs']['game_id']
		self.playerID = self.scope['user'].username if self.scope['user'].is_authenticated else await self.generatePlayerID()
		self.room_group_name = f'game_{self.gameID}'

		await self.accept()

		if self.gameID not in self.gameStates:
			self.gameStates[self.gameID] = {
				'paddlePosition': {},
				'scores': {},
				'ballPosition': {
					'x': self.SCREEN_WIDTH / 2,
					'y': self.SCREEN_HEIGHT / 2
				},
				'ballDirection': {
					'x': random.choice([-5, 5]),
					'y': random.choice([-5, 5])
				}
			}

		if self.playerID not in self.gameStates[self.gameID]['paddlePosition']:
			self.playerSide = 'left' if len(self.gameStates[self.gameID]['paddlePosition']) == 0 else 'right'
			self.gameStates[self.gameID]['paddlePosition'][self.playerID] =  {
				'y' : (self.SCREEN_HEIGHT - self.PADDLE_HEIGHT) / 2,
				'playerID' : self.playerID,
				'side' : self.playerSide
			}
			self.gameStates[self.gameID]['scores'][self.playerID] = {
				'score' : 0,
				'playerID' : self.playerID,
				'side' : self.playerSide
			}

		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		if len(self.channel_layer.groups[self.room_group_name]) == 2:
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type' : 'notifyPlayers',
					'status' : 'GameStarting',
					'side' : self.playerSide,
					'playerID' : self.playerID,
					'gameState' : self.gameStates[self.gameID]
				}
			)
			self.gameTask = asyncio.create_task(self.gameLoop(self.gameID))

	async def disconnect(self, close_code):
		pass

	async def notifyPlayers(self, event):
		await self.send(text_data=json.dumps({
			'type': 'notifyPlayers',
			'status': event['status'],
			'side': event['side'],
			'playerID': event['playerID'],
			'gameState': event['gameState']
		}))

	async def gameLoop(self, gameID):
		await asyncio.sleep(4) # wait for a couple seconds to allow players to get ready baa3
		while True:
			# ball position update
			self.gameStates[gameID]['ballPosition']['x'] += self.gameStates[gameID]['ballDirection']['x']
			self.gameStates[gameID]['ballPosition']['y'] += self.gameStates[gameID]['ballDirection']['y']
			# collision detection
			if self.gameStates[gameID]['ballPosition']['y'] < 0 or self.gameStates[gameID]['ballPosition']['y'] > self.SCREEN_HEIGHT:
				self.gameStates[gameID]['ballDirection']['y'] *= -1
			# paddle collision detection
			for playerID in self.gameStates[gameID]['paddlePosition']:
				if self.gameStates[gameID]['paddlePosition'][playerID]['side'] == 'left':
					if self.gameStates[gameID]['ballPosition']['x'] < self.PADDLE_WIDTH and self.gameStates[gameID]['ballPosition']['y'] > self.gameStates[gameID]['paddlePosition'][playerID]['y'] and self.gameStates[gameID]['ballPosition']['y'] < self.gameStates[gameID]['paddlePosition'][playerID]['y'] + self.PADDLE_HEIGHT:
						self.gameStates[gameID]['ballDirection']['x'] *= -1
				else:
					if self.gameStates[gameID]['ballPosition']['x'] > self.SCREEN_WIDTH - self.PADDLE_WIDTH and self.gameStates[gameID]['ballPosition']['y'] > self.gameStates[gameID]['paddlePosition'][playerID]['y'] and self.gameStates[gameID]['ballPosition']['y'] < self.gameStates[gameID]['paddlePosition'][playerID]['y'] + self.PADDLE_HEIGHT:
						self.gameStates[gameID]['ballDirection']['x']  *= -1
			# score detection
			if self.gameStates[gameID]['ballPosition']['x'] < 0 or self.gameStates[gameID]['ballPosition']['x'] > self.SCREEN_WIDTH:
				if self.gameStates[gameID]['ballPosition']['x'] < 0:
					for playerID in self.gameStates[gameID]['paddlePosition']:
						if self.gameStates[gameID]['paddlePosition'][playerID]['side'] == 'right':
							self.gameStates[gameID]['scores'][playerID]['score'] += 1
							break
				elif self.gameStates[gameID]['ballPosition']['x'] > self.SCREEN_WIDTH:
					for playerID in self.gameStates[gameID]['paddlePosition']:
						if self.gameStates[gameID]['paddlePosition'][playerID]['side'] == 'left':
							self.gameStates[gameID]['scores'][playerID]['score'] += 1
							break
				self.gameStates[gameID]['ballPosition']['x'] = self.SCREEN_WIDTH / 2
				self.gameStates[gameID]['ballPosition']['y'] = self.SCREEN_HEIGHT / 2
				self.gameStates[gameID]['ballDirection']['x'] = random.choice([-5, 5])
				self.gameStates[gameID]['ballDirection']['y'] = random.choice([-5, 5])

			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'gameStateUpdate',
					'gameState': self.gameStates[gameID],
					'playerID': self.playerID,
					'side': self.playerSide
				}
			)
			await asyncio.sleep(0.03) # 30 FPS

	async def gameStateUpdate(self, event):
		await self.send(text_data=json.dumps({
			'type': 'gameStateUpdate',
			'gameState': event['gameState']
		}))

	async def paddlePositionUpdate(self, event):
		await self.send(text_data=json.dumps({
			'type': 'paddlePositionUpdate',
			'playerID': event['playerID'],
			'y': event['y'],
			'side': event['side']
		}))

	async def receive(self, text_data):
		data = json.loads(text_data)
		if data['type'] == 'paddleMove':
			if data['direction'] == 'up':
				position = self.gameStates[self.gameID]['paddlePosition'][self.playerID]['y'] - self.PADDLE_SPEED
				if position < 0:
					position = 0
			else:
				position = self.gameStates[self.gameID]['paddlePosition'][self.playerID]['y'] + self.PADDLE_SPEED
				if position > self.SCREEN_HEIGHT - self.PADDLE_HEIGHT:
					position = self.SCREEN_HEIGHT - self.PADDLE_HEIGHT
			self.gameStates[self.gameID]['paddlePosition'][self.playerID]['y'] = position
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'paddlePositionUpdate',
					'playerID': self.playerID,
					'side': self.playerSide,
					'y': position
				}
			)