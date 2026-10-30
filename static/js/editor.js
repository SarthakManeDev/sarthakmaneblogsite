// "Insert image" button for the blog editor: uploads the picked image and
// inserts a Markdown image tag at the cursor.
(function () {
  const button = document.querySelector("[data-insert-image]");
  const input = document.querySelector("[data-image-input]");
  const textarea = document.querySelector("textarea[name='body']");
  if (!button || !input || !textarea) return;

  const csrf = document.querySelector("input[name='csrfmiddlewaretoken']").value;

  function insertAtCursor(text) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    textarea.value = textarea.value.slice(0, start) + text + textarea.value.slice(end);
    textarea.selectionStart = textarea.selectionEnd = start + text.length;
    textarea.focus();
  }

  button.addEventListener("click", () => input.click());

  input.addEventListener("change", async () => {
    const file = input.files[0];
    if (!file) return;
    const label = button.textContent;
    button.disabled = true;
    button.textContent = "Uploading…";
    try {
      const body = new FormData();
      body.append("image", file);
      const response = await fetch(button.dataset.uploadUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrf },
        body,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Upload failed");
      const alt = file.name.replace(/\.[^.]+$/, "").replace(/[-_]/g, " ");
      insertAtCursor(`\n\n![${alt}](${data.url})\n\n`);
    } catch (err) {
      alert(err.message);
    } finally {
      button.disabled = false;
      button.textContent = label;
      input.value = "";
    }
  });
})();
