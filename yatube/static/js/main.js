// Yatube JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // AJAX Like functionality
    initLikeButtons();
    
    // Share functionality
    initShareButtons();
    
    // Auto-dismiss alerts
    initAlertDismiss();
});

// Like button AJAX
function initLikeButtons() {
    const likeForms = document.querySelectorAll('.like-form');
    
    likeForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const url = form.action;
            const button = form.querySelector('button');
            const icon = button.querySelector('i');
            const countSpan = button.querySelector('.likes-count');
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Update icon
                    if (data.liked) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                        button.classList.remove('text-muted');
                        button.classList.add('text-danger');
                    } else {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                        button.classList.remove('text-danger');
                        button.classList.add('text-muted');
                    }
                    
                    // Update count
                    if (countSpan) {
                        countSpan.textContent = data.likes_count;
                    }
                    
                    // Animation
                    button.style.transform = 'scale(1.2)';
                    setTimeout(() => {
                        button.style.transform = 'scale(1)';
                    }, 150);
                }
            } catch (error) {
                console.error('Error:', error);
                // Fallback to regular form submit
                form.submit();
            }
        });
    });
}

// Share button functionality
function initShareButtons() {
    const shareButtons = document.querySelectorAll('.share-btn');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const url = this.dataset.url;
            
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'Yatube',
                        url: url
                    });
                } catch (err) {
                    if (err.name !== 'AbortError') {
                        copyToClipboard(url);
                    }
                }
            } else {
                copyToClipboard(url);
            }
        });
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Ссылка скопирована!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        // Fallback
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('Ссылка скопирована!');
    });
}

// Show toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '1100';
    toast.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-body d-flex align-items-center">
                <i class="bi bi-check-circle text-success me-2"></i>
                ${message}
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Auto-dismiss alerts
function initAlertDismiss() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Confirm delete
function confirmDelete(message = 'Вы уверены, что хотите удалить?') {
    return confirm(message);
}

// Image preview before upload
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}
