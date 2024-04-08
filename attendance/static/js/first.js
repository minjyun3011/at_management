// CSRFトークン取得用の関数
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// FullCalendarインスタンスを格納するための変数をグローバルスコープで宣言
var calendar;
// サーバーからイベントデータを取得してカレンダーに表示する関数
// function fetchEvents() {
//     axios.get('/api/get_events') // 修正されたエンドポイント
//         .then(response => {
//             const events = response.data;
//             events.forEach(event => calendar.addEvent(event)); // カレンダーにイベントを追加
            
//             // 取得したイベントデータをローカルストレージに保存
//             localStorage.setItem('events', JSON.stringify(events));
//         })
//         .catch(error => {
//             console.error('Error fetching events:', error);
//         });
// }
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
function initializeCalendar() {
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
        // loadOrFetchEvents(); // イベントのロードまたはフェッチを呼び出す
    }
}

function saveEventAndRefreshCalendar(eventData) {
    // カレンダーがすでに初期化されているかを確認
    if (calendar) {
        // カレンダーにイベントを追加
        calendar.addEvent({
            title: eventData.full_name,
            start: eventData.start_time,
            end: eventData.end_time,
            allDay: true
        });
        // 必要に応じて、ここでカレンダーの再初期化や特定の更新処理を行う
        console.log("Calendar updated with new event.");
    } else {
        // 必要に応じてカレンダーを初期化
        console.log("Initializing calendar...");
        initializeCalendar(); // この関数はカレンダーを初期化するためのものです
        // 初期化後、イベントを追加する処理も必要に応じて実装
    }
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
        // loadOrFetchEvents(); // イベントのロードまたはフェッチを呼び出す
    }
});


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
    console.log("Received data from servers:", data);
    saveEventToLocalstorage(data);

    // カレンダーがまだ初期化されていない場合のみ初期化を行う
    if (!calendar) {
        console.log("Initializing calendar because it's not yet initialized.");
        initializeCalendar();
    }

    // イベントの追加処理（カレンダーが初期化されていることが保証されている）
    console.log("Calendar is initialized, adding event.");
    saveEventAndRefreshCalendar(data);
    console.log("Event added, now rendering the calendar.");
    calendar.render();
    
    // その後にページのリダイレクトを行う
    window.location.href = '/';
})
.catch(error => {
    console.error("Error in processing the response:", error);
});
}
