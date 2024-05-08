// CSRFトークン取得用の関数
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// FullCalendarインスタンスを格納するための変数をグローバルスコープで宣言
var calendar;

function saveEventToLocalstorage(eventData) {
    // ローカルストレージから現在のイベントリストを取得する
    const eventsJson = localStorage.getItem('events');
    console.log("Retrieved events from localStorage:", eventsJson); // 取得したデータの生のJSONを表示

    const existingEvents = eventsJson ? JSON.parse(eventsJson) : [];
    console.log("Parsed existing events:", existingEvents); // 解析後のイベントリストを表示

    // 新しいイベントデータをリストに追加する
    existingEvents.push(eventData);
    console.log("Updated events list with new event:", existingEvents); // 更新後のイベントリストを表示

    // 更新されたリストをローカルストレージに保存する
    localStorage.setItem('events', JSON.stringify(existingEvents));
    console.log("Saved updated events list to localStorage."); // 保存処理が完了したことを表示
}
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        console.log('Found calendar element, initializing calendar...');
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            selectable: true,
            select: function(info) {
                // イベントモーダルを表示するコード
                var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
                eventModal.show();
                document.getElementById('calendar_date').value = info.startStr.split('T')[0]; // 選択された日付をモーダルの入力欄に設定
            },
            events: fetchAndFormatEvents // 別の関数としてイベントの取得とフォーマットを行う
        });
        calendar.render();
    } else {
        console.log('Calendar element not found.');
    }
});

function fetchAndFormatEvents(fetchInfo, successCallback, failureCallback) {
    axios.post("/api/get_events/", {
        start_time: fetchInfo.startStr,
        end_time: fetchInfo.endStr,
    }, {
        headers: { 'X-CSRFToken': getCsrfToken() }
    }).then(function(response) {
        const formattedEvents = formatEvents(response.data);
        successCallback(formattedEvents);
    }).catch(function(error) {
        console.error("Error fetching events:", error);
        failureCallback(error);
    });
}

function formatEvents(eventsData) {
    return eventsData.map(event => {
        const startDateTime = new Date(`${event.calendar_date}T${event.start_time}`);
        const endDateTime = new Date(`${event.calendar_date}T${event.end_time}`);
        return {
            id: event.id,
            title: `${startDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })} ~ ${endDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })}`,
            start: startDateTime.toISOString(),
            end: endDateTime.toISOString(),
            color: event.status === '出席' ? '#57e32c' : '#f53b57',
            textColor: '#000000'
        };
    });
}

function submitEvent() {
    const eventData = {
        calendar_date: document.getElementById('calendar_date').value,
        start_time: document.getElementById('start_time').value,
        end_time: document.getElementById('end_time').value,
        status: document.getElementById('status').value,
        transportation_to: document.getElementById('transportation_to').value,
        transportation_from: document.getElementById('transportation_from').value,
        absence_reason: document.getElementById('absence_reason').value
    };

    axios.post('/api/add_event/', eventData, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    }).then(function(response) {
        const newEvent = formatEvents([response.data.eventData])[0];
        calendar.addEvent(newEvent);
        alert('イベントが正常に追加されました。');
        window.location.href = '/home1/'; // リダイレクトはイベントの追加後に実行
    }).catch(function(error) {
        console.error('Error adding event:', error);
        alert('イベントの追加に失敗しました。');
    });
}



function clearAllEventsFromLocalStorage() {
    localStorage.removeItem('events');  // 'events' キーに関連するデータを削除
    console.log("All events data removed from localStorage.");
}
