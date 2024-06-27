document.addEventListener("DOMContentLoaded", function() {
    let timerDuration = parseInt(document.getElementById('timer').getAttribute('data-duration'), 10); // Time left in seconds
    const timerElement = document.getElementById('timer');
    let warningShown = localStorage.getItem('warningShown') === 'true'; // Retrieve from localStorage
    let warningClosed = localStorage.getItem('warningClosed') === 'true'; // Retrieve from localStorage
    let sessionFinished = timerElement.getAttribute('data-finished') === 'true'; // Check if the session is finished

    function updateTimer() {
        if (sessionFinished) {
            clearInterval(timerInterval);
            return;
        }
        let minutes = Math.floor(timerDuration / 60);
        let seconds = timerDuration % 60;
        timerElement.innerHTML = `Time Left: ${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;

        if (timerDuration <= 30 && !warningShown && !warningClosed) {
            showWarningPopup();
            warningShown = true; // Set the warning as shown
            localStorage.setItem('warningShown', 'true'); // Store in localStorage
        }

        if (timerDuration <= 0) {
            clearInterval(timerInterval);
            // Redirect to finish chat screen
            window.location.href = timerElement.getAttribute('data-finish-url');
        } else {
            timerDuration -= 5; // Decrease by 1 second
        }
    }

    function showWarningPopup() {
        const popup = document.createElement('div');
        popup.id = 'warning-popup';
        popup.classList.add('popup');
        popup.innerHTML = `
            <div class="popup-content">
                <p>You have 30 seconds left to finish your answer.</p>
                <button id="close-popup">Close</button>
            </div>
        `;
        document.body.appendChild(popup);

        const closeButton = document.getElementById('close-popup');
        closeButton.addEventListener('click', function() {
            warningClosed = true; // Set the warning as closed
            localStorage.setItem('warningClosed', 'true'); // Store in localStorage
            document.body.removeChild(popup);
            

        });
    }

    const timerInterval = setInterval(updateTimer, 5000); // Update every second
    updateTimer();

    // Attach the remaining time to the form submission
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function() {
            const remainingTimeInput = document.createElement('input');
            remainingTimeInput.type = 'hidden';
            remainingTimeInput.name = 'remaining_time';
            remainingTimeInput.value = timerDuration;
            chatForm.appendChild(remainingTimeInput);
        });
    }
});