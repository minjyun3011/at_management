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
        var calendar = new FullCalendar.Calendar(calendarEl, {
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
    console.log('Received event data:', response.data); // 受け取ったデータのログ出力

    const formattedEvents = response.datta.map(event => {
        console.log('Processing event:', event); // 処理中のイベントログ

        const startDateTimeString = `${event.calendar_date}T${event.start_time}`;
        const endDateTimeString = `${event.calendar_date}T${event.end_time}`;

        console.log('Combined start date and time:', startDateTimeString); // 組み合わせた開始日時のログ
        console.log('Combined end date and time:', endDateTimeString); // 組み合わせた終了日時のログ

        const startDateTime = new Date(startDateTimeString);
        const endDateTime = new Date(endDateTimeString);

        console.log('Parsed Sart Date Time:', startDateTime); // 解析した開始日時のログ
        console.log('Parsed End Date Time:', endDateTime); // 解析した終了日時のログ

        if (isNaN(startDateTime.getTime()) || isNaN(endDateTime.getTime())) {
            console.error('Invalid date time value for', startDateTimeString, endDateTimeString);
            return null; // 無効なイベントはスキップ
        }

        const formattedStartTime = startDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false });
        const formattedEndTime = endDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false });

        console.log('Formatted Start Time:', formattedStartTime); // フォーマットされた開始時刻のログ
        console.log('Formatted End Time:', formattedEndTime); // フォーマットされた終了時刻のログ

        return {
            id: event.id,
            title: `${formattedStartTime} ~ ${formattedEndTime}`,
            start: startDateTime.toISOString(),
            end: endDateTime.toISOString(),
            status: event.status,
            transportation_to: event.transportation_to,
            transportation_from: event.transportation_from,
            absence_reason: event.absence_reason,
            allDay: false
        };
    }).filter(event => event !== null); // 無効なイベントをフィルタリング

    console.log('Formatted Events:', formattedEvents); // 最終的にフォーマットされたイベントのログ
    successCallback(formattedEvents);
})
.catch(function(error) {
    console.error("Error fetching events:", error); // イベント取得失敗時のエラーログ
    failureCallback(error);
});

            }
        });

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
    const eventData = response.data.eventData;

    // 時刻データを 'HH:MM' 形式で取得
    const startTime = new Date(eventData.start).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
    const endTime = new Date(eventData.end).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });

    // タイトルを `16:00 ~ 18:00` 形式で設定
    const eventTitle = `${startTime} ~ ${endTime} ${eventData.status}`;

    // カレンダーイベントオブジェクトを設定
    calendar.addEvent({
        id: eventData.id, // イベントID
        title: eventTitle, // タイムレンジをタイトルとして使用
        start: eventData.start, // イベントの開始日時
        end: eventData.end, // イベントの終了日時
        status: eventData.status, // 出席状態
        transportation_to: eventData.transportation_to, // 往路の送迎サービス
        transportation_from: eventData.transportation_from, // 復路の送迎サービス
        absence_reason: eventData.absence_reason, // 欠席理由
        color: eventData.status === '出席' ? '#57e32c' : '#f53b57', // イベントの色を出席状態に基づいて設定
        textColor: '#000000' // テキスト色を設定
    });

    calendar.render(); // カレンダーの再描画を強制
    // 処理成功後にhome1.htmlへ画面遷移
    window.location.href = '/home1/';
})
.catch(function(error) {
    console.error('Error adding event:', error);
    alert('イベントの追加に失敗しました。');
});
}
