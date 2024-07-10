document.addEventListener("DOMContentLoaded", function() {
    const notification = document.getElementById('notification');
    if (notification) {
        setTimeout(() => {
            notification.style.transition = "opacity 0.5s ease-out";
            notification.style.opacity = "0";
            setTimeout(() => {
                notification.style.display = "none";
                // Optionally, redirect after notification disappears
                window.location.href = notification.getAttribute('data-redirect');
            }, 500); // match this to the transition duration
        }, 2000); // Show message for 2 seconds before fading out
    }
});
