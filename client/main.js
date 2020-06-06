
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

var Player = function(name, stones) {
	this.name = name;
	this.stones = stones;
}
Player.prototype = {
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

// Should be initialized with currentPlayer
var GameState = function(players) {
	this.players = players;
	
	for (let i = 0; i < players.length; i++) {
		
		if (this.players[i].hasStone(6, 6)) {
			this.doubleDinner = this.players[i].getStone(6, 6);
			this.activePlayer = i;
			this.currentPlayer = players[i];
			break;
		}
	}
	
}

GameState.prototype = {
	board: [],

	doubleDinner: null,
	
	nextPlayer: function() {
		this.activePlayer += 1
		if (this.activePlayer > this.players.length - 1) {
			this.activePlayer = 0;
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
		new Player(playerNames[k], stones.slice(k*handSize, (k+1)*handSize)
		)
	)
}
// =====================================================================

var gameState = new GameState(players);
const boardDiv = document.getElementById('board');
const playersDiv = document.getElementById('players');
var doubleSizaButton;

var app = new Vue({
	el: '#app',
	data: function() {
		return {
			gameState: new GameState(players)
		};
	},

	methods: {
		stoneOnClick: function(stone) {
			let player = this.gameState.getActivePlayer();
			player.removeStone(stone);
			this.gameState.addStone(stone);
			this.gameState.nextPlayer();
		},

		stoneDisabled: function(player, stone) {
			if (this.gameState.getActivePlayer() != player) {
				return true;
			}

			let options = this.gameState.options();

			if (options.includes(stone.sideup) ||
				options.includes(stone.sidedown)) {
				return false;
			} else {
				return true;
			}
		}
	},

	mounted: function() {
		let player = this.gameState.getActivePlayer();
		player.removeStone(this.gameState.doubleDinner);
		this.gameState.addStone(this.gameState.doubleDinner);
		this.gameState.doubleDinner = null;
		this.gameState.nextPlayer();
	}
});
