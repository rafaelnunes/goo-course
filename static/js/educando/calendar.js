$(document).ready(function(){
	/* initialize the external events
	-----------------------------------------------------------------*/
	$('#external-events div.external-event').each(function() {

		// create an Event Object (http://arshaw.com/fullcalendar/docs/event_data/Event_Object/)
		// it doesn't need to have a start or end
		var eventObject = {
			title: $.trim($(this).text()) // use the element's text as the event title
		};

		// store the Event Object in the DOM element so we can get to it later
		$(this).data('eventObject', eventObject);

	});

	/* initialize the calendar
	-----------------------------------------------------------------*/
	var calendar = $('#calendar').fullCalendar({
		buttonText: {
			prev: '<i class="icon-chevron-left"></i>',
			next: '<i class="icon-chevron-right"></i>'
		},
	
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month'
		},
		events: function(start, end, callback){
			$.ajax({
				url: '/calendar/events',
				type: 'GET',
				dataType: 'json',
				success: function(resp){
					var loaded = [];
					$(resp.events).each(function(index, ev){
						loaded.push({
							title: ev.summary,
							start: $.fullCalendar.parseDate(ev.start_date, 'yyyy-MM-dd HH:mm'),
							id: ev.id,
							course: ev.course,
							course_title: ev.course_title,
							allDay: false,
							className: ev.className
						});
					});
					callback(loaded);
				},
			});
		},
		editable: true,
		selectable: true,
		selectHelper: true,
		timeFormat: 'H(:mm)TT ',
		select: function(start, end, allDay) {
			var courses = [];
			$.ajax({url: '/get-courses', type: 'GET', async: false}).done(function(response){ courses = response.courses;});

			var tmpl = Mustache.render($('#tmpl_add_event').html(), {'courses': courses});

			var div = bootbox.dialog({
				title: 'Add a new event to ' + $.fullCalendar.formatDate(start, 'dd/MM/yyyy'),
				message: tmpl,
				buttons: {
					success: {
						label : "<i class='icon-calendar'></i> Add Event",
						className : "btn-sm btn-success",
						callback: function() {
							add_event(start);
						},
					}
				},

			});

			$('#event_time').timepicker({
				minuteStep: 1,
				showMeridian: false
			}).next().on(ace.click_event, function(){
				$(this).prev().focus();
			});

			calendar.fullCalendar('unselect');
		},
		eventClick: function(calEvent, jsEvent, view) {
			var tmpl = Mustache.render($('#tmpl_add_event').html(),
				{'id': calEvent.id, 'summary': calEvent.title, 'time': $.fullCalendar.formatDate(calEvent.start, 'HH:mm'), 'courses': {'id': calEvent.course, 'title': calEvent.course_title }});

			var div = bootbox.dialog({
				title: 'Edit event on ' + $.fullCalendar.formatDate(calEvent.start, 'dd/MM/yyyy'),
				message: tmpl,
				buttons: {
					"delete" : {
						"label" : "<i class='icon-trash'></i> Delete Event",
						"className" : "btn-sm btn-danger",
						"callback": function() {
							calendar.fullCalendar('removeEvents' , function(ev){
								return (ev._id == calEvent._id);
							});
							delete_event(calEvent.id);
						},
					},
					success: {
						label : "<i class='icon-calendar'></i> Update Event",
						className : "btn-sm btn-success",
						callback: function() {
							calendar.fullCalendar('removeEvents' , function(ev){
								return (ev._id == calEvent._id);
							});
							delete_event(calEvent.id);
							add_event(calEvent.start);
						},
					}
				},

			});
		},
		
	});

	$('#calendar').fullCalendar('addEventSource', gcalendar_url);
	setTimeout(function(){
		$('#load-gcal').remove();
	}, 3000);
});


function add_event(evt_date){
	var evt_title = $('#event_title').val();
	var evt_start = $('#event_time').val();
	var course = $('#event_course').find(":selected").val();

	$.ajax({
		url: '/calendar/add',
		type: 'POST',
		dataType: 'json',
		data: {
			'course': course,
			'date': $.fullCalendar.formatDate(evt_date, 'yyyy-MM-dd'),
			'time': evt_start,
			'text': evt_title,
			'id': $('#calEvent_id').val(),
		},
		success: function(response){
			$('#calendar').fullCalendar('renderEvent',{
				title: response.summary,
				start: $.fullCalendar.parseDate(response.start_date, 'yyyy-MM-dd HH:mm'),
				id: response.id,
				course: response.course,
				course_title: response.course_title,
				allDay: false,
				className: 'label-yellow'
			}, true);
			$('#calendar').fullCalendar('rerenderEvents');
		},
		error: function(err){
			$.gritter.add({
				title: 'Error',
				text: 'Event not added',
				class_name: 'gritter-error gritter-left',
			});
		},

	});
}

function delete_event(id){
	$.ajax({
		url: '/calendar/delete',
		type: 'POST',
		dataType: 'json',
		data: {
			'id': id,
		},
	});
}
