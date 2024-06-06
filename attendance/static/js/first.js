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
            events: fetchAndFormatEvents,
            eventTimeFormat: { // 表示形式の設定
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            },
            eventContent: function(arg) {
                let customHtml = '';
                if (arg.event.allDay) {
                    customHtml = '<div class="fc-event-title">' + arg.event.title + '</div>';
                } else {
                    customHtml = `
                        <div class="fc-event-title">${arg.event.title}</div>
                    `;
                }
                return { html: customHtml };
            }
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
        const startDateTime = event.start_time ? new Date(`${event.calendar_date}T${event.start_time}`) : null;
        const endDateTime = event.end_time ? new Date(`${event.calendar_date}T${event.end_time}`) : null;

        let title = '';
        let allDay = false; // 全日イベントかどうかのフラグ

        if (event.status === 'AB') {
            title = '欠席予定';
            allDay = true; // 欠席の場合は全日イベントとして扱う
        } else if (startDateTime && endDateTime) {
            title = `出席 ${startDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })}~${endDateTime.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })}`;
        } else {
            title = '時間未設定';
        }

        return {
            id: event.recipient_number + event.calendar_date,
            title: title,
            start: startDateTime ? startDateTime.toISOString() : new Date(event.calendar_date).toISOString(),
            end: endDateTime ? endDateTime.toISOString() : new Date(event.calendar_date).toISOString(),
            textColor: '#000000',
            allDay: allDay, // 欠席の場合は全日イベントとして扱う
            classNames: event.status === 'AB' ? ['absent'] : [] // クラス名を設定
        };
    });
}
function fetchEventDetails(date, recipientNumber) {
    console.log(`Fetching event details for date: ${date} and recipient_number: ${recipientNumber}`);  // デバッグ用ログ
    axios.get(`/api/get_event_details/`, {
        params: {
            date: date,
            recipient_number: recipientNumber
        },
        headers: { 'X-CSRFToken': getCsrfToken() }
    })
    .then(function(response) {
        console.log('API response status:', response.status);  // APIレスポンスのステータスコードをログに表示
        console.log('API response data:', response.data);  // APIレスポンスのデータをログに表示
        if (response.status === 200 && response.data.combined_data && response.data.combined_data.length > 0) {
            displayEventDetails(response.data.combined_data[0]); 
            var detailsModal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
            detailsModal.show();
        } else if (response.status === 204) {
            console.log('No event data found for this date');  // 204の場合のログ
            document.getElementById('calendar_date').value = date;
            document.getElementById('calendar_date_display').textContent = date; // 日付のテキスト表示を設定
            var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
            console.log('Showing event modal');  // モーダル表示前のログ
            eventModal.show();
        } else {
            console.warn('Unexpected status code:', response.status);  // その他のステータスコードの警告ログ
        }
    })
    .catch(function(error) {
        console.error("Error fetching event details:", error);  // エラーログ
    });
}

function displayEventDetails(event) {
    console.log('Displaying event details with data:', event);  // 受け取ったデータをログに表示

    if (!event) {
        console.error('No data available to display.');
        document.getElementById('eventDate').textContent = 'No date provided';
        return;
    }

    document.getElementById('eventDate').textContent = `日付: ${event.calendar_date || 'No date provided'}`;

    // ステータスを日本語で表示
    const statusText = event.status === 'PR' ? '出席' : (event.status === 'AB' ? '欠席' : 'No status provided');
    document.getElementById('eventStatus').textContent = `状態: ${statusText}`;

    if (event.status === 'AB') { // 欠席の場合
        document.getElementById('eventTime').style.display = 'none';
        document.getElementById('absenceReason').style.display = 'block';
        document.getElementById('absenceReason').textContent = `欠席理由: ${event.absence_reason || 'No reason provided'}`;
        document.getElementById('transportationDetails').style.display = 'none';
    } else { // 出席の場合
        document.getElementById('eventTime').style.display = 'block';
        const startDate = event.start_time ? new Date(`${event.calendar_date}T${event.start_time}`) : null;
        const endDate = event.end_time ? new Date(`${event.calendar_date}T${event.end_time}`) : null;
        document.getElementById('eventTime').textContent = startDate && endDate
            ? `時間: ${startDate.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })} - ${endDate.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false })}`
            : '時間未設定';

        let transportationDetails = '';
        if (event.transportation_to === 'US' && event.transportation_from === 'US') {
            transportationDetails = '送迎（行き・帰り）あり';
        } else if (event.transportation_to === 'US' && event.transportation_from === 'NU') {
            transportationDetails = '送迎あり（行きのみ）';
        } else if (event.transportation_to === 'NU' && event.transportation_from === 'US') {
            transportationDetails = '送迎あり（帰りのみ）';
        } else {
            transportationDetails = '送迎なし';
        }

        document.getElementById('transportationDetails').textContent = transportationDetails;
        document.getElementById('transportationDetails').style.display = 'block';
        document.getElementById('absenceReason').style.display = 'none';
    }

    if (event.updater) {
        document.getElementById('eventUpdater').textContent = `更新者: ${event.updater}`;
        document.getElementById('eventUpdater').style.display = 'block';
        document.getElementById('eventInputter').style.display = 'none';
    } else if (event.inputter) {
        document.getElementById('eventInputter').textContent = `入力者: ${event.inputter}`;
        document.getElementById('eventInputter').style.display = 'block';
        document.getElementById('eventUpdater').style.display = 'none';
    } else {
        document.getElementById('eventUpdater').style.display = 'none';
        document.getElementById('eventInputter').style.display = 'none';
    }

    document.querySelector('.edit-button').addEventListener('click', function() {
        var detailsModal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
        detailsModal.hide();

        document.getElementById('eventDetailsModal').addEventListener('hidden.bs.modal', function onModalHidden() {
            displayEditEventDetails(event);
        }, { once: true });
    });
}

function displayEditEventDetails(data) {
    if (!data) {
        console.error('No data available for editing.');
        return;
    }

    document.getElementById('edit_calendar_date_display').textContent = data.calendar_date || '';
    document.getElementById('edit_calendar_date').value = data.calendar_date || '';
    document.getElementById('edit_start_time').value = data.start_time || '';
    document.getElementById('edit_end_time').value = data.end_time || '';
    document.getElementById('edit_status').value = data.status || '';
    document.getElementById('edit_transportation_to').value = data.transportation_to || '';
    document.getElementById('edit_transportation_from').value = data.transportation_from || '';
    document.getElementById('edit_absence_reason').value = data.absence_reason || '';
    document.getElementById('edit_updater').value = data.updater || '';

    toggleFields(data.status);  // ステータスに基づいてフィールドを表示/非表示にする

    var editModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('editEventModal'));
    editModal.show();
}



function parseISODateTime(dateTimeString) {
    return new Date(dateTimeString);
}

function formatTime(date) {
    return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', hour12: false });
}



// 追加の出欠情報をモデルに保存＆カレンダー再描画するメインの関数
function submitEvent() {
    const eventData = {
        calendar_date: document.getElementById('calendar_date').value,
        start_time: document.getElementById('start_time').value,
        end_time: document.getElementById('end_time').value,
        status: document.getElementById('status').value,
        transportation_to: document.getElementById('transportation_to').value,
        transportation_from: document.getElementById('transportation_from').value,
        absence_reason: document.getElementById('absence_reason').value || "",
        inputter: document.getElementById('inputter').value  // 入力者フィールドを追加
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
    }).catch(function(error) {
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
    const recipientNumber = sessionStorage.getItem('recipient_number');
    console.log(`Submitting event edit for recipient_number: ${recipientNumber}`);  // デバッグ用ログ
    const eventData = {
        recipient_number: recipientNumber,
        calendar_date: document.getElementById('edit_calendar_date').value,
        start_time: document.getElementById('edit_start_time').value,
        end_time: document.getElementById('edit_end_time').value,
        status: document.getElementById('edit_status').value,
        transportation_to: document.getElementById('edit_transportation_to').value,
        transportation_from: document.getElementById('edit_transportation_from').value,
        absence_reason: document.getElementById('edit_absence_reason').value,
        updater: document.getElementById('edit_updater').value // 更新者フィールドを追加
    };

    axios.post('/api/edit_event/', eventData, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    }).then(function(response) {
        if (response.status === 200) {
            const updatedEvent = response.data.eventData;
            console.log('Event updated:', updatedEvent);  // デバッグ用ログ
            var eventModal = bootstrap.Modal.getInstance(document.getElementById('editEventModal'));

            // モーダルが完全に閉じられた後に実行されるイベントハンドラを設定
            document.getElementById('editEventModal').addEventListener('hidden.bs.modal', function (e) {
                // カレンダーイベントを更新
                fetchEventDetails(updatedEvent.calendar_date, updatedEvent.recipient_number);  // recipient_numberを渡す
                console.log(`Fetching details for date: ${updatedEvent.calendar_date} and recipient_number: ${updatedEvent.recipient_number}`);  // デバッグ用ログ

                // モーダルが閉じたことを確認した後にアラートを表示
                alert('イベントが正常に更新されました。');

                // リダイレクトはアラート後に実行
                window.location.href = '/home1/';
            }, { once: true }); // イベントリスナーは一度だけ実行されるように設定

            // モーダルを非表示にする
            eventModal.hide();
        }
    }).catch(function(error) {
        console.error('Error editing event:', error.response ? error.response.data : error.message);
        alert('Error editing event: ' + (error.response ? error.response.data.message : error.message));
    });
}




// ステータスに応じてフィールドを表示/非表示にする関数
function toggleFields(status) {
    const transportationFields = document.querySelectorAll('.transportation-group');
    const absenceFields = document.querySelectorAll('.absence-group');
    const timeFields = document.querySelectorAll('.time-group');

    if (status === 'PR') { // 出席
        transportationFields.forEach(field => field.classList.remove('hidden'));
        absenceFields.forEach(field => field.classList.add('hidden'));
        timeFields.forEach(field => field.classList.remove('hidden'));
    } else if (status === 'AB') { // 欠席
        transportationFields.forEach(field => field.classList.add('hidden'));
        absenceFields.forEach(field => field.classList.remove('hidden'));
        timeFields.forEach(field => field.classList.add('hidden'));
    }
}

// モーダルが表示されたときに現在のステータスに基づいてフィールドを設定
document.addEventListener('DOMContentLoaded', function() {
    const editEventModal = document.getElementById('editEventModal');
    const eventModal = document.getElementById('eventModal');

    editEventModal.addEventListener('shown.bs.modal', function() {
        const status = document.getElementById('edit_status').value;
        toggleFields(status);
    });

    eventModal.addEventListener('shown.bs.modal', function() {
        const status = document.getElementById('status').value;
        toggleFields(status);
    });

    // ステータスが変更されたときにフィールドの表示を更新
    document.getElementById('edit_status').addEventListener('change', function() {
        toggleFields(this.value);
    });

    document.getElementById('status').addEventListener('change', function() {
        toggleFields(this.value);
    });
});




function clearAllEventsFromLocalStorage() {
    localStorage.removeItem('events');  // 'events' キーに関連するデータを削除
    console.log("All events data removed from localStorage.");
}
