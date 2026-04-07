/**
 * AICTE Activity & Points Management System
 * Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // Theme Toggle
    // ==========================================
    const themeToggleBtn = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;
    
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        htmlEl.setAttribute('data-theme', savedTheme);
    } else {
        const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
        if (prefersLight) {
            htmlEl.setAttribute('data-theme', 'light');
        }
    }
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlEl.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // ==========================================
    // Mobile Navigation
    // ==========================================
    const mobileToggle = document.getElementById('navMobileToggle');
    const navLinks = document.getElementById('navLinks');
    
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // ==========================================
    // Flash Messages Auto-dismiss
    // ==========================================
    const flashMessages = document.querySelectorAll('.flash-message[data-auto-dismiss]');
    
    flashMessages.forEach(msg => {
        const timeout = parseInt(msg.getAttribute('data-auto-dismiss'), 10) || 5000;
        
        setTimeout(() => {
            msg.classList.add('fading-out');
            setTimeout(() => {
                const parent = msg.parentElement;
                msg.remove();
                if (parent && parent.children.length === 0) {
                    parent.remove();
                }
            }, 300); // match CSS animation duration
        }, timeout);
    });

    // ==========================================
    // Password Toggle
    // ==========================================
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const input = toggle.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                toggle.textContent = '🙈';
            } else {
                input.type = 'password';
                toggle.textContent = '👁️';
            }
        });
    });

    // ==========================================
    // Signup Form Role Toggle
    // ==========================================
    const roleBtns = document.querySelectorAll('.role-btn');
    const roleInput = document.getElementById('roleInput');
    const studentFields = document.querySelector('.student-fields');
    const clubFields = document.querySelector('.club-fields');
    const labelFullName = document.getElementById('label_full_name');
    
    if (roleBtns.length > 0 && roleInput) {
        roleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active from all
                roleBtns.forEach(b => b.classList.remove('active'));
                
                // Add active to clicked
                btn.classList.add('active');
                
                // Update hidden input
                const role = btn.getAttribute('data-role');
                roleInput.value = role;
                
                // Toggle fields
                if (role === 'student') {
                    if (clubFields) clubFields.style.display = 'none';
                    if (studentFields) studentFields.style.display = 'contents';
                    if (labelFullName) labelFullName.textContent = 'Full Name';
                    
                    // Toggle required
                    document.getElementById('department').setAttribute('required', 'required');
                    document.getElementById('roll_number').setAttribute('required', 'required');
                    const cbName = document.getElementById('club_name');
                    if(cbName) cbName.removeAttribute('required');
                    
                } else if (role === 'club') {
                    if (studentFields) studentFields.style.display = 'none';
                    if (clubFields) clubFields.style.display = 'contents';
                    if (labelFullName) labelFullName.textContent = 'Organizer Name';
                    
                    // Toggle required
                    document.getElementById('department').removeAttribute('required');
                    document.getElementById('roll_number').removeAttribute('required');
                    const cbName = document.getElementById('club_name');
                    if(cbName) cbName.setAttribute('required', 'required');
                }
            });
        });
        
        // Trigger initial state based on hidden input
        const initialRole = roleInput.value;
        const initialBtn = document.querySelector(`.role-btn[data-role="${initialRole}"]`);
        if (initialBtn) initialBtn.click();
    }

    // ==========================================
    // Confirm Actions (Delete/Register)
    // ==========================================
    const confirmButtons = document.querySelectorAll('.confirm-action');
    
    confirmButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const message = btn.getAttribute('data-confirm') || 'Are you sure you want to perform this action?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // ==========================================
    // Set minimum date for event inputs to today
    // ==========================================
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs.length > 0) {
        const today = new Date().toISOString().split('T')[0];
        dateInputs.forEach(input => {
            if (!input.value) {
                // If it's a completely new form, set min to today
                input.setAttribute('min', today);
            }
        });
    }

});
