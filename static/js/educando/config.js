$(document).ready(function(){
	$('.save_change').on('change', function(evt){
		$.ajax({
			url: '/settings/update',
			type: 'POST',
			dataType: 'json',
			data: {
				'conf_name': $(evt.currentTarget).attr('name'),
				'conf_value': $(evt.currentTarget).is(':checked'),
			},
			success: function(response){
				$.gritter.add({
					title: 'Success',
					text: 'Configuração atualizada',
					class_name: 'gritter-success gritter-left'
				});
			},
		});
	});

	$('.change_setting').on('click', function(evt){
		evt.preventDefault();
		$.ajax({
			url: '/settings/update',
			type: 'POST',
			dataType: 'json',
			data: {
				'conf_name': $(evt.currentTarget).data('name'),
				'conf_value': $($(evt.currentTarget).data('target')).val(),
			},
			success: function(response){
				$.gritter.add({
					title: 'Success',
					text: 'Configuração atualizada',
					class_name: 'gritter-success gritter-left'
				});
			},
		});
	});

	$('#new-passwd').on('click', function(evt){
		evt.preventDefault();

		if( $('#newpasswd').val().length === 0)
			$.gritter.add({
				title: 'Error',
				text: 'A senha não pode ser vazia',
				class_name: 'gritter-error gritter-left'
			});

		$.ajax({
			url: $(evt.currentTarget).attr('href'),
			type: 'POST',
			dataType: 'json',
			data: {
				'newpass': $('#newpasswd').val()
			},
			success: function(response){
				$.gritter.add({
					title: 'Success',
					text: 'Senha modificada',
					class_name: 'gritter-success gritter-left'
				});
			},
		});
	});
});