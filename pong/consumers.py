import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
	playersNum = 0

	@classmethod
	async def assignPlayer(self):
		self.playersNum += 1
		if (self.playersNum <= 2):
			return f'player {self.playersNum}'
		else:
			return 'spectator'

	async def connect(self):
		await self.accept()
		playerId = self.assignPlayer()
		status = 'connected' if self.playersNum == 2 else 'waiting'
		await self.send(text_data=json.dumps({
			'assignment' : playerId,
			'status' : status
		}))

	async def disconnect(self, close_code):
		pass

	async def receive(self, text_data):
		data = json.loads(text_data)
		await self.send(text_data=json.dumps({
			'message': 'Your response here'
		}))