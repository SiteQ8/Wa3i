(function () {
  var d = document, root = d.documentElement;
  root.classList.add("js");
  var AR = "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669";
  function toAr(n) { return ("" + n).replace(/[0-9]/g, function (x) { return AR[+x]; }); }
  var slice = function (x) { return Array.prototype.slice.call(x); };
  var reduce = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);

  /* reading progress + back to top */
  var prog = d.getElementById("progress"), totop = d.getElementById("totop");
  function onScroll() {
    if (prog) {
      var h = d.body.scrollHeight - innerHeight;
      prog.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + "%";
    }
    if (totop) { totop.classList.toggle("show", scrollY > 480); }
  }
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (totop) totop.addEventListener("click", function () { scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  /* scroll reveal */
  var reveals = slice(d.querySelectorAll(".reveal"));
  if (!reduce && "IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else { reveals.forEach(function (el) { el.classList.add("in"); }); }

  /* animated counters */
  var counters = slice(d.querySelectorAll("[data-count]"));
  function runCounter(el) {
    if (reduce) { el.textContent = toAr(+el.getAttribute("data-count")); return; }
    var target = +el.getAttribute("data-count"), start = null, dur = 1100;
    requestAnimationFrame(function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      el.textContent = toAr(Math.floor((1 - Math.pow(1 - p, 3)) * target));
      if (p < 1) requestAnimationFrame(step); else el.textContent = toAr(target);
    });
  }
  if ("IntersectionObserver" in window && counters.length) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { runCounter(e.target); co.unobserve(e.target); } });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { co.observe(el); });
  } else { counters.forEach(function (el) { el.textContent = toAr(+el.getAttribute("data-count")); }); }

  /* confetti */
  function confetti() {
    if (reduce) return;
    var c = d.createElement("canvas"); c.className = "confetti-canvas";
    d.body.appendChild(c); var ctx = c.getContext("2d");
    c.width = innerWidth; c.height = innerHeight;
    var cols = ["#ea580c", "#0891b2", "#059669", "#7c3aed", "#db2777", "#fbbf24", "#2563eb"];
    var parts = [];
    for (var k = 0; k < 150; k++) parts.push({
      x: Math.random() * c.width, y: -20 - Math.random() * c.height * 0.5,
      r: 5 + Math.random() * 7, col: cols[k % cols.length],
      vy: 2.5 + Math.random() * 4.5, vx: -2.5 + Math.random() * 5,
      rot: Math.random() * 6.28, vr: -0.25 + Math.random() * 0.5
    });
    var t0 = performance.now();
    (function frame(ts) {
      ctx.clearRect(0, 0, c.width, c.height);
      parts.forEach(function (p) {
        p.y += p.vy; p.x += p.vx; p.rot += p.vr; p.vy += 0.04;
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot);
        ctx.fillStyle = p.col; ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 0.6); ctx.restore();
      });
      if (ts - t0 < 2800) requestAnimationFrame(frame);
      else if (c.parentNode) c.parentNode.removeChild(c);
    })(t0);
  }

  /* glossary live filter */
  var q = d.getElementById("q");
  if (q) {
    var terms = slice(d.querySelectorAll(".term")), gc = d.getElementById("gc"), ge = d.getElementById("gempty");
    q.addEventListener("input", function () {
      var v = (q.value || "").toLowerCase().trim(), shown = 0;
      terms.forEach(function (t) {
        var ok = v === "" || t.getAttribute("data-s").indexOf(v) !== -1;
        t.style.display = ok ? "" : "none"; if (ok) shown++;
      });
      if (gc) gc.textContent = toAr(shown);
      if (ge) ge.style.display = shown === 0 ? "block" : "none";
    });
  }

  /* checklist: progress bar, persistence, confetti on completion */
  var clist = d.getElementById("cl-list");
  if (clist) {
    var boxes = slice(clist.querySelectorAll("input[type=checkbox]"));
    var bar = d.getElementById("cl-bar"), lbl = d.getElementById("cl-lbl"), done = d.getElementById("cl-done");
    var KEY = "wa3i-oct-checklist";
    try { var saved = JSON.parse(localStorage.getItem(KEY) || "[]"); boxes.forEach(function (b, i) { if (saved[i]) b.checked = true; }); } catch (e) {}
    function upd(fire) {
      var n = 0; boxes.forEach(function (b) { if (b.checked) n++; });
      var pct = Math.round(n / boxes.length * 100);
      if (bar) bar.style.width = pct + "%";
      if (lbl) lbl.textContent = toAr(n) + " من " + toAr(boxes.length);
      try { localStorage.setItem(KEY, JSON.stringify(boxes.map(function (b) { return b.checked ? 1 : 0; }))); } catch (e) {}
      var full = n === boxes.length;
      if (done) done.classList.toggle("show", full);
      if (fire && full) confetti();
    }
    boxes.forEach(function (b) { b.addEventListener("change", function () { upd(true); }); });
    upd(false);
  }

  /* phishing quiz game */
  var quizEl = d.getElementById("quiz");
  if (quizEl) {
    var data = [];
    try { data = JSON.parse(d.getElementById("quiz-data").textContent); } catch (e) {}
    var i = 0, score = 0;
    var card = d.getElementById("q-card"), msg = d.getElementById("q-msg"),
      fb = d.getElementById("q-fb"), pv = d.getElementById("q-prog"),
      btns = d.getElementById("q-btns"), next = d.getElementById("q-next"),
      result = d.getElementById("q-result"), progwrap = d.getElementById("q-progwrap"),
      barq = d.getElementById("q-bar");
    function render() {
      var it = data[i];
      card.className = "q-card";
      msg.textContent = it.m;
      fb.style.display = "none"; fb.className = "q-fb";
      btns.style.display = "flex"; next.style.display = "none";
      pv.textContent = "الرسالة " + toAr(i + 1) + " من " + toAr(data.length);
      if (barq) barq.style.width = (i / data.length * 100) + "%";
    }
    function answer(guess) {
      var it = data[i], correct = (guess === it.p);
      if (correct) score++;
      card.className = "q-card " + (it.p ? "is-phish" : "is-safe");
      btns.style.display = "none";
      fb.style.display = "block";
      fb.className = "q-fb " + (correct ? "ok" : "no");
      var verdict = it.p ? "رسالة تصيّد" : "رسالة آمنة";
      fb.innerHTML = "<b>" + (correct ? "إجابة صحيحة" : "ليست صحيحة") + "</b>، فهذه " + verdict + "، " + it.e;
      next.style.display = "inline-flex";
      next.textContent = (i < data.length - 1) ? "الرسالة التالية" : "شاهد نتيجتك";
      if (barq) barq.style.width = ((i + 1) / data.length * 100) + "%";
    }
    function showResult() {
      card.style.display = "none"; if (progwrap) progwrap.style.display = "none";
      result.style.display = "block";
      var pct = Math.round(score / data.length * 100);
      var msgTxt = score === data.length ? "عين صقر، لا تنطلي عليك حيلة."
        : (pct >= 60 ? "جيد جدًا، وعيك يحميك، واصل التدقيق."
          : "لا بأس، الآن تعرف ما يجب أن تنتبه له في المرة القادمة.");
      result.innerHTML = '<div class="q-emoji">' + (score === data.length ? "\uD83C\uDFC6" : (pct >= 60 ? "\uD83D\uDC4F" : "\uD83D\uDCA1")) + "</div>"
        + '<div class="q-score" dir="ltr">' + toAr(score) + " / " + toAr(data.length) + "</div>"
        + '<p class="q-final">' + msgTxt + "</p>"
        + '<div class="q-actions"><button class="q-retry">أعد المحاولة</button><button class="q-share">شارك نتيجتك \uD83D\uDCE4</button></div>';
      if (score === data.length) confetti();
      result.querySelector(".q-share").addEventListener("click", function () {
        var txt = "حصلت على " + toAr(score) + " من " + toAr(data.length) + " في اختبار «هل هذه رسالة تصيّد؟» من وعي، اختبر نفسك: https://siteq8.github.io/Wa3i/content/quiz.html";
        if (navigator.share) { navigator.share({ text: txt }).catch(function () {}); }
        else { window.open("https://wa.me/?text=" + encodeURIComponent(txt), "_blank"); }
      });
      result.querySelector(".q-retry").addEventListener("click", function () {
        i = 0; score = 0; result.style.display = "none"; card.style.display = "";
        if (progwrap) progwrap.style.display = ""; render();
        scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
      });
    }
    d.getElementById("q-yes").addEventListener("click", function () { answer(true); });
    d.getElementById("q-no").addEventListener("click", function () { answer(false); });
    next.addEventListener("click", function () {
      if (i < data.length - 1) { i++; render(); } else showResult();
    });
    render();
  }
})();
