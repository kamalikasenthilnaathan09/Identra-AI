/**
 * Identra AI - Dashboard JS
 * Card hover effects, GSAP counter animations, sidebar transitions
 */

document.addEventListener('DOMContentLoaded', function () {

    if (typeof gsap === 'undefined') return;

    // ── Stat Card Counter Animations ──────────────────────────────────────
    document.querySelectorAll('.stat-item-val').forEach(el => {
        const finalValue = parseInt(el.innerText) || 0;
        el.innerText = '0';
        gsap.to(el, {
            innerText: finalValue,
            duration: 1.8,
            snap: { innerText: 1 },
            ease: 'power2.out',
            delay: 0.3
        });
    });

    // ── Glass Card Hover Micro-animations ─────────────────────────────────
    document.querySelectorAll('.glass-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, { y: -3, duration: 0.25, ease: 'power2.out' });
        });
        card.addEventListener('mouseleave', () => {
            gsap.to(card, { y: 0, duration: 0.25, ease: 'power2.out' });
        });
    });

    // ── Document Row Item Hover ────────────────────────────────────────────
    document.querySelectorAll('.document-item-row').forEach(row => {
        row.addEventListener('mouseenter', () => {
            gsap.to(row, { x: 4, duration: 0.2, ease: 'power1.out' });
        });
        row.addEventListener('mouseleave', () => {
            gsap.to(row, { x: 0, duration: 0.2, ease: 'power1.out' });
        });
    });

    // ── Timeline Node Entrance ─────────────────────────────────────────────
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        document.querySelectorAll('.timeline-node-item').forEach((node, i) => {
            gsap.from(node, {
                x: -30,
                opacity: 0,
                duration: 0.5,
                delay: i * 0.08,
                ease: 'power2.out',
                scrollTrigger: {
                    trigger: node,
                    start: 'top 90%',
                    once: true
                }
            });
        });
    }

    // ── Storage Bar Animated Fill ──────────────────────────────────────────
    const storageFill = document.querySelector('.storage-bar-fill');
    if (storageFill) {
        const targetWidth = storageFill.style.width;
        storageFill.style.width = '0%';
        gsap.to(storageFill, {
            width: targetWidth,
            duration: 1.5,
            ease: 'power2.out',
            delay: 0.5
        });
    }

    // ── Sidebar Nav Item Hover Glow ────────────────────────────────────────
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('mouseenter', () => {
            gsap.to(item, { paddingLeft: '1.2rem', duration: 0.2, ease: 'power1.out' });
        });
        item.addEventListener('mouseleave', () => {
            if (!item.classList.contains('active')) {
                gsap.to(item, { paddingLeft: '1rem', duration: 0.2, ease: 'power1.out' });
            }
        });
    });

});
