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
    var startTime = document.getElementById('start_time').value;
    var endTime = document.getElementById('end_time').value;

    axios.post('/api/add_event/', {
        full_name: fullName,
        gender: gender,
        start_time: startTime,
        end_time: endTime,
    }, {
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(function(response) {
        console.log(response.data);
        var myModalEl = document.getElementById('eventModal');
        var modal = bootstrap.Modal.getInstance(myModalEl);
        modal.hide(); // モーダルを閉じる
        calendar.refetchEvents(); // カレンダーのイベントを更新
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert('イベントの追加に失敗しました');
    });
}
