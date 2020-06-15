var REFRESH_RATE = 1000;

var app = new Vue({
	el: '#app',
	data: function() {
		return {
			gameOcurring: false,

			user: null,
			
			gameSessionId: null,
			
			stoneDistribution: null,

			display: 'login',
		};
	},

	methods: {

		registerUser: function(user) {
			this.user = user;
			this.display = 'lobby';
		},

		joinGame: function(gameSessionId) {
			let app = this;
			
			axios.post('/join_game', {
				userId: this.user.id,
				gameSessionId: gameSessionId
			})
			.then(function(response) {
				app.gameSessionId = gameSessionId;
				app.display = 'pre-board';
			})
			.catch(function(err) {
				console.log('wow such lack of internet');
			})
		},
		
		startGame: function() {
			let app = this;
			app.display = 'board';
		}
	}
});
