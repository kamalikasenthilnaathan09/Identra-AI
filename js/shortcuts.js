/**
 * Identra AI - Keyboard Shortcuts
 * Global hotkey mapping
 */

document.addEventListener('keydown', function(e) {
    // Skip if user is typing in an input/textarea
    const tag = document.activeElement.tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

    if (e.ctrlKey || e.metaKey) {
        switch(e.key.toLowerCase()) {
            case 'k':
                e.preventDefault();
                if (typeof showToast === 'function') showToast('info', 'Opening Smart Search...');
                window.location.href = '/search/';
                break;
            case 'u':
                e.preventDefault();
                if (typeof showToast === 'function') showToast('info', 'Opening Documents...');
                window.location.href = '/documents/';
                break;
            case 'p':
                e.preventDefault();
                if (typeof showToast === 'function') showToast('info', 'Opening Profile...');
                window.location.href = '/dashboard/profile';
                break;
            case '/':
                e.preventDefault();
                if (typeof showToast === 'function') showToast('info', 'Opening AI Assistant...');
                window.location.href = '/assistant/';
                break;
        }
    }
});
