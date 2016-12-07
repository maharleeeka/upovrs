  $(document).ready(function() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1;
    var yyyy = today.getFullYear();

    if(dd<10){
        dd='0'+dd
    } 
    if(mm<10){
        mm='0'+mm
    }

    $('#calendar').fullCalendar({
      header: {
        left: 'month,agendaWeek,agendaDay,listMonth',
        center: 'title',
        right: 'prev,next today'
      },
      defaultDate: mm+'/'+dd+'/'+yyyy,
      navLinks: true, // can click day/week names to navigate views
      businessHours: true, // display business hours
      editable: true,

      events: [
          // {
          //    title: getEventTitle()[0],
          //    start: '2016-12-03T13:00:00',
          // },


        // areas where "Meeting" must be dropped
        // {
        //   id: 'availableForMeeting',
        //   start: '2016-12-11 T10:00:00',
        //   end: '2016-12-11 T16:00:00',
        //   rendering: 'background'
        // },

        // // red areas where no events can be dropped
        // {
        //   start: '2016-12-24',
        //   end: '2016-12-28',
        //   overlap: false,
        //   rendering: 'background',
        //   color: '#ff9f89'
        // },
      ]
    });
    
  });

function getEventTitle(){
  
  console.log(events[0]);

return events;
} 

function getEventDate(){

}

function get () {

}