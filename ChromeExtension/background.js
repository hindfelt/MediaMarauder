chrome.action.onClicked.addListener((tab) => {
    if (tab.url) {
      const webhookUrl = "https://192.168.0.198:8080/svtdl-hook"; // Replace with your actual webhook URL
      
      fetch(webhookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: tab.url })
      })
        .then((response) => console.log("Webhook called successfully:", response))
        .catch((error) => console.error("Error calling webhook:", error));
    }
  });
  