document.addEventListener("DOMContentLoaded", function() {
    const confirmationModal = document.getElementById("confirmation-modal");
    const confirmationMessage = document.getElementById("confirmation-message");
    const confirmYesButton = document.getElementById("confirm-yes");
    const confirmNoButton = document.getElementById("confirm-no");

    document.querySelectorAll('[data-action-url]').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const actionUrl = button.getAttribute('data-action-url');
            confirmationMessage.textContent = "Are you sure you want to perform this action?";
            confirmationModal.style.display = "block";

            confirmYesButton.onclick = function() {
                const form = button.closest('form');
                if (form) {
                    form.action = actionUrl;
                    form.submit();
                } else {
                    window.location.href = actionUrl;
                }
            };

            confirmNoButton.onclick = function() {
                confirmationModal.style.display = "none";
            };
        });
    });
});
