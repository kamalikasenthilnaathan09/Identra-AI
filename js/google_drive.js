/**
 * Identra AI - Google Drive Client Module JS
 * Handles AJAX Drive file browser, search, MIME filtering, pagination, batch import,
 * duplicate detection, AI category preview, and auto-sync toggling.
 */

let currentFilter = '';
let currentQuery = '';
let nextPageToken = null;
let currentDriveFiles = [];

document.addEventListener('DOMContentLoaded', function () {
    const driveBrowser = document.getElementById('drive-browser-card');
    if (!driveBrowser) return;

    loadDriveFiles();

    // Search Input Handler
    const searchInput = document.getElementById('drive-search-input');
    let searchTimeout = null;
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            currentQuery = this.value.trim();
            searchTimeout = setTimeout(() => {
                nextPageToken = null;
                loadDriveFiles();
            }, 350);
        });
    }

    // MIME Filter Chips
    document.querySelectorAll('.chip-filter').forEach(chip => {
        chip.addEventListener('click', function () {
            document.querySelectorAll('.chip-filter').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.getAttribute('data-type') || '';
            nextPageToken = null;
            loadDriveFiles();
        });
    });
});

function loadDriveFiles(append = false) {
    const tableBody = document.getElementById('drive-files-tbody');
    const loadingSpinner = document.getElementById('drive-loading-spinner');
    const emptyState = document.getElementById('drive-empty-state');
    const loadMoreBtn = document.getElementById('load-more-btn');

    if (!append) {
        tableBody.innerHTML = '';
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';
    }

    let url = `/google-drive/api/files?q=${encodeURIComponent(currentQuery)}&type=${encodeURIComponent(currentFilter)}`;
    if (nextPageToken && append) {
        url += `&pageToken=${encodeURIComponent(nextPageToken)}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (loadingSpinner) loadingSpinner.style.display = 'none';

            if (data.error) {
                if (typeof showToast === 'function') showToast('error', data.error);
                return;
            }

            const files = data.files || [];
            currentDriveFiles = files;
            nextPageToken = data.nextPageToken || null;

            if (loadMoreBtn) {
                loadMoreBtn.style.display = nextPageToken ? 'inline-flex' : 'none';
            }

            if (files.length === 0 && !append) {
                if (emptyState) emptyState.style.display = 'block';
                return;
            }

            files.forEach(file => {
                const row = document.createElement('tr');
                row.className = 'drive-file-row';
                
                const mimeIcon = getMimeIconClass(file.mimeType, file.name);
                const formattedSize = formatBytes(file.size || 0);
                const modDate = file.modifiedTime ? new Date(file.modifiedTime).toLocaleDateString() : 'N/A';

                // Duplicate Detection Badge check
                let actionCell = '';
                if (file.is_imported) {
                    actionCell = `
                        <span class="badge" style="background: rgba(16, 185, 129, 0.18); color: #10B981; border: 1px solid #10B981;">
                            <i class="fa-solid fa-check"></i> Already Synced
                        </span>
                    `;
                } else {
                    actionCell = `
                        <div style="display:flex; justify-content:flex-end; gap:6px;">
                            <button class="action-btn" onclick="previewDriveFile('${file.id}')" title="Preview AI Category & Snippet">
                                <i class="fa-regular fa-eye"></i>
                            </button>
                            <button class="btn btn-primary btn-import-file" style="padding: 0.38rem 0.8rem; font-size: 0.8rem;" onclick="importDriveFile('${file.id}', '${escapeHtml(file.name)}', '${file.mimeType}', ${file.size || 0}, this)">
                                <i class="fa-solid fa-cloud-arrow-down"></i> Import
                            </button>
                        </div>
                    `;
                }

                // Confidence badge color
                const confScore = file.confidence || 0.95;
                const confPct = file.confidence_pct || `${Math.round(confScore * 100)}%`;
                let confBadgeColor = '#10B981';
                if (confScore < 0.60) confBadgeColor = '#F87171';
                else if (confScore < 0.80) confBadgeColor = '#F59E0B';

                row.innerHTML = `
                    <td style="text-align:center;">
                        ${file.is_imported ? '' : `<input type="checkbox" class="file-select-checkbox" data-id="${file.id}" data-name="${escapeHtml(file.name)}" data-size="${file.size || 0}" onchange="updateBatchCount()" style="cursor:pointer;">`}
                    </td>
                    <td>
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div class="mime-icon ${mimeIcon.bgClass}">
                                <i class="fa-solid ${mimeIcon.iconClass}"></i>
                            </div>
                            <div>
                                <div style="font-weight:600; color:#fff;">${escapeHtml(file.name)}</div>
                                <div style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(file.mimeType)}</div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div style="display:flex; flex-direction:column; gap:2px;">
                            <span class="badge badge-indigo" style="font-size:0.75rem;">📁 ${file.category || 'Personal Documents'}</span>
                            <span style="font-size:0.72rem; color:${confBadgeColor};"><i class="fa-solid fa-bolt"></i> ${confPct} Confidence</span>
                        </div>
                    </td>
                    <td>${formattedSize}</td>
                    <td>${modDate}</td>
                    <td style="text-align:right;">${actionCell}</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(err => {
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            console.error(err);
            if (typeof showToast === 'function') showToast('error', 'Error connecting to Google Drive API.');
        });
}

function updateBatchCount() {
    const checked = document.querySelectorAll('.file-select-checkbox:checked');
    const batchBtn = document.getElementById('batch-import-btn');
    const countSpan = document.getElementById('selected-count');

    if (batchBtn && countSpan) {
        countSpan.innerText = checked.length;
        batchBtn.style.display = checked.length > 0 ? 'inline-flex' : 'none';
    }
}

function toggleSelectAll(checked) {
    document.querySelectorAll('.file-select-checkbox').forEach(cb => {
        cb.checked = checked;
    });
    updateBatchCount();
}

function batchImportSelected() {
    const checked = document.querySelectorAll('.file-select-checkbox:checked');
    if (checked.length === 0) return;

    const filesToImport = [];
    checked.forEach(cb => {
        filesToImport.push({
            drive_file_id: cb.getAttribute('data-id'),
            file_name: cb.getAttribute('data-name'),
            size: parseInt(cb.getAttribute('data-size'))
        });
    });

    const batchBtn = document.getElementById('batch-import-btn');
    batchBtn.disabled = true;
    batchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Batch Syncing...';

    fetch('/google-drive/api/batch-import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files: filesToImport })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (typeof showToast === 'function') showToast('success', data.message);
            setTimeout(() => location.reload(), 1200);
        } else {
            batchBtn.disabled = false;
            if (typeof showToast === 'function') showToast('error', data.error || 'Batch import failed.');
        }
    });
}

function previewDriveFile(fileId) {
    const modal = document.getElementById('drive-preview-modal');
    modal.style.display = 'flex';

    fetch('/google-drive/api/preview-file/' + fileId)
        .then(res => res.json())
        .then(data => {
            document.getElementById('prev-file-name').innerText = data.name;
            document.getElementById('prev-file-category').innerText = data.category + ' (' + (data.subcategory || 'General') + ')';
            document.getElementById('prev-file-confidence').innerText = data.confidence;
            document.getElementById('prev-file-keywords').innerText = data.matched_keywords || 'None';
            document.getElementById('prev-file-snippet').innerText = data.snippet || 'No OCR text preview available.';

            const confirmBtn = document.getElementById('prev-import-confirm-btn');
            confirmBtn.onclick = function() {
                closeDrivePreviewModal();
                importDriveFile(data.id, data.name, data.mimeType, data.size, confirmBtn);
            };
        });
}

function closeDrivePreviewModal() {
    document.getElementById('drive-preview-modal').style.display = 'none';
}

function importDriveFile(fileId, fileName, mimeType, size, button) {
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Importing...';

    fetch('/google-drive/api/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            drive_file_id: fileId,
            file_name: fileName,
            mime_type: mimeType,
            size: size
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            button.className = 'btn btn-secondary btn-import-file';
            button.style.color = '#10B981';
            button.style.borderColor = 'rgba(16, 185, 129, 0.4)';
            button.innerHTML = '<i class="fa-solid fa-check"></i> Imported';
            if (typeof showToast === 'function') showToast('success', data.message);
            setTimeout(() => location.reload(), 1200);
        } else {
            button.disabled = false;
            button.innerHTML = originalText;
            if (typeof showToast === 'function') showToast('error', data.error || 'Import failed.');
        }
    })
    .catch(err => {
        button.disabled = false;
        button.innerHTML = originalText;
        console.error(err);
        if (typeof showToast === 'function') showToast('error', 'Network error during file import.');
    });
}

function toggleAutoSync(enabled) {
    fetch('/google-drive/api/toggle-autosync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: enabled })
    })
    .then(res => res.json())
    .then(data => {
        if (typeof showToast === 'function') showToast('info', data.message);
    });
}

function getMimeIconClass(mimeType, fileName) {
    const m = (mimeType || '').toLowerCase();
    const name = (fileName || '').toLowerCase();

    if (m.includes('pdf') || name.endsWith('.pdf')) {
        return { iconClass: 'fa-file-pdf', bgClass: 'mime-pdf' };
    } else if (m.includes('word') || name.endsWith('.docx') || name.endsWith('.doc')) {
        return { iconClass: 'fa-file-word', bgClass: 'mime-docx' };
    } else if (m.includes('image') || name.endsWith('.png') || name.endsWith('.jpg') || name.endsWith('.jpeg')) {
        return { iconClass: 'fa-file-image', bgClass: 'mime-image' };
    } else if (m.includes('spreadsheet') || m.includes('excel') || name.endsWith('.xlsx') || name.endsWith('.csv')) {
        return { iconClass: 'fa-file-excel', bgClass: 'mime-sheet' };
    } else if (m.includes('presentation') || m.includes('powerpoint') || name.endsWith('.pptx') || name.endsWith('.ppt')) {
        return { iconClass: 'fa-file-powerpoint', bgClass: 'mime-ppt' };
    } else {
        return { iconClass: 'fa-file-lines', bgClass: 'mime-txt' };
    }
}

function formatBytes(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
