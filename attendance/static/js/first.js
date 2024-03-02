// CSRF対策
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,

        select: function(info) {
            // モーダルを表示し、ユーザーにイベントの詳細入力を促す
            $('#eventModal').modal('show');
            // モーダル内の開始時間と終了時間のフィールドを選択した範囲で設定するロジックをここに追加
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

// イベントの送信関数（モーダルの保存ボタンに紐付ける）
function submitEvent() {
    var eventName = document.getElementById('eventName').value; // モーダル内の入力フィールドから値を取得
    var gender = document.getElementById('gender').value; // 性別の選択を取得

    // CSRFトークンを取得
    const csrfToken = getCookie('csrftoken');

    // フォームデータを使用してサーバーにPOSTリクエストを送信
    axios.post('/api/add_event/', { // Djangoのビューに対応するエンドポイントに修正
        full_name: eventName,
        gender: gender,
        // start_time と end_time の値を適切に設定するロジックをここに追加
    }, {
        headers: {
            'X-CSRFToken': csrfToken,
        }
    })
    .then(function(response) {
        console.log(response.data);
        $('#eventModal').modal('hide'); // 成功時にモーダルを閉じる
        calendar.refetchEvents(); // イベントの追加後、イベントを再取得
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert('イベントの追加に失敗しました');
    });
}
