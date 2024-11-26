document.addEventListener('DOMContentLoaded', function() {
    // Get current tab URL and send it to webhook
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentUrl = tabs[0].url;
        
        fetch('https://0x4d.in/svtdl-hook', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: currentUrl })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            document.body.innerHTML = 'URL sent successfully: ' + currentUrl;
            console.log(currentUrl);
               // Close the popup after 3 seconds
            setTimeout(() => {
                window.close();
            }, 3000);
        })
        .catch(error => {
            document.body.innerHTML = 'Error sending URL: ' + error.message;
            setTimeout(() => {
                window.close();
            }, 3000);
        });
    });
});