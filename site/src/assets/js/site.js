// wubba.studio: small, dependency-free behaviour.
// Every page works as plain HTML without it; this file adds the menu, the brief builder,
// form validation, copy-to-clipboard and the lazy video.

const reduce = matchMedia("(prefers-reduced-motion: reduce)");
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function cssMs(name, fallback) {
  const value = parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
  return Number.isFinite(value) ? value : fallback;
}

// Text swap from transitions.dev: old text exits up with a blur, new text enters from below.
function swapText(el, next) {
  if (!el || el.textContent === next) return;
  if (reduce.matches) {
    el.textContent = next;
    return;
  }
  const dur = cssMs("--text-swap-dur", 150);
  clearTimeout(el._swap);
  el.classList.add("is-exit");
  el._swap = setTimeout(() => {
    el.textContent = next;
    el.classList.remove("is-exit");
    el.classList.add("is-enter-start");
    void el.offsetHeight;
    el.classList.remove("is-enter-start");
  }, dur);
}

let liveRegion;
function announce(text) {
  if (!liveRegion) {
    liveRegion = document.createElement("p");
    liveRegion.className = "sr-only";
    liveRegion.setAttribute("aria-live", "polite");
    document.body.append(liveRegion);
  }
  liveRegion.textContent = "";
  requestAnimationFrame(() => (liveRegion.textContent = text));
}

// ------------------------------------------------------------------ top bar

function bar() {
  const el = $("[data-bar]");
  if (!el || !("IntersectionObserver" in window)) return;
  const sentinel = document.createElement("div");
  sentinel.setAttribute("aria-hidden", "true");
  sentinel.className = "bar-sentinel";
  document.body.prepend(sentinel);
  new IntersectionObserver(([entry]) => el.classList.toggle("is-stuck", !entry.isIntersecting)).observe(sentinel);
}

// ------------------------------------------------------------------ mobile menu

function menu() {
  const toggle = $("[data-menu-toggle]");
  const panel = $("[data-menu]");
  if (!toggle || !panel) return;
  const root = document.documentElement;
  const label = $(".sr-only", toggle);
  const behind = () => $$("main, footer");
  const focusables = () => [toggle, ...$$("a[href], button", panel)];

  function onKey(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      close();
      return;
    }
    if (event.key !== "Tab") return;
    const items = focusables();
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function open() {
    panel.inert = false;
    behind().forEach((el) => (el.inert = true));
    panel.classList.add("is-open");
    root.classList.add("menu-open");
    toggle.setAttribute("aria-expanded", "true");
    label.textContent = "Close menu";
    document.addEventListener("keydown", onKey);
    requestAnimationFrame(() => $("a[href]", panel)?.focus({ preventScroll: true }));
  }

  function close(restoreFocus = true) {
    if (toggle.getAttribute("aria-expanded") !== "true") return;
    panel.classList.remove("is-open");
    root.classList.remove("menu-open");
    panel.inert = true;
    behind().forEach((el) => (el.inert = false));
    toggle.setAttribute("aria-expanded", "false");
    label.textContent = "Menu";
    document.removeEventListener("keydown", onKey);
    if (restoreFocus) toggle.focus({ preventScroll: true });
  }

  toggle.addEventListener("click", () => (toggle.getAttribute("aria-expanded") === "true" ? close() : open()));
  panel.addEventListener("click", (event) => {
    if (event.target.closest("a[href]")) close(false);
  });
  matchMedia("(min-width: 881px)").addEventListener("change", (event) => {
    if (event.matches) close(false);
  });
}

// ------------------------------------------------------------------ brief builder

function builder() {
  const root = $("[data-builder]");
  if (!root) return;
  const line = $("[data-idea]", root);
  const slots = {
    product: $('[data-slot="product"]', line),
    place: $('[data-slot="place"]', line),
  };
  const picked = (name) => $(`input[name="${name}"]:checked`, root);

  function render() {
    swapText(slots.product, picked("product").dataset.phrase);
    swapText(slots.place, picked("place").dataset.phrase);
  }

  // /brief?product=keyboard&place=cockpit pre-selects an idea (handy for links in outreach emails)
  const params = new URLSearchParams(location.search);
  for (const name of ["product", "place"]) {
    const wanted = params.get(name);
    const input = wanted && $$(`input[name="${name}"]`, root).find((option) => option.value === wanted);
    if (input) {
      input.checked = true;
      slots[name].textContent = input.dataset.phrase;
    }
  }

  root.addEventListener("change", render);

  $("[data-shuffle]", root)?.addEventListener("click", () => {
    for (const name of ["product", "place"]) {
      const options = $$(`input[name="${name}"]`, root).filter((option) => !option.checked);
      options[Math.floor(Math.random() * options.length)].checked = true;
    }
    render();
  });

  const use = $("[data-use-idea]", root);
  use?.addEventListener("click", () => {
    const message = $("[data-message]");
    if (!message) return;
    const idea = `Idea: an AI streamer tests our ${picked("product").dataset.phrase} ${picked("place").dataset.phrase}.`;
    const rest = message.value.replace(/^Idea: .*(\r?\n)*/, "");
    const fresh = !rest.trim();
    message.value = `${idea}\n\n${fresh ? "Product link: \nGoal: \nTimeline: " : rest}`;
    message.dispatchEvent(new Event("input", { bubbles: true }));
    message.focus({ preventScroll: true });
    if (fresh) {
      const caret = message.value.indexOf("Product link: ") + "Product link: ".length;
      message.setSelectionRange(caret, caret);
    }
    message.closest("[data-field]")?.scrollIntoView({ behavior: reduce.matches ? "auto" : "smooth", block: "center" });
    announce("Idea added to your brief.");
  });
}

// ------------------------------------------------------------------ brief form

function form() {
  const el = $("[data-form]");
  if (!el) return;
  const email = $('input[name="email"]', el);
  const message = $("[data-message]", el);
  const count = $("[data-count]", el);
  const max = 4000;
  const number = new Intl.NumberFormat("en-US");
  const inbox = "contact@wubba.studio";

  const fieldOf = (input) => input.closest("[data-field]");
  const validEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);

  function updateCount() {
    const n = message.value.length;
    count.textContent = `${number.format(n)} / ${number.format(max)}`;
    count.classList.toggle("is-over", n > max);
  }

  function clearError(input) {
    const field = fieldOf(input);
    if (!field.classList.contains("is-error")) return;
    field.classList.remove("is-error");
    input.removeAttribute("aria-invalid");
  }

  // Error shake from transitions.dev. The message stays until the field is corrected.
  function showError(input, text) {
    const field = fieldOf(input);
    const box = $(".field__box", field);
    $("[data-error]", field).textContent = text;
    field.classList.add("is-error");
    input.setAttribute("aria-invalid", "true");
    if (reduce.matches) return;
    box.classList.remove("is-shaking");
    void box.offsetWidth;
    box.classList.add("is-shaking");
    const shake = cssMs("--shake-dur-a", 80) * 2 + cssMs("--shake-dur-b", 60) * 2;
    setTimeout(() => box.classList.remove("is-shaking"), shake + 20);
  }

  function done(title, text) {
    el.classList.remove("is-sending");
    $("[data-status-title]", el).textContent = title;
    $("[data-status-text]", el).textContent = text;
    el.classList.add("is-sent");
    $("[data-status]", el).focus({ preventScroll: true });
  }

  message.addEventListener("input", () => {
    updateCount();
    clearError(message);
  });
  email.addEventListener("input", () => clearError(email));
  updateCount();

  el.addEventListener("submit", async (event) => {
    event.preventDefault();
    const invalid = [];
    const address = email.value.trim();
    const text = message.value.trim();

    if (!validEmail(address)) {
      showError(email, address ? "That email address looks incomplete. Check it and try again." : "Enter an email address we can reply to.");
      invalid.push(email);
    }
    if (!text) {
      showError(message, "Tell us what you’re launching and what the campaign needs to do.");
      invalid.push(message);
    } else if (message.value.length > max) {
      showError(message, "Keep it under 4,000 characters. A link and a few lines are enough.");
      invalid.push(message);
    }
    if (invalid.length) {
      invalid[0].focus();
      return;
    }

    const endpoint = el.dataset.endpoint;
    if (endpoint) {
      el.classList.add("is-sending");
      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ email: address, message: text, page: location.pathname }),
        });
        if (!response.ok) throw new Error(String(response.status));
        done("Brief sent.", `We reply from ${inbox}.`);
      } catch {
        el.classList.remove("is-sending");
        showError(message, `The brief didn’t go through. Try again, or email it to ${inbox}.`);
      }
      return;
    }

    // No endpoint yet: hand the brief to the visitor's email app, already written.
    const subject = `Brief from ${address}`;
    const body = `${text}\n\nReply to: ${address}`;
    location.href = `mailto:${inbox}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    done("Your email app should open.", `The brief is already written in it. If nothing opened, send it to ${inbox}.`);
  });
}

// ------------------------------------------------------------------ copy the email address

function copy() {
  $$("[data-copy]").forEach((button) => {
    const label = $("[data-copy-label]", button);
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.copy);
        swapText(label, "Copied");
        announce("Email address copied.");
        clearTimeout(button._reset);
        button._reset = setTimeout(() => swapText(label, "Copy"), 1800);
      } catch {
        location.href = `mailto:${button.dataset.copy}`;
      }
    });
  });
}

// ------------------------------------------------------------------ the film, when the owner adds it

function reels() {
  $$("[data-reel] video[data-src]").forEach((video) => {
    if (reduce.matches) {
      video.controls = true;
      video.preload = "metadata";
      video.src = video.dataset.src;
      return;
    }
    new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          if (!video.getAttribute("src")) video.src = video.dataset.src;
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      },
      { threshold: 0.25 },
    ).observe(video);
  });
}

bar();
menu();
builder();
form();
copy();
reels();
