// CSRFトークン取得用の関数
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}


// FullCalendarインスタンスを格納するための変数をグローバルスコープで宣言
var calendar;

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,

        select: function(info) {
            var eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
            eventModal.show();

            
            // 選択された日付をYYYY-MM-DDの形式で取得
            var selectedDate = info.startStr.split('T')[0];

            // モーダルのカレンダー日付フィールドに値を設定
            document.getElementById('calendar_date').value = selectedDate;

        },

        events: function (info, successCallback, failureCallback) {
            axios.post("/api/get_events/", {
                start_time: info.startStr,
                end_time: info.endStr,
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
});function submitEvent() {
    var fullName = document.getElementById('full_name').value;
    var gender = document.getElementById('gender').value;
    var startTimeInput = document.getElementById('start_time').value;
    var endTimeInput = document.getElementById('end_time').value;
    var calendarDateInput = document.getElementById('calendar_date').value;

    // 日付と時間を組み合わせる
    var combinedStartDateTime = new Date(calendarDateInput + 'T' + startTimeInput).toISOString();
    var combinedEndDateTime = new Date(calendarDateInput + 'T' + endTimeInput).toISOString();

    axios.post('/api/add_event/', {
    full_name: fullName,
    gender: gender,
    start_time: combinedStartDateTime,
    end_time: combinedEndDateTime,
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
            start: combinedStartDateTime, // イベントの開始日時
            end: combinedEndDateTime // イベントの終了日時
        });
        calendar.render(); // カレンダーの再描画を強制
    })

    .catch(function(error) {
        console.error('Error:', error);
        alert("イベントの取得に失敗しました");
    });
}
