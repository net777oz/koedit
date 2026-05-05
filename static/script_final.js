document.addEventListener('DOMContentLoaded', () => {
    const gallery = document.getElementById('gallery');
    const fileInput = document.getElementById('file-input');
    const hoverInput = document.getElementById('hover-input');
    const statusMsg = document.getElementById('status-msg');
    const packBtn = document.getElementById('pack-btn');
    const autoAnimCheck = document.getElementById('generate-gif-check');
    const loader = document.getElementById('loader');

    let currentImageId = null;
    let isHoverUpload = false;

    function loadImages() {
        // Added cache buster to API call
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
            const mainUrl = `${img.url}?t=${t}`;
            const hoverUrl = img.hover_url ? `${img.hover_url}?t=${t}` : null;

            card.innerHTML = `
                <div class="card-img-container">
                    <div class="img-wrapper">
                        <img src="${mainUrl}" class="card-img main-img" id="img-${img.id}">
                        ${hoverUrl ? `<img src="${hoverUrl}" class="hover-img">` : ''}
                    </div>
                    ${hoverUrl ? '<div class="has-anim-badge">🎬</div>' : ''}
                    <div class="card-overlay">
                        <span class="edit-icon" title="Replace Portrait">✏️</span>
                        <span class="hover-icon" title="Upload Hover Image">🎬</span>
                        <span class="delete-hover-icon" title="Remove Animation">❌</span>
                        <span class="reset-icon" title="Reset to Original" data-id="${img.id}">🔄</span>
                    </div>
                </div>
                <div class="card-id"># ${String(img.id).padStart(4, '0')}</div>
                ${img.name ? `<div class="card-name">${img.name}</div>` : ''}
            `;
            
            card.addEventListener('click', (e) => {
                if (e.target.closest('.card-overlay')) return;
                currentImageId = img.id; isHoverUpload = false; fileInput.click();
            });

            card.querySelector('.edit-icon').addEventListener('click', (e) => {
                e.stopPropagation(); currentImageId = img.id; isHoverUpload = false; fileInput.click();
            });

            card.querySelector('.hover-icon').addEventListener('click', (e) => {
                e.stopPropagation(); currentImageId = img.id; isHoverUpload = true; hoverInput.click();
            });

            card.querySelector('.reset-icon').addEventListener('click', (e) => {
                e.stopPropagation(); resetToOriginal(e.target.getAttribute('data-id'));
            });
            
            card.querySelector('.delete-hover-icon').addEventListener('click', (e) => {
                e.stopPropagation(); deleteHover(img.id);
            });

            gallery.appendChild(card);
        });
    }

    function resetToOriginal(id) {
        loader.style.display = 'flex';
        fetch(`/api/reset/${id}`, { method: 'POST' })
        .then(() => { location.reload(); });
    }

    function handleFileSelection(file, isHover) {
        if (!file || !currentImageId) return;
        isHoverUpload = isHover;
        const cropModal = document.getElementById('crop-modal');
        const cropImage = document.getElementById('crop-image');
        cropImage.src = URL.createObjectURL(file);
        cropModal.style.display = 'flex';
        if (window.cropper) window.cropper.destroy();
        cropImage.onload = () => {
            window.cropper = new Cropper(cropImage, { aspectRatio: 64/80, viewMode: 1 });
        };
    }

    fileInput.addEventListener('change', (e) => { handleFileSelection(e.target.files[0], false); });
    hoverInput.addEventListener('change', (e) => { handleFileSelection(e.target.files[0], true); });

    document.getElementById('crop-cancel').addEventListener('click', () => {
        document.getElementById('crop-modal').style.display = 'none';
        if (window.cropper) window.cropper.destroy();
    });

    document.getElementById('crop-confirm').addEventListener('click', () => {
        if (!window.cropper) return;
        window.cropper.getCroppedCanvas({ width: 256, height: 320 }).toBlob((blob) => {
            document.getElementById('crop-modal').style.display = 'none';
            if (window.cropper) window.cropper.destroy();
            uploadFileDirectly(blob, isHoverUpload);
        }, 'image/png');
    });

    function uploadFileDirectly(fileOrBlob, isHover) {
        const formData = new FormData();
        formData.append('file', fileOrBlob, isHover ? 'hover.webp' : 'cropped.png');
        const autoAnim = document.getElementById('generate-gif-check')?.checked;
        if (autoAnim) formData.append('generate_gif', 'true');
        
        loader.style.display = 'flex';
        fetch(isHover ? `/api/upload_hover/${currentImageId}` : `/api/upload/${currentImageId}`, { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.success) location.href = location.pathname + "?t=" + new Date().getTime();
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

    function deleteHover(id) {
        if (!confirm(`Remove animation for #${id}?`)) return;
        loader.style.display = 'flex';
        fetch(`/api/delete_hover/${id}`, { method: 'POST' })
        .then(() => { location.reload(); });
    }

    function showStatus(text, type) {
        statusMsg.textContent = text;
        statusMsg.className = 'status-msg ' + type;
    }
});
