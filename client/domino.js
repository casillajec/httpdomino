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
		//return '[' + this.sideup + '|' + this.sidedown + ']';
		return this.sideup + '|' + this.sidedown;
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

var DominoTreeNode = function(stone, parent_node) {
	this.stone = stone;
	this.parent_node = parent_node;
	parent_node.child_node = this;
}

DominoTreeNode.prototype = {
	parent_node: null,
	child_node: null,
	stone: null,
}

var DominoTree = function() {}
DominoTree.prototype = {
	root: null,
	left: null,
	right: null,

	empty: function() {
		return !this.root;
	},

	addStone: function(stone, placement) {
		if (this.empty()) {
			this.root = {stone: stone};
			return;
		}
		
		let tmp = this[placement];
		if (!tmp) {
			this[placement] = new DominoTreeNode(stone, this);
			return;
		}

		while (tmp.child_node) { tmp = tmp.child_node }
		tmp.child_node = new DominoTreeNode(stone, tmp);
	},

	getFreeNmbrs: function() {
		if (this.empty()){
			return [];
		}

		let freeNmbrs = [this.root.stone.sideup, this.root.stone.sidedown];

		let tmp = this.left;
		let prev = this.root;
		while (tmp) {
			if ([prev.stone.sideup, prev.stone.sidedown].includes(tmp.stone.sideup)) {
				freeNmbrs[0] = tmp.stone.sidedown;
			} else {
				freeNmbrs[0] = tmp.stone.sideup;
			}
			prev = tmp;
			tmp = tmp.child_node;
		}

		tmp = this.right;
		prev = this.root;
		while (tmp) {
			if ([prev.stone.sideup, prev.stone.sidedown].includes(tmp.stone.sideup)) {
				freeNmbrs[1] = tmp.stone.sidedown;
			} else {
				freeNmbrs[1] = tmp.stone.sideup;
			}
			prev = tmp;
			tmp = tmp.child_node;
		}

		return freeNmbrs;
	},

	toStr: function() {
		if (this.empty()) {
			return '';
		}

		let flattened = [this.root.stone.toStr()];

		let tmp = this.left;
		let tmpStr = '[/]';
		let prev = this.root;
		while (tmp) {
			if ([prev.stone.sideup, prev.stone.sidedown].includes(tmp.stone.sideup)) {
				tmpStr = '[' + tmp.stone.sidedown + '|' + tmp.stone.sideup + ']';
			} else {
				tmpStr = '[' + tmp.stone.sideup + '|' + tmp.stone.sidedown + ']';
			}
			flattened.unshift(tmpStr);
			prev = tmp;
			tmp = tmp.child_node;
		}

		tmp = this.right;
		tmpStr = '[/]';
		prev = this.root;
		while (tmp) {
			if ([prev.stone.sideup, prev.stone.sidedown].includes(tmp.stone.sideup)) {
				tmpStr = '[' + tmp.stone.sideup + '|' + tmp.stone.sidedown + ']';
			} else {
				tmpStr = '[' + tmp.stone.sidedown + '|' + tmp.stone.sideup + ']';
			}
			flattened.push(tmpStr);
			prev = tmp;
			tmp = tmp.child_node;
		}

		let str = '';
		for (stoneStr of flattened) { str += stoneStr + ' '; }

		return str;
	}
}

// Should be initialized with currentPlayer
var GameState = function(playerNames) {
	this.playerNames = playerNames;

	this.locked = false;
}

GameState.prototype = {
	board: new DominoTree(),
	
	activePlayer: 0,
	
	version: 0,
	
	gameSessionId: null,
	
	nextPlayer: function() {
		this.activePlayer += 1
		if (this.activePlayer > this.playerNames.length - 1) {
			this.activePlayer = 0;
		}
	},
	
	getActivePlayer: function() {
		return this.playerNames[this.activePlayer];
	},

	applyDiffs: function(diffs) {
		//while (this.locked) {};
		this.locked = true;
		
		let aux = null, placement = null;
		for(let diff of diffs) {
			if (diff.version != this.version + 1) { continue; }

			if (diff.stone) {
				aux = diff.stone.split('|');
				
				placement = diff.placement ? diff.placement.toLowerCase() : diff.placement;
				
				this.board.addStone(
					new Stone(parseInt(aux[0]), parseInt(aux[1])),
					placement
				);
			}
			
			this.nextPlayer();
			this.version++;
		}

		this.locked = false;
	}
}
