document.addEventListener("DOMContentLoaded", function() {
    const flashMessages = document.querySelectorAll('.flashes .flash-success, .flashes .flash-danger');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.display = 'none';
        }, 1000);  // Display for 1 second (1000 milliseconds)
    });
});
