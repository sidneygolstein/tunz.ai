document.getElementById('logout').addEventListener('click', function() {
    fetch('/auth/logout', {
        method: 'POST'
    }).then(() => {
        window.location.href = '/auth/admin_login';
    });
});