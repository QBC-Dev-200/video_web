document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('likeButton');
    const collectButton = document.getElementById('collectButton');
    const commentButton = document.getElementById('commentButton');
    const commentsSection = document.querySelector('.comments-section');
    const commentsList = document.querySelector('.comments-list');
    const commentInput = document.querySelector('.comment-input textarea');
    const sendCommentButton = document.querySelector('.send-comment');

    // 获取视频信息
    async function loadVideoInfo() {
        try {
            const response = await fetch('/get_one_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ video_id: videoId })
            });

            const data = await response.json();

            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            const videoMsg = data.video_msg;
            
            // 更新视频源
            const videoElement = document.getElementById('mainVideo');
            videoElement.src = `/video/${videoMsg.video}`;
            
            // 更新作者信息
            const authorInfo = document.querySelector('.author-info');
            const authorAvatar = document.querySelector('.author-avatar');
            const authorName = document.querySelector('.author-name');
            
            authorAvatar.src = `/get_user_img/${videoMsg.user_img}`;
            authorName.textContent = `@${videoMsg.user_name}`;
            
            // 更新视频信息
            const videoTitle = document.querySelector('.video-title');
            const videoDescription = document.querySelector('.video-description');
            videoTitle.textContent = videoMsg.title;
            videoDescription.textContent = videoMsg.intor;
            
            // 更新统计数据
            document.querySelector('.likes-count').textContent = videoMsg.likes_count;
            document.querySelector('.comments-count').textContent = videoMsg.comment_count;
            document.querySelector('.collections-count').textContent = videoMsg.collection_count;

            // 添加作者信息点击事件
            authorInfo.addEventListener('click', () => {
                window.location.href = `/other_userhome/${videoMsg.user_id}`;
            });

            // 将用户ID存储为数据属性
            authorInfo.dataset.userId = videoMsg.user_id;

            // 检查当前用户的点赞和收藏状态
            checkInteractionStatus();
        } catch (error) {
            console.error('Error loading video:', error);
        }
    }

    // 检查互动状态
    async function checkInteractionStatus() {
        try {
            const response = await fetch('/check_interaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ video_id: videoId })
            });

            const data = await response.json();
            
            if (data.is_liked) {
                likeButton.classList.add('active');
            }
            if (data.is_collected) {
                collectButton.classList.add('active');
            }
        } catch (error) {
            console.error('Error checking interaction status:', error);
        }
    }

    // 处理点赞
    likeButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/like_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ video_id: videoId })
            });

            const data = await response.json();
            
            if (data.message === '点赞成功') {
                likeButton.classList.add('active');
                const likesCount = likeButton.querySelector('.likes-count');
                likesCount.textContent = parseInt(likesCount.textContent) + 1;
            } else if (data.message === '取消点赞成功') {
                likeButton.classList.remove('active');
                const likesCount = likeButton.querySelector('.likes-count');
                likesCount.textContent = parseInt(likesCount.textContent) - 1;
            }
        } catch (error) {
            console.error('Error liking video:', error);
        }
    });

    // 处理收藏
    collectButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/collection_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ video_id: videoId })
            });

            const data = await response.json();
            
            if (data.message === '收藏成功') {
                collectButton.classList.add('active');
                const collectCount = collectButton.querySelector('.collections-count');
                collectCount.textContent = parseInt(collectCount.textContent) + 1;
            } else if (data.message === '取消收藏成功') {
                collectButton.classList.remove('active');
                const collectCount = collectButton.querySelector('.collections-count');
                collectCount.textContent = parseInt(collectCount.textContent) - 1;
            }
        } catch (error) {
            console.error('Error collecting video:', error);
        }
    });

    // 显示/隐藏评论区
    commentButton.addEventListener('click', () => {
        commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
        if (commentsSection.style.display === 'block') {
            loadComments();
        }
    });

    // 加载评论
    async function loadComments() {
        try {
            const response = await fetch('/get_comments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ video_id: videoId })
            });

            const data = await response.json();
            
            commentsList.innerHTML = '';
            data.comments.forEach(comment => {
                const commentElement = createCommentElement(comment);
                commentsList.appendChild(commentElement);
            });
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    }

    // 创建评论元素
    function createCommentElement(comment) {
        const div = document.createElement('div');
        div.className = 'comment-item';
        div.innerHTML = `
            <img class="comment-avatar" src="/get_user_img/${comment.user_img}" alt="用户头像">
            <div class="comment-content">
                <div class="comment-username">@${comment.user_name}</div>
                <div class="comment-text">${comment.content}</div>
                <div class="comment-time">${comment.time}</div>
            </div>
        `;
        return div;
    }

    // 发送评论
    sendCommentButton.addEventListener('click', async () => {
        const content = commentInput.value.trim();
        if (!content) return;

        try {
            const response = await fetch('/comment_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    video_id: videoId,
                    content: content
                })
            });

            const data = await response.json();
            
            if (data.message === '评论成功') {
                commentInput.value = '';
                loadComments();  // 重新加载评论
                // 更新评论数
                const commentsCount = commentButton.querySelector('.comments-count');
                commentsCount.textContent = parseInt(commentsCount.textContent) + 1;
            }
        } catch (error) {
            console.error('Error sending comment:', error);
        }
    });

    // 初始加载
    loadVideoInfo();
}); 