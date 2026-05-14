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
                
                // Optional: dynamically add the review to the DOM here
                // For demo, we just reload the page or show toast
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
});
