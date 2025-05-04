document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const searchResults = document.getElementById('searchResults');

    // 搜索功能
    async function performSearch() {
        const searchContent = searchInput.value.trim();
        if (!searchContent) return;

        try {
            const formData = new FormData();
            formData.append('search_content', searchContent);

            const response = await fetch('/search_result', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                console.error('Error:', data.error);
                return;
            }

            // 清空现有结果
            searchResults.innerHTML = '';

            // 显示搜索结果
            if (data.videos && data.videos.length > 0) {
                data.videos.forEach(video => {
                    const videoElement = createVideoElement(video);
                    searchResults.appendChild(videoElement);
                });
            } else {
                searchResults.innerHTML = '<p class="no-results">未找到相关视频</p>';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // 创建视频元素
    function createVideoElement(video) {
        const div = document.createElement('div');
        div.className = 'video-item';
        div.innerHTML = `
            <video class="video-preview" src="/video/${video.video}" muted></video>
            <div class="video-info">
                <h3 class="video-title">${video.title}</h3>
                <div class="author-info">
                    <img class="author-avatar" src="/get_user_img/${video.user_img}" alt="作者头像">
                    <span class="author-name">@${video.user_name}</span>
                </div>
            </div>
        `;

        // 添加点击事件
        div.addEventListener('click', () => {
            window.location.href = `/video_index/${video.id}`;
        });

        // 添加视频预览
        const videoPreview = div.querySelector('.video-preview');
        div.addEventListener('mouseenter', () => {
            videoPreview.play();
            log.data({'msg':'/focus'})
        });
        div.addEventListener('mouseleave', () => {
            videoPreview.pause();
            videoPreview.currentTime = 0;
        });

        // 添加作者头像点击事件
        const authorInfo = div.querySelector('.author-info');
        authorInfo.addEventListener('click', (e) => {
            e.stopPropagation();
            window.location.href = `/other_userhome/${video.user_id}`;
        });

        return div;
    }

    // 绑定事件
    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
}); 