document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const filterType = document.getElementById('filterType');
    const filterPriceRange = document.getElementById('filterPriceRange');
    const priceVal = document.getElementById('priceVal');
    const filterSubsidy = document.getElementById('filterSubsidy');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    const roomsGrid = document.getElementById('roomsGrid');
    const roomCount = document.getElementById('roomCount');
    const quickTags = document.querySelectorAll('.quick-tag-pill');

    // Update Price Slider Display
    filterPriceRange.addEventListener('input', function() {
        const val = parseInt(this.value);
        if (val === 25000) {
            priceVal.textContent = '不限';
        } else {
            priceVal.textContent = `$${val.toLocaleString()} / 月`;
        }
        fetchRooms();
    });

    // Reset Filters
    resetFiltersBtn.addEventListener('click', () => {
        searchInput.value = '';
        filterType.value = '全部';
        filterPriceRange.value = 25000;
        priceVal.textContent = '不限';
        filterSubsidy.checked = false;
        fetchRooms();
    });

    // Quick Tag Clicks
    quickTags.forEach(tagEl => {
        tagEl.addEventListener('click', () => {
            const tagName = tagEl.getAttribute('data-tag');
            // If search box already has this tag, remove it; else add it
            if (searchInput.value.includes(`#${tagName}`)) {
                searchInput.value = searchInput.value.replace(`#${tagName}`, '').trim();
            } else {
                searchInput.value = `#${tagName}`;
            }
            fetchRooms();
        });
    });

    // Form Query String & Fetch
    const fetchRooms = async () => {
        showSkeletons();
        
        const params = new URLSearchParams();
        const query = searchInput.value.trim();
        const type = filterType.value;
        const maxPrice = parseInt(filterPriceRange.value);
        const subsidy = filterSubsidy.checked;

        if (query) params.append('query', query);
        if (type && type !== '全部') params.append('type', type);
        if (maxPrice < 25000) params.append('price_max', maxPrice);
        if (subsidy) params.append('has_subsidy', '1');

        try {
            const response = await fetch(`/api/rooms?${params.toString()}`);
            if (response.ok) {
                const rooms = await response.json();
                renderRooms(rooms);
            } else {
                roomsGrid.innerHTML = '<p class="empty-state">載入資料庫出錯，請稍後再試。</p>';
                roomCount.textContent = '載入失敗';
            }
        } catch (error) {
            console.error('Fetch rooms error:', error);
            roomsGrid.innerHTML = '<p class="empty-state">網路連線錯誤，請確認伺服器運作正常。</p>';
            roomCount.textContent = '連線錯誤';
        }
    };

    // Render Skeletons for Loading State
    const showSkeletons = () => {
        roomsGrid.innerHTML = Array(3).fill(0).map(() => `
            <div class="skeleton-card">
                <div class="skeleton-img"></div>
                <div class="skeleton-text skeleton-title"></div>
                <div class="skeleton-text skeleton-subtitle"></div>
                <div class="skeleton-text skeleton-tags"></div>
                <div class="skeleton-btn"></div>
            </div>
        `).join('');
    };

    // Render Room Cards
    const renderRooms = (rooms) => {
        roomCount.textContent = `共找到 ${rooms.length} 間房源`;

        if (!rooms || rooms.length === 0) {
            roomsGrid.innerHTML = `
                <div class="no-rooms-state">
                    🔍
                    <p>沒有找到符合條件的房源</p>
                    <span>請嘗試修改您的關鍵字或放寬篩選條件。</span>
                </div>
            `;
            return;
        }

        roomsGrid.innerHTML = rooms.map((room, index) => {
            const subsidyBadge = room.has_subsidy === 1 
                ? '<span class="room-badge subsidy">可租補</span>' 
                : '';
            
            const tagsHtml = room.tags_list.map(tag => `
                <span class="room-tag-pill">#${tag}</span>
            `).join('');

            const animationDelay = `style="animation-delay: ${index * 0.05}s;"`;

            return `
                <div class="room-card" ${animationDelay}>
                    <div class="room-card-image">
                        <img src="${room.image_url || '/static/images/room_demo.png'}" alt="${room.title}" loading="lazy">
                        ${subsidyBadge}
                        <div class="room-card-price">NT$ ${room.price.toLocaleString()} <small>/ 月</small></div>
                    </div>
                    <div class="room-card-info">
                        <div class="room-card-meta">
                            <span class="room-type-badge">${room.type}</span>
                            <span class="room-size-badge">${room.size} 坪</span>
                        </div>
                        <h3 class="room-card-title">${room.title}</h3>
                        <p class="room-card-address">📍 ${room.address}</p>
                        <div class="room-card-tags">
                            ${tagsHtml}
                        </div>
                        <a href="/room/${room.id}" class="btn-primary btn-full text-center">查看房源詳情</a>
                    </div>
                </div>
            `;
        }).join('');
    };

    // Search input enter/change trigger
    searchBtn.addEventListener('click', fetchRooms);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            fetchRooms();
        }
    });

    filterType.addEventListener('change', fetchRooms);
    filterSubsidy.addEventListener('change', fetchRooms);

    // Room Modal elements & logic
    const roomModal = document.getElementById('roomModal');
    const openRoomModalBtn = document.getElementById('openRoomModalBtn');
    const closeRoomModalBtn = document.getElementById('closeRoomModalBtn');
    const cancelRoomBtn = document.getElementById('cancelRoomBtn');
    const roomForm = document.getElementById('roomForm');
    const submitRoomBtn = document.getElementById('submitRoomBtn');
    const roomImageInput = document.getElementById('roomImage');
    const roomFileNameDisplay = document.getElementById('roomFileNameDisplay');
    const roomImagePreviewContainer = document.getElementById('roomImagePreviewContainer');
    const roomImagePreview = document.getElementById('roomImagePreview');
    const removeRoomImageBtn = document.getElementById('removeRoomImageBtn');
    const toast = document.getElementById('toast');

    // Toast show function
    function showToast(message, isError = false) {
        toast.textContent = message;
        toast.style.backgroundColor = isError ? 'var(--danger-color)' : 'var(--success-color)';
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Open/Close Modal
    const openModal = () => {
        roomModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    const closeModal = () => {
        roomModal.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(() => {
            roomForm.reset();
            clearImagePreview();
        }, 300);
    };

    if (openRoomModalBtn) openRoomModalBtn.addEventListener('click', openModal);
    if (closeRoomModalBtn) closeRoomModalBtn.addEventListener('click', closeModal);
    if (cancelRoomBtn) cancelRoomBtn.addEventListener('click', closeModal);

    if (roomModal) {
        roomModal.addEventListener('click', (e) => {
            if (e.target === roomModal) {
                closeModal();
            }
        });
    }

    // Image Preview Handling
    if (roomImageInput) {
        roomImageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                if (file.size > 5 * 1024 * 1024) {
                    alert('圖片大小不能超過 5MB');
                    this.value = '';
                    return;
                }
                roomFileNameDisplay.textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    roomImagePreview.src = e.target.result;
                    roomImagePreviewContainer.style.display = 'block';
                }
                reader.readAsDataURL(file);
            } else {
                clearImagePreview();
            }
        });
    }

    if (removeRoomImageBtn) {
        removeRoomImageBtn.addEventListener('click', () => {
            roomImageInput.value = '';
            clearImagePreview();
        });
    }

    function clearImagePreview() {
        if (roomFileNameDisplay) roomFileNameDisplay.textContent = '選擇照片';
        if (roomImagePreview) roomImagePreview.src = '';
        if (roomImagePreviewContainer) roomImagePreviewContainer.style.display = 'none';
    }

    // Submit Room Form
    if (roomForm) {
        roomForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const originalBtnText = submitRoomBtn.textContent;
            submitRoomBtn.textContent = '發布中...';
            submitRoomBtn.disabled = true;

            const formData = new FormData(roomForm);

            try {
                const response = await fetch('/api/rooms', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    showToast(result.message || '房源刊登成功！');
                    closeModal();
                    // Refresh list
                    fetchRooms();
                } else {
                    showToast(result.error || '刊登失敗', true);
                }
            } catch (error) {
                console.error('Submit room error:', error);
                showToast('網路連線錯誤', true);
            } finally {
                submitRoomBtn.textContent = originalBtnText;
                submitRoomBtn.disabled = false;
            }
        });
    }

    // Esc key listener for modal closing
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // Initial Fetch
    fetchRooms();
});
