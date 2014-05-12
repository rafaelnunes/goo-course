$(document).ready(function(){
	$('.toggleIt').click(function(evt){
		evt.preventDefault();
		var id_target = $(evt.currentTarget).data('target');
		
		$(id_target).fadeToggle();
			
	});

	$('.modalIt').click(function(evt){
		evt.preventDefault();
		var id_target = $(evt.currentTarget).data('target');
		$(id_target).modal();
	});

	$('[data-rel=tooltip]').tooltip();

	load_notifications();
	load_messages();
});

function load_notifications(){
	$.ajax({
			url: '/notifications',
			type: 'get',
			dataType: 'json',
			success : function(response) {
				for(var i in response.notifications){
					var tmpl = Mustache.render($('#tmpl_notification').html(), {'notify': response.notifications[i]});
					$('#ul-notify').append(tmpl);
				}

				var size = response.notifications.length;
				$('#notify-header-size').html('<i class="icon-warning-sign"></i>' + size +' Notifications');
				$('#notify-size').text(size);

			},
			error: function(err){
				console.log('Could not get notifications');
				console.warn(err);
				//TODO show notification
			
			}
	});
}

function load_messages(){
	$.ajax({
			url: '/inbox/recent',
			type: 'get',
			dataType: 'json',
			success : function(response) {
				for(var i in response.messages){
					var tmpl = Mustache.render($('#tmpl_message').html(), {'message': response.messages[i]});
					$('#ul-messages').append(tmpl);
				}

				$('#ul-messages').append('<li><a href="/inbox">See all messages<i class="icon-arrow-right"></i></a></li>');

				var size = response.messages.length;
				$('#messages-header-size').html('<i class="icon-warning-sign"></i>' + size +' Messages');
				$('#messages-size').text(size);

			},
			error: function(err){
				console.log('Could not get notifications');
				console.warn(err);
				//TODO show notification
			
			}
	});
}

function send_message(){
	var message_to = $('#message_to');
	var message_text = $('#message_text');
	var message_subject = $('#message_subject');

	$.ajax({
			url: '/send-message',
			type: 'POST',
			dataType: 'json',
			data: {
				'message_to': message_to.val(),
				'message_text': message_text.val(),
				'message_subject': message_subject.val(),
			},
			success : function(response) {
					$.gritter.add({
						title: 'Message Sent',
						text: '',
						class_name: 'gritter-success  gritter-light'
					});

					message_subject.val('');
					message_text.val('');

					$('#modal-sendmessage').modal('toggle');
				
			},
			error: function(err){
				console.log('Could not get notifications');
				console.warn(err);
				//TODO show notification
			
			}
	});
}
