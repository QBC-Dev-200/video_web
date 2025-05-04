document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('videoFile');
    const previewArea = document.querySelector('.preview-area');
    const videoPreview = document.getElementById('videoPreview');
    const uploadForm = document.getElementById('uploadForm');

    // 点击上传区域触发文件选择
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // 处理拖放
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#fe2c55';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.3)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.3)';
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // 处理文件选择
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    // 处理文件预览
    function handleFile(file) {
        if (!file.type.startsWith('video/')) {
            alert('请选择视频文件！');
            return;
        }

        const url = URL.createObjectURL(file);
        videoPreview.src = url;
        previewArea.hidden = false;
        dropZone.hidden = true;
    }

    // 处理表单提交
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files.length) {
            alert('请选择要上传的视频！');
            return;
        }

        const formData = new FormData(uploadForm);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert('上传成功！');
                window.location.href = '/';
            } else {
                alert(data.error || '上传失败，请重试');
            }
        } catch (error) {
            alert('上传出错，请重试');
            console.error('Error:', error);
        }
    });
}); 