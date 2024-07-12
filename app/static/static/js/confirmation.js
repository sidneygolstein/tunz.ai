document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('confirmation-modal');
    const confirmYes = document.getElementById('confirm-yes');
    const confirmNo = document.getElementById('confirm-no');
    const confirmationMessage = document.getElementById('confirmation-message');
    let formToSubmit = null;

    document.querySelectorAll('button[data-action]').forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();
            formToSubmit = button.closest('form');
            const actionType = button.getAttribute('data-action');
            
            if (actionType === 'delete') {
                confirmationMessage.textContent = 'Are you sure you want to delete this HR?';
            } 
            else if (actionType === 'accept-HR') {
                confirmationMessage.textContent = 'Are you sure you want to accept this HR?';
            } else if (actionType === 'deny-HR') {
                confirmationMessage.textContent = 'Are you sure you want to deny this HR?';
            } else if (actionType === 'create-itw') {
                confirmationMessage.textContent = 'Are you sure you want to create this interview?';
            } else {
                confirmationMessage.textContent = 'Are you sure you want to perform this action?';
            }
            
            modal.style.display = 'block';
        });
    });

    confirmYes.addEventListener('click', () => {
        if (formToSubmit) {
            formToSubmit.submit();
        }
        modal.style.display = 'none';
    });

    confirmNo.addEventListener('click', () => {
        modal.style.display = 'none';
    });
});
