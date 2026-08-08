/**
 * Identra AI - Main JavaScript
 * Global initialization, GSAP & AOS setup
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── AOS Scroll Animations ──────────────────────────────────────────────
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 750,
            once: true,
            offset: 80,
            easing: 'ease-out-cubic'
        });
    }

    // ── Animated Background Blobs ──────────────────────────────────────────
    const blobs = document.querySelectorAll('.glow-blob');
    if (typeof gsap !== 'undefined' && blobs.length > 0) {
        blobs.forEach((blob, i) => {
            gsap.to(blob, {
                x: i % 2 === 0 ? 40 : -40,
                y: i % 2 === 0 ? -30 : 30,
                duration: 8 + i * 2,
                repeat: -1,
                yoyo: true,
                ease: 'power1.inOut'
            });
        });
    }

    // ── Flash Message Auto-Dismiss ─────────────────────────────────────────
    setTimeout(function () {
        const flashes = document.querySelectorAll('.flash-message');
        flashes.forEach(function (flash) {
            if (typeof gsap !== 'undefined') {
                gsap.to(flash, {
                    x: 100,
                    opacity: 0,
                    duration: 0.35,
                    ease: 'power2.in',
                    onComplete: () => flash.remove()
                });
            } else {
                flash.remove();
            }
        });
    }, 5000);

    // ── Input Focus Glow Effects ───────────────────────────────────────────
    document.querySelectorAll('input, textarea, select').forEach(el => {
        el.addEventListener('focus', () => {
            el.style.borderColor = 'var(--neon-cyan)';
            el.style.boxShadow = '0 0 10px rgba(0, 212, 255, 0.15)';
            el.style.outline = 'none';
        });
        el.addEventListener('blur', () => {
            el.style.borderColor = 'var(--border-subtle)';
            el.style.boxShadow = 'none';
        });
    });

});
