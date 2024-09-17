import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import iCalendarPlugin from '@fullcalendar/icalendar'


let calendarEl = document.getElementById('calendar');
let calendar = new Calendar(calendarEl, {
  plugins: [ dayGridPlugin, timeGridPlugin, listPlugin, iCalendarPlugin ],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,listWeek'
  },
  events: {
    url: 'https://raw.githubusercontent.com/MarcinVaadin/plany-zajec/main/strefazajec.ics',
    format: 'ics'
  },
  locale: 'pl'
});
calendar.render();