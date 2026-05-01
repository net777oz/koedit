document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.getElementById('gallery');
    const fileInput = document.getElementById('file-input');
    const p2Input = document.getElementById('p2-input');
    const hoverInput = document.getElementById('hover-input');
    const statusMsg = document.getElementById('status-msg');
    const packBtn = document.getElementById('pack-btn');
    const autoAnimCheck = document.getElementById('generate-gif-check');
    const loader = document.getElementById('loader');

    let currentImageId = null;
    let uploadType = 'p1';

    // Tab switching logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });

    function loadImages() {
        fetch(`/api/images?t=${new Date().getTime()}`)
            .then(res => res.json())
            .then(data => { renderGallery(data.images); });
    }
    loadImages();

    function renderGallery(images) {
        gallery.innerHTML = '';
        const t = new Date().getTime();
        images.forEach(img => {
            const card = document.createElement('div');
            card.className = 'card';
            
            // Default: P1 Anim > P1 Static
            const displayUrl = (img.p1_anim || img.p1_static) + `?t=${t}`;
            // Hover: P2 Anim > P2 Static > P1 Anim > P1 Static
            const hoverUrl = (img.p2_anim || img.p2_static || img.p1_anim || img.p1_static) + `?t=${t}`;
            
            const hasP2 = !!img.p2_static;
            const hasP1Anim = !!img.p1_anim;
            const hasP2Anim = !!img.p2_anim;

            card.innerHTML = `
                <div class="card-img-container">
                    <div class="img-wrapper">
                        <img src="${displayUrl}" class="card-img main-img" id="img-${img.id}">
                        <img src="${hoverUrl}" class="card-img hover-img" style="position:absolute; left:0; top:0;">
                    </div>
                    <div class="badge-container">
                        ${hasP1Anim ? '<div class="badge anim-badge" title="P1 Anim Active">🎬1</div>' : ''}
                        ${hasP2 ? '<div class="badge p2-badge" title="P2 Static Active">🖼️2</div>' : ''}
                        ${hasP2Anim ? '<div class="badge anim-badge" title="P2 Anim Active">🎬2</div>' : ''}
                    </div>
                    <div class="card-overlay">
                        <div class="overlay-group">
                            <span class="btn-icon p1-btn" title="Upload Portrait 1" data-id="${img.id}">🖼️1</span>
                            <span class="btn-icon p2-btn" title="Upload Portrait 2" data-id="${img.id}">🖼️2</span>
                            <span class="btn-icon reset-v1-btn" title="Reset P1" data-id="${img.id}">🔄1</span>
                            <span class="btn-icon delete-v2-btn" title="Delete P2" data-id="${img.id}">❌2</span>
                        </div>
                    </div>
                </div>
                <div class="card-id"># ${String(img.id).padStart(4, '0')}</div>
                ${img.name ? `<div class="card-name">${img.name}</div>` : ''}
            `;
            
            card.querySelector('.p1-btn').addEventListener('click', (e) => {
                e.stopPropagation(); currentImageId = img.id; uploadType = 'p1'; fileInput.click();
            });

            card.querySelector('.p2-btn').addEventListener('click', (e) => {
                e.stopPropagation(); currentImageId = img.id; uploadType = 'p2'; p2Input.click();
            });

            card.querySelector('.reset-v1-btn').addEventListener('click', (e) => {
                e.stopPropagation(); resetP1(img.id);
            });

            card.querySelector('.delete-v2-btn').addEventListener('click', (e) => {
                e.stopPropagation(); deleteP2(img.id);
            });

            gallery.appendChild(card);
        });
    }

    function resetP1(id) {
        if (!confirm(`Reset Portrait 1 of #${id} to original?`)) return;
        loader.style.display = 'flex';
        fetch(`/api/reset/${id}`, { method: 'POST' })
        .then(() => { location.reload(); });
    }

    function deleteP2(id) {
        if (!confirm(`Delete Portrait 2 and its animation for #${id}?`)) return;
        loader.style.display = 'flex';
        fetch(`/api/delete_v2/${id}`, { method: 'POST' })
        .then(() => { location.reload(); });
    }

    function handleFileSelection(file, type) {
        if (!file || !currentImageId) return;
        uploadType = type;
        const cropModal = document.getElementById('crop-modal');
        const cropImage = document.getElementById('crop-image');
        cropImage.src = URL.createObjectURL(file);
        cropModal.style.display = 'flex';
        if (window.cropper) window.cropper.destroy();
        cropImage.onload = () => {
            // P1 is 64x80, P2 is 128x160. Both 4:5 ratio.
            window.cropper = new Cropper(cropImage, { aspectRatio: 64/80, viewMode: 1 });
        };
    }

    fileInput.addEventListener('change', (e) => { handleFileSelection(e.target.files[0], 'p1'); });
    p2Input.addEventListener('change', (e) => { handleFileSelection(e.target.files[0], 'p2'); });

    document.getElementById('crop-cancel').addEventListener('click', () => {
        document.getElementById('crop-modal').style.display = 'none';
        if (window.cropper) window.cropper.destroy();
    });

    document.getElementById('crop-confirm').addEventListener('click', () => {
        if (!window.cropper) return;
        const size = uploadType === 'p1' ? { width: 128, height: 160 } : { width: 256, height: 320 };
        window.cropper.getCroppedCanvas(size).toBlob((blob) => {
            document.getElementById('crop-modal').style.display = 'none';
            if (window.cropper) window.cropper.destroy();
            uploadFileDirectly(blob);
        }, 'image/png');
    });

    function uploadFileDirectly(blob) {
        const formData = new FormData();
        formData.append('file', blob, 'portrait.png');
        const autoAnim = document.getElementById('generate-gif-check')?.checked;
        if (autoAnim) formData.append('generate_gif', 'true');
        
        loader.style.display = 'flex';
        const endpoint = uploadType === 'p1' ? `/api/upload_v1/${currentImageId}` : `/api/upload_v2/${currentImageId}`;
        
        fetch(endpoint, { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.success) location.reload();
            else { loader.style.display = 'none'; alert(data.error); }
        });
    }

    packBtn.addEventListener('click', () => {
        packBtn.disabled = true; loader.style.display = 'flex';
        fetch('/api/pack', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            packBtn.disabled = false; loader.style.display = 'none';
            alert(data.message || data.error);
        });
    });
});
