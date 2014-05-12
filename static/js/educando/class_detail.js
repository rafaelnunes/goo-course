$(document).ready(function(d){
		var hash = window.location.hash;
		$('ul.nav-tabs a[href="' + hash + '"]').tab('show');

		$('.nav-tabs a').click(function (e) {
			$(this).tab('show');
			var scrollmem = $('body').scrollTop();
			window.location.hash = this.hash;
			$('html,body').scrollTop(scrollmem);
		});

		$('.modalVideo').click(function(evt){modal_video(evt);});

		$('#modal-video').on('hidden.bs.modal', function () {
			player.pauseVideo();
		});

		$('#add-comment').click(add_comment);
		$('.del-comment').click(function(evt){delete_comment(evt);});
		$('#add-video-comment').click(function(evt){ add_video_comment(evt);});

		load_youtube_sdk();
		updateVideoDuration();
		setup_hangout_button();

});

function modal_video(evt){
	$('#modal-title').text($(evt.currentTarget).data('title'));

	var ytId = $(evt.currentTarget).data('video');

	if(player.getVideoData().video_id !== ytId)
		player.cueVideoById({'videoId': ytId, 'suggestedQuality': 'large'});
	
	$('#modal-video').modal();

	$.ajax({
		url: '/get-video-comments',
		type: 'POST',
		dataType: 'json',
		data: {
			'video': ytId,
		},
		success: function(response){
			$("#video-comments").empty();

			if(response.comments.length > 0)
				$("#video-comments").empty();

			for(var i in response.comments){
				var comment = response.comments[i];
				var tmpl = Mustache.render($('#tmpl_video_comment').html(), {'text': comment.comment, 'vtime': comment.time, 'parsed_time': parse_vtime(comment.time, true), 'cid': comment.id});
				$("#video-comments").append(tmpl);
			}
		},
		error: function(err){
			console.warn(err);
			$.gritter.add({
				title: 'Error',
				text: 'Não foi possível comentar, tente novamente em alguns segundos.',
				class_name: 'gritter-error gritter-left'
			});
		},
	});
}
function load_youtube_sdk(){
	var tag = document.createElement('script');

	tag.src = "https://www.youtube.com/iframe_api";
	var firstScriptTag = document.getElementsByTagName('script')[0];
	firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}

function onYouTubeIframeAPIReady() {
	player = new YT.Player('ytplayer', {
		height: '390',
		width: '640',
		videoId: '1',
	});

	setTimeout(function(){
		$('#modal-video').addClass('modal');
	}, 500);
}

function updateVideoDuration(){
	$('.video-duration').each(function(index, el){
		vid = $(el).data('video');
		$.ajax({
			url: 'https://gdata.youtube.com/feeds/api/videos/'+ vid +'?v=2&alt=jsonc',
			type: 'GET',
			dataType: 'json',
			success : function(response) {
				var text_duration = parse_vtime(response.data.duration);
				$(el).text(text_duration);
			},
			error: function(err){
				console.log('Could not set video duration');
			
			}
		});
	});
}

function parse_vtime(vtime, is_parseInt){
	var minutes = Math.floor(vtime / 60);
	var seconds = vtime - minutes * 60;

	if (minutes < 10)
		minutes = '0'+ minutes;

	if (seconds < 10)
		seconds = '0'+ seconds;

	return minutes + ':' + (is_parseInt ? parseInt(seconds, 10) : seconds) + ' min';
}

function setup_gclient_sdk(){
	gapi.client.load('drive', 'v2');
	$('#import-drive').click(function(event){
		event.preventDefault();
		gapi.auth.authorize(
			{
				'client_id': ace.data.get('GOOGLE_CLIENT_ID'),
				'scope': 'https://www.googleapis.com/auth/drive',
				'immediate': false
			},
			function(authResult){
				if(authResult.access_token){
					$('#modal-gdrive').modal();
					loadDriveFiles();
				}else{
					console.warn('Auth error');
				}
			}
		);
	});

	$('#more-files').click(function(evt){
		evt.preventDefault();
		var nextToken = $(evt.currentTarget).data('token');
		loadDriveFiles(nextToken);
	});

}

function loadDriveFiles(pageToken) {
  var query = {'maxResults': 10};
  var is_paging = pageToken !== undefined;
  if(is_paging)
	query['pageToken'] = pageToken;

  var request = gapi.client.drive.files.list(query);
  request.execute(function(resp){
		buildModalContent(resp, is_paging);
  });
}

function buildModalContent(response, is_paging){
	if(!is_paging)
		$("#gdrive-container").empty();

	for(var i in response.items){
		file = response.items[i];
		if(file.mimeType !== 'application/vnd.google-apps.folder'){
			var tmpl = Mustache.render($('#tmpl_gdive').html(), {'file': file, 'fjson': JSON.stringify(file)});
			$("#gdrive-container").append(tmpl);
		}
	}

	$('#more-files').attr('data-token', response.nextPageToken);

	$('.get_gdrive_file').click(function(evt){
		evt.preventDefault();

		if ($(evt.currentTarget).hasClass('gimported'))
			return;

		file = $(evt.currentTarget).data('fjson');

		$(evt.currentTarget).children('i').attr('class', 'icon-spinner icon-spin orange bigger-125');

		$.ajax({
			url: '/addmaterial_gdrive',
			type: 'POST',
			dataType: 'json',
			data: {
				'class_id': $.cls_id,
				'id': file.id,
				'url': file.alternateLink,
				'title': file.title,
				'size': file.fileSize,
				'mime': file.mimeType
			},
			success : function(response) {
				$(evt.currentTarget).children('i').attr('class', 'icon-check-sign green bigger-125');
				$(evt.currentTarget).addClass('gimported');

				var tmpl = Mustache.render($('#tmpl_add_gfile').html(), {'file': file});
				$('#material_row').append(tmpl);
			},
			error: function(err){
				console.log('Could not add file');
				//TODO show notification
			
			}
		});

	});

}

function setup_hangout_button(){
	$('#hangout-button').click(function(evt){
		evt.preventDefault();
		hangout_window = window.open($(evt.currentTarget).data('hangouturl'),
			'hangout_window',
			'toolbar=no,location=yes,status=yes,menubar=no,scrollbars=yes,resizable=yes,width=1024,height=768'
		);
	});
}

function open_hangout(btn){
	$('#modal-hangout').modal('toggle');
	hangout_window = window.open($(btn).data('hangouturl'),
			'hangout_window',
			'toolbar=no,location=yes,status=yes,menubar=no,scrollbars=yes,resizable=yes,width=1024,height=768'
		);
}

function add_comment(){
	var comment_txt = $('#comment-text');

	$.ajax({
			url: '/addcomment',
			type: 'POST',
			dataType: 'json',
			data: {
				'class_id': $.cls_id,
				'comment': comment_txt.val()
			},
			success : function(response) {
				var tmpl = Mustache.render($('#tmpl_new_comment').html(), response);
				$('#comment_list').append(tmpl);
				comment_txt.val('');

				//bind del to the trash button
				$('#adel-' + response.comment_ts).click(function(evt){delete_comment(evt);});
			},
			error: function(err){
				console.log('Could not add comment');
				console.warn(err);
				//TODO show notification
			
			}
		});
}

function delete_comment(evt){
	evt.preventDefault();

	comment_ts = $(evt.currentTarget).data('time');
	
	$.ajax({
			url: '/delete-comment',
			type: 'POST',
			dataType: 'json',
			data: {
				'class_id': $.cls_id,
				'comment_ts': comment_ts
			},
			success : function(response) {
				$('#dv-' + comment_ts).remove();
			},
			error: function(err){
				$.gritter.add({
				title: 'Error',
				text: 'Não foi possível remover o comentário, tente novamente.',
				class_name: 'gritter-error gritter-left'
			});
			
			}
	});
}

function add_video_comment(evt){
	evt.preventDefault();
	var icomm = $('#text-video-comment');

	$.ajax({
		url: '/comment-video',
		type: 'POST',
		dataType: 'json',
		data: {
			'comment': icomm.val(),
			'time': player.getCurrentTime(),
			'video': player.getVideoData().video_id,
		},
		success: function(response){
			icomm.val('');
			var tmpl = Mustache.render($('#tmpl_video_comment').html(), {'text': response.comment, 'vtime': response.time, 'parsed_time': parse_vtime(response.time, true), 'cid': response.id });
			$("#video-comments").append(tmpl);
		},
		error: function(err){
			console.warn(err);
			$.gritter.add({
				title: 'Error',
				text: 'Não foi possível comentar, tente novamente.',
				class_name: 'gritter-error gritter-left'
			});
		},
	});

}

function del_video_comment(link){
	var cid = $(link).data('comment');
	$.ajax({
		url: '/delete-video-comment',
		type: 'POST',
		dataType: 'json',
		data: {
			'comment_id': cid,
		},
		success: function(response){
			$('#video-comment-' + cid).remove();
		},
		error: function(err){
			console.warn(err);
			$.gritter.add({
				title: 'Error',
				text: 'Não foi possível remover o comentário, tente novamente.',
				class_name: 'gritter-error gritter-left'
			});
		},
	});
}


function load_on_time(link){
	time = $(link).data('time');
	player.seekTo(time, true); // allowSeekAhead = true

	return false;
}