let lobbyHtml = `
<div id="lobby">
	<h2>{{ user.user_name }}</h2>
	
	<div class="game-session" v-for="gameSession in gameSessions">
		<p>{{ gameSession.game_status }}</p>
		<span v-for="player in gameSession.players">{{ player.user_name }}, </span>
		<button @click="joinGame(gameSession.game_session_id)"
		        :disabled="!canJoinGame(gameSession)">
			Unirse
		</button>
	</div>
</div>
`

function pluck(array, prop) {
	let plucked = []
	
	for(el of array) {
		plucked.push(el[prop]);
	}
	
	return plucked;
}

Vue.component('lobby', {
	template: lobbyHtml,
	
	props: ['user'],

	data: function(){
		return {
			refreshInterval: null,

			gameSessions: [],
		}
	},

	methods: {
		refresh: function() {
			let app = this;
			
			axios.get('/game_sessions')
			.then(function(response) {
				app.gameSessions = response.data;
			})
			.catch(function(err) {
				console.log('such internet loss');
			});
		},
		
		canJoinGame: function(gameSession) {
			let userNames = pluck(gameSession.players, 'user_name');
			
			return gameSession.game_status == 'WAITING'
				&& (gameSession.players.length < 4 ||
					userNames.includes(this.user.user_name));
		},

		joinGame: function(gameSessionId) {
			this.$emit('joined-game', gameSessionId);
		}
	},

	mounted: function() {
		this.refreshInterval = setInterval(this.refresh, REFRESH_RATE);
	},

	destroyed: function() {
		clearInterval(this.refreshInterval);
	}

})
