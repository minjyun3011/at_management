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
    console.log('DOM fully loaded and parsed');
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        console.log('Found calendar element, initializing calendar...');
        // カレンダーを初期化
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            selectable: true,
            select: function(info) {
                var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
                eventModal.show();
                var selectedDate = info.startStr.split('T')[0];
                document.getElementById('calendar_date').value = selectedDate;
            },
            events: function(info, successCallback, failureCallback) {
                axios.post("/api/get_events/", {
                    start_time: info.startStr,
                    end_time: info.endStr,
                }, {
                    headers: { 'X-CSRFToken': getCsrfToken() },
                })
                .then(function(response) {
                    console.log('Events fetched successfully', response.data);
                    response.data.forEach(event => {
                        calendar.addEvent({
                            title: event.title || `${event.status} - ${event.calendar_date}`, // タイトルがない場合はステータスと日付を表示
                            start: event.start_time,
                            end: event.end_time,
                            status: event.status,
                            transportation_to: event.transportation_to,
                            transportation_from: event.transportation_from,
                            absence_reason: event.absence_reason
                        });
                    });
                })
                .catch(function(error) {
                    console.error("Event fetching failed:", error);
                    failureCallback(error);
                    alert("イベントの取得に失敗しました");
                });
            }
        });

        // カレンダーを描画
        console.log('Rendering calendar...');
        calendar.render();
        console.log('Rendered calendar.');
    } else {
        console.log('Calendar element not found.');
    }
});


function clearAllEventsFromLocalStorage() {
    localStorage.removeItem('events');  // 'events' キーに関連するデータを削除
    console.log("All events data removed from localStorage.");
}

//カレンダー選択時イベントモーダルでの出欠情報保存の処理
function submitEvent() {
    var dateInput = document.getElementById('calendar_date').value;
    var startTimeInput = document.getElementById('start_time').value;
    var endTimeInput = document.getElementById('end_time').value;
    var statusInput = document.getElementById('status').value; // 出席状態
    var transportationToInput = document.getElementById('transportation_to').value; // 往路の送迎サービス
    var transportationFromInput = document.getElementById('transportation_from').value; // 復路の送迎サービス
    var absenceReasonInput = document.getElementById('absence_reason').value; // 欠席理由

    axios.post('/api/add_event/', {
        calendar_date: dateInput,
        start_time: startTimeInput,
        end_time: endTimeInput,
        status: statusInput,
        transportation_to: transportationToInput,
        transportation_from: transportationFromInput,
        absence_reason: absenceReasonInput,
    }, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',

        }
    })
    .then(function(response) {
    console.log(response.data);
    saveEventToLocalstorage(response.data);  // ローカルストレージに保存
    const startTime = new Date(response.data.eventData.start).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
    const endTime = new Date(response.data.eventData.end).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
    const eventTitle = `${startTime} ~ ${endTime}`;

    calendar.addEvent({
        id: response.data.event_id, // イベントIDを追加
        title: eventTitle,  // タイムレンジをタイトルとして使用
        start: response.data.eventData.start, // イベントの開始日時
        end: response.data.eventData.end, // イベントの終了日時
        status: response.data.eventData.status, // 出席状態
        transportation_to: response.data.eventData.transportation_to, // 往路の送迎サービス
        transportation_from: response.data.eventData.transportation_from, // 復路の送迎サービス
        absence_reason: response.data.eventData.absence_reason, // 欠席理由
    });
    calendar.render(); // カレンダーの再描画を強制
    // 処理成功後にhome1.htmlへ画面遷移
    window.location.href = '/home1/';
})
.catch(function(error) {
    console.error('Error:', error);
    alert("イベントの追加に失敗しました");
});

}
