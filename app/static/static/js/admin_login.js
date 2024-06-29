document.getElementById('admin-login-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const response = await fetch('/auth/admin_login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (response.ok) {
        alert('Login successful');
        window.location.href = `/admin/home?admin_id=${data.admin_id}`; // Corrected URL
    } else {
        alert(data.msg);
    }
});
