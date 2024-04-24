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
                    successCallback(response.data);
                })
                .catch(function(error) {
                    console.error("Event fetching failed:", error);
                    failureCallback(error);
                    alert("イベントの取得に失敗しました");
                });
            }
        });

        // ローカルストレージからイベントデータを読み込む
        var storedEvents = JSON.parse(localStorage.getItem('events') || '[]');
        console.log('Loaded events from localStorage:', storedEvents);
        storedEvents.forEach(function(eventData) {
            var startDateTime = eventData.calendar_date + 'T' + eventData.start_time + ':00';
            var endDateTime = eventData.calendar_date + 'T' + eventData.end_time + ':00';

            console.log('Adding event:', eventData);
            calendar.addEvent({
                title: eventData.full_name,
                gender:gender,
                calendar:eventData.calendar_date,
                start: startDateTime,
                end: endDateTime,
            });
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

    // 日付と時間を組み合わせる
    var startDateTime = new Date(dateInput + 'T' + startTimeInput).toISOString();
    var endDateTime = new Date(dateInput + 'T' + endTimeInput).toISOString();

    axios.post('/api/add_event/', {
        date: dateInput,
        start_time: startTimeInput,
        end_time: endTimeInput,
        status: statusInput,
        transportation_to: transportationToInput,
        transportation_from: transportationFromInput,
        absence_reason: absenceReasonInput,
    }, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(function(response) {
        console.log(response.data);
        saveEventToLocalstorage(response.data);
        calendar.addEvent({
            id: response.data.event_id, // イベントIDを追加
            title: response.data.title, // イベントタイトルとして使用
            start: startDateTime, // イベントの開始日時
            end: endDateTime, // イベントの終了日時
            status: statusInput, // 出席状態
            transportation_to: transportationToInput, // 往路の送迎サービス
            transportation_from: transportationFromInput, // 復路の送迎サービス
            absence_reason: absenceReasonInput, // 欠席理由
        });
        calendar.render(); // カレンダーの再描画を強制
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert("イベントの追加に失敗しました");
    });
}


function submitForm() {
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
    window.location.href = '/';
})}
