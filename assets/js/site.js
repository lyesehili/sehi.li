"use strict";

// Native <details> keeps navigation usable without JavaScript.
const moreMenu = document.querySelector(".more-menu");
if (moreMenu) {
  document.addEventListener("click", (event) => {
    if (!moreMenu.contains(event.target)) moreMenu.open = false;
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && moreMenu.open) {
      moreMenu.open = false;
      moreMenu.querySelector("summary").focus();
    }
  });
  moreMenu.addEventListener("focusout", (event) => {
    if (!moreMenu.contains(event.relatedTarget)) moreMenu.open = false;
  });
}

// External players load only after a click. Without JS, links open YouTube.
document.querySelectorAll("a[data-youtube]").forEach((link) => {
  const id = link.dataset.youtube;
  if (!/^[a-zA-Z0-9_-]{11}$/.test(id)) return;
  link.addEventListener("click", (event) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    const frame = document.createElement("iframe");
    frame.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
    frame.title = link.getAttribute("aria-label") || "Gaming clip";
    frame.className = "video-frame";
    frame.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen";
    frame.allowFullscreen = true;
    frame.referrerPolicy = "strict-origin-when-cross-origin";
    frame.tabIndex = 0;
    const external = document.createElement("a");
    external.href = link.href;
    external.className = "clip-external";
    external.textContent = "Watch on YouTube";
    link.replaceWith(frame, external);
    frame.focus();
  });
});
