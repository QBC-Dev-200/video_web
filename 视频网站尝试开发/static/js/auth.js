document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (window.location.pathname === '/register') {
                    alert('注册成功！');
                    window.location.href = '/login';
                } else if (window.location.pathname === '/login') {
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        window.location.href = '/';
                    }
                }
            } else {
                alert(data.error || '操作失败，请重试');
            }
        } catch (error) {
            alert('发生错误，请重试');
            console.error('Error:', error);
        }
    });
}); 