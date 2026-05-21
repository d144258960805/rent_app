document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('reviewModal');
    const openBtn = document.getElementById('openReviewModalBtn');
    const closeBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const form = document.getElementById('reviewForm');
    const submitBtn = document.getElementById('submitBtn');
    
    const fileInput = document.getElementById('reviewImage');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const toast = document.getElementById('toast');

    const reviewsList = document.querySelector('.reviews-list');
    const currentRoomId = document.getElementById('currentRoomId').value;
    
    // Lightbox Elements
    const lightboxModal = document.getElementById('lightboxModal');
    const lightboxImage = document.getElementById('lightboxImage');
    const closeLightboxBtn = document.getElementById('closeLightboxBtn');

    // Modal Logic
    const openModal = () => {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    };

    const closeModal = () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(() => {
            form.reset();
            clearImagePreview();
        }, 300); // Wait for transition
    };

    openBtn.addEventListener('click', openModal);
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // File Upload Preview Logic
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        
        if (file) {
            // Validate size (5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('圖片大小不能超過 5MB');
                this.value = '';
                return;
            }

            fileNameDisplay.textContent = file.name;
            
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreviewContainer.style.display = 'block';
            }
            reader.readAsDataURL(file);
        } else {
            clearImagePreview();
        }
    });

    removeImageBtn.addEventListener('click', () => {
        fileInput.value = '';
        clearImagePreview();
    });

    function clearImagePreview() {
        fileNameDisplay.textContent = '選擇照片';
        imagePreview.src = '';
        imagePreviewContainer.style.display = 'none';
    }

    function showToast(message, isError = false) {
        toast.textContent = message;
        toast.style.backgroundColor = isError ? 'var(--danger-color)' : 'var(--success-color)';
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Relative Time Formatter (Handles SQLite UTC timestamps)
    function formatTime(timeStr) {
        if (!timeStr) return '';
        const parts = timeStr.match(/(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)/);
        if (!parts) return timeStr;
        
        // SQLite stores CURRENT_TIMESTAMP in UTC
        const utcDate = new Date(Date.UTC(
            parseInt(parts[1]),
            parseInt(parts[2]) - 1,
            parseInt(parts[3]),
            parseInt(parts[4]),
            parseInt(parts[5]),
            parseInt(parts[6])
        ));
        
        const now = new Date();
        const diffMs = now - utcDate;
        const diffSec = Math.floor(diffMs / 1000);
        
        if (diffSec < 60) {
            return '剛剛';
        }
        const diffMin = Math.floor(diffSec / 60);
        if (diffMin < 60) {
            return `${diffMin} 分鐘前`;
        }
        const diffHr = Math.floor(diffMin / 60);
        if (diffHr < 24) {
            return `${diffHr} 小時前`;
        }
        const diffDay = Math.floor(diffHr / 24);
        if (diffDay < 7) {
            return `${diffDay} 天前`;
        }
        
        return utcDate.toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }

    // HTML Escape Helper
    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    // Render Reviews list
    const renderReviews = (reviews) => {
        if (!reviews || reviews.length === 0) {
            reviewsList.innerHTML = '<p class="empty-state">目前還沒有評論，成為第一個留下真實評價的租客吧！</p>';
            return;
        }

        reviewsList.innerHTML = reviews.map((review, index) => {
            const avatarChar = '匿';
            const relativeTime = formatTime(review.created_at);
            const imageHtml = review.image_url 
                ? `<div class="review-image-thumbnail">
                     <img src="${review.image_url}" alt="評論圖片" class="review-thumb-img">
                   </div>`
                : '';
            
            const gradientIndex = review.id % 4;
            const gradients = [
                'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                'linear-gradient(135deg, #10b981 0%, #047857 100%)',
                'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
            ];
            const avatarStyle = `style="background: ${gradients[gradientIndex]};"`;
            const animationStyle = `style="animation-delay: ${index * 0.08}s;"`;

            return `
                <div class="review-card" ${animationStyle}>
                    <div class="review-card-header">
                        <div class="reviewer-info">
                            <div class="avatar" ${avatarStyle}>${avatarChar}</div>
                            <div>
                                <div class="reviewer-name">匿名逢甲學生</div>
                                <div class="review-time">${relativeTime}</div>
                            </div>
                        </div>
                    </div>
                    <div class="review-content">${escapeHTML(review.content)}</div>
                    ${imageHtml}
                </div>
            `;
        }).join('');
        
        attachThumbnailListeners();
    };

    // Fetch reviews from API
    const fetchReviews = async () => {
        try {
            const response = await fetch(`/api/reviews?room_id=${currentRoomId}`);
            if (response.ok) {
                const reviews = await response.json();
                renderReviews(reviews);
            } else {
                console.error('無法載入評論資料');
            }
        } catch (error) {
            console.error('載入評論時發生網路錯誤:', error);
        }
    };

    // Lightbox popup handlers
    function attachThumbnailListeners() {
        const thumbnails = document.querySelectorAll('.review-thumb-img');
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', () => {
                lightboxImage.src = thumb.src;
                lightboxModal.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
        });
    }

    const closeLightbox = () => {
        lightboxModal.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(() => {
            lightboxImage.src = '';
        }, 300);
    };

    closeLightboxBtn.addEventListener('click', closeLightbox);
    lightboxModal.addEventListener('click', (e) => {
        if (e.target === lightboxModal) {
            closeLightbox();
        }
    });

    // Main gallery image click to zoom
    const mainGalleryImg = document.querySelector('.gallery-main img');
    if (mainGalleryImg) {
        mainGalleryImg.style.cursor = 'zoom-in';
        mainGalleryImg.addEventListener('click', () => {
            lightboxImage.src = mainGalleryImg.src;
            lightboxModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    // Global Key Listener for ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeLightbox();
        }
    });

    // Form Submit Logic
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = '上傳中...';
        submitBtn.disabled = true;

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/reviews', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                showToast(result.message);
                closeModal();
                // Reload comment list dynamically without page reload
                fetchReviews();
            } else {
                showToast(result.error || '上傳失敗', true);
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('網路連線錯誤', true);
        } finally {
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
        }
    });

    // Initial load of reviews
    fetchReviews();
});
