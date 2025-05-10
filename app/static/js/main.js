document.addEventListener('DOMContentLoaded', function() {

    setActiveNavItem();
    initFormValidation();
    initPasswordToggles();
    initPasswordStrengthChecker();

});

function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
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
                
                // Show error messages for invalid fields
                showFormErrors(form);
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
                
                // Update password strength indicators
                if (document.querySelector('.password-requirements')) {
                    updatePasswordRequirements(passwordField.value);
                }
            });
        }
    });
}

function initPasswordStrengthChecker() {
    const passwordFields = document.querySelectorAll('#password');
    
    passwordFields.forEach(function(passwordField) {
        // Add the password checker if it's a registration, password reset, or profile form
        const isRelevantForm = passwordField.closest('form') && 
            (window.location.pathname.includes('register') || 
             window.location.pathname.includes('reset-password') ||
             window.location.pathname.includes('profile'));
        
        if (isRelevantForm) {
            const formText = passwordField.parentElement.nextElementSibling;
            
            if (formText && formText.classList.contains('form-text')) {
                // Create requirements div
                const requirementsDiv = document.createElement('div');
                requirementsDiv.className = 'password-requirements mt-2';
                
                // For profile page, keep the "leave blank" message and add requirements
                if (window.location.pathname.includes('profile')) {
                    const leaveBlankText = formText.innerHTML;
                    requirementsDiv.innerHTML = `
                        ${leaveBlankText}
                        <div class="password-reqs-container" style="display: none;">
                            <p class="mb-1 mt-2 text-muted"><small>Password must meet the following requirements:</small></p>
                            <ul class="ps-3 mb-0">
                                <li class="requirement length-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least 8 characters long</small></li>
                                <li class="requirement uppercase-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least one uppercase letter</small></li>
                                <li class="requirement digit-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least one number</small></li>
                                <li class="requirement special-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least one special character</small></li>
                            </ul>
                        </div>
                    `;
                    
                    // Replace the form text with our new div
                    formText.parentNode.replaceChild(requirementsDiv, formText);
                    
                    // Ensure the requirements are hidden on page load
                    setTimeout(function() {
                        const reqContainer = document.querySelector('.password-reqs-container');
                        if (reqContainer && !passwordField.value) {
                            reqContainer.style.display = 'none';
                        }
                    }, 0);
                } else {
                    // Standard requirements for register and reset-password
                    requirementsDiv.innerHTML = `
                        <p class="mb-1 text-muted"><small>Password must meet the following requirements:</small></p>
                        <ul class="ps-3 mb-0">
                            <li class="requirement length-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least 8 characters long</small></li>
                            <li class="requirement uppercase-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least one uppercase letter</small></li>
                            <li class="requirement digit-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least one number</small></li>
                            <li class="requirement special-requirement"><small><i class="bi bi-x-circle text-danger"></i> At least one special character</small></li>
                        </ul>
                    `;
                    
                    // Replace the form text with our new div
                    formText.parentNode.replaceChild(requirementsDiv, formText);
                }
                
                // Initial update - only check if there's a value
                if (passwordField.value) {
                    updatePasswordRequirements(passwordField.value);
                    // Show requirements container on profile page if there's a value
                    if (window.location.pathname.includes('profile')) {
                        const reqContainer = document.querySelector('.password-reqs-container');
                        if (reqContainer) reqContainer.style.display = 'block';
                    }
                }
                
                // For profile page, show/hide requirements based on if field has value
                if (window.location.pathname.includes('profile')) {
                    passwordField.addEventListener('input', function() {
                        const reqContainer = document.querySelector('.password-reqs-container');
                        if (reqContainer) {
                            if (this.value) {
                                reqContainer.style.display = 'block';
                                updatePasswordRequirements(this.value);
                            } else {
                                reqContainer.style.display = 'none';
                            }
                        }
                    });
                    
                    // Double check that requirements are hidden on page load
                    if (!passwordField.value) {
                        const reqContainer = document.querySelector('.password-reqs-container');
                        if (reqContainer) reqContainer.style.display = 'none';
                    }
                }
                
                const confirmPasswordField = document.querySelector('#password_confirm');
                if (confirmPasswordField) {
                    // Add event listeners to check if passwords match
                    confirmPasswordField.addEventListener('input', function() {
                        checkPasswordsMatch(passwordField.value, confirmPasswordField.value);
                    });
                    
                    passwordField.addEventListener('input', function() {
                        if (confirmPasswordField.value !== '') {
                            checkPasswordsMatch(passwordField.value, confirmPasswordField.value);
                        }
                    });
                }
            }
        }
    });
}

function updatePasswordRequirements(password) {
    const lengthReq = document.querySelector('.length-requirement');
    const uppercaseReq = document.querySelector('.uppercase-requirement');
    const digitReq = document.querySelector('.digit-requirement');
    const specialReq = document.querySelector('.special-requirement');
    
    // Check length
    if (password.length >= 8) {
        updateRequirementStatus(lengthReq, true);
    } else {
        updateRequirementStatus(lengthReq, false);
    }
    
    // Check uppercase
    if (/[A-Z]/.test(password)) {
        updateRequirementStatus(uppercaseReq, true);
    } else {
        updateRequirementStatus(uppercaseReq, false);
    }
    
    // Check digit
    if (/[0-9]/.test(password)) {
        updateRequirementStatus(digitReq, true);
    } else {
        updateRequirementStatus(digitReq, false);
    }
    
    // Check special character
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        updateRequirementStatus(specialReq, true);
    } else {
        updateRequirementStatus(specialReq, false);
    }
}

function checkPasswordsMatch(password, confirmPassword) {
    const confirmPasswordField = document.querySelector('#password_confirm');
    if (!confirmPasswordField) return;
    
    if (password === confirmPassword && password !== '') {
        confirmPasswordField.setCustomValidity('');
        
        // Remove any existing mismatch error message
        const existingErrorDiv = confirmPasswordField.parentElement.nextElementSibling;
        if (existingErrorDiv && existingErrorDiv.classList.contains('password-mismatch-error')) {
            existingErrorDiv.remove();
        }
    } else {
        confirmPasswordField.setCustomValidity('Passwords do not match');
        
        // Add mismatch error message if it doesn't exist
        let errorDiv = confirmPasswordField.parentElement.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('password-mismatch-error')) {
            // Remove any existing error div first
            if (errorDiv && errorDiv.classList.contains('password-mismatch-error')) {
                errorDiv.remove();
            }
            
            // Create new error div
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback d-block password-mismatch-error';
            errorDiv.innerHTML = '<i class="bi bi-x-circle text-danger me-1"></i> Passwords do not match';
            
            // Insert after the input group
            confirmPasswordField.parentElement.insertAdjacentElement('afterend', errorDiv);
        }
    }
}

function updateRequirementStatus(element, isValid) {
    if (!element) return;
    
    const icon = element.querySelector('i');
    if (isValid) {
        icon.classList.remove('bi-x-circle', 'text-danger');
        icon.classList.add('bi-check-circle', 'text-success');
        element.classList.add('text-success');
        element.classList.remove('text-danger');
    } else {
        icon.classList.remove('bi-check-circle', 'text-success');
        icon.classList.add('bi-x-circle', 'text-danger');
        element.classList.add('text-danger');
        element.classList.remove('text-success');
    }
}

// Function to display form errors in a more visible way
function showFormErrors(form) {
    const invalidInputs = form.querySelectorAll(':invalid');
    const errorMessages = [];
    
    invalidInputs.forEach(function(input) {
        const label = form.querySelector(`label[for="${input.id}"]`);
        let fieldName = label ? label.textContent : input.name;
        let errorMessage = '';
        
        // Get custom validation message if exists
        if (input.validationMessage) {
            errorMessage = `${fieldName}: ${input.validationMessage}`;
        } else {
            errorMessage = `${fieldName} is required`;
        }
        
        // Check for server-side error messages
        const feedbackEl = input.parentElement.nextElementSibling;
        if (feedbackEl && feedbackEl.classList.contains('invalid-feedback')) {
            errorMessage = `${fieldName}: ${feedbackEl.textContent}`;
        }
        
        errorMessages.push(errorMessage);
    });
    
    // Check for any existing form-level errors
    const formErrors = form.querySelectorAll('.invalid-feedback');
    formErrors.forEach(function(errorEl) {
        if (errorEl.previousElementSibling && !errorEl.previousElementSibling.querySelector(':invalid')) {
            errorMessages.push(errorEl.textContent);
        }
    });
    
    if (errorMessages.length > 0) {
        showErrorAlert(errorMessages);
    }
}

function showErrorAlert(messages) {
    // Remove any existing error alerts
    const existingAlerts = document.querySelectorAll('.error-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create error alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show error-alert';
    alertDiv.setAttribute('role', 'alert');
    
    let alertContent = '<div class="d-flex justify-content-between align-items-start">';
    alertContent += '<div class="me-4"><strong><i class="bi bi-exclamation-triangle-fill me-2"></i>Please correct the following errors:</strong>';
    alertContent += '<ul class="mb-0 mt-2">';
    messages.forEach(message => {
        alertContent += `<li>${message}</li>`;
    });
    alertContent += '</ul></div>';
    alertContent += '<button type="button" class="btn-close ms-3" data-bs-dismiss="alert" aria-label="Close"></button>';
    alertContent += '</div>';
    
    alertDiv.innerHTML = alertContent;
    
    // Insert at the top of the form or page
    const formCard = document.querySelector('.card-body');
    if (formCard) {
        formCard.insertBefore(alertDiv, formCard.firstChild);
    } else {
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        } else {
            document.body.insertBefore(alertDiv, document.body.firstChild);
        }
    }
    
    // Scroll to the alert
    alertDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.password-toggle');
    
    toggleButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const passwordInput = button.previousElementSibling;
            const icon = button.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            }
        });
    });
}