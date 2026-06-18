/* June's Place — small, dependency-free interactions */
(function () {
  "use strict";

  /* ---- sticky nav shadow on scroll ---- */
  var nav = document.getElementById("nav");
  var onScroll = function () {
    if (window.scrollY > 8) nav.classList.add("is-scrolled");
    else nav.classList.remove("is-scrolled");
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---- mobile drawer ---- */
  var toggle = document.getElementById("navToggle");
  var drawer = document.getElementById("navDrawer");

  function setDrawer(open) {
    drawer.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    toggle.innerHTML = open
      ? '<svg viewBox="0 0 24 24" width="24" height="24"><use href="#ico-close"/></svg>'
      : '<svg viewBox="0 0 24 24" width="24" height="24"><use href="#ico-menu"/></svg>';
  }

  toggle.addEventListener("click", function () {
    setDrawer(drawer.hidden);
  });

  // close drawer when a link is tapped
  drawer.addEventListener("click", function (e) {
    if (e.target.closest("a")) setDrawer(false);
  });

  // close on resize to desktop
  window.addEventListener("resize", function () {
    if (window.innerWidth >= 1000) setDrawer(false);
  });

  /* ---- scroll reveal ---- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry, i) {
          if (entry.isIntersecting) {
            // gentle stagger for siblings entering together
            entry.target.style.transitionDelay = Math.min(i * 60, 240) + "ms";
            entry.target.classList.add("is-in");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }
})();
