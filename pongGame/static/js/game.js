const gameId = "123";
const socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const scoreboard = document.getElementById('scoreboard');

let playerID = null;
let playerSide = null;
let gameStarted = false;
let playersConnected = false;

const paddleWidth = 10;
const paddleHeight = 100;

const ballSize = 10;

const player = {
    x: 0,
    y: (canvas.height - paddleHeight) / 2,
    width: paddleWidth,
    height: paddleHeight,
    score: 0,
    color: 'white'
};

const opponent = {
    x: canvas.width - paddleWidth,
    y: (canvas.height - paddleHeight) / 2,
    width: paddleWidth,
    height: paddleHeight,
    score: 0,
    color: 'white'
};

const ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    size: ballSize,
    color: 'white'
};

socket.onopen = function(event) {
    console.log('WebSocket is connected.');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);

	if (data.status === 'GameStarting') {
		playerID = data.playerID;
		if (data.side === 'left') {
			playerSide = 'left';
			player.x = 0;
			opponent.x = canvas.width - paddleWidth;
		}
		else {
			playerSide = 'right';
			player.x = canvas.width - paddleWidth;
			opponent.x = 0;
		}
		for (const playerDataID in data.gameState.paddlePosition) {
			const playerData = data.gameState.paddlePosition[playerDataID];
			if (playerData.playerID === playerID) {
				player.y = playerData.y;
			}
			else {
				opponent.y = playerData.y;
			}
		}
		for (const scoresPlayerID in data.gameState.scores) {
			const scores = data.gameState.scores[scoresPlayerID];
			if (scores.playerID === playerID) {
				player.score = scores.score;
			}
			else {
				opponent.score = scores.score;
			}
		}
		ball.x = data.gameState.ballPosition.x;
		ball.y = data.gameState.ballPosition.y;
		gameStarted = true;
	}
	if (data.type === 'gameStateUpdate') {
		for (const playerDataID in data.gameState.paddlePosition) {
			const playerData = data.gameState.paddlePosition[playerDataID];
			if (playerData.playerID === playerID) {
				player.y = playerData.y;
			}
			else {
				opponent.y = playerData.y;
			}
		}
		for (const scoresPlayerID in data.gameState.scores) {
			const scores = data.gameState.scores[scoresPlayerID];
			if (scores.playerID === playerID) {
				player.score = scores.score;
			}
			else {
				opponent.score = scores.score;
			}
		}
		ball.x = data.gameState.ballPosition.x;
		ball.y = data.gameState.ballPosition.y;
	}
	if (data.type == 'paddlePositionUpdate') {
		if (data.playerID === playerID) {
			player.y = data.y;
		}
		else {
			opponent.y = data.y;
		}
	}
};

socket.onclose = function(event) {
    console.log('WebSocket is closed now.');
};

function movePaddle(direction) {
	if (playerID != 'spectator') {
		const moveData = {
			type: 'paddleMove',
			sender: playerID,
			direction: direction, // 'up' or 'down'
		};
		socket.send(JSON.stringify(moveData));
	}
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowUp') {
        movePaddle('up');
    } else if (event.key === 'ArrowDown') {
        movePaddle('down');
    }
});

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
	ctx.fillStyle = 'black';
	ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = player.color;
    ctx.fillRect(player.x, player.y, player.width, player.height);
    
    ctx.fillStyle = opponent.color;
    ctx.fillRect(opponent.x, opponent.y, opponent.width, opponent.height);

    ctx.fillStyle = ball.color;
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.size, 0, Math.PI * 2);
    ctx.fill();

	if (playersConnected == false)
		scoreboard.textContent = 'player did not connect yet.';
	else
		scoreboard.textContent = "players connected.";
}

function gameLoop() {
    draw();
    requestAnimationFrame(gameLoop);
}

window.onload = function() {
    gameLoop();
};