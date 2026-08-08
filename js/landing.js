/**
 * Identra AI - Landing Page JS Architecture
 * GSAP entrance timelines, floating 3D icons, particle glow & interactive FAQ accordion
 */

document.addEventListener('DOMContentLoaded', function () {
    // ── FAQ Accordion Handler ──────────────────────────────────────────────
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', () => {
            const item = question.parentElement;
            const isActive = item.classList.contains('active');
            
            // Close all items
            document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('active'));
            
            // Toggle clicked item
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    if (typeof gsap === 'undefined') return;

    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    }

    // ── Hero Section Entrance (Clean GSAP Timeline) ──────────────────────────
    const heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    heroTl
        .from('.hero-badge',         { y: -20, opacity: 0, duration: 0.6 })
        .from('.hero-title',         { y: 35,  opacity: 0, duration: 0.7 }, '-=0.3')
        .from('.hero-subtitle',      { y: 25,  opacity: 0, duration: 0.6 }, '-=0.4')
        .from('.hero-actions',       { y: 20,  opacity: 0, duration: 0.5 }, '-=0.3')
        .from('.hero-art-container', { scale: 0.85, opacity: 0, duration: 0.8, ease: 'back.out(1.4)' }, '-=0.5');

    // ── Brain Mesh & Glow Motion ───────────────────────────────────────────
    gsap.to('.brain-mesh', {
        y: -15,
        duration: 3.5,
        repeat: -1,
        yoyo: true,
        ease: 'power1.inOut'
    });

    gsap.to('.brain-glow', {
        scale: 1.18,
        opacity: 0.6,
        duration: 2.8,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
    });

    // ── 6 Floating Icons Individual Staggered Parallax Motion ────────────────
    const floatingIcons = document.querySelectorAll('.floating-icon');
    floatingIcons.forEach((icon, i) => {
        const yDir = i % 2 === 0 ? -20 : 20;
        const rot  = i % 2 === 0 ? 6   : -6;
        const dur  = 3.5 + i * 0.5;

        gsap.to(icon, {
            y: yDir,
            rotation: rot,
            duration: dur,
            repeat: -1,
            yoyo: true,
            ease: 'power1.inOut',
            delay: i * 0.2
        });
    });

    // ── Stat Counter Scroll Animation ─────────────────────────────────────
    document.querySelectorAll('.stat-number').forEach(el => {
        const finalText = el.innerText;
        const numMatch = finalText.match(/\d+/);
        
        if (numMatch && typeof ScrollTrigger !== 'undefined') {
            const num = parseInt(numMatch[0]);
            const prefix = finalText.includes('<') ? '<' : '';
            const suffix = finalText.includes('+') ? '+' : finalText.includes('%') ? '%' : '';

            ScrollTrigger.create({
                trigger: el,
                start: 'top 90%',
                once: true,
                onEnter: () => {
                    gsap.fromTo(el,
                        { innerText: 0 },
                        {
                            innerText: num,
                            duration: 2,
                            snap: { innerText: 1 },
                            ease: 'power2.out',
                            onUpdate: function () {
                                el.innerText = prefix + Math.round(el.innerText) + suffix;
                            },
                            onComplete: () => { el.innerText = finalText; }
                        }
                    );
                }
            });
        }
    });

    // ── Smooth Scroll Link Active Handling ────────────────────────────────
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                const offsetTop = target.getBoundingClientRect().top + window.pageYOffset - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });

                document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
});
