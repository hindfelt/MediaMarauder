document.getElementById("refresh").addEventListener("click", () => {
    fetch("https://192.168.0.198:8080/status") // Replace with your actual server URL
      .then((response) => response.json())
      .then((data) => {
        document.getElementById("status").innerText = JSON.stringify(data, null, 2);
      })
      .catch((error) => console.error("Error fetching status:", error));
  });
  