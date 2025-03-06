gsap.registerPlugin(ScrollTrigger);

// Initialize GSAP animations
window.addEventListener('DOMContentLoaded', () => {
    // Hero content animation
    gsap.to('.hero-content', {
        opacity: 1,
        y: 0,
        duration: 1.5,
        ease: 'power3.out'
    });

    // Feature cards animation
    gsap.utils.toArray('.feature-card').forEach((card, i) => {
        gsap.to(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top bottom-=100',
                end: 'top center',
                toggleActions: 'play none none reverse'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: i * 0.2,
            ease: 'power3.out'
        });
    });

    // Status cards animation
    gsap.utils.toArray('.status-card').forEach((card, i) => {
        gsap.to(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top bottom-=100',
                end: 'top center',
                toggleActions: 'play none none reverse'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: i * 0.2,
            ease: 'power3.out'
        });
    });

    // How it works steps animation
    gsap.utils.toArray('.step').forEach((step, i) => {
        gsap.to(step, {
            scrollTrigger: {
                trigger: step,
                start: 'top bottom-=100',
                end: 'top center',
                toggleActions: 'play none none reverse'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: i * 0.3,
            ease: 'power3.out'
        });
    });

    // AI Personas animation
    gsap.utils.toArray('.persona-card').forEach((card, i) => {
        gsap.to(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top bottom-=100',
                end: 'top center',
                toggleActions: 'play none none reverse'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: i * 0.2,
            ease: 'power3.out'
        });
    });

    // Pricing cards animation
    gsap.utils.toArray('.pricing-card').forEach((card, i) => {
        gsap.to(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top bottom-=100',
                end: 'top center',
                toggleActions: 'play none none reverse'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: i * 0.2,
            ease: 'power3.out'
        });
    });

    // FAQ items animation
    gsap.utils.toArray('.faq-item').forEach((item, i) => {
        gsap.to(item, {
            scrollTrigger: {
                trigger: item,
                start: 'top bottom-=100',
                end: 'top center',
                toggleActions: 'play none none reverse'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            delay: i * 0.1,
            ease: 'power3.out'
        });
    });

    // CTA section animation
    gsap.to('.cta-content', {
        scrollTrigger: {
            trigger: '.cta-content',
            start: 'top bottom-=100',
            end: 'top center',
            toggleActions: 'play none none reverse'
        },
        opacity: 1,
        y: 0,
        duration: 1,
        ease: 'power3.out'
    });

    // Demo container animation
    gsap.to('.demo-container', {
        scrollTrigger: {
            trigger: '.demo-container',
            start: 'top bottom-=100',
            end: 'top center',
            toggleActions: 'play none none reverse'
        },
        opacity: 1,
        y: 0,
        duration: 1,
        ease: 'power3.out'
    });

    // Navbar hide/show on scroll
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        const navbar = document.querySelector('.navbar');
        
        if (currentScroll > lastScroll && currentScroll > 100) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
        }
        lastScroll = currentScroll;
    });

    // Animated background glow
    const glow1 = document.getElementById('glow1');
    const glow2 = document.getElementById('glow2');

    gsap.to([glow1, glow2], {
        x: 'random(-50, 50)',
        y: 'random(-50, 50)',
        duration: 'random(10, 20)',
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
        stagger: {
            amount: 5,
            from: 'random'
        }
    });

    // Parallax effect on scroll
    gsap.utils.toArray('.feature-card').forEach(card => {
        gsap.to(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top bottom',
                end: 'bottom top',
                scrub: 1
            },
            y: 50,
            ease: 'none'
        });
    });

    // Mouse movement effect on cards
    document.querySelectorAll('.feature-card, .persona-card, .pricing-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;

            gsap.to(card, {
                rotateY: deltaX * 5,
                rotateX: -deltaY * 5,
                duration: 0.5,
                ease: 'power2.out'
            });
        });

        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                rotateY: 0,
                rotateX: 0,
                duration: 0.5,
                ease: 'power2.out'
            });
        });
    });

    // Smooth scroll for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Button hover effect
    document.querySelectorAll('.cta-button, .pricing-button').forEach(button => {
        button.addEventListener('mousemove', (e) => {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            button.style.setProperty('--x', `${x}px`);
            button.style.setProperty('--y', `${y}px`);
        });
    });

    // FAQ accordion functionality
    document.querySelectorAll('.faq-question').forEach(question => {
        question.addEventListener('click', () => {
            const faqItem = question.parentElement;
            const isActive = faqItem.classList.contains('active');
            
            // Close all FAQ items
            document.querySelectorAll('.faq-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // If the clicked item wasn't active, open it
            if (!isActive) {
                faqItem.classList.add('active');
            }
        });
    });

    // Typing effect for demo comment
    if (document.querySelector('.demo-comment')) {
        const demoComment = document.querySelector('.demo-comment');
        const originalText = demoComment.textContent;
        demoComment.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < originalText.length) {
                demoComment.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, Math.random() * 50 + 20);
            }
        };
        
        ScrollTrigger.create({
            trigger: demoComment,
            start: 'top bottom-=200',
            onEnter: typeWriter
        });
    }

    // Persona switcher functionality
    const personaExamples = document.querySelectorAll('.persona-example');
    if (personaExamples.length > 0) {
        const personaButtons = document.querySelectorAll('.persona-button');
        
        personaButtons.forEach(button => {
            button.addEventListener('click', () => {
                const persona = button.getAttribute('data-persona');
                
                // Update active button
                personaButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Show corresponding example
                personaExamples.forEach(example => {
                    example.style.display = 'none';
                    if (example.getAttribute('data-persona') === persona) {
                        example.style.display = 'block';
                    }
                });
            });
        });
    }

    // Feature demo tabs
    const demoTabs = document.querySelectorAll('.demo-tab');
    if (demoTabs.length > 0) {
        const demoContents = document.querySelectorAll('.demo-content-item');
        
        demoTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const feature = tab.getAttribute('data-feature');
                
                // Update active tab
                demoTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show corresponding content
                demoContents.forEach(content => {
                    content.style.display = 'none';
                    if (content.getAttribute('data-feature') === feature) {
                        content.style.display = 'block';
                    }
                });
            });
        });
    }

    // Countdown timer for limited offer
    const countdownElement = document.getElementById('countdown-timer');
    if (countdownElement) {
        // Set the countdown date (24 hours from now)
        const countdownDate = new Date();
        countdownDate.setDate(countdownDate.getDate() + 1);
        
        const updateCountdown = () => {
            const now = new Date().getTime();
            const distance = countdownDate - now;
            
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            countdownElement.innerHTML = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (distance < 0) {
                clearInterval(countdownInterval);
                countdownElement.innerHTML = "EXPIRED";
            }
        };
        
        updateCountdown();
        const countdownInterval = setInterval(updateCountdown, 1000);
    }

    // Testimonial slider
    const testimonialSlider = document.querySelector('.testimonial-slider');
    if (testimonialSlider) {
        const testimonials = testimonialSlider.querySelectorAll('.testimonial');
        const totalTestimonials = testimonials.length;
        let currentTestimonial = 0;
        
        const showTestimonial = (index) => {
            testimonials.forEach((testimonial, i) => {
                testimonial.style.display = i === index ? 'block' : 'none';
                testimonial.style.opacity = i === index ? 1 : 0;
            });
        };
        
        const nextTestimonial = () => {
            currentTestimonial = (currentTestimonial + 1) % totalTestimonials;
            showTestimonial(currentTestimonial);
        };
        
        const prevTestimonial = () => {
            currentTestimonial = (currentTestimonial - 1 + totalTestimonials) % totalTestimonials;
            showTestimonial(currentTestimonial);
        };
        
        // Initialize slider
        showTestimonial(0);
        
        // Add navigation buttons
        const nextButton = document.querySelector('.testimonial-next');
        const prevButton = document.querySelector('.testimonial-prev');
        
        if (nextButton) nextButton.addEventListener('click', nextTestimonial);
        if (prevButton) prevButton.addEventListener('click', prevTestimonial);
        
        // Auto-advance every 5 seconds
        setInterval(nextTestimonial, 5000);
    }
});
