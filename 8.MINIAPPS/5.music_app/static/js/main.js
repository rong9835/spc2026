// ==========================================
//          BeatSpace 클라이언트 메인 엔진
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    // 1. Lucide 아이콘 초기 렌더링
    lucide.createIcons();

    // 2. 알림 벨 드롭다운 토글 기능 바인딩
    initNotificationBell();

    // 3. 백그라운드 실시간 알림 폴링 (8초 주기)
    if (USER_LOGGED_IN) {
        startNotificationPolling();
    }

    // 4. 유튜브 검색 이벤트 리스너 설정 (인덱스 페이지 전용)
    const ytSearchBtn = document.getElementById('yt-search-btn');
    const ytSearchInput = document.getElementById('yt-search-input');
    if (ytSearchBtn && ytSearchInput) {
        ytSearchBtn.addEventListener('click', performYoutubeSearch);
        ytSearchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performYoutubeSearch();
            }
        });
    }
});

// ==========================================
//          실시간 알림 및 폴링 시스템
// ==========================================

let alertedNotificationIds = new Set(); // 이미 토스트 알림을 띄운 ID 리스트 기록 (중복 방지)
let pollingTimer = null;

function startNotificationPolling() {
    // 첫 실행
    pollNotifications();
    // 8초마다 주기적 호출
    pollingTimer = setInterval(pollNotifications, 8000);
}

function pollNotifications() {
    fetch('/api/notifications')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const count = data.unread_count;
                const badge = document.getElementById('notification-badge');
                
                // 1. 헤더 알림 종에 빨간색 배지 상태 업데이트
                if (count > 0) {
                    badge.classList.remove('hidden');
                } else {
                    badge.classList.add('hidden');
                }

                // 2. 새로운 알림이 있다면 화면 우측 하단에 네온 토스트 팝업(푸시 알람)을 띄웁니다.
                data.notifications.forEach(n => {
                    if (!alertedNotificationIds.has(n.id)) {
                        alertedNotificationIds.add(n.id);
                        
                        // 아름다운 푸시 알림 사운드 합성음 연주 (Audio API - 별도 파일 불필요!)
                        playNotificationSound();
                        
                        // 알림 토스트 출력
                        showPushToast(n);
                    }
                });
            }
        })
        .catch(err => console.error("알림 동기화 오류:", err));
}

// 브라우저 자체 오디오 신디사이저를 사용한 맑은 알림 사운드 생성 효과음 (Premium User Experience)
function playNotificationSound() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        // 1번째 높은 미음
        const osc1 = audioCtx.createOscillator();
        const gain1 = audioCtx.createGain();
        osc1.connect(gain1);
        gain1.connect(audioCtx.destination);
        osc1.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 (라)
        gain1.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain1.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
        osc1.start(audioCtx.currentTime);
        osc1.stop(audioCtx.currentTime + 0.3);

        // 2번째 조금 늦게 나오는 높은 솔음
        const osc2 = audioCtx.createOscillator();
        const gain2 = audioCtx.createGain();
        osc2.connect(gain2);
        gain2.connect(audioCtx.destination);
        osc2.frequency.setValueAtTime(1046.5, audioCtx.currentTime + 0.1); // C6 (도)
        gain2.gain.setValueAtTime(0.08, audioCtx.currentTime + 0.1);
        gain2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
        osc2.start(audioCtx.currentTime + 0.1);
        osc2.stop(audioCtx.currentTime + 0.4);
    } catch(e) {
        // 일부 브라우저 보안 제약 등으로 인한 실패는 무시 처리
    }
}

// 실시간 푸시 토스트 DOM 생성 및 추가
function showPushToast(n) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = "toast-animate-in glassmorphism rounded-2xl p-4 border border-neon-purple/30 shadow-neon-glow flex items-start gap-3 cursor-pointer hover:border-neon-pink/40 hover:scale-[1.02] transition-all relative overflow-hidden bg-obsidian-card/90";
    
    // 그라데이션 라인 디자인 포인트
    toast.innerHTML = `
        <div class="absolute left-0 top-0 bottom-0 w-[4px] bg-gradient-to-b from-neon-purple to-neon-pink"></div>
        <div class="p-2 bg-neon-purple/10 rounded-xl text-neon-purple shrink-0">
            <i data-lucide="bell-ring" class="w-5 h-5"></i>
        </div>
        <div class="flex-grow min-w-0">
            <div class="text-xs text-slate-400 font-semibold flex justify-between items-center mb-1">
                <span>실시간 새 알림</span>
                <span class="text-[9px] text-slate-500">방금 전</span>
            </div>
            <div class="text-sm font-medium text-white">
                <span class="text-neon-purple font-bold">${n.sender_name}</span>님이 의견을 보냈습니다.
            </div>
            <div class="text-xs text-slate-400 font-medium truncate mt-1 bg-black/30 px-2.5 py-1.5 rounded-lg border border-white/5">
                "${n.comment_content}"
            </div>
        </div>
    `;

    // 토스트 클릭 시 해당 곡 상세 댓글 스페이스로 원클릭 이동
    toast.addEventListener('click', function() {
        window.location.href = `/song/${n.youtube_id}#comments-section`;
    });

    container.appendChild(toast);
    lucide.createIcons();

    // 4.5초 후 토스트 페이드아웃 애니메이션 적용 후 제거
    setTimeout(() => {
        toast.classList.remove('toast-animate-in');
        toast.classList.add('toast-animate-out');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4500);
}

// 전역 단순 텍스트 상태 안내 토스트 경고창
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    let borderColor = 'border-white/10';
    let iconName = 'info';
    let textColor = 'text-neon-blue';
    let iconBg = 'bg-neon-blue/10';

    if (type === 'success') {
        borderColor = 'border-neon-purple/20';
        iconName = 'check-circle';
        textColor = 'text-neon-purple';
        iconBg = 'bg-neon-purple/10';
    } else if (type === 'error') {
        borderColor = 'border-red-500/20';
        iconName = 'alert-triangle';
        textColor = 'text-red-400';
        iconBg = 'bg-red-500/10';
    }

    toast.className = `toast-animate-in glassmorphism rounded-xl p-3.5 border ${borderColor} flex items-center gap-3 bg-obsidian-card/90 shadow-lg`;
    toast.innerHTML = `
        <div class="p-1.5 rounded-lg ${iconBg} ${textColor} shrink-0">
            <i data-lucide="${iconName}" class="w-4 h-4"></i>
        </div>
        <span class="text-sm font-semibold text-white">${message}</span>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.classList.remove('toast-animate-in');
        toast.classList.add('toast-animate-out');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// 헤더 알림벨 클릭 동작 구성
function initNotificationBell() {
    const bellBtn = document.getElementById('notification-bell-btn');
    const dropdown = document.getElementById('notification-dropdown');
    const markAllReadBtn = document.getElementById('mark-all-read-btn');

    if (!bellBtn || !dropdown) return;

    // 종 아이콘 클릭 시 드롭다운 켜고 끄기 + 목록 로딩
    bellBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        const isOpen = !dropdown.classList.contains('hidden');
        
        if (isOpen) {
            dropdown.classList.add('hidden');
            bellBtn.querySelector('i').classList.remove('scale-110', 'text-neon-purple');
        } else {
            dropdown.classList.remove('hidden');
            bellBtn.querySelector('i').classList.add('scale-110', 'text-neon-purple');
            // 드롭다운 내부 알림리스트 동적 갱신
            loadNotificationDropdownList();
        }
    });

    // 외부 클릭 시 알림 창 닫기
    document.addEventListener('click', function(e) {
        if (!dropdown.classList.contains('hidden') && !dropdown.contains(e.target) && e.target !== bellBtn) {
            dropdown.classList.add('hidden');
            bellBtn.querySelector('i').classList.remove('scale-110', 'text-neon-purple');
        }
    });

    // 일괄 읽음 처리
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            fetch('/api/notifications/mark-read', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('notification-badge').classList.add('hidden');
                        showToast('알림을 모두 읽음 처리했습니다.', 'success');
                        dropdown.classList.add('hidden');
                    }
                });
        });
    }
}

// 드롭다운에 최신 5개 알림 목록 동적 빌드
function loadNotificationDropdownList() {
    const listContainer = document.getElementById('notification-list');
    if (!listContainer) return;

    fetch('/api/notifications')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.notifications.length > 0) {
                listContainer.innerHTML = '';
                // 최대 최신 5개만 슬라이스 노출
                data.notifications.slice(0, 5).forEach(n => {
                    const item = document.createElement('a');
                    item.href = `/song/${n.youtube_id}#comments-section`;
                    item.className = "block px-4 py-3 hover:bg-white/[0.03] transition-colors relative flex items-start gap-2.5 group";
                    
                    item.innerHTML = `
                        <div class="p-1.5 bg-neon-purple/10 rounded-lg text-neon-purple shrink-0 mt-0.5 group-hover:bg-neon-purple group-hover:text-white transition-all">
                            <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
                        </div>
                        <div class="min-w-0 flex-grow">
                            <div class="text-xs text-slate-300">
                                <strong class="text-white">${n.sender_name}</strong>님이 댓글을 남겼습니다.
                            </div>
                            <div class="text-[10px] text-slate-500 font-bold truncate mt-0.5 font-sans">${n.song_title}</div>
                            <div class="text-xs italic text-slate-400 mt-1 truncate">"${n.comment_content}"</div>
                        </div>
                        <!-- 안 읽은 표시 구체 -->
                        <span class="w-1.5 h-1.5 bg-neon-purple rounded-full shrink-0 self-center"></span>
                    `;
                    listContainer.appendChild(item);
                });
                lucide.createIcons();
            } else {
                listContainer.innerHTML = `
                    <div class="px-4 py-8 text-center text-xs text-slate-500">
                        <i data-lucide="bell-off" class="w-6 h-6 mx-auto mb-2 text-slate-600"></i>
                        읽지 않은 새로운 알림이 없습니다.
                    </div>
                `;
                lucide.createIcons();
            }
        });
}

// ==========================================
//          음악 SNS 소셜 상호작용 (좋아요/댓글/태그)
// ==========================================

// 1. 메인 카드 목록에서 좋아요 다이렉트 토글 처리
function toggleCardLike(event, youtubeId) {
    event.preventDefault(); // 디테일 링크로 이동하는 부모 카드 동작 방지
    event.stopPropagation();

    if (!USER_LOGGED_IN) {
        showToast('로그인 후 좋아요를 표현할 수 있습니다.', 'error');
        return;
    }

    fetch(`/api/songs/${youtubeId}/like`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // 특정 음악 카드 요소들 찾기
                const card = document.querySelector(`.glassmorphism-card[data-youtube-id="${youtubeId}"]`);
                if (card) {
                    const btn = card.querySelector('button[title="좋아요"]');
                    const countSpan = btn.querySelector('.like-count');
                    const heartIcon = btn.querySelector('i');
                    
                    countSpan.textContent = data.like_count;
                    
                    if (data.liked) {
                        btn.classList.add('text-neon-pink');
                        btn.classList.remove('text-slate-400');
                        heartIcon.classList.add('fill-current');
                        showToast('좋아요 목록에 추가되었습니다!', 'success');
                    } else {
                        btn.classList.remove('text-neon-pink');
                        btn.classList.add('text-slate-400');
                        heartIcon.classList.remove('fill-current');
                        showToast('좋아요를 해제했습니다.', 'info');
                    }
                    lucide.createIcons();
                }
            }
        })
        .catch(() => showToast('네트워크 오류가 발생했습니다.', 'error'));
}

// 2. 곡 상세 페이지 내부 큰 하트 좋아요 처리
function toggleDetailLike(youtubeId) {
    if (!USER_LOGGED_IN) {
        showToast('로그인 후 좋아요를 누를 수 있습니다.', 'error');
        return;
    }

    fetch(`/api/songs/${youtubeId}/like`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const btn = document.getElementById('song-like-btn');
                const heartIcon = document.getElementById('like-icon');
                const countSpan = document.getElementById('detail-like-count');
                const textSpan = document.getElementById('detail-like-text');

                countSpan.textContent = data.like_count;

                if (data.liked) {
                    btn.className = "flex items-center gap-2 px-5 py-3 rounded-2xl font-bold transition-all duration-300 shadow-pink-glow shrink-0 border border-neon-pink/30 text-neon-pink bg-neon-pink/10 focus:outline-none transform active:scale-95";
                    heartIcon.classList.add('fill-current');
                    textSpan.textContent = "좋아요 취소";
                    showToast('이 음악을 좋아합니다! ❤️', 'success');
                } else {
                    btn.className = "flex items-center gap-2 px-5 py-3 rounded-2xl font-bold transition-all duration-300 shadow-sm shrink-0 border border-white/10 text-slate-300 bg-white/5 hover:border-neon-pink/30 hover:text-neon-pink focus:outline-none transform active:scale-95";
                    heartIcon.classList.remove('fill-current');
                    textSpan.textContent = "좋아요";
                    showToast('좋아요를 취소했습니다.', 'info');
                }
                lucide.createIcons();
            }
        })
        .catch(() => showToast('서버 통신 중 오류가 발생했습니다.', 'error'));
}

// 3. 해시태그 추가 API 호출 및 동적 렌더링
function addHashtag(youtubeId) {
    const input = document.getElementById('hashtag-input');
    const tag = input.value.trim();

    if (!tag) {
        showToast('추가할 해시태그 내용을 입력해 주세요.', 'error');
        return;
    }

    fetch(`/api/songs/${youtubeId}/hashtag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag })
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(resObj => {
        if (resObj.status === 200) {
            const cleanTag = resObj.data.tag;
            const tagList = document.getElementById('detail-tag-list');
            
            // 기존 '해시태그 없음' 문구가 있었다면 제거
            const noMsg = document.getElementById('no-tags-msg');
            if (noMsg) noMsg.remove();

            // 신규 태그 엘리먼트 생성 및 추가
            const span = document.createElement('span');
            span.className = "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-obsidian-card border border-white/5 text-xs text-slate-300 hover:border-neon-purple/20 transition-all font-semibold animate-fade-in";
            span.setAttribute('data-tag-name', cleanTag);
            span.innerHTML = `
                <span>#${cleanTag}</span>
                <button onclick="deleteHashtag('${youtubeId}', '${cleanTag}')" 
                        class="text-slate-500 hover:text-red-400 p-0.5 rounded-full hover:bg-white/5 transition-all"
                        title="태그 삭제">
                    <i data-lucide="x" class="w-3.5 h-3.5"></i>
                </button>
            `;
            tagList.appendChild(span);
            input.value = '';
            showToast(`#${cleanTag} 태그가 추가되었습니다.`, 'success');
            lucide.createIcons();
        } else {
            showToast(resObj.data.message || '태그 추가 중 에러가 발생했습니다.', 'error');
        }
    })
    .catch(() => showToast('네트워크 요청에 실패했습니다.', 'error'));
}

// 4. 해시태그 삭제 처리
function deleteHashtag(youtubeId, tag) {
    if (!confirm(`#${tag} 해시태그를 정말 삭제하시겠습니까?`)) return;

    fetch(`/api/songs/${youtubeId}/hashtag/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag })
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(resObj => {
        if (resObj.status === 200) {
            // 화면에서 해당 태그 지우기
            const tagEl = document.querySelector(`span[data-tag-name="${tag}"]`);
            if (tagEl) {
                tagEl.style.transition = 'all 0.4s ease';
                tagEl.style.opacity = '0';
                tagEl.style.transform = 'scale(0.8)';
                setTimeout(() => {
                    tagEl.remove();
                    // 해시태그가 다 지워져서 비었다면 알림 메시지 복원
                    const tagList = document.getElementById('detail-tag-list');
                    if (tagList && tagList.children.length === 0) {
                        tagList.innerHTML = `<p id="no-tags-msg" class="text-xs text-slate-500 py-2">등록된 해시태그가 없습니다. 자유롭게 등록해 보세요!</p>`;
                    }
                }, 400);
            }
            showToast('태그를 삭제했습니다.', 'info');
        } else {
            showToast(resObj.data.message || '태그 삭제 권한이 없습니다.', 'error');
        }
    });
}

// 5. 실시간 댓글 작성 제출
function postComment(youtubeId) {
    const textarea = document.getElementById('comment-textarea');
    const content = textarea.value.strip ? textarea.value.strip() : textarea.value.trim();

    if (!content) {
        showToast('댓글 내용을 작성해 주세요.', 'error');
        return;
    }

    fetch(`/api/songs/${youtubeId}/comment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
    })
    .then(res => res.json().then(data => ({ status: res.status, data })))
    .then(resObj => {
        if (resObj.status === 200) {
            const container = document.getElementById('comments-container');
            
            // 기존 '댓글 없음' 지우기
            const noMsg = document.getElementById('no-comments-msg');
            if (noMsg) noMsg.remove();

            // 신규 댓글 아이템 생성
            const div = document.createElement('div');
            div.className = "py-3 flex flex-col gap-1.5 text-sm animate-fade-in group border-b border-white/5";
            
            // 관리자 확인 배지 세팅
            let adminBadge = '';
            
            div.innerHTML = `
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-1.5 font-bold">
                        <i data-lucide="user" class="w-3.5 h-3.5 text-slate-400"></i>
                        <span class="text-white">${resObj.data.username}</span>
                        ${adminBadge}
                    </div>
                    <span class="text-[10px] text-slate-500">${resObj.data.created_at}</span>
                </div>
                <p class="text-slate-300 font-normal leading-relaxed break-all pr-2">
                    ${resObj.data.content}
                </p>
            `;
            
            // 새로운 댓글을 최상단으로 올리기
            container.insertBefore(div, container.firstChild);
            textarea.value = '';
            
            // 댓글 총 개수 배지 업데이트
            const badge = document.getElementById('comment-total-badge');
            if (badge) {
                const curCount = parseInt(badge.textContent);
                badge.textContent = `${curCount + 1}개`;
            }

            showToast('의견 댓글을 성공적으로 등록했습니다!', 'success');
            lucide.createIcons();
            
            // 등록 후 상단으로 스크롤 고정
            container.scrollTop = 0;
        } else {
            showToast(resObj.data.message || '댓글 등록 실패', 'error');
        }
    })
    .catch(() => showToast('네트워크 연결 불안정', 'error'));
}

// ==========================================
//          유튜브 실시간 검색 및 등록 프로세스
// ==========================================

function performYoutubeSearch() {
    const input = document.getElementById('yt-search-input');
    const query = input.value.trim();

    if (!query) {
        showToast('유튜브 검색어를 입력해 주세요.', 'error');
        return;
    }

    const panel = document.getElementById('yt-search-results-panel');
    const list = document.getElementById('yt-results-list');
    const closeBtn = document.getElementById('close-yt-panel-btn');

    // 패널 열기 및 스피너 로더 노출
    panel.classList.remove('hidden');
    list.innerHTML = `
        <div class="col-span-full py-16 text-center text-slate-400">
            <div class="animate-spin w-8 h-8 border-4 border-neon-pink border-t-transparent rounded-full mx-auto mb-4"></div>
            유튜브에서 실시간 노래 검색 데이터를 로딩 중입니다...
        </div>
    `;

    // 닫기 버튼 제어 활성화
    if (closeBtn) {
        closeBtn.onclick = function() {
            panel.classList.add('hidden');
        };
    }

    fetch(`/api/youtube/search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(videos => {
            if (videos.length === 0) {
                list.innerHTML = `
                    <div class="col-span-full py-12 text-center text-slate-500">
                        유튜브에서 동영상 검색 결과를 발견할 수 없었습니다. 다른 키워드를 입력해 보세요.
                    </div>
                `;
                return;
            }

            list.innerHTML = '';
            videos.forEach(v => {
                const card = document.createElement('div');
                card.className = "flex gap-4 p-3 bg-obsidian-card/85 hover:bg-white/[0.02] border border-white/5 hover:border-neon-pink/20 rounded-2xl items-center transition-all duration-300 relative group";
                
                // HTML 이스케이프 유틸리티 적용
                const cleanTitle = v.title.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
                const cleanDesc = v.description.replace(/"/g, '&quot;').replace(/'/g, '&#39;');

                card.innerHTML = `
                    <!-- 썸네일 -->
                    <div class="w-24 h-16 rounded-xl overflow-hidden shrink-0 bg-black relative">
                        <img src="${v.thumbnail}" alt="${cleanTitle}" class="w-full h-full object-cover">
                    </div>
                    <!-- 아티스트 비디오 설명 정보 -->
                    <div class="flex-grow min-w-0">
                        <h4 class="font-bold text-sm text-white line-clamp-1 group-hover:text-neon-pink transition-colors pr-2">${v.title}</h4>
                        <p class="text-[11px] text-slate-500 line-clamp-1 mt-1 font-normal">${v.description || '유튜브 동영상 소개글'}</p>
                    </div>
                    <!-- 등록 액션 버튼 -->
                    <button onclick="registerYoutubeSong('${v.id}', '${cleanTitle}', '${cleanDesc}', '${v.thumbnail}')"
                            class="shrink-0 bg-neon-pink hover:bg-pink-500 hover:shadow-pink-glow text-white font-bold text-xs px-3 py-2 rounded-xl transition-all flex items-center gap-1">
                        <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i>
                        <span>등록</span>
                    </button>
                `;
                list.appendChild(card);
            });
            lucide.createIcons();
        })
        .catch(() => {
            list.innerHTML = `
                <div class="col-span-full py-12 text-center text-red-400">
                    유튜브 데이터를 불러오는 도중 오류가 발생했습니다. 잠시 후 다시 검색해 주세요.
                </div>
            `;
        });
}

// 유튜브 검색 카드의 등록 버튼 클릭 시 호출
function registerYoutubeSong(youtubeId, title, description, thumbnailUrl) {
    if (!USER_LOGGED_IN) {
        showToast('로그인한 회원만 노래를 새롭게 등록할 수 있습니다.', 'error');
        return;
    }

    showToast('음악을 스페이스에 등록 요청 중...', 'info');

    fetch('/api/songs/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            youtube_id: youtubeId,
            title: title,
            description: description,
            thumbnail_url: thumbnailUrl
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            // 등록 성공 혹은 이미 등록된 경우 바로 해당 디테일(의견교환장소)로 부드러운 페이지 리다이렉트 이동!
            setTimeout(() => {
                window.location.href = `/song/${data.youtube_id}`;
            }, 1000);
        } else {
            showToast(data.message || '등록 실패', 'error');
        }
    })
    .catch(() => showToast('서버 연결 실패', 'error'));
}
