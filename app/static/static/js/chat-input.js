document.addEventListener("DOMContentLoaded", function() {
    const textarea = document.getElementById("chat-textarea");
    const form = document.getElementById("chat-form");
    const sendButton = document.getElementById("send-button");
    const chatBox = document.getElementById("chat-box");

    // Resize textarea dynamically
    textarea.addEventListener("input", function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Prevent form submission on Enter key, but allow line breaks
    textarea.addEventListener("keydown", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
        }
    });

    // Form submission
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        
        // Display the user's answer immediately
        const userAnswer = textarea.value;
        displayMessage(userAnswer, 'user');

        // Disable the send button
        disableSendButton();

        // Submit the form using fetch to prevent full page reload
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData
        }).then(response => {
            if (response.ok) {
                // Wait for the next question and enable the send button
                return response.text();
            } else {
                throw new Error("Failed to send message.");
            }
        }).then(html => {
            // Parse the response HTML and extract the new question
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newQuestionElement = doc.querySelector("#chat-box .message.assistant:last-child p");

            if (newQuestionElement) {
                const newQuestion = newQuestionElement.textContent;
                // Display the assistant's response
                displayMessage(newQuestion, 'assistant');
                
                // Clear the textarea and re-enable the send button
                textarea.value = '';
                textarea.style.height = 'auto';
                enableSendButton();
            } else {
                console.error("No new question received.");
                enableSendButton();
            }
        }).catch(error => {
            console.error("Failed to send message:", error);
            enableSendButton();
        });
    });

    function displayMessage(message, role) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", role);
        messageElement.innerHTML = `<p>${message}</p>`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
    }

    function disableSendButton() {
        sendButton.disabled = true;
        sendButton.style.backgroundColor = "#a0a0a0";
    }

    function enableSendButton() {
        sendButton.disabled = false;
        sendButton.style.backgroundColor = "#03005b";
    }
});
