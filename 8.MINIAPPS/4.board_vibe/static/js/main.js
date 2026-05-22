// Session-based liked posts tracker to persist like button states locally
const getLikedPosts = () => {
    try {
        return JSON.parse(sessionStorage.getItem('vibe_liked_posts') || '[]');
    } catch (e) {
        return [];
    }
};

const addLikedPost = (id) => {
    const liked = getLikedPosts();
    if (!liked.includes(id)) {
        liked.push(id);
        sessionStorage.setItem('vibe_liked_posts', JSON.stringify(liked));
    }
};

// Initialize like button states on load
document.addEventListener('DOMContentLoaded', () => {
    const liked = getLikedPosts();
    liked.forEach(id => {
        const btn = document.getElementById(`like-btn-${id}`);
        if (btn) {
            btn.classList.add('liked');
        }
    });
});

// Like Post Function via AJAX
function likePost(id) {
    const btn = document.getElementById(`like-btn-${id}`);
    if (!btn) return;

    // Optional: Prevent double likes locally in the current session
    const liked = getLikedPosts();
    if (liked.includes(id.toString()) || liked.includes(Number(id))) {
        // Already liked this session - we can still send the request, or alert.
        // Let's allow voting but let the UI keep glowing.
    }

    btn.disabled = true;

    fetch(`/like/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const countSpan = btn.querySelector('.like-count');
            if (countSpan) {
                countSpan.textContent = data.likes;
            }
            btn.classList.add('liked');
            addLikedPost(id);
        } else {
            console.error('Failed to like post:', data.error);
        }
    })
    .catch(error => {
        console.error('Error liking post:', error);
    })
    .finally(() => {
        btn.disabled = false;
    });
}

// Delete Post Function via AJAX
function deletePost(id) {
    if (!confirm('이 소중한 생각 카드를 영구히 삭제하시겠습니까?')) {
        return;
    }

    const card = document.getElementById(`post-card-${id}`);
    if (!card) return;

    fetch(`/delete/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Trigger beautiful exit animation
            card.classList.add('card-removed');
            
            // Remove DOM element after animation ends
            setTimeout(() => {
                card.remove();
                
                // Check if all cards are gone to show empty state
                const grid = document.querySelector('.cards-grid');
                if (grid && grid.children.length === 0) {
                    location.reload(); // Quickest way to clean render empty state
                }
            }, 400);
        } else {
            alert('삭제에 실패했습니다: ' + (data.error || '알 수 없는 오류'));
        }
    })
    .catch(error => {
        console.error('Error deleting post:', error);
        alert('서버 통신 중 오류가 발생했습니다.');
    });
}
