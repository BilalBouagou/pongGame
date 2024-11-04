const socket = new WebSocket('ws://localhost:8000/ws/pong/');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const scoreboard = document.getElementById('scoreboard');

let playerId = null;
let gameStarted = false;
let playersConnected = false;

const paddleWidth = 10;
const paddleHeight = 100;
const playerSpeed = 5;

const ballSize = 10;
let ballSpeedX = 5;
let ballSpeedY = 5;

const player = {
    x: 0,
    y: (canvas.height - paddleHeight) / 2,
    width: paddleWidth,
    height: paddleHeight,
    color: 'white'
};

const opponent = {
    x: canvas.width - paddleWidth,
    y: (canvas.height - paddleHeight) / 2,
    width: paddleWidth,
    height: paddleHeight,
    color: 'white'
};

const ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    size: ballSize,
    color: 'white'
};

function reset() {
	ball.x = canvas.width / 2;
	ball.y = canvas.height / 2;
	player.x = 0;
	player.y = (canvas.height - paddleHeight) / 2;
	opponent.x = canvas.width - paddleWidth;
	opponent.y = (canvas.height - paddleHeight) / 2;
}

socket.onopen = function(event) {
    console.log('WebSocket is connected.');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message from server:', data);

    if (data.assignment) {
        playerId = data.assignment;
		if (playerId == 'player 1') {
			player.x = 0;
			player.y = (canvas.height - paddleHeight) / 2;
			opponent.x = canvas.width - paddleWidth;
			opponent.y = (canvas.height - paddleHeight) / 2;
		}
		else {
			opponent.x = 0;
			opponent.y = (canvas.height - paddleHeight) / 2;
			player.x = canvas.width - paddleWidth;
			player.y = (canvas.height - paddleHeight) / 2;
		}
		if (data.status) {
			if (data.status === 'playing') {
				gameStarted = true;
			}
			if (data.status === 'connected') {
				playersConnected = true;
			}
		}
    }
};

socket.onclose = function(event) {
    console.log('WebSocket is closed now.');
};

function movePaddle(direction) {
	if (playerId != 'spectator') {
		const moveData = {
			action: 'move_paddle',
			sender: playerId,
			direction: direction, // 'up' or 'down'
		};
		socket.send(JSON.stringify(moveData));

		if (direction === 'up') {
			player.y -= playerSpeed;
		}
		else {
			player.y += playerSpeed;
		}
	}
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowUp') {
        movePaddle('up');
    } else if (event.key === 'ArrowDown') {
        movePaddle('down');
    }
});

function updateGame(data) {
    // Handle other game updates (scores, etc.)
}

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

function update() {
    ball.x += ballSpeedX;
    ball.y += ballSpeedY;

    if (ball.y + ball.size > canvas.height || ball.y - ball.size < 0) {
        ballSpeedY = -ballSpeedY;
    }

    if (ball.x - ball.size < player.x + player.width && 
        ball.y > player.y && 
        ball.y < player.y + player.height) {
        ballSpeedX = -ballSpeedX;
    }

    if (ball.x + ball.size > opponent.x && 
        ball.y > opponent.y && 
        ball.y < opponent.y + opponent.height) {
        ballSpeedX = -ballSpeedX;
    }

    if (ball.x + ball.size < 0 || ball.x - ball.size > canvas.width) {
        ball.x = canvas.width / 2;
        ball.y = canvas.height / 2;
        ballSpeedX = -ballSpeedX;
		if (ball.x + ball.size < player.x || ball.x + ball.size > player.x) { // report score
			const data = {
				action: 'score',
				sender: playerId,
			};
			socket.send(JSON.stringify(data));
		}
    }
}

function gameLoop() {
	if (gameStarted)
    	update();
    draw();
    requestAnimationFrame(gameLoop);
}

window.onload = function() {
    gameLoop();
};