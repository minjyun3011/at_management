// CSRFトークン取得用の関数
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}
//カレンダー環境本体のセット
var calendar;

// ローカルストレージからイベントデータを保存する関数
// function saveEventToLocalstorage(eventData) {
//     const eventsJson = localStorage.getItem('events');
//     const existingEvents = eventsJson ? JSON.parse(eventsJson) : [];
//     existingEvents.push(eventData);
//     localStorage.setItem('events', JSON.stringify(existingEvents));
//     console.log("Saved updated events list to localStorage.");
// }

//カレンダー初期化①
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
    var date = info.startStr.split('T')[0];
    var recipientNumber = sessionStorage.getItem('recipient_number');
    console.log("Recipient Number: ", recipientNumber); // ここで取得したrecipientNumberを確認
    fetchEventDetails(date, recipientNumber);
},
            events: fetchAndFormatEvents // 別の関数としてイベントの取得とフォーマットを行う
        });
        calendar.render();
    } else {
        console.log('Calendar element not found.');
    }
});

//カレンダー初期化① ＃モデルとの照合＆そのユーザーの全ての出欠情報をとってくる
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

//カレンダー初期化① ＃カレンダー描画時の出力内容の設定
function formatEvents(eventsData) {
    return eventsData.map(event => {
        const startDateTime = new Date(`${event.calendar_date}T${event.start_time}`);
        const endDateTime = new Date(`${event.calendar_date}T${event.end_time}`);
        return {
            id: event.recipient_number + event.calendar_date, // Unique IDの生成
            title: `${startDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })} ~ ${endDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })}`,
            start: startDateTime.toISOString(),
            end: endDateTime.toISOString(),
            color: event.status === '出席' ? '#57e32c' : '#f53b57',
            textColor: '#000000'
        };
    });
}
//カレンダーの日付選択② ＃イベントモーダル表示
function fetchEventDetails(date, recipientNumber) {
    axios.get(`/api/get_event_details/`, {
        params: {
            date: date,
            recipient_number: recipientNumber
        },
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
    .then(function(response) {
        console.log("API Response:", response.data);
        if (response.status === 200 && response.data) {
            // 取得したデータを表示する
            displayEventDetails(response.data);
            var detailsModal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
            detailsModal.show();
        } else if (response.status === 204) {
            // データがなければ新規登録モーダルを表示
            document.getElementById('calendar_date').value = date; // 日付フィールドに選択された日付を設定
            var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
            eventModal.show();
        }
    })
    .catch(function(error) {
        console.error("Error fetching event details:", error);
    });
}

// 取得したイベントデータをHTML仕様で表示するための関数
function displayEventDetails(data) {
    if (!data) {
        console.error('No data available to display.');
        return;
    }

    // 期待するデータ構造に基づいて変数を設定
    const event = data;
    const startDate = parseISODateTime(`${event.calendar_date}T${event.start_time}`);
    const endDate = parseISODateTime(`${event.calendar_date}T${event.end_time}`);

    // DOMにデータを設定
    document.getElementById('eventDate').textContent = event.calendar_date || 'No date provided';
    document.getElementById('eventTime').textContent = `${formatTime(startDate)} - ${formatTime(endDate)}`;
    document.getElementById('eventStatus').textContent = event.status || 'No status provided';

    // 編集ボタンにイベントリスナーを追加
document.querySelector('.edit-button').addEventListener('click', function() {
    // 詳細モーダルを閉じる
    var detailsModal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
    detailsModal.hide();

    // 詳細モーダルが閉じた後に編集モーダルを開く
    detailsModal.addEventListener('hidden.bs.modal', function onModalHidden() {
        displayEditEventDetails(data);
        detailsModal.removeEventListener('hidden.bs.modal', onModalHidden); // リスナーを削除
    });
});

}


// 編集用のイベントデータを表示する関数
function displayEditEventDetails(data) {
    console.log("Event data received for editing:", data);

    if (!data) {
        console.error('No data available for editing.');
        return;
    }

    // 編集フォームの各フィールドにデータを設定
    document.getElementById('edit_calendar_date').value = data.calendar_date || '';
    document.getElementById('edit_start_time').value = data.start_time || '';
    document.getElementById('edit_end_time').value = data.end_time || '';
    document.getElementById('edit_status').value = data.status || '';
    document.getElementById('edit_transportation_to').value = data.transportation_to || '';
    document.getElementById('edit_transportation_from').value = data.transportation_from || '';
    document.getElementById('edit_absence_reason').value = data.absence_reason || '';

    // 編集モーダルを表示
    var editModal = new bootstrap.Modal(document.getElementById('editEventModal'));
    editModal.show();
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
        var eventModalElement = document.getElementById('eventModal');
        var eventModal = bootstrap.Modal.getInstance(eventModalElement);

        // イベントリスナーを削除してから再設定
        eventModalElement.removeEventListener('hidden.bs.modal', onEventModalHidden);
        eventModalElement.addEventListener('hidden.bs.modal', onEventModalHidden);

        function onEventModalHidden(e) {
            calendar.addEvent(newEvent);
            calendar.render();
            alert('イベントが正常に追加されました。');
            window.location.href = '/home1/';
            eventModalElement.removeEventListener('hidden.bs.modal', onEventModalHidden);
        }

        eventModal.hide();
    })
    .catch(function(error) {
        console.error('Error adding event:', error);
        alert('イベントの追加に失敗しました。');
    });
}


function closeModal(modalId) {
    var modalElement = document.getElementById(modalId);
    var modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
        modalInstance.hide();
    }
}

// 更新ボタンを押した際の処理
function submitEditEvent() {
    const recipientNumber = sessionStorage.getItem('recipient_number'); // セッションストレージから取得
    const eventData = {
        recipient_number: recipientNumber,
        calendar_date: document.getElementById('edit_calendar_date').value,
        start_time: document.getElementById('edit_start_time').value,
        end_time: document.getElementById('edit_end_time').value,
        status: document.getElementById('edit_status').value,
        transportation_to: document.getElementById('edit_transportation_to').value,
        transportation_from: document.getElementById('edit_transportation_from').value,
        absence_reason: document.getElementById('edit_absence_reason').value
    };

    axios.post('/api/edit_event/', eventData, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    }).then(function(response) {
        if (response.status === 200) {
            const updatedEvent = formatEvents([response.data.eventData])[0];
            var eventModal = bootstrap.Modal.getInstance(document.getElementById('editEventModal'));

            // モーダルが完全に閉じられた後に実行されるイベントハンドラを設定
            document.getElementById('editEventModal').addEventListener('hidden.bs.modal', function (e) {
                // イベントをカレンダーに追加
                calendar.addEvent(updatedEvent);
                // カレンダーを再描画
                calendar.render();

                // モーダルが閉じたことを確認した後にアラートを表示
                alert('イベントが正常に更新されました。');

                // リダイレクトはアラート後に実行
                window.location.href = '/home1/';
            }, { once: true }); // イベントリスナーは一度だけ実行されるように設定

            // モーダルを非表示にする
            eventModal.hide();
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
