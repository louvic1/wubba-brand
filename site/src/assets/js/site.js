// wubba.studio: small, dependency-free behaviour.
// Every page works as plain HTML without it; this file adds the menu, the brief builder,
// the brief form and its hand-off to email, the copy buttons and the film controls.

const reduce = matchMedia("(prefers-reduced-motion: reduce)");
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const INBOX = "contact@wubba.studio";

function cssValue(name, fallback) {
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
  const dur = cssValue("--text-swap-dur", 150);
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

// The brief draft lives in this tab only, so a reload or a page change doesn't lose it.
const draft = {
  get(key) {
    try {
      return sessionStorage.getItem(`wubba:${key}`) ?? "";
    } catch {
      return "";
    }
  },
  set(key, value) {
    try {
      if (value) sessionStorage.setItem(`wubba:${key}`, value);
      else sessionStorage.removeItem(`wubba:${key}`);
    } catch {
      // storage refused (private window, blocked site data): the form works without it
    }
  },
};

// Copies to the clipboard. Where the browser refuses, selects the text so it can be copied by hand.
async function copyText(text, fallback) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    if (fallback?.select) {
      fallback.focus();
      fallback.select();
    } else if (fallback) {
      const range = document.createRange();
      range.selectNodeContents(fallback);
      getSelection().removeAllRanges();
      getSelection().addRange(range);
    }
    return false;
  }
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

// One green action per screen: the bar's "Send a brief" steps aside while the page shows its own.
function primary() {
  const targets = $$("[data-primary]");
  if (!targets.length || !("IntersectionObserver" in window)) return;
  const inView = new Set();
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) inView.add(entry.target);
        else inView.delete(entry.target);
      }
      document.documentElement.classList.toggle("primary-in-view", inView.size > 0);
    },
    { rootMargin: `-${cssValue("--bar-h", 64)}px 0px 0px 0px` },
  );
  targets.forEach((target) => observer.observe(target));
}

// ------------------------------------------------------------------ mobile menu

function menu() {
  const toggle = $("[data-menu-toggle]");
  const panel = $("[data-menu]");
  if (!toggle || !panel) return;
  const root = document.documentElement;
  const label = $(".sr-only", toggle);
  // everything the open menu covers leaves the tab order and the accessibility tree
  const behind = () => $$(".skip, main, footer");

  function onKey(event) {
    if (event.key !== "Escape") return;
    event.preventDefault();
    close();
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

  // /brief?product=keyboard&place=cockpit pre-selects an idea (the closing bands and outreach emails use it)
  const params = new URLSearchParams(location.search);
  for (const name of ["product", "place"]) {
    const wanted = params.get(name);
    const input = wanted && $$(`input[name="${name}"]`, root).find((option) => option.value === wanted);
    if (input) {
      input.checked = true;
      slots[name].textContent = input.dataset.phrase;
    }
  }

  // the idea arrives written into an empty brief (the builder sits below the form on phones)
  const message = $("[data-message]");
  if (params.get("product") && params.get("place") && message && !message.value && !draft.get("brief")) {
    message.value = `Idea: an AI streamer tests our ${picked("product").dataset.phrase} ${picked("place").dataset.phrase}.\n\nProduct link: \nGoal: \nTimeline: `;
  }

  root.addEventListener("change", render);

  $("[data-shuffle]", root)?.addEventListener("click", () => {
    for (const name of ["product", "place"]) {
      const options = $$(`input[name="${name}"]`, root).filter((option) => !option.checked);
      options[Math.floor(Math.random() * options.length)].checked = true;
    }
    render();
  });

  $("[data-use-idea]", root)?.addEventListener("click", () => {
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
  const foot = $("[data-form-foot]", el);
  const submitLabel = $("[data-submit-label]", el);
  const status = $("[data-status]", el);
  const handoff = $("[data-handoff]", el);
  const ready = $("[data-handoff-body]", el);
  const gmail = $("[data-handoff-gmail]", el);
  const outlook = $("[data-handoff-outlook]", el);
  const mailto = $("[data-handoff-mailto]", el);
  const max = 4000;
  const mailtoMax = 1900; // encoded length: Outlook for Windows cuts mailto: links much past 2,000
  const subject = "Brief for Wubba";
  const number = new Intl.NumberFormat("en-US");

  const fieldOf = (input) => input.closest("[data-field]");
  const validEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);

  // Phones hand mailto: links to their mail app reliably; desktops more often live in webmail.
  if (matchMedia("(pointer: coarse)").matches) {
    mailto.classList.replace("btn--line", "btn--green");
    gmail.classList.replace("btn--green", "btn--line");
    gmail.before(mailto);
  }

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
    const shake = cssValue("--shake-dur-a", 80) * 2 + cssValue("--shake-dur-b", 60) * 2;
    setTimeout(() => box.classList.remove("is-shaking"), shake + 20);
  }

  let saving;
  function save() {
    clearTimeout(saving);
    saving = setTimeout(() => {
      draft.set("email", email.value.trim());
      draft.set("brief", message.value);
    }, 250);
  }

  // The longest mailto: body that stays under the limit once encoded, cut on a whole word.
  function mailtoBody(text, tail) {
    const enc = encodeURIComponent;
    const budget = mailtoMax - enc(subject).length - `mailto:${INBOX}?subject=&body=`.length;
    if (enc(text + tail).length <= budget) return { body: text + tail, long: false };
    let lo = 0;
    let hi = text.length;
    while (lo < hi) {
      const mid = Math.ceil((lo + hi) / 2);
      if (enc(`${text.slice(0, mid).trimEnd()} […]${tail}`).length <= budget) lo = mid;
      else hi = mid - 1;
    }
    const cut = text.slice(0, lo).replace(/\s+\S*$/, "").trimEnd();
    return { body: `${cut} […]${tail}`, long: true };
  }

  // Without a form endpoint the site can't send the brief itself. It writes the email and
  // hands it over: Gmail, Outlook, the visitor's mail app, or the clipboard. It never claims it was sent.
  function openHandoff(failed) {
    const address = email.value.trim();
    const text = message.value.trim();
    const tail = `\n\nReply to: ${address}`;
    const body = `${text}${tail}`;
    const short = mailtoBody(text, tail);
    const enc = encodeURIComponent;
    $("[data-handoff-title]", el).textContent = failed
      ? "It didn’t go through. Send it from your email instead."
      : "One more step: send it from your email.";
    handoffText.textContent = "Your brief is written and addressed. Pick how you want to send it.";
    clearButton.hidden = true;
    ready.value = body;
    mailto.href = `mailto:${INBOX}?subject=${enc(subject)}&body=${enc(short.body)}`;
    gmail.href = `https://mail.google.com/mail/?view=cm&fs=1&to=${enc(INBOX)}&su=${enc(subject)}&body=${enc(body)}`;
    outlook.href = `https://outlook.office.com/mail/deeplink/compose?to=${enc(INBOX)}&subject=${enc(subject)}&body=${enc(body)}`;
    $("[data-handoff-long]", el).hidden = !short.long;
    foot.hidden = true;
    handoff.hidden = false;
    // the preview shows the whole email, "Reply to" included, up to its cap
    ready.style.height = "auto";
    ready.style.height = `${Math.min(ready.scrollHeight + 2, 320)}px`;
    $("[data-handoff-title]", el).focus({ preventScroll: true });
    handoff.scrollIntoView({ behavior: reduce.matches ? "auto" : "smooth", block: "nearest" });
  }

  function closeHandoff() {
    handoff.hidden = true;
    foot.hidden = false;
  }

  // Once a way to send was picked, the panel says what comes next. It never says the email went
  // out: the page cannot know that.
  const handoffText = $("[data-handoff-text]", el);
  const clearButton = $("[data-handoff-clear]", el);
  function handedOff() {
    $("[data-handoff-title]", el).textContent = `Sent it? We reply from ${INBOX}.`;
    handoffText.textContent = "If nothing opened, pick another way below.";
    clearButton.hidden = false;
  }
  [gmail, outlook, mailto].forEach((link) => link.addEventListener("click", handedOff));
  clearButton.addEventListener("click", () => {
    message.value = "";
    draft.set("brief", "");
    updateCount();
    closeHandoff();
    announce("Brief cleared.");
    message.focus();
  });

  function sent() {
    el.classList.add("is-sent");
    draft.set("brief", "");
    status.focus({ preventScroll: true });
  }

  if (!email.value) email.value = draft.get("email");
  if (!message.value) message.value = draft.get("brief");
  updateCount();

  el.addEventListener("input", (event) => {
    if (event.target !== email && event.target !== message) return;
    if (event.target === message) updateCount();
    clearError(event.target);
    save();
    // the brief changed, so the email written from it is stale
    if (!handoff.hidden) closeHandoff();
  });

  const copyButton = $("[data-handoff-copy]", el);
  const copyLabel = $("[data-handoff-copy-label]", el);
  copyButton.addEventListener("click", async () => {
    const copied = await copyText(ready.value, ready);
    swapText(copyLabel, copied ? "Copied" : "Selected");
    announce(copied ? "Brief copied." : "The brief is selected. Copy it with your keyboard or the menu.");
    clearTimeout(copyButton._reset);
    copyButton._reset = setTimeout(() => swapText(copyLabel, "Copy the brief"), 2200);
  });

  $("[data-edit]", el).addEventListener("click", () => {
    el.classList.remove("is-sent");
    message.focus();
  });

  el.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (el.classList.contains("is-sending")) return;
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
      // the whole field, label included, comes into view clear of the bar
      fieldOf(invalid[0]).scrollIntoView({ behavior: reduce.matches ? "auto" : "smooth", block: "nearest" });
      invalid[0].focus({ preventScroll: true });
      return;
    }

    const endpoint = el.dataset.endpoint;
    if (!endpoint) {
      openHandoff(false);
      return;
    }

    el.classList.add("is-sending");
    el.setAttribute("aria-busy", "true");
    swapText(submitLabel, "Sending…");
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ email: address, message: text, page: location.pathname }),
      });
      if (!response.ok) throw new Error(String(response.status));
      sent();
    } catch {
      openHandoff(true);
    } finally {
      el.classList.remove("is-sending");
      el.removeAttribute("aria-busy");
      swapText(submitLabel, "Send the brief");
    }
  });
}

// ------------------------------------------------------------------ copy the email address

function copy() {
  $$("[data-copy]").forEach((button) => {
    const label = $("[data-copy-label]", button);
    const source = $("[data-copy-text]", button.parentElement);
    button.addEventListener("click", async () => {
      const copied = await copyText(button.dataset.copy, source);
      swapText(label, copied ? "Copied" : "Selected");
      announce(copied ? "Email address copied." : "The email address is selected.");
      clearTimeout(button._reset);
      button._reset = setTimeout(() => swapText(label, "Copy"), 1800);
    });
  });
}

// ------------------------------------------------------------------ the film, once the owner adds it

function films() {
  $$("[data-film]").forEach((box) => {
    const video = $("video", box);
    const play = $("[data-film-play]", box);
    const sound = $("[data-film-sound]", box);
    let held = reduce.matches; // with reduced motion the film waits for a click
    const load = () => {
      if (!video.getAttribute("src")) video.src = video.dataset.src;
    };

    function render() {
      $("[data-film-play-label]", play).textContent = video.paused ? "Play" : "Pause";
      $("use", play).setAttribute("href", video.paused ? "#i-play" : "#i-pause");
      $("[data-film-sound-label]", sound).textContent = video.muted ? "Sound on" : "Sound off";
      $("use", sound).setAttribute("href", video.muted ? "#i-sound" : "#i-mute");
    }

    ["play", "pause", "volumechange"].forEach((type) => video.addEventListener(type, render));
    play.addEventListener("click", () => {
      load();
      held = !video.paused;
      if (video.paused) video.play().catch(() => {});
      else video.pause();
    });
    sound.addEventListener("click", () => {
      load();
      video.muted = !video.muted;
      if (!video.muted && video.paused) {
        held = false;
        video.play().catch(() => {});
      }
    });
    render();

    if (held) {
      video.preload = "metadata";
      load();
      return;
    }
    new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return video.pause();
        load();
        if (!held) video.play().catch(() => {});
      },
      { threshold: 0.25 },
    ).observe(video);
  });
}

// ------------------------------------------------------------------ the horizons draw in when they come into view

// The head script sets .reveal-ready before the first paint, so a reveal only ever draws in.
// Anything on screen draws at once; the rest draws as it scrolls into view. .reveal-live tells
// the head script's fail-safe that this ran.
function reveals() {
  const items = $$("[data-reveal]");
  document.documentElement.classList.add("reveal-live");
  if (!("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-in"));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add("is-in");
      observer.unobserve(entry.target);
    }
  });
  items.forEach((item) => observer.observe(item));
}

bar();
primary();
menu();
builder();
form();
copy();
films();
reveals();
