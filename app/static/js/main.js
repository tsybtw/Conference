document.addEventListener('DOMContentLoaded', function() {

    setActiveNavItem();
    initFormValidation();
    initPasswordToggles();

    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const dismissBtn = new bootstrap.Alert(alert);
            dismissBtn.close();
        });
    }, 5000);
});

function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar .nav-link');
    
    navLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
        
        const passwordField = form.querySelector('#password');
        const confirmPasswordField = form.querySelector('#password_confirm');
        
        if (passwordField && confirmPasswordField) {
            confirmPasswordField.addEventListener('input', function() {
                if (passwordField.value !== confirmPasswordField.value) {
                    confirmPasswordField.setCustomValidity('Passwords do not match');
                } else {
                    confirmPasswordField.setCustomValidity('');
                }
            });
            
            passwordField.addEventListener('input', function() {
                if (confirmPasswordField.value !== '') {
                    if (passwordField.value !== confirmPasswordField.value) {
                        confirmPasswordField.setCustomValidity('Passwords do not match');
                    } else {
                        confirmPasswordField.setCustomValidity('');
                    }
                }
            });
        }
    });
}

function initPasswordToggles() {
    // Handle already existing toggle buttons
    const toggleButtons = document.querySelectorAll('.password-toggle');
    
    toggleButtons.forEach(function(btn) {
        const inputGroup = btn.closest('.input-group');
        const passwordField = inputGroup.querySelector('input[type="password"]');
        
        if (passwordField) {
            btn.addEventListener('click', function() {
                if (passwordField.type === 'password') {
                    passwordField.type = 'text';
                    btn.innerHTML = '<i class="bi bi-eye"></i>';
                } else {
                    passwordField.type = 'password';
                    btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
                }
            });
        }
    });
    
    // For backward compatibility - add buttons to any password fields that don't have them
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    passwordFields.forEach(function(field) {
        const inputGroup = field.closest('.input-group');
        
        if (inputGroup && !inputGroup.querySelector('.password-toggle')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'btn btn-outline-secondary password-toggle';
            toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
            toggleBtn.setAttribute('aria-label', 'Toggle password visibility');
            
            toggleBtn.addEventListener('click', function() {
                if (field.type === 'password') {
                    field.type = 'text';
                    toggleBtn.innerHTML = '<i class="bi bi-eye"></i>';
                } else {
                    field.type = 'password';
                    toggleBtn.innerHTML = '<i class="bi bi-eye-slash"></i>';
                }
            });
            
            inputGroup.appendChild(toggleBtn);
        }
    });
} 