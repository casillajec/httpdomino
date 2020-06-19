let preBoardHtml = `
<div id="pre-board">
	<p>Players:</p>
	<span v-for="player in players">{{ player.user_name }}, </span>
	<button @click="startGame()"
			:disabled="!canStartGame()" >
		Empezar
	</button>
</div>
`;

Vue.component('pre-board', {
	template: preBoardHtml,
	
	mounted: function() {
		this.refresh();
		this.refreshInterval = setInterval(this.refresh, REFRESH_RATE);
	},
	
	destroyed: function() {
		clearInterval(this.refreshInterval);
	},
	
	methods: {
		refresh: function() {
			let app = this;
			
			axios.get('/game_session_players/' + this.gameSessionId)
			.then(function(response) {
				app.players = response.data;
			})
			.catch(function(err) {
				console.log('such lack of internet');
			})
		},
		
		canStartGame: function() {
			return this.players.length % 2 == 0;
		},
		
		startGame: function() {
			if (!this.canStartGame()) {
				return;
			}
			
			let app = this;
			let stones = null, playerNames = null;
			axios.post('/start_game_session', {
				gameSessionId: app.gameSessionId,
				userId: app.user.id
			})
			.then(function(response) {
				stones = response.data.player_stones;
				playerNames = response.data.player_names;
				app.$emit('started-game', stones, playerNames);
				
			}, function(err) {
				console.log('such patria');
			})
		},
	},
	
	props: ['gameSessionId', 'user'],
	
	data: function() {
		return {
			refreshInterval: null,
			
			players: []
		};
	},
});
