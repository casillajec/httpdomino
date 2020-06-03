
var Stone = function(sideup, sidedown) {
	this.sideup = sideup;
	this.sidedown = sidedown;
}
Stone.prototype = {
	hasNmbr: function(nmbr) {
		return this.sideup == nmbr || this.sidedown == nmbr;
	},
	
	is: function(nmbr1, nmbr2) {
		return (this.sideup == nmbr1 && this.sidedown == nmbr2)
		    || (this.sideup == nmbr2 && this.sidedown == nmbr1);
	},
	
	toStr: function() {
		return this.sideup + ' | ' + this.sidedown;
	}
}

var Hand = function(stones) {
	this.stones = stones;
}
Hand.prototype = {
	hasNmbr: function(nmbr) {
		return this.stones.some(function(stone) {
			return stone.hasNmbr(nmbr);
		});
	},
	
	hasStone: function(nmbr1, nmbr2) {
		return this.stones.some(function(stone) {
			return stone.is(nmbr1, nmbr2);
		});
	},
	
	getStone: function(nmbr1, nmbr2) {
		for (stone of this.stones) {
			if (stone.is(nmbr1, nmbr2)) {
				return stone;
			}
		}
	},
	
	removeStone: function(stone) {
		let idx = this.stones.indexOf(stone);
		this.stones.splice(idx, 1);
	}
}

var Player = function(name, hand) {
	this.name = name;
	this.hand = hand;
}
Player.prototype = {
	hasNmbr: function(nmbr) {
		return this.hand.hasNmbr(nmbr);
	},
	
	hasStone: function(nmbr1, nmbr2) {
		return this.hand.hasStone(nmbr1, nmbr2);
	},
	
	getStone: function(nmbr1, nmbr2) {
		return this.hand.getStone(nmbr1, nmbr2);
	},
	
	removeStone: function(stone) {
		this.hand.removeStone(stone);
	}
}

// Should be initialized with currentPlayer
var GameState = function(players) {
	this.players = players;
	
	for (let i = 0; i < players.length; i++) {
		
		if (this.players[i].hasStone(6, 6)) {
			this.activePlayer = i;
			this.currentPlayer = players[i];
			break;
		}
	}
	
}

GameState.prototype = {
	board: [],
	
	nextPlayer: function() {
		
		let player = this.players[this.activePlayer];
		let playerDiv = document.getElementById('player-' + player.name);
		let stoneButtons = playerDiv.getElementsByClassName('stone-button');
		for (var stoneButton of stoneButtons) {
			stoneButton.disabled = true;
		}
		
		this.activePlayer += 1
		if (this.activePlayer > this.players.length - 1) {
			this.activePlayer = 0;
		}
		
		player = this.players[this.activePlayer];
		console.log(player.name);
		playerDiv = document.getElementById('player-' + player.name);
		stoneButtons = playerDiv.getElementsByClassName('stone-button');
		let options = this.options();
		
		for (var stoneButton of stoneButtons) {
			//console.log(stoneButton.dataset.sideup + ' | ' + stoneButton.dataset.sidedown);
			if (options.includes(parseInt(stoneButton.dataset.sideup)) ||
				options.includes(parseInt(stoneButton.dataset.sidedown))) {
				stoneButton.disabled = false;
			} else {
				stoneButton.disabled = true;
			}
		}
	},
	
	getActivePlayer: function() {
		return this.players[this.activePlayer];
	},
	
	options: function() {
		if (this.board.length == 0 || this.board.length == 1) {
			return [6];
		}
		
		let options = [];
		if (this.board[0].sideup != this.board[1].sideup &&
		    this.board[0].sideup != this.board[1].sidedown)
			options.push(this.board[0].sideup)
		else
			options.push(this.board[0].sidedown)
		
		lst = this.board.length - 1;
		if (this.board[lst].sideup != this.board[lst - 1].sideup &&
		    this.board[lst].sideup != this.board[lst - 1].sidedown)
		    options.push(this.board[lst].sideup)
		else
			options.push(this.board[lst].sideup)
			
		return options;
	},
	
	addStone: function(stone) {
		if (this.board.length == 0) {
			this.board.push(stone);
			return;
		}
		
		if (this.board[0].hasNmbr(stone.sideup) ||
		    this.board[0].hasNmbr(stone.sidedown))
			this.board.unshift(stone);
		else
			this.board.push(stone);
		
	}
}

// This should be handled by the server ================================
playerNames = [
	'Bernardo',
	'Juan',
	'Sofia',
	'Vanessa'
]
const nPlayers = playerNames.length;

stones = [];
for (var i = 0; i <= 6; i++) {
	for (var j = i; j <= 6; j++) {
		stones.push(new Stone(i, j));
	}
}
stones.sort(function(){ return Math.random() - 0.5 });
const nStones = stones.length;
const handSize = nStones/nPlayers;

players = [];
const startingPlayer = -1;
for (var k = 0; k < nPlayers; k++){
	players.push(
		new Player(
			name = playerNames[k],
			hand = new Hand(stones.slice(k*handSize, (k+1)*handSize))
		)
	)
}
// =====================================================================

var gameState = new GameState(players);
const boardDiv = document.getElementById('board');
const playersDiv = document.getElementById('players');
var doubleSizaButton;

function getBoardString(board) {
	let boardString = ''
	
	for (let stone of board) {
		boardString += stone.toStr() + ' ';
	}
	
	return boardString;
}

for (let player of gameState.players) {
	let playerDiv = document.createElement('div');
	let playerNameP = document.createElement('p');
	playerNameP.innerHTML = player.name;
	playerDiv.appendChild(playerNameP);
	playerDiv.id = 'player-' + player.name;
	
	for (let stone of player.hand.stones) {
		let stoneButton = document.createElement('button');
		stoneButton.disabled = true;
		stoneButton.innerHTML = stone.toStr();
		stoneButton.dataset.sideup = stone.sideup;
		stoneButton.dataset.sidedown = stone.sidedown;
		stoneButton.className = 'stone-button';
		
		stoneButton.onclick = function(evt) {
			/*let stoneP = document.createElement('p');
			stoneP.innerHTML = stone.toStr();
			boardDiv.appendChild(stoneP);*/
			
			player.removeStone(stone);		
			playerDiv.removeChild(stoneButton);
			gameState.addStone(stone);
			gameState.nextPlayer();
			boardDiv.innerHTML = getBoardString(gameState.board);
		}
		
		if (stone.is(6, 6)) {
			doubleSizaButton = stoneButton;
		}
		playerDiv.appendChild(stoneButton);
	}
	playersDiv.appendChild(playerDiv)
}

doubleSizaButton.onclick();
