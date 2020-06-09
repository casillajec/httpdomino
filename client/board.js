let boardHtml = `
<div v-if="gameState">
<div id="board">
	<button :disabled="!(placingStone && stoneInSide(selectedStone, 0))"
			@click="placeStone(selectedStone, 'left')">
		(-
	</button>

	<p>{{ gameState.board.toStr() }}</p>

	<button :disabled="!(placingStone && stoneInSide(selectedStone, 1))"
			@click="placeStone(selectedStone, 'right')">
		-)
	</button>
</div>

<div id="players">
	<div v-for="player in gameState.players"
		 :style="{backgroundColor: player == gameState.getActivePlayer() ? 'coral' : 'white'}">
		<p>{{player.name}}</p>
		<button v-for="stone in player.stones"
				@click="stoneOnClick(stone)"
				:disabled="stoneDisabled(player, stone)">
			{{stone.toStr()}}
		</button>
		<button :disabled="passDisable(player)"
				@click="passTurn">Paso</button>
	</div>			
</div>
</div>
`

Vue.component('board', {
	template: boardHtml,
	
	props: ['stoneDistribution'],

	data: function() {
		return {
			gameState: null,

			placingStone: false,

			selectedStone: null
		};
	},

	methods: {
		stoneOnClick: function(stone) {
			this.selectedStone = stone;
			this.placingStone = true;
		},

		placeStone: function(stone, placement) {
			let player = this.gameState.getActivePlayer();
			player.removeStone(stone);
			this.gameState.board.addStone(stone, placement);
			this.gameState.nextPlayer();
			this.selectedStone = null;
			this.placingStone = false;
		},

		stoneDisabled: function(player, stone) {
			if (this.gameState.getActivePlayer() != player) {
				return true;
			}

			let options = this.gameState.board.getFreeNmbrs();

			if (options.includes(stone.sideup) ||
				options.includes(stone.sidedown)) {
				return false;
			} else {
				return true;
			}
		},

		stoneInSide: function(stone, side) {
			if (!stone) {
				return false;
			}

			let freeNmbrs = this.gameState.board.getFreeNmbrs();
			
			return [stone.sideup, stone.sidedown].includes(freeNmbrs[side]);
		},

		passDisable: function(player) {
			if (this.gameState.getActivePlayer() != player) {
				return true;
			}
			
			let freeNmbrs = this.gameState.board.getFreeNmbrs();
			return !player.stones.every(function(stone) {
				return (!stone.hasNmbr(freeNmbrs[0]) && !stone.hasNmbr(freeNmbrs[1]));
			});
		},

		passTurn: function() {
			this.gameState.nextPlayer();
		}
	},

	mounted: function() {
		// Init game state
		let players = [], stones = null;
		let aux;
		for(let player in this.stoneDistribution) {
			stones = [];
			for (let stone of this.stoneDistribution[player]) {
				aux = stone.split('|');
				stones.push(new Stone(parseInt(aux[0]), parseInt(aux[1])));
			}

			players.push(new Player(player, stones));
		}
		this.gameState = new GameState(players);
		
		let player = this.gameState.getActivePlayer();
		player.removeStone(this.gameState.doubleDinner);
		this.gameState.board.addStone(this.gameState.doubleDinner);
		this.gameState.doubleDinner = null;
		this.gameState.nextPlayer();
		
		// Refresh interval
		// TODO
	}
})
