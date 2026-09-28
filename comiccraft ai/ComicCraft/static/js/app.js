const form = document.getElementById("comic-form");
const button = document.getElementById("submit-btn");

if (form && button) {
  form.addEventListener("submit", () => {
    button.disabled = true;
    button.textContent = "Creating your comic…";
  });
}
