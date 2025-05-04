document.addEventListener('DOMContentLoaded', function() {
    const videoGrid = document.getElementById('videoGrid');
    const userId = document.querySelector('.user-info').dataset.userId;
    console.log('Loading videos for user:', userId); // 调试日志

    // 加载用户视频
    async function loadUserVideos() {
        try {
            const response = await fetch('/get_user_videos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: parseInt(userId) }) // 确保ID是数字
            });

            const data = await response.json();

            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            if (!data.videos || data.videos.length === 0) {
                // 处理没有视频的情况
                videoGrid.innerHTML = '<p class="no-videos">暂无视频</p>';
                return;
            }

            // 渲染视频网格
            data.videos.forEach(video => {
                const videoItem = createVideoItem(video);
                videoGrid.appendChild(videoItem);
            });
        } catch (error) {
            console.error('Error loading videos:', error);
        }
    }

    // 创建视频项
    function createVideoItem(video) {
        const div = document.createElement('div');
        div.className = 'video-item';
        
        // 添加点击事件跳转到视频页面
        div.addEventListener('click', () => {
            window.location.href = `/video_index/${video.id}`;
        });
        
        const videoEl = document.createElement('video');
        videoEl.src = `/video/${video.video}`;
        videoEl.muted = true;  // 默认静音
        
        // 鼠标悬停时播放预览
        div.addEventListener('mouseenter', () => {
            videoEl.play();
        });
        
        div.addEventListener('mouseleave', () => {
            videoEl.pause();
            videoEl.currentTime = 0;
        });

        const info = document.createElement('div');
        info.className = 'video-info';
        info.innerHTML = `
            <h3 class="video-title">${video.title}</h3>
            <div class="video-time">${video.time}</div>
        `;

        div.appendChild(videoEl);
        div.appendChild(info);

        return div;
    }

    // 加载视频
    loadUserVideos();
}); 