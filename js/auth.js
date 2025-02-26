document.addEventListener('DOMContentLoaded', function() {
    // Show alert function
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Register form handling
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                showAlert('Passwords do not match!', 'danger');
                return;
            }
            
            if (password.length < 6) {
                showAlert('Password must be at least 6 characters long!', 'danger');
                return;
            }

            // Store user data in localStorage (for demo purposes)
            const userData = {
                username,
                email,
                password // In a real app, never store passwords in localStorage
            };
            localStorage.setItem('userData', JSON.stringify(userData));
            showAlert('Registration successful! Please login.', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        });
    }

    // Login form handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Get stored user data (for demo purposes)
            const userData = JSON.parse(localStorage.getItem('userData'));
            
            if (userData && userData.email === email && userData.password === password) {
                showAlert('Login successful!', 'success');
                setTimeout(() => {
                    window.location.href = '../index.html';
                }, 2000);
            } else {
                showAlert('Invalid email or password!', 'danger');
            }
        });
    }
});
