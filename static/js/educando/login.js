$(document).ready(function(){

	//Register submit button
	$('#btn-register').on('click', function(evt){
		var form = $('#form-register');
		fname = $('#fname');
		email = $('#email');
		passwd = $('#passwd');
		rpasswd = $('#rpasswd');

		if(fname.val().length === 0 || email.val().length === 0 || passwd.val().length === 0){
			$('.error-message').text('Todos os campos são obrigatórios');
			$('.error-message').addClass('text-danger');
			return false;
		}

		if(fname.val().split(' ').length < 2){
			$('.error-message').text('Por favor informe seu nome completo');
			$('.error-message').addClass('text-danger');
			return false;
		}

		if(!is_email(email.val())){
			$('.error-message').text('Inisira um endereço de email válido');
			$('.error-message').addClass('text-danger');
			return false;
		}

		if(passwd.val() !== rpasswd.val()){
			$('.error-message').text("Senha e confirmação não são iguais");
			$('.error-message').addClass('text-danger');
			return false;
		}

		if(!$('#agreement').is(':checked')){
			$('.error-message').text("Você precia aceita nossos termos e condições");
			$('.error-message').addClass('text-danger');
			return false;
		}

		form.submit();
	});

	
	$('#btn-forgot').on('click', function(evt){
		fmail = $('#fmail').val();

		if(!is_email(fmail)){
			$('.forgot-message').text("Endereço de email inválido");
			$('.forgot-message').addClass('text-danger');
			return false;
		}

		$.ajax({
			url: '/forgot-password',
			type: 'POST',
			dataType: 'json',
			data: {
				'email': fmail,
			},
			success : function(response) {
				if(response.success){
					$.gritter.add({
						title: response.title,
						text: response.message,
						class_name: 'gritter-success gritter-center'
					});
				}else{
					$.gritter.add({
						title: response.title,
						text: response.message,
						class_name: 'gritter-error gritter-center'
					});
				}
			},
			error: function(err){
				$.gritter.add({
					title: 'Erro ao reiniciar senha!',
					text: '',
					class_name: 'gritter-error gritter-center'
				});
			
			}

		});
	});
	
	setup_facebook_login();
});

function is_email(email){
	regex = /^([\w-\+\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
    return regex.test(email);
}


function setup_facebook_login(){
	window.fbAsyncInit = function() {
		FB.init({
			appId      : '1389243914644183', // App ID
			status     : true, // check login status
			cookie     : true, // enable cookies to allow the server to access the session
			xfbml      : true  // parse XFBML
		});

		setup_facebook_button();
	};
}

function setup_facebook_button(){
	$('#fb_login_btn').click(function(evt){
		FB.getLoginStatus(function(response){
			if(response.status == 'connected'){
				FB.api('/me', function(api_response) {
					redirect_fb_logged(api_response);
				});
			}else{
				FB.login(function(response) {
					if (response.authResponse) {
						FB.api('/me', function(api_response) {
							redirect_fb_logged(api_response);
						});
					}
				}, {scope: 'email'});
			}
		});
		
	});
}

function facebook_login() {
    console.log('Bem vindo! Buscando suas informações.... ');
    FB.api('/me', function(api_response) {
      console.log('Good to see you, ' + api_response.name + '.');
      redirect_fb_logged(api_response);
    });
}

function redirect_fb_logged(fb_obj){
	$.ajax({
		url: '/login_fb',
		type: 'POST',
		dataType: 'json',
		data: {'fb_object': JSON.stringify(fb_obj)},
		success : function(resp) {
			window.location.replace(resp.redirect_to);
		},
		error: function(err){
			console.warn(err); //TODO Show error notification
		}

	});
}

function setup_gplus_button(){
	gapi.signin.render('customGPlusButton', {
		'callback': 'gplusCallback',
		'clientid': ace.data.get('GOOGLE_CLIENT_ID'),
		'cookiepolicy': 'single_host_origin',
		'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/plus.me',
	});
}

function gplusCallback(authResult) {
	if (authResult['g-oauth-window']) {
		if(authResult['access_token']){
			user_object = {};

			//TODO Feio pra caraleo!!!!! Mas as duas chamadas sao assincronas
			gapi.client.load('plus','v1', function(){
				var request = gapi.client.plus.people.get({'userId': 'me'});
				request.execute(function(resp) {
					user_object.id = resp.id;
					user_object.first_name = resp.name.givenName;
					user_object.last_name = resp.name.familyName;
					user_object.url = resp.url;
					
					gapi.client.load('oauth2','v2',function(){
						gapi.client.oauth2.userinfo.get().execute(function(resp){
							user_object.email = resp.email;
							redirect_gplus_logged(user_object);
						});
					});
				});
			});



			

		}else if(authResult['error']){
			console.warn('Could not authenticate'); //TODO Show error notification
			console.warn(authResult['error']);
		}
			
	}
}

function redirect_gplus_logged(user_object){
	$.ajax({
		url: '/login_gplus',
		type: 'POST',
		dataType: 'json',
		data: {'gplus_object': JSON.stringify(user_object)},
		success : function(resp) {
			window.location.replace(resp.redirect_to);
		},
		error: function(err){
			console.warn(err); //TODO Show error notification
		}

	});
}