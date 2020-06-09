let loginHtml = `
<div id="login">
	<p>Nombre:</p>
	<input type="text" v-model="userName"></input>
	<button @click="sendLogin">Entrar</button>
</div>
`;

Vue.component('login', {
	template: loginHtml,

	data: function() {
		return {
			userName: ''
		};
	},

	methods: {
		sendLogin: function() {
			if (!this.userName) { return; }
			
			let app = this;
			axios.post('/login', { userName: this.userName })
			.then(function(response) {
				let user = response.data;
				app.$emit('logged-in', user);
			})
			.catch(function(err) {
				console.log('such lack of connection');
			})
		}
	}
});
