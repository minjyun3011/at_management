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

            // モーダルの開始時間と終了時間のフィールドに値を設定
            document.getElementById('start_time').value = info.startStr;
            document.getElementById('end_time').value = info.endStr;
            document.getElementById('calendar_date').value = info.startStr; // 例えば、開始時間をカレンダーの日付として保存する

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
});
function submitEvent() {
    var fullName = document.getElementById('full_name').value;
    var gender = document.getElementById('gender').value;
    
    // Dateオブジェクトを生成する際の変数名が重複しているため、変更する
    var startTimeInput = document.getElementById('start_time').value; 
    var endTimeInput = document.getElementById('end_time').value; 
    var calendarDateInput = document.getElementById('calendar_date').value; 

    // ISO文字列形式で送信
    var startTime = new Date(startTimeInput).toISOString();
    var endTime = new Date(endTimeInput).toISOString();
    var calendarDate = new Date(calendarDateInput).toISOString();

    axios.post('/api/add_event/', {
        full_name: fullName,
        gender: gender,
        start_time: startTime,
        end_time: endTime,
        calendar_date: calendarDate, 
    }, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(function(response) {
        console.log(response.data);
        // 成功時の処理
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert('イベントの追加に失敗しました');
    });
}
