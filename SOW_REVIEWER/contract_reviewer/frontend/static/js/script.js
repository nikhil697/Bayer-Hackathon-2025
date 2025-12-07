// Toast message function
function showToast(message) {
  const toast = document.createElement("div");
  toast.innerText = message;
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.right = "20px";
  toast.style.background = "#007bff";
  toast.style.color = "#fff";
  toast.style.padding = "12px 18px";
  toast.style.borderRadius = "8px";
  toast.style.boxShadow = "0 4px 10px rgba(0,0,0,0.2)";
  toast.style.zIndex = 1000;

  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 2500);
}

// Auto-run toast if Django messages exist
document.addEventListener("DOMContentLoaded", () => {
  const msg = document.getElementById("django-message");
  if (msg) {
    showToast(msg.innerText);
  }
});
