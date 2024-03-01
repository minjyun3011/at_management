const calendarEl = document.getElementById('calendar');
const date = new Date();
const currentYear = date.getFullYear();
const currentMonth = date.getMonth();
const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

// カレンダーのHTML構造を生成
let calendarHtml = '<table><thead><tr>';
for (let i = 0; i < 7; i++) {
  calendarHtml += `<th>${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i]}</th>`;
}
calendarHtml += '</tr></thead><tbody><tr>';

for (let i = 1; i <= daysInMonth; i++) {
  const dayOfWeek = new Date(currentYear, currentMonth, i).getDay();
  if (i === 1) {
    calendarHtml += '<tr>';
    for (let j = 0; j < dayOfWeek; j++) {
      calendarHtml += '<td></td>';
    }
  }
  calendarHtml += `<td>${i}</td>`;
  if (dayOfWeek === 6) {
    calendarHtml += '</tr>';
    if (i < daysInMonth) {
      calendarHtml += '<tr>';
    }
  } else if (i === daysInMonth) {
    for (let j = dayOfWeek + 1; j <= 6; j++) {
      calendarHtml += '<td></td>';
    }
    calendarHtml += '</tr>';
  }
}
calendarHtml += '</tbody></table>';
calendarEl.innerHTML = calendarHtml;


