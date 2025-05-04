document.addEventListener('DOMContentLoaded', function() {
    let isLoading = false;
    let isPlaying = false;
    let currentVideoId = null;  // 添加当前视频ID的跟踪

    // 获取视频元素（将重复使用的元素提前获取）
    const videoElement = document.querySelector('video');
    const videoWrapper = document.querySelector('.video-wrapper');

    // 添加播放状态指示器到 HTML
    const playIndicator = document.createElement('div');
    playIndicator.className = 'play-indicator';
    playIndicator.innerHTML = '<i class="fas fa-play"></i>';
    videoWrapper.appendChild(playIndicator);

    // 添加进度条到视频容器
    const progressContainer = document.createElement('div');
    progressContainer.className = 'progress-container';
    
    // 创建进度条
    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    
    // 创建缓冲条
    const bufferBar = document.createElement('div');
    bufferBar.className = 'buffer-bar';
    
    progressContainer.appendChild(bufferBar);
    progressContainer.appendChild(progressBar);
    videoWrapper.appendChild(progressContainer);

    // 更新进度条
    function updateProgress(video) {
        const progress = (video.currentTime / video.duration) * 100;
        progressBar.style.width = `${progress}%`;
        
        // 更新缓冲进度
        if (video.buffered.length > 0) {
            const buffered = (video.buffered.end(video.buffered.length - 1) / video.duration) * 100;
            bufferBar.style.width = `${buffered}%`;
        }
    }

    // 处理进度条点击
    progressContainer.addEventListener('click', (e) => {
        const rect = progressContainer.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        videoElement.currentTime = pos * videoElement.duration;
    });

    // 监听视频时间更新事件
    videoElement.addEventListener('timeupdate', () => {
        updateProgress(videoElement);
    });

    // 修改加载视频函数
    async function loadVideo(direction = 'next') {
        if (isLoading) return;
        isLoading = true;

        try {
            let response;
            if (direction === 'previous') {
                // 不再需要传递 video_id
                response = await fetch('/get_last_videos', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
            } else {
                response = await fetch('/get_video');
            }
            
            const data = await response.json();
            
            if (data.error) {
                console.error('Error:', data.error);
                // 如果是已经到第一个视频的错误，可以给用户提示
                if (response.status === 400) {
                    alert('已经是第一个视频了');
                }
                return;
            }

            const videoMsg = data.video_msg;
            currentVideoId = videoMsg.id;  // 保存当前视频ID
            console.log('Current video ID:', currentVideoId); // 调试日志
            
            // 更新视频源
            videoElement.src = `/video/${videoMsg.video}`;
            
            // 更新视频信息和作者头像
            const authorElement = document.querySelector('.author');
            const descriptionElement = document.querySelector('.description');
            const authorAvatar = document.querySelector('.author-avatar') || createAuthorAvatar();
            
            // 更新作者头像
            if (videoMsg.user_img && videoMsg.user_img !== 'None') {
                authorAvatar.src = `/get_user_img/${videoMsg.user_img}`;
            } else {
                authorAvatar.src = '/get_user_img/None';
            }
            
            authorElement.textContent = `@${videoMsg.user_name}`;
            descriptionElement.textContent = `${videoMsg.title} ${videoMsg.intor}`;
            
            // 更新互动数据
            const likesElement = document.querySelector('.interaction-buttons .button:first-child span');
            const commentsElement = document.querySelector('.interaction-buttons .button:nth-child(2) span');
            const collectionsElement = document.querySelector('.interaction-buttons .button:nth-child(3) span');
            likesElement.textContent = videoMsg.likes_count;
            commentsElement.textContent = videoMsg.comments_count;
            collectionsElement.textContent = videoMsg.collections_count;

            // 重置进度条
            progressBar.style.width = '0%';
            bufferBar.style.width = '0%';

            // 只有在之前是播放状态时才自动播放新视频
            if (isPlaying) {
                videoElement.play();
            }

            const authorContainer = document.querySelector('.author-container');
            if (authorContainer) {
                authorContainer.dataset.userId = videoMsg.user_id;
            }
        } catch (error) {
            console.error('Error:', error);
        } finally {
            isLoading = false;
        }
    }

    // 修改 createAuthorAvatar 函数
    function createAuthorAvatar() {
        const authorInfo = document.querySelector('.video-info');
        const avatarContainer = document.createElement('div');
        avatarContainer.className = 'author-container';
        
        const avatar = document.createElement('img');
        avatar.className = 'author-avatar';
        avatar.alt = '作者头像';
        
        // 添加点击事件
        avatarContainer.addEventListener('click', (e) => {
            e.stopPropagation();  // 阻止事件冒泡，避免触发视频暂停/播放
            const userId = avatarContainer.dataset.userId;  // 从 dataset 中获取用户ID
            if (userId) {
                window.location.href = `/other_userhome/${userId}`;
            }
        });
        
        // 将现有的作者名称元素移动到容器中
        const authorName = authorInfo.querySelector('.author');
        avatarContainer.appendChild(avatar);
        avatarContainer.appendChild(authorName);
        
        // 将容器插入到视频信息区域的开头
        authorInfo.insertBefore(avatarContainer, authorInfo.firstChild);
        
        return avatar;
    }

    // 修改滚轮事件处理
    function handleSwipe() {
        const videoContainer = document.querySelector('.video-container');
        let startY;
        let endY;
        let lastWheelTime = 0;

        videoContainer.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
        });

        videoContainer.addEventListener('touchend', (e) => {
            endY = e.changedTouches[0].clientY;
            const diff = startY - endY;

            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    loadVideo('next');
                } else {
                    loadVideo('previous');
                }
            }
        });

        // 修改鼠标滚轮支持
        videoContainer.addEventListener('wheel', (e) => {
            const now = Date.now();
            if (now - lastWheelTime < 500) return;  // 500ms的节流
            lastWheelTime = now;

            if (Math.abs(e.deltaY) > 50) {
                if (e.deltaY > 0) {
                    // 向下滚动，获取下一个视频
                    loadVideo('next');
                } else if (e.deltaY < 0 && currentVideoId) {
                    // 向上滚动且有当前视频ID时，获取上一个视频
                    loadVideo('previous');
                }
            }
        });
    }

    // 添加底部导航事件处理
    const bottomNav = document.querySelector('.bottom-nav');
    bottomNav.addEventListener('click', function(e) {
        const navItem = e.target.closest('.nav-item');
        if (!navItem) return;

        const icon = navItem.querySelector('i');
        if (icon.classList.contains('fa-user')) {
            window.location.href = '/userhome';
        } else if (icon.classList.contains('fa-plus-square')) {
            window.location.href = '/upload';
        } else if (icon.classList.contains('fa-search')) {
            window.location.href = '/search';
        }
    });

    // 视频结束时自动加载下一个
    videoElement.addEventListener('ended', () => {
        loadVideo();
    });

    // 修改视频点击暂停/播放功能
    const videoContainer = document.querySelector('.video-container');
    videoContainer.addEventListener('click', (e) => {
        // 如果点击的是互动按钮区域，不处理暂停/播放
        if (e.target.closest('.interaction-buttons') || 
            e.target.closest('.video-info')) {
            return;
        }
        
        const video = document.querySelector('video');
        const playIndicator = document.querySelector('.play-indicator');
        
        if (video.paused) {
            video.play();
            isPlaying = true;
            playIndicator.style.opacity = '0';
        } else {
            video.pause();
            isPlaying = false;
            playIndicator.style.opacity = '1';
        }
    });

    // 初始化时加载第一个视频
    isPlaying = true;
    handleSwipe();
    loadVideo('next');

    // 添加页面关闭事件处理
    window.addEventListener('beforeunload', async function(e) {
        try {
            // 发送清除请求
            await fetch('/clear_last_videos', {
                method: 'GET',
                keepalive: true  // 确保请求在页面关闭时也能完成
            });
        } catch (error) {
            console.error('Error clearing video history:', error);
        }
    });
});