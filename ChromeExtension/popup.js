document.addEventListener('DOMContentLoaded', function () {
    const serverUrlInput = document.getElementById('serverUrl');
    const saveServerUrlButton = document.getElementById('saveServerUrlButton');
    const languageButtons = document.querySelectorAll('.language-button');
    const statusDiv = document.getElementById('status');
    const tokenInput = document.getElementById('token');
    const saveTokenButton = document.getElementById('saveTokenButton');

    // Debugging check for language buttons
    if (!languageButtons || languageButtons.length === 0) {
        console.error("No language buttons found in the DOM.");
        return;
    }

    // Load the saved server URL on popup load
    chrome.storage.local.get(['serverUrl'], function (result) {
        if (result.serverUrl) {
            serverUrlInput.value = result.serverUrl;
        }
    });

    // Load the saved token on popup load
    chrome.storage.local.get(['token'], function (result) {
        if (result.token) {
            tokenInput.value = result.token;
        }
    });

    // Save the entered server token when clicking the "Save Token" button
    saveTokenButton.addEventListener('click', function () {
        const tokenToSave = tokenInput.value.trim();
        if (tokenToSave) {
            chrome.storage.local.set({ token: tokenToSave }, function () {
                statusDiv.textContent = 'Token saved successfully!';
                statusDiv.style.display = 'block';
                statusDiv.className = 'success';

                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 3000);
            });
        } else {
            statusDiv.textContent = 'Please enter a valid server token.';
            statusDiv.style.display = 'block';
            statusDiv.className = 'error';

            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
    });

    // Save the entered server URL when clicking the "Save Server URL" button
    saveServerUrlButton.addEventListener('click', function () {
        const serverUrl = serverUrlInput.value.trim();
        if (serverUrl) {
            chrome.storage.local.set({ serverUrl: serverUrl }, function () {
                statusDiv.textContent = 'Server URL saved successfully!';
                statusDiv.style.display = 'block';
                statusDiv.className = 'success';

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

    // Add click handlers to all language buttons
    languageButtons.forEach((button) => {
        button.addEventListener('click', function () {
            console.log(`Attaching click listener to button with language: ${button.getAttribute('data-lang')}`);
            const language = button.getAttribute('data-lang');
            console.log(`Button clicked for language: ${language}`);

            chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                if (!tabs || tabs.length === 0) {
                    statusDiv.textContent = 'No active tab found.';
                    statusDiv.style.display = 'block';
                    statusDiv.className = 'error';
                    return;
                }

                const currentUrl = tabs[0].url;

                chrome.storage.local.get(['serverUrl'], function (result) {
                    const serverUrl = result.serverUrl;
                    if (!serverUrl) {
                        statusDiv.textContent = 'Please save the server URL first.';
                        statusDiv.style.display = 'block';
                        statusDiv.className = 'error';
                        return;
                    }
                    chrome.storage.local.get(['token'], function (result) {
                        const tokenIn = result.token;
                        if (!tokenIn) {
                            statusDiv.textContent = 'Please save the server token first.';
                            statusDiv.style.display = 'block';
                            statusDiv.className = 'error';
                            return;
                        }
                        console.log("ready to post  to webhook")
                        fetch(`${serverUrl}/svtdl-hook`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Auth': tokenIn,
                            },
                            body: JSON.stringify({
                                url: currentUrl,
                                subtitle_lang: language,
                            }),
                        })
                            .then((response) => {
                                if (!response.ok) {
                                    // Handle invalid token or other server errors
                                    if (response.status === 401) {
                                        throw new Error("Invalid or missing token");
                                    }
                                    throw new Error(`Server error: ${response.status}`);
                                }
                                return response.json();
                            })//response.json())
                            .then((data) => {
                                if (data.error) {
                                    throw new Error(data.error);
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
    });
});
