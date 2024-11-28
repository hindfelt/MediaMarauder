document.addEventListener('DOMContentLoaded', function () {
    const serverUrlInput = document.getElementById('serverUrl');
    const saveServerUrlButton = document.getElementById('saveServerUrlButton');
    const sendUrlButton = document.getElementById('sendUrlButton');
    const statusDiv = document.getElementById('status');

    // Load the saved server URL on popup load
    chrome.storage.local.get(['serverUrl'], function (result) {
        if (result.serverUrl) {
            serverUrlInput.value = result.serverUrl;
            sendUrlButton.disabled = false; // Enable the Send URL button
        }
    });

    // Save the entered server URL when clicking the "Save Server URL" button
    saveServerUrlButton.addEventListener('click', function () {
        console.log('saveServerUrlButton clicked');
        const serverUrl = serverUrlInput.value.trim();
        if (serverUrl) {
            chrome.storage.local.set({ serverUrl: serverUrl }, function () {
                statusDiv.textContent = 'Server URL saved successfully!';
                statusDiv.style.display = 'block';
                statusDiv.className = 'success';
                sendUrlButton.disabled = false; // Enable Send URL button

                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 3000);
            });
        } else {
            statusDiv.textContent = 'Please enter a valid server URL.';
            statusDiv.style.display = 'block';
            statusDiv.className = 'error';

            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
    });

    // Send the current tab's URL to the saved server URL
    sendUrlButton.addEventListener('click', function () {
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            const currentUrl = tabs[0].url;

            chrome.storage.local.get(['serverUrl'], function (result) {
                const serverUrl = result.serverUrl;
                if (!serverUrl) {
                    statusDiv.textContent = 'Please save the server URL first.';
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'error';
                    return;
                }

                fetch(`${serverUrl}/svtdl-hook`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: currentUrl }),
                })
                    .then((response) => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        statusDiv.textContent = 'URL sent successfully!';
                        statusDiv.style.display = 'block';
                        statusDiv.className = 'success';

                        setTimeout(() => {
                            window.close();
                        }, 3000);
                    })
                    .catch((error) => {
                        statusDiv.textContent = `Error sending URL: ${error.message}`;
                        statusDiv.style.display = 'block';
                        statusDiv.className = 'error';

                        setTimeout(() => {
                            statusDiv.style.display = 'none';
                        }, 3000);
                    });
            });
        });
    });
});
