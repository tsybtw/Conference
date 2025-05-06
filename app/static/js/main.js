document.addEventListener('DOMContentLoaded', function() {

    setActiveNavItem();
    initFormValidation();

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