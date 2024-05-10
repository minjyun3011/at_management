// CSRFトークン取得用の関数
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}
//カレンダー環境本体のセット
var calendar;

// ローカルストレージからイベントデータを保存する関数
function saveEventToLocalstorage(eventData) {
    const eventsJson = localStorage.getItem('events');
    const existingEvents = eventsJson ? JSON.parse(eventsJson) : [];
    existingEvents.push(eventData);
    localStorage.setItem('events', JSON.stringify(existingEvents));
    console.log("Saved updated events list to localStorage.");
}

//JS起動時の自動処理（カレンダー初期化）
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        console.log('Found calendar element, initializing calendar...');
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'ja',
            headerToolbar: {
            left: 'title prev next',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
            titleFormat: { // タイトルのフォーマットをカスタマイズ
            year: 'numeric',  // 年は数字で
            month: 'long',    // 月は長い名前で
        },
            selectable: true,
            select: function(info) {
                var eventModal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
                    eventModal.show();
                resetModals();
                // 選択された日付のイベント詳細を取得する
                fetchEventDetails(info.startStr.split('T')[0]);
            },
            events: fetchAndFormatEvents // 別の関数としてイベントの取得とフォーマットを行う
        });
        calendar.render();
    } else {
        console.log('Calendar element not found.');
    }
});

// JS起動時に、既存の出欠情報をカレンダーに描画するための関数(events)
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

//submitEvent()関数にてカレンダーに追加するイベントデータの形を決める関数
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

//カレンダーの日付を選択した時に始まる処理関数（select)
function fetchEventDetails(date) {
    axios.get(`/api/get_event_details/`, {
        params: { date: date },
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
    .then(function(response) {
        if (response.data.length > 0) {
            displayEventDetails(response.data);
            new bootstrap.Modal(document.getElementById('eventDetailsModal')).show();
        } else {
            document.getElementById('calendar_date').value = date; // Set date for new event
            new bootstrap.Modal(document.getElementById('eventModal')).show();
        }
    })
    .catch(function(error) {
        console.error("Error fetching event details:", error);
    });
}
function resetModals() {
    // Reset event modal form contents without destroying the modal instance
    var eventForm = document.getElementById('eventForm');
    eventForm.reset();  // Reset all form inputs to default

    // Manually clear any specific states or selections
    document.getElementById('calendar_date').value = '';
    document.getElementById('start_time').value = '';
    document.getElementById('end_time').value = '';
    document.getElementById('status').value = '';
    document.getElementById('transportation_to').value = '';
    document.getElementById('transportation_from').value = '';
    document.getElementById('absence_reason').value = '';

    // Close the modals if they are open
    var detailsModalInstance = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
    if (detailsModalInstance) {
        detailsModalInstance.hide();
    }

    var eventModalInstance = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
    if (eventModalInstance) {
        eventModalInstance.hide();
    }
}

// 取得したイベントデータをHTML仕様で表示するための関数
function displayEventDetails(data) {
    if (!data || data.length === 0) {
        console.error('No data available to display.');
        return;
    }

    // 期待するデータ構造に基づいて変数を設定
    const event = data[0]; // 複数イベントがある場合は、適切なイベントデータを選択
    const startDate = parseISODateTime(`${event.calendar_date}T${event.start_time}`);
    const endDate = parseISODateTime(`${event.calendar_date}T${event.end_time}`);

    // DOMにデータを設定
    document.getElementById('eventDate').textContent = event.calendar_date || 'No date provided';
    document.getElementById('eventTime').textContent = `${formatTime(startDate)} - ${formatTime(endDate)}`;
    document.getElementById('eventStatus').textContent = event.status || 'No status provided';
}

function parseISODateTime(dateTimeStr) {
    const dateTime = new Date(dateTimeStr);
    if (isNaN(dateTime.getTime())) {
        console.error('Invalid date/time string:', dateTimeStr);
        return new Date();  // デフォルトの日付オブジェクトを返す（エラーハンドリングの一環）
    }
    return dateTime;
}

function formatTime(date) {
    return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false });
}



//追加の出欠情報をモデルに保存＆カレンダー再描画するメインの関数
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
    var eventModal = bootstrap.Modal.getInstance(document.getElementById('eventModal'));

    // モーダルが完全に閉じられた後に実行されるイベントハンドラを設定
    document.getElementById('eventModal').addEventListener('hidden.bs.modal', function (e) {
        // イベントをカレンダーに追加
        calendar.addEvent(newEvent);
        // カレンダーを再描画
        calendar.render();

        // モーダルが閉じたことを確認した後にアラートを表示
        alert('イベントが正常に追加されました。');

        // リダイレクトはアラート後に実行
        window.location.href = '/home1/';
    }, { once: true }); // イベントリスナーは一度だけ実行されるように設定

    // モーダルを非表示にする
    eventModal.hide();
})
.catch(function(error) {
    console.error('Error adding event:', error);
    alert('イベントの追加に失敗しました。');
});
}

//既存のデータを編集するために入力フォームに既存のデータ内容を表示するための関数
function submitEditEvent() {
    // 現在のイベントデータを取得
    const eventData = {
        id: document.getElementById('event_id').value, // イベントID
        calendar_date: document.getElementById('calendar_date').value,
        start_time: document.getElementById('start_time').value,
        end_time: document.getElementById('end_time').value,
        status: document.getElementById('status').value,
        transportation_to: document.getElementById('transportation_to').value,
        transportation_from: document.getElementById('transportation_from').value,
        absence_reason: document.getElementById('absence_reason').value
    };

    // APIに編集データを送信
    axios.post('/api/edit_event/', eventData, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    }).then(function(response) {
        if (response.status === 200) {
            alert('イベントが正常に更新されました。');
            window.location.reload(); // 画面をリロードして更新を反映
        }
    }).catch(function(error) {
        console.error('Error editing event:', error);
        alert('イベントの更新に失敗しました。');
    });
}


function clearAllEventsFromLocalStorage() {
    localStorage.removeItem('events');  // 'events' キーに関連するデータを削除
    console.log("All events data removed from localStorage.");
}
