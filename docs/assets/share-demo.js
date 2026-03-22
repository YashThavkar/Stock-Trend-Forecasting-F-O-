(function () {
  function init() {
    if (location.protocol !== "http:" && location.protocol !== "https:") return;
    const row = document.getElementById("demo-permalink");
    const input = document.getElementById("demo-permalink-url");
    const btn = document.getElementById("demo-permalink-copy");
    if (!row || !input || !btn) return;

    const baseUrl = new URL("./", location.href).href;
    input.value = baseUrl;
    row.hidden = false;

    btn.addEventListener("click", async () => {
      const text = input.value;
      try {
        await navigator.clipboard.writeText(text);
        const prev = btn.textContent;
        btn.textContent = "Copied";
        setTimeout(() => {
          btn.textContent = prev;
        }, 2000);
      } catch {
        input.focus();
        input.select();
        input.setSelectionRange(0, text.length);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
