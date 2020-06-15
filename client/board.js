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

	<div v-for="lPlayerName of gameState.playerNames"
		 :style="{backgroundColor: lPlayerName == gameState.getActivePlayer() ? 'coral' : 'white'}">
		<p>{{lPlayerName}}</p>
		
		<div v-if="playerName == lPlayerName">
		<button v-for="stone in player.stones"
				@click="stoneOnClick(stone)"
				:disabled="stoneDisabled(player, stone)">
			{{stone.toStr()}}
		</button>
		<button :disabled="passDisable(player)"
				@click="passTurn">Paso</button>
		</div>
		<div v-else>
			Other player stones
		</div>
	</div>			
</div>
</div>
`

Vue.component('board', {
	template: boardHtml,
	
	props: ['gameSessionId', 'playerId', 'playerName'],

	data: function() {
		return {
			gameState: null,
			
			player: null,

			placingStone: false,

			selectedStone: null,

			refreshInterval: null,
		};
	},

	methods: {
		stoneOnClick: function(stone) {
			this.selectedStone = stone;
			this.placingStone = true;
		},

		placeStone: function(stone, placement) {
			this.registerPlay(stone, placement);
			this.player.removeStone(stone);
			this.selectedStone = null;
			this.placingStone = false;
		},

		stoneDisabled: function(player, stone) {
			if (this.gameState.getActivePlayer() != this.playerName) {
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
		},

		refresh: function() {
			let app = this;
			
			if (!app.gameState) { return; }
			
			axios.get('/get_game_state_diffs/' + 
			          app.gameSessionId + '/' + 
			          app.gameState.version)
			.then(function (response) {
				let gameStateDiffs = response.data;
				app.gameState.applyDiffs(gameStateDiffs);
				app.$forceUpdate();
			})
			.catch(function (err) {
				console.log(err);
			})
		},
		
		registerPlay: function(stone, placement) {
			let app = this;
			
			axios.post('/register_play', {
				gameSessionId: app.gameSessionId,
				userId: app.playerId,
				version: app.gameState.version,
				stone: stone.toStr(),
				placement: placement,
				tstamp: + new Date()
			})
			.then(function(response) {})
			.catch(function (err) {
				console.log('man your internet is so bad');
			})
						
		}
	},

	mounted: function() {
		let app = this;
		
		axios.get('/get_player_stones/' + 
				   app.gameSessionId + '/' + 
				   app.playerId)
		.then(function(response) {
			
			app.gameState = new GameState(response.data.player_names);
			
			let stones = [],
				aux = null,
				tmpStone = null,
				doubleDinner = null;
			
			for (let stone of response.data.player_stones) {
				aux = stone.split('|');
				tmpStone = new Stone(parseInt(aux[0]), parseInt(aux[1]));
				if (tmpStone.is(6, 6)) { doubleDinner = tmpStone; }
				stones.push(tmpStone);
			}
			
			app.player = new Player(app.playerName, stones);
			
			if (doubleDinner) {
				app.registerPlay(doubleDinner);
				app.player.removeStone(doubleDinner);
			}
		})
		.catch(function(err) {
			console.log('such patria');
		});
		
		// Refresh interval
		this.refreshInterval = setInterval(this.refresh, REFRESH_RATE);
	},

	destroyed: function() {
		clearInterval(this.refreshInterval);
	}
})
