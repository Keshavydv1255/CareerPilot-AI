document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("streamChatForm");
  const questionInput = document.getElementById("chatQuestion");
  const submitButton = document.getElementById(
    "askCareerPilotButton"
  );
  const responseCard = document.getElementById(
    "streamResponseCard"
  );
  const responseBox = document.getElementById(
    "streamResponse"
  );
  const statusBadge = document.getElementById(
    "streamStatus"
  );

  if (
    !form ||
    !questionInput ||
    !submitButton ||
    !responseCard ||
    !responseBox ||
    !statusBadge
  ) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (!question) {
      questionInput.focus();
      return;
    }

    responseCard.classList.remove("d-none");
    responseBox.textContent = "";

    statusBadge.textContent = "Generating...";
    statusBadge.className = "badge text-bg-primary";

    submitButton.disabled = true;
    submitButton.innerHTML = `
      <span
        class="spinner-border spinner-border-sm me-2"
        role="status">
      </span>
      CareerPilot is thinking...
    `;

    const formData = new FormData();
    formData.append("question", question);

    try {
      const response = await fetch("/chat/stream", {
        method: "POST",
        body: formData,
        headers: {
          Accept: "text/plain",
        },
      });

      if (!response.ok) {
        throw new Error(
          `Request failed with status ${response.status}`
        );
      }

      if (!response.body) {
        throw new Error("Streaming is not supported.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, {
          stream: true,
        });

        responseBox.textContent += chunk;

        window.scrollTo({
          top: document.body.scrollHeight,
          behavior: "smooth",
        });
      }

      responseBox.textContent += decoder.decode();

      statusBadge.textContent = "Complete";
      statusBadge.className = "badge text-bg-success";

    } catch (error) {
      console.error("Streaming error:", error);

      responseBox.textContent =
        "CareerPilot could not complete the streamed response. " +
        "Please try again.";

      statusBadge.textContent = "Failed";
      statusBadge.className = "badge text-bg-danger";

    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Ask CareerPilot";
    }
  });
});