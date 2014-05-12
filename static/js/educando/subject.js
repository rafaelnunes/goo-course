$(document).ready(function(){
	//binding events
	$('#btn-add-subject').click(add_subject);

	$('.follow-course').click(function(evt){ follow_course(evt); });

	$('.unfollow-course').click(function(evt){ unfollow_course(evt); });

	$('.del-course').click(function(evt){ delete_course(evt); });

	$('#invite-btn').click(function(evt){ invite_friend(evt); });
});

function add_subject(){
	var title = $('#subject_title').val();
	var desc = $('#subject-desc').val();

	$.ajax({
		url: '/subjects', //TODO remove hard coded urls
		method: 'POST',
		dataType: 'json',
		data:{
			'title': title,
			'desc': desc,
		},
		success: function(response){
			if(response.success){
				window.location.replace(response.redirect);
			}else{
				$('.form-error').remove();
				$('#div-form-error').removeClass('hide');
				$('#div-form-error').append('<span class="bottom5 form-error">' + response.message + '</span>');
			}
		},
		error: function(err){
			console.warn(err); // TODO alert message
		},

	});
}

function follow_course(click_event){
	click_event.preventDefault();

	$.ajax({
		url: '/follow-course', //TODO remove hard coded urls
		method: 'POST',
		dataType: 'json',
		data:{
			'course_id': $(click_event.currentTarget).data('target'),
		},
		success: function(response){
			if(response.success){
				$(click_event.currentTarget).attr('class', 'unfollow-course orange');
				$(click_event.currentTarget).children('i').attr('class', 'icon-star');
			}
		},
		error: function(err){
			console.warn(err);
		},

	});

}

function unfollow_course(click_event){
	click_event.preventDefault();

	$.ajax({
		url: '/unfollow-course', //TODO remove hard coded urls
		method: 'POST',
		dataType: 'json',
		data:{
			'course_id': $(click_event.currentTarget).data('target'),
		},
		success: function(response){
			if(response.success){
				$(click_event.currentTarget).attr('class', 'follow-course grey');
				$(click_event.currentTarget).children('i').attr('class', 'icon-star-empty');
			}
		},
		error: function(err){
			console.warn(err);
		},

	});

}

function delete_course(evt){
	evt.preventDefault();

	$.ajax({
		url: '/delete-course', //TODO remove hard coded urls
		method: 'POST',
		dataType: 'json',
		data:{
			'course_id': $(evt.currentTarget).data('target'),
		},
		success: function(response){
			$('#div-course-' + $(evt.currentTarget).data('target')).remove();
		},
		error: function(err){
			$.gritter.add({
				title: 'Error',
				text: 'Erro ao remover curso. Tente novamente.',
				class_name: 'gritter-error gritter-left',
			});
		},

	});

}

function invite_friend(evt){
	evt.preventDefault();

	var email = $('#email');

	$.ajax({
		url: '/invite-friend', //TODO remove hard coded urls
		method: 'POST',
		dataType: 'json',
		data:{
			'course_id': $(evt.currentTarget).data('target'),
			'email': email.val(),
		},
		success: function(response){
			$('#dv-invite-form').fadeToggle();
			$.gritter.add({
				title: 'Success',
				text: 'Convite enviado para "' + email.val() + '"',
				class_name: 'gritter-success gritter-left',
			});
			email.val('');
		},
		error: function(err){
			$.gritter.add({
				title: 'Error',
				text: 'Erro ao enviar convite. Tente novamente.',
				class_name: 'gritter-error gritter-left',
			});
		},

	});
}