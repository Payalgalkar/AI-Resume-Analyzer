// ============================
// LOADER
// ============================

function showLoader() {

    const loader = document.getElementById("loader");

    if (loader) {
        loader.style.display = "block";
    }
}


// ============================
// COPY REPORT
// ============================

function copyText() {

    const report = document.getElementById("analysisText");

    if (!report) {
        alert("No report found.");
        return;
    }

    navigator.clipboard.writeText(report.innerText)
        .then(() => {
            alert("Report copied successfully!");
        })
        .catch(() => {
            alert("Unable to copy report.");
        });
}


// ============================
// DOWNLOAD REPORT
// ============================

function downloadReport() {

    const report = document.getElementById("analysisText");

    if (!report) {
        alert("No report available.");
        return;
    }

    const blob = new Blob(
        [report.innerText],
        {
            type: "text/plain"
        }
    );

    const link = document.createElement("a");

    link.href = URL.createObjectURL(blob);

    link.download = "ATS_Report.txt";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
}


// ============================
// CHART.JS
// ============================

document.addEventListener("DOMContentLoaded", () => {

    const chartCanvas = document.getElementById("myChart");

    if (chartCanvas && typeof Chart !== "undefined") {

        new Chart(chartCanvas, {

            type: "doughnut",

            data: {

                labels: [
                    "Matched Skills",
                    "Missing Skills",
                    "Formatting"
                ],

                datasets: [{
                    data: [70, 20, 10],

                    backgroundColor: [
                        "#38bdf8",
                        "#ef4444",
                        "#22c55e"
                    ],

                    borderWidth: 0
                }]
            },

            options: {

                responsive: true,

                plugins: {

                    legend: {
                        labels: {
                            color: "#ffffff"
                        }
                    }
                }
            }
        });
    }
});


// ============================
// CHATBOT
// ============================

async function sendMessage() {

    const input = document.getElementById("userInput");

    const chat = document.getElementById("chatMessages");

    if (!input || !chat) return;

    const message = input.value.trim();

    if (message === "") return;

    // USER MESSAGE

    const userDiv = document.createElement("div");

    userDiv.className = "user-message";

    userDiv.innerHTML = `
        <div class="message-content">
            ${message}
        </div>
    `;

    chat.appendChild(userDiv);

    input.value = "";

    // TYPING MESSAGE

    const typingDiv = document.createElement("div");

    typingDiv.className = "ai-message";

    typingDiv.id = "typing";

    typingDiv.innerHTML = `
        <div class="message-content">
            Gemini AI is typing...
        </div>
    `;

    chat.appendChild(typingDiv);

    chat.scrollTop = chat.scrollHeight;

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        const typing = document.getElementById("typing");

        if (typing) {
            typing.remove();
        }

        const aiDiv = document.createElement("div");

        aiDiv.className = "ai-message";

        aiDiv.innerHTML = `
            <div class="message-content">
                ${data.reply.replace(/\n/g, "<br>")}
            </div>
        `;

        chat.appendChild(aiDiv);

        chat.scrollTop = chat.scrollHeight;

    } catch (error) {

        console.error(error);

        const typing = document.getElementById("typing");

        if (typing) {
            typing.remove();
        }

        const errorDiv = document.createElement("div");

        errorDiv.className = "ai-message";

        errorDiv.innerHTML = `
            <div class="message-content">
                Unable to connect with Gemini AI.
            </div>
        `;

        chat.appendChild(errorDiv);
    }
}


// ============================
// ENTER KEY SUPPORT
// ============================

document.addEventListener("DOMContentLoaded", () => {

    const input = document.getElementById("userInput");

    if (input) {

        input.addEventListener("keypress", function(event) {

            if (event.key === "Enter") {

                event.preventDefault();

                sendMessage();
            }
        });
    }
});