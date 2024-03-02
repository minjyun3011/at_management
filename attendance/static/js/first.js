// CSRF対策
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,

        select: function(info) {
    var myModal = new bootstrap.Modal(document.getElementById('myModal'));
    myModal.show();

    // モーダルの開始時間と終了時間のフィールドに値を設定
    document.getElementById('start_time').value = info.startStr;
    document.getElementById('end_time').value = info.endStr;
},

        events: function (info, successCallback, failureCallback) {
            axios.post("/api/events/", { // Djangoのビューに対応するエンドポイントに修正
                start: info.startStr,
                end: info.endStr,
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
    var eventName = document.getElementById('full_name').value;
    var gender = document.getElementById('gender').value;
    var startTime = document.getElementById('start_time').value;
    var endTime = document.getElementById('end_time').value;

    // CSRFトークンの取得
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    axios.post('/api/add_event/', {
        full_name: eventName,
        gender: gender,
        start_time: startTime,
        end_time: endTime,
    }, {
        headers: {
            // CSRFトークンをリクエストヘッダーに設定
            'X-CSRFToken': csrfToken,
        }
    })
    .then(function(response) {
        console.log(response.data);
        $('#eventModal').modal('hide'); // モーダルを閉じる
        calendar.refetchEvents(); // カレンダーのイベントを更新
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert('イベントの追加に失敗しました');
    });
}

