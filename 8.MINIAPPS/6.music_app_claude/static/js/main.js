/*
 * main.js
 * -------
 * 모든 페이지에서 함께 쓰는 자바스크립트 도우미들입니다.
 *  - postJSON / deleteJSON : 서버에 데이터를 보내고 결과(JSON)를 받는 함수
 *  - showToast            : 화면 위에 잠깐 떴다 사라지는 알림 메시지
 *  - escapeHtml           : 입력값을 안전하게 화면에 표시 (악성 코드 방지)
 *  - 알림(종 아이콘) 폴링  : 로그인 상태라면 새 알림이 있는지 주기적으로 확인
 */

// 서버에 JSON 데이터를 POST 방식으로 보냅니다.
async function postJSON(url, body) {
    try {
        const res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        return await res.json();
    } catch (error) {
        console.error("요청 실패:", error);
        return { success: false, message: "네트워크 오류가 발생했습니다." };
    }
}

// 서버에 DELETE(삭제) 요청을 보냅니다.
async function deleteJSON(url) {
    try {
        const res = await fetch(url, { method: "DELETE" });
        return await res.json();
    } catch (error) {
        console.error("요청 실패:", error);
        return { success: false, message: "네트워크 오류가 발생했습니다." };
    }
}

// 화면 위쪽에 잠깐 나타났다 사라지는 알림 메시지를 띄웁니다.
function showToast(message, type) {
    const toast = document.getElementById("toast");
    if (!toast) return;

    // 성공이면 초록색, 실패면 빨간색
    const color = type === "error" ? "bg-rose-600" : "bg-emerald-600";
    toast.className =
        "fixed top-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-lg shadow-lg " +
        "text-sm font-medium text-white " + color;
    toast.textContent = message;

    // 2.5초 뒤에 숨깁니다.
    setTimeout(() => {
        toast.className = "hidden";
    }, 2500);
}

// 사용자가 입력한 글자를 화면에 안전하게 넣기 위해 특수문자를 변환합니다.
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

/* ===== 알림(종 아이콘) 기능 ===== */
// 로그인한 상태일 때만 동작합니다. (base.html 에서 window.IS_LOGGED_IN 을 정해줌)
if (window.IS_LOGGED_IN) {
    const bellButton = document.getElementById("bell-button");
    const bellDropdown = document.getElementById("bell-dropdown");

    // 종을 누르면 알림 목록을 펼치거나 접습니다. 펼칠 때는 '읽음' 처리합니다.
    if (bellButton) {
        bellButton.addEventListener("click", async () => {
            bellDropdown.classList.toggle("hidden");
            if (!bellDropdown.classList.contains("hidden")) {
                await postJSON("/api/notifications/read", {});
                document.getElementById("bell-badge").classList.add("hidden");
            }
        });
    }

    // 서버에서 안 읽은 알림을 가져와 종 아이콘에 표시합니다.
    async function loadNotifications() {
        try {
            const res = await fetch("/api/notifications");
            const data = await res.json();
            if (!data.success) return;

            const badge = document.getElementById("bell-badge");
            const list = document.getElementById("bell-list");

            // 안 읽은 개수 배지 표시
            if (data.unread_count > 0) {
                badge.textContent = data.unread_count;
                badge.classList.remove("hidden");
            }

            // 알림 목록 그리기
            if (data.notifications.length === 0) {
                list.innerHTML =
                    '<p class="text-xs text-slate-500 px-2 py-2">새 알림이 없습니다.</p>';
                return;
            }
            list.innerHTML = "";
            data.notifications.forEach((n) => {
                const item = document.createElement("a");
                item.href = "/song/" + n.youtube_id;
                item.className = "block text-xs p-2 rounded hover:bg-slate-700";
                item.innerHTML =
                    '<span class="text-indigo-400 font-medium">' +
                    escapeHtml(n.sender_name) + "</span>님이 <b>" +
                    escapeHtml(n.song_title) + "</b>에 댓글을 남겼어요";
                list.appendChild(item);
            });
        } catch (error) {
            console.error("알림 불러오기 실패:", error);
        }
    }

    // 페이지가 열리면 한 번 확인하고, 이후 15초마다 다시 확인합니다.
    loadNotifications();
    setInterval(loadNotifications, 15000);
}
