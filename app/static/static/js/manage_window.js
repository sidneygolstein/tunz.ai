(function() {
    // Mark the current window's URL as open in localStorage
    function markCurrentWindowAsOpen() {
        localStorage.setItem(window.location.href, 'open');
    }

    // Check if the current window's URL is already open
    function isCurrentWindowURLAlreadyOpen() {
        return localStorage.getItem(window.location.href) === 'open';
    }

    // Focus the current window if the URL is already open
    function focusCurrentWindowIfAlreadyOpen() {
        if (isCurrentWindowURLAlreadyOpen()) {
            window.focus();
            return true;
        }
        return false;
    }

    // Mark the current window's URL as open
    markCurrentWindowAsOpen();

    // Check and focus the window if the URL is already open
    focusCurrentWindowIfAlreadyOpen();
})();
