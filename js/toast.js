/**
 * Identra AI - Toast Notification System
 * Global showToast(type, message, duration) function
 */

(function() {
    const ICONS = {
        success: 'fa-circle-check',
        error:   'fa-circle-xmark',
        warning: 'fa-triangle-exclamation',
        info:    'fa-circle-info'
    };

    const TITLES = {
        success: 'Success',
        error:   'Error',
        warning: 'Warning',
        info:    'Information'
    };

    function getContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    window.showToast = function(type, message, duration) {
        type = type || 'info';
        duration = duration || 5000;

        const container = getContainer();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fa-solid ${ICONS[type] || ICONS.info}"></i>
            </div>
            <div class="toast-body">
                <div class="toast-title">${TITLES[type] || 'Notice'}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.closest('.toast').remove()">
                <i class="fa-solid fa-xmark"></i>
            </button>
            <div class="toast-progress" style="animation-duration: ${duration}ms;"></div>
        `;

        container.appendChild(toast);

        // GSAP entrance animation
        if (typeof gsap !== 'undefined') {
            gsap.from(toast, {
                x: 100,
                opacity: 0,
                duration: 0.4,
                ease: 'power2.out'
            });
        }

        // Auto dismiss
        setTimeout(function() {
            if (toast.parentNode) {
                if (typeof gsap !== 'undefined') {
                    gsap.to(toast, {
                        x: 100,
                        opacity: 0,
                        duration: 0.3,
                        ease: 'power2.in',
                        onComplete: function() { toast.remove(); }
                    });
                } else {
                    toast.remove();
                }
            }
        }, duration);
    };
})();
