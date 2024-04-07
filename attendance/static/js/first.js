// CSRFトークン取得用の関数
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// FullCalendarインスタンスを格納するための変数をグローバルスコープで宣言
var calendar;
// サーバーからイベントデータを取得してカレンダーに表示する関数
function fetchEvents() {
    axios.get('/api/get_events') // 修正されたエンドポイント
        .then(response => {
            const events = response.data;
            events.forEach(event => calendar.addEvent(event)); // カレンダーにイベントを追加
            
            // 取得したイベントデータをローカルストレージに保存
            localStorage.setItem('events', JSON.stringify(events));
        })
        .catch(error => {
            console.error('Error fetching events:', error);
        });
}
function saveEventToLocalstorage(eventData) {
    // ローカルストレージから現在のイベントリストを取得する
    const existingEvents = JSON.parse(localStorage.getItem('events')) || [];
    // 新しいイベントデータをリストに追加する
    existingEvents.push(eventData);
    // 更新されたリストをローカルストレージに保存する
    localStorage.setItem('events', JSON.stringify(existingEvents));
}

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
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
                    successCallback(response.data);
                })
                .catch(function(error) {
                    console.error("Event fetching failed:", error);
                    failureCallback(error);
                    alert("イベントの取得に失敗しました");
                });
            },
        });

        calendar.render();
        loadOrFetchEvents(); // イベントのロードまたはフェッチを呼び出す
    }
});

function loadOrFetchEvents() {
    var storedEvents = JSON.parse(localStorage.getItem('events'));
    if (storedEvents) {
        storedEvents.forEach(event => calendar.addEvent({
            title: event.full_name,
            start: event.start_time,
            end: event.end_time,
            allDay: true
        }));
    }
}


function submitEvent() {
    var fullName = document.getElementById('full_name').value;
    var gender = document.getElementById('gender').value;
    var startTimeInput = document.getElementById('start_time').value;
    var endTimeInput = document.getElementById('end_time').value;
    var calendarDateInput = document.getElementById('calendar_date').value;

    // 日付と時間を組み合わせる
    var startDateTime = new Date(calendarDateInput + 'T' + startTimeInput).toISOString();
    var endDateTime = new Date(calendarDateInput + 'T' + endTimeInput).toISOString();


    axios.post('/api/add_event/', {
    full_name: fullName,
    gender: gender,
    start_time: startDateTime,
    end_time: endDateTime,
    calendar_date: calendarDateInput,
}, {
    headers: {
        'X-CSRFToken': getCsrfToken(),
        
    }
})
    .then(function(response) {
        console.log(response.data);
        // 成功時の処理：カレンダーにイベントを追加
        calendar.addEvent({
            id: response.data.event_id, // イベントIDを追加
            title: fullName, // フルネームをイベントタイトルとして使用
            start: startDateTime, // イベントの開始日時
            end: endDateTime ,// イベントの終了日時
            calendar_date: calendarDateInput,
        });
        calendar.render(); // カレンダーの再描画を強制
    })

    .catch(function(error) {
        console.error('Error:', error);
        alert("イベントの取得に失敗しました");
    });

}function submitForm() {
    var fullName = document.getElementById('full_name').value;
    var gender = document.getElementById('gender').value;
    var calendarDate = document.getElementById('calendar_date').value;
    var startTime = document.getElementById('start_time').value;
    var endTime = document.getElementById('end_time').value;

    // 日付と時間を組み合わせてISO8601形式に変換
    var startDateTime = new Date(calendarDate + 'T' + startTime).toISOString();
    var endDateTime = new Date(calendarDate + 'T' + endTime).toISOString();

    var jsonData = JSON.stringify({
        full_name: fullName,
        gender: gender,
        calendar_date: calendarDate,
        start_time: startDateTime,
        end_time: endDateTime
    });

    fetch('/api/event_add/', {
        method: 'POST',
        body: jsonData,
        headers: {
            "X-CSRFToken": getCsrfToken(),
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }
        return response.json();  // サーバーからのレスポンスをJSON形式で解析
    })
    .then(data => {
        console.log("Received data from servers:", data);  // サーバーから受け取ったデータをログに記録
        saveEventToLocalstorage(data);

        // カレンダーが初期化されているかチェックし、イベントを追加
        if (calendar) {
            console.log("Calendar is initialized, adding event."); 
            calendar.addEvent({
                title: fullName,
                start: startDateTime,
                end: endDateTime,
                allDay: true
            });
            console.log("Event added, now rendering the calendar."); 
            calendar.render();  // カレンダーの再描画
        } else {
            console.log("Calendar is not initialized."); 
        }
    })
    .catch(error => {
        console.error("Error in processing the response:", error); 
    });
}
