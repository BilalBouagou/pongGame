import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
	players = set()
	playersNum = 0

	async def assignPlayer(self):
		self.playersNum += 1
		if self.playersNum <= 2:
			player_id = f'player {self.playersNum}'
			self.players.add(player_id)
			return player_id
		else:
			return 'spectator'

	async def connect(self):
		await self.accept()
		playerId = await self.assignPlayer()
		status = 'connected' if self.playersNum == 2 else 'waiting'
		await self.send(text_data=json.dumps({
			'assignment': playerId,
			'status': status
		}))
		if (self.playersNum == 2):
			await self.broadcast_player_count()

	async def disconnect(self, close_code):
		if self.playersNum > 0:
			self.players.remove(f'player {self.playersNum}')
			self.playersNum -= 1
			await self.broadcast_player_count()

	async def broadcast_player_count(self):
		count = len(self.players)
		for player in self.players:
			await self.channel_layer.group_send(
				player,
				{
					'status': 'playing',
					'type': 'player_count',
					'count': count
				}
			)

	async def player_count(self, event):
		count = event['count']
		await self.send(text_data=json.dumps({
			'type': 'player_count',
			'count': count
		}))

	async def receive(self, text_data):
		data = json.loads(text_data)
		await self.send(text_data=json.dumps({
			'message': 'Your response here'
		}))