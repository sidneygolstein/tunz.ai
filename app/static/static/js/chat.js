document.addEventListener("DOMContentLoaded", function() {
    const timerElement = document.getElementById('timer');
    const finishUrl = timerElement.getAttribute('data-finish-url');
    const sessionId = timerElement.getAttribute('data-session-id'); // Get session ID
    let sessionFinished = timerElement.getAttribute('data-finished') === 'true'; // Check if the session is finished

    // Retrieve the initial duration and remaining time
    let initialDuration = parseInt(timerElement.getAttribute('data-duration'), 10); // Initial duration in seconds
    let timerDuration = localStorage.getItem('remainingTime_' + sessionId);
    
    if (!timerDuration) {
        timerDuration = initialDuration; // Set to initial duration if no stored time
    } else {
        timerDuration = parseInt(timerDuration, 10);
    }

    // Set warning flags
    let warningShown = sessionStorage.getItem('warningShown') === 'true'; // Retrieve from sessionStorage
    let warningClosed = sessionStorage.getItem('warningClosed') === 'true'; // Retrieve from sessionStorage

    function updateTimer() {
        if (sessionFinished) {
            clearInterval(timerInterval);
            localStorage.removeItem('remainingTime_' + sessionId); // Clear storage on finish
            return;
        }
        let minutes = Math.floor(timerDuration / 60);
        let seconds = timerDuration % 60;
        timerElement.innerHTML = `Time Left: ${minutes}:${seconds < 10 ? '0' + seconds : seconds}`;

        if (timerDuration <= 30 && !warningShown && !warningClosed) {
            showWarningPopup();
            warningShown = true; // Set the warning as shown
            sessionStorage.setItem('warningShown', 'true'); // Store in sessionStorage
        }

        if (timerDuration <= 0) {
            clearInterval(timerInterval);
            // Redirect to finish chat screen
            window.location.href = finishUrl;
        } else {
            timerDuration -= 1; // Decrease by 1 second
            // Save remaining time to localStorage
            localStorage.setItem('remainingTime_' + sessionId, timerDuration);
        }
    }

    function showWarningPopup() {
        if (document.getElementById('warning-popup')) {
            return; // If the popup already exists, do nothing
        }

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
            sessionStorage.setItem('warningClosed', 'true'); // Store in sessionStorage
            document.body.removeChild(popup);
        });
    }

    const timerInterval = setInterval(updateTimer, 1000); // Update every second
    updateTimer();

    // Attach the remaining time to the form submission and disable the submit button
    const chatForm = document.getElementById('chat-form');
    const sendButton = document.getElementById('send-button');
    if (chatForm) {
        chatForm.addEventListener('submit', function() {
            sendButton.disabled = true; // Disable send button on form submission
            const remainingTimeInput = document.createElement('input');
            remainingTimeInput.type = 'hidden';
            remainingTimeInput.name = 'remaining_time';
            remainingTimeInput.value = timerDuration;
            chatForm.appendChild(remainingTimeInput);
        });
    }
});
