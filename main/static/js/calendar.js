  $(document).ready(function() {
    $('#calendar').fullCalendar({
      header: {
        left: 'month,agendaWeek,agendaDay,listMonth',
        center: 'title',
        right: 'prev,next today'
      },
      defaultDate: '2016-09-12',
      navLinks: true, // can click day/week names to navigate views
      businessHours: true, // display business hours
      editable: true,
      // events: [
      //   {
      //     title: 'Business Lunch',
      //     start: '2016-09-03T13:00:00',
      //     constraint: 'businessHours'
      //   },
      //   {
      //     title: 'Meeting',
      //     start: '2016-09-13T11:00:00',
      //     constraint: 'availableForMeeting', // defined below
      //     color: '#257e4a'
      //   },
      //   {
      //     title: 'Conference',
      //     start: '2016-09-18',
      //     end: '2016-09-20'
      //   },
      //   {
      //     title: 'Party',
      //     start: '2016-09-29T20:00:00'
      //   },

      //   // areas where "Meeting" must be dropped
      //   {
      //     id: 'availableForMeeting',
      //     start: '2016-09-11T10:00:00',
      //     end: '2016-09-11T16:00:00',
      //     rendering: 'background'
      //   },
      //   {
      //     id: 'availableForMeeting',
      //     start: '2016-09-13T10:00:00',
      //     end: '2016-09-13T16:00:00',
      //     rendering: 'background'
      //   },

      //   // red areas where no events can be dropped
      //   {
      //     start: '2016-09-24',
      //     end: '2016-09-28',
      //     overlap: false,
      //     rendering: 'background',
      //     color: '#ff9f89'
      //   },
      //   {
      //     start: '2016-09-06',
      //     end: '2016-09-08',
      //     overlap: false,
      //     rendering: 'background',
      //     color: '#ff9f89'
      //   }
      // ]
    });
    
  });