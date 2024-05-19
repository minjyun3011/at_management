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

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'ja',
            headerToolbar: {
                left: 'title prev next',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            titleFormat: {
                year: 'numeric',  // 年は数字で
                month: 'long',    // 月は長い名前で
            },
            selectable: true,
            select: function(info) {
                var date = info.startStr.split('T')[0];
                var recipientNumber = sessionStorage.getItem('recipient_number');
                fetchEventDetails(date, recipientNumber);
            },
            events: fetchAndFormatEvents
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
            id: event.recipient_number + event.calendar_date,
            title: `${startDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })} ~ ${endDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })}`,
            start: startDateTime.toISOString(),
            end: endDateTime.toISOString(),
            color: event.status === '出席' ? '#57e32c' : '#f53b57',
            textColor: '#000000'
        };
    });
}

function fetchEventDetails(date, recipientNumber) {
    axios.get(`/api/get_event_details/`, {
        params: {
            date: date,
            recipient_number: recipientNumber
        },
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
    .then(function(response) {
        if (response.status === 200 && response.data) {
            displayEventDetails(response.data);
            var detailsModal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
            detailsModal.show();
        } else if (response.status === 204) {
            document.getElementById('calendar_date').value = date;
            var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
            eventModal.show();
        }
    })
    .catch(function(error) {
        console.error("Error fetching event details:", error);
    });
}

function displayEventDetails(data) {
    if (!data) {
        console.error('No data available to display.');
        return;
    }

    const event = data;
    const startDate = parseISODateTime(`${event.calendar_date}T${event.start_time}`);
    const endDate = parseISODateTime(`${event.calendar_date}T${event.end_time}`);

    document.getElementById('eventDate').textContent = event.calendar_date || 'No date provided';
    document.getElementById('eventTime').textContent = `${formatTime(startDate)} - ${formatTime(endDate)}`;
    document.getElementById('eventStatus').textContent = event.status || 'No status provided';

    document.querySelector('.edit-button').addEventListener('click', function() {
        var detailsModal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
        detailsModal.hide();

        document.getElementById('eventDetailsModal').addEventListener('hidden.bs.modal', function onModalHidden() {
            displayEditEventDetails(data);
        }, { once: true });
    });
}

function displayEditEventDetails(data) {
    if (!data) {
        console.error('No data available for editing.');
        return;
    }

    document.getElementById('edit_calendar_date').value = data.calendar_date || '';
    document.getElementById('edit_start_time').value = data.start_time || '';
    document.getElementById('edit_end_time').value = data.end_time || '';
    document.getElementById('edit_status').value = data.status || '';
    document.getElementById('edit_transportation_to').value = data.transportation_to || '';
    document.getElementById('edit_transportation_from').value = data.transportation_from || '';
    document.getElementById('edit_absence_reason').value = data.absence_reason || '';

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
