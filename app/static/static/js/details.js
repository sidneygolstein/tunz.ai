document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.details-button').forEach(button => {
        button.addEventListener('click', function() {
            const sessionId = this.getAttribute('data-session-id');
            const detailsRow = document.getElementById('details-' + sessionId);
            if (detailsRow.style.display === 'none' || detailsRow.style.display === '') {
                detailsRow.style.display = 'table-row';
            } else {
                detailsRow.style.display = 'none';
            }
        });
    });
});
