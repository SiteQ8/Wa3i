#!/usr/bin/env python3
"""Build the Wa3i (وعي) Arabic cybersecurity awareness site from content/.

Renders every Arabic collection to a clean right to left HTML page and builds the
landing index, with October Awareness Month highlighted, a searchable glossary, a
gamified checklist, and a phishing quiz game. Markdown is the source of truth, and
the shared behavior in wa3i.js is inlined into every page.

    python3 build.py
"""
import html
import json
import os
import re

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "SiteQ8/Wa3i"
AUTHOR_AR = "علي العنزي"
AD = str.maketrans("0123456789", "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669")
SITE_AR = "وعي"
SITE_LAT = "Wa3i"
SITE_TAGLINE = "دليل عربي مبسّط للأمن السيبراني: عادات تحميك، ومفاهيم تفهمها، وأطر الخليج التنظيمية، بلغة واضحة للجميع."

PAGES = [
    {"slug": "october-awareness", "file": "october-awareness.md", "emoji": "\U0001F4C5",
     "title": "شهر التوعية بالأمن السيبراني",
     "desc": "أكتوبر شهر التوعية بالأمن السيبراني. سبع عادات أساسية يبدأ بها كل شخص هذا الشهر ليحمي حساباته وأجهزته وبياناته.",
     "unit": "توصيات", "color": "#ea580c", "featured": True},
    {"slug": "quiz", "file": "quiz.md", "emoji": "\U0001F3AF",
     "title": "اختبر نفسك: هل هذه رسالة تصيّد؟",
     "desc": "لعبة قصيرة تعرض عليك رسائل حقيقية، فاكتشف أيها تصيّد وأيها آمن، مع شرح فوري لكل إجابة ونتيجة في النهاية.",
     "unit": "رسائل", "color": "#e11d48", "special": "quiz", "game": True},
    {"slug": "personal-security", "file": "personal-security.md", "emoji": "\U0001F512",
     "title": "الأمن الشخصي على الإنترنت",
     "desc": "ثماني نصائح عملية لحماية حساباتك وهاتفك وخصوصيتك، من كلمات المرور والمصادقة الثنائية إلى الروابط المشبوهة وشبكات الواي فاي العامة.",
     "unit": "نصائح", "color": "#0891b2"},
    {"slug": "financial-security", "file": "financial-security.md", "emoji": "\U0001F4B3",
     "title": "الأمان المالي والمصرفي",
     "desc": "ثماني قواعد تحمي أموالك من الاحتيال المصرفي والرسائل المزيّفة باسم البنك وعروض الأرباح الوهمية، ومن الاحتيال الذي قد يأتي ممن تعرف.",
     "unit": "قواعد", "color": "#059669"},
    {"slug": "ai-security", "file": "ai-security.md", "emoji": "\U0001F916",
     "title": "الذكاء الاصطناعي والأمن",
     "desc": "سبع نصائح لزمن الذكاء الاصطناعي: من الأصوات والفيديوهات المزيّفة ورسائل الاحتيال المتقنة، إلى ما يجب ألا تكتبه في روبوتات المحادثة.",
     "unit": "نصائح", "color": "#7c3aed"},
    {"slug": "privacy", "file": "privacy.md", "emoji": "\U0001F510",
     "title": "الخصوصية وحماية بياناتك",
     "desc": "ثماني عادات تحفظ خصوصيتك، من ضبط الأذونات والحدّ من التتبّع إلى تقليل أثرك الرقمي واستعادة السيطرة على بياناتك ممن يجمعها.",
     "unit": "عادات", "color": "#0284c7"},
    {"slug": "for-parents-teachers", "file": "for-parents-teachers.md", "emoji": "\U0001F46A",
     "title": "للمعلمين والأهل",
     "desc": "ثماني إرشادات لحماية الأطفال والطلاب على الإنترنت وتعليمهم كيف يحمون أنفسهم، من الحوار والتنمر الإلكتروني إلى الرقابة الأبوية والألعاب.",
     "unit": "إرشادات", "color": "#db2777"},
    {"slug": "concepts", "file": "concepts.md", "emoji": "\U0001F4A1",
     "title": "مفاهيم الأمن السيبراني",
     "desc": "شرح مبسّط لعشرين مفهومًا في الأمن السيبراني، من جدار الحماية والتشفير إلى الثقة الصفرية والدفاع في العمق، بأمثلة من حياتك اليومية.",
     "unit": "مفاهيم", "color": "#2563eb"},
    {"slug": "small-business", "file": "small-business.md", "emoji": "\U0001F3E2",
     "title": "الأمن للمؤسسات الصغيرة",
     "desc": "عشر أساسيات تحمي أي عمل صغير دون ميزانية كبيرة: من الأساسيات المجانية والحد الأدنى من الصلاحيات إلى الاستعداد لبرامج الفدية وخطة الاستجابة للحوادث.",
     "unit": "أساسيات", "color": "#6366f1"},
    {"slug": "gulf-frameworks", "file": "gulf-frameworks.md", "emoji": "\U0001F4CB",
     "title": "الأطر التنظيمية في الخليج",
     "desc": "نظرة مبسّطة على أبرز الأطر التنظيمية للأمن السيبراني في الخليج ومعاييره الدولية، ما هو كل إطار، ولمن يوجّه، وعلامَ يركّز.",
     "unit": "أطر", "color": "#14b8a6"},
    {"slug": "glossary", "file": "glossary.md", "emoji": "\U0001F4D6",
     "title": "مسرد المصطلحات",
     "desc": "قاموس ثنائي اللغة لأهم مصطلحات الأمن السيبراني، إنجليزي وعربي مع شرح مختصر، قابل للبحث كي لا تحتار في الترجمة.",
     "unit": "مصطلحًا", "color": "#2dd4bf", "special": "glossary"},
]

CHROME = ('<div class="progress" id="progress"></div>\n'
          '<button class="totop" id="totop" aria-label="أعلى الصفحة">\u2191</button>\n')


def esc(s):
    return html.escape(str(s))


def ar(n):
    return str(n).translate(AD)


def head(title, desc, css):
    return (
        '<!doctype html>\n<html lang="ar" dir="rtl"><head>\n'
        '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>' + esc(title) + '</title>\n'
        '<meta name="description" content="' + esc(desc) + '">\n'
        '<meta property="og:title" content="' + esc(title) + '">\n'
        '<meta property="og:description" content="' + esc(desc) + '">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:locale" content="ar_AR">\n'
        '<meta property="og:image" content="https://siteq8.github.io/Wa3i/og.png">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:image" content="https://siteq8.github.io/Wa3i/og.png">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">\n'
        '<link rel="stylesheet" href="' + css + '">\n'
        '</head>\n<body>\n' + CHROME
    )


def topbar(home, links):
    nav = "".join('<a href="' + href + '">' + esc(text) + "</a>" for text, href in links)
    return ('<div class="topbar"><div class="wrap">'
            '<a class="brand" href="' + home + '"><span class="logo">\U0001F6E1\uFE0F</span>'
            '<span class="ar-name">' + SITE_AR + "</span></a>"
            '<nav class="topnav">' + nav + "</nav></div></div>\n")


def site_footer():
    js = open(os.path.join(HERE, "wa3i.js"), encoding="utf-8").read()
    return ('<footer class="sitefoot"><div class="wrap">'
            '<span>هذا الدليل مفتوح المصدر، <a href="https://github.com/' + REPO + '">شارك في تطويره</a>.</span>'
            '<span>بقلم <a href="https://github.com/SiteQ8">علي العنزي</a> &middot; <a href="https://3li.info">الموقع الشخصي</a></span>'
            "</div></footer>\n<script>" + js + "</script>\n")


def count_tips(page):
    text = open(os.path.join(HERE, "content", page["file"]), encoding="utf-8").read()
    if page.get("special") in ("glossary", "quiz"):
        return len([ln for ln in text.splitlines() if "|" in ln])
    return len(re.findall(r"^## \d+\.", text, re.M))


def md_body(path):
    text = open(path, encoding="utf-8").read()
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    body = re.sub(r"<h2>(\d+)\.\s*", lambda m: '<h2 class="reveal"><span class="n">' + ar(m.group(1)) + "</span> ", body)
    body = body.replace("<p>", '<p class="reveal">')
    return body


def glossary_html(page):
    lines = [ln for ln in open(os.path.join(HERE, "content", page["file"]), encoding="utf-8").read().splitlines() if "|" in ln]
    items = ""
    for ln in lines:
        parts = [p.strip() for p in ln.split("|")]
        term, dfn = (parts + ["", ""])[:2]
        search = (term + " " + dfn).lower()
        items += ('<div class="term" data-s="' + esc(search) + '">'
                  '<div class="ar-term-big">' + esc(term) + "</div>"
                  '<div class="def">' + esc(dfn) + "</div></div>\n")
    n = len(lines)
    out = '<div class="gsearch"><span class="gico">\U0001F50D</span><input id="q" type="text" placeholder="ابحث في المصطلحات..." autocomplete="off"></div>\n'
    out += '<div class="gcount">عرض <b id="gc">' + ar(n) + '</b> من ' + ar(n) + ' مصطلحًا</div>\n'
    out += '<div class="terms" id="terms">\n' + items + "</div>\n"
    out += '<div class="gempty" id="gempty">لا توجد نتائج مطابقة، <b>جرّب كلمة أخرى.</b></div>\n'
    return out


def page_footer_links(edit):
    return ('<div class="pagefoot"><div class="row">'
            '<span class="grow">هذه إرشادات عامة للتوعية، وليست بديلًا عن استشارة مختص عند الحاجة، فخذ منها ما يناسبك.</span>'
            '</div><div class="row" style="margin-top:12px">'
            '<a href="../">&larr; كل الأدلة</a>'
            '<span class="fdot"></span>'
            '<a href="' + edit + '">حسّن هذه الصفحة</a></div></div>\n')


def build_page(page):
    edit = "https://github.com/" + REPO + "/edit/main/content/" + page["file"]
    n = count_tips(page)
    out = head(page["title"] + " | " + SITE_AR, page["desc"], "../style.css")
    out += topbar("../", [("كل الأدلة", "../"), ("المستودع", "https://github.com/" + REPO)])
    out += '<main class="wrap prose" style="--cat:' + page["color"] + '">\n'
    out += "<h1>" + esc(page["title"]) + "</h1>\n"
    out += ('<div class="byline">بقلم <a href="https://github.com/SiteQ8">' + esc(AUTHOR_AR) + "</a>"
            '<span class="dot"></span>' + ar(n) + " " + page["unit"]
            + '<span class="dot"></span><a href="../">أدلة أخرى</a></div>\n')
    if page["slug"] == "october-awareness":
        out += ('<a class="callout" href="october-checklist.html">'
                '<span class="cico">\U0001F4CB</span>'
                '<span>حمّل <b>قائمة أكتوبر القابلة للطباعة</b> وشاركها في عملك أو مدرستك أو بيتك.</span>'
                '<span class="cgo">&larr;</span></a>\n')
        out += ('<div class="callout postercall"><span class="cico">\U0001F5BC\uFE0F</span>'
                '<span>ملصقات أكتوبر للطباعة: '
                '<a href="../posters/wa3i-poster-phishing.pdf">التصيّد</a> &middot; '
                '<a href="../posters/wa3i-poster-passwords.pdf">كلمات المرور</a> &middot; '
                '<a href="../posters/wa3i-poster-updates.pdf">التحديث والنسخ الاحتياطي</a>'
                '، اطبعها وعلّقها في عملك أو مدرستك.</span></div>\n')
    if page.get("special") == "glossary":
        out += glossary_html(page)
    else:
        out += md_body(os.path.join(HERE, "content", page["file"])) + "\n"
    out += page_footer_links(edit)
    out += "</main>\n" + site_footer() + "</body></html>\n"
    with open(os.path.join(HERE, "content", page["slug"] + ".html"), "w", encoding="utf-8") as fh:
        fh.write(out)


def build_quiz(page):
    lines = [ln for ln in open(os.path.join(HERE, "content", page["file"]), encoding="utf-8").read().splitlines() if "|" in ln]
    data = []
    for ln in lines:
        m, verdict, e = [p.strip() for p in ln.split("|")]
        data.append({"m": m, "p": verdict == "phishing", "e": e})
    edit = "https://github.com/" + REPO + "/edit/main/content/" + page["file"]
    out = head(page["title"] + " | " + SITE_AR, page["desc"], "../style.css")
    out += topbar("../", [("كل الأدلة", "../"), ("المستودع", "https://github.com/" + REPO)])
    out += '<main class="wrap prose quiz-page" style="--cat:' + page["color"] + '">\n'
    out += "<h1>اختبر نفسك: هل هذه رسالة تصيّد؟</h1>\n"
    out += ('<div class="byline">بقلم <a href="https://github.com/SiteQ8">' + esc(AUTHOR_AR) + "</a>"
            '<span class="dot"></span>' + ar(len(data)) + " رسائل"
            '<span class="dot"></span><a href="../">أدلة أخرى</a></div>\n')
    out += '<p class="quiz-intro">تصلك كل يوم رسائل، بعضها حقيقي وبعضها فخّ، فهل تميّز بينها؟ اقرأ كل رسالة ثم قرّر إن كانت تصيّدًا أم آمنة، وستعرف الجواب فورًا مع شرحه.</p>\n'
    out += '<div id="quiz">\n'
    out += '<div id="q-progwrap"><div class="q-progbar"><span id="q-bar"></span></div><span id="q-prog"></span></div>\n'
    out += '<div id="q-card" class="q-card">'
    out += '<div class="q-label"><span class="q-dot"></span> رسالة واردة</div>'
    out += '<div id="q-msg" class="q-msg"></div>'
    out += ('<div id="q-btns" class="q-btns">'
            '<button id="q-yes" class="q-btn phish">\U0001F3A3 تصيّد</button>'
            '<button id="q-no" class="q-btn safe">\u2705 آمنة</button></div>')
    out += '<div id="q-fb" class="q-fb"></div>'
    out += '<button id="q-next" class="q-next"></button>'
    out += "</div>\n"
    out += '<div id="q-result" class="q-result"></div>\n'
    out += '<script id="quiz-data" type="application/json">' + json.dumps(data, ensure_ascii=False) + "</script>\n"
    out += page_footer_links(edit)
    out += "</main>\n" + site_footer() + "</body></html>\n"
    with open(os.path.join(HERE, "content", page["slug"] + ".html"), "w", encoding="utf-8") as fh:
        fh.write(out)


def build_index():
    desc = "وعي، دليل عربي مبسّط للأمن السيبراني من علي العنزي. عادات تحميك، مفاهيم تفهمها، أمن المؤسسات الصغيرة، أطر الخليج، ومسرد مصطلحات، مع لعبة لاكتشاف التصيّد وقائمة أكتوبر التفاعلية."
    n_guides = len(PAGES)
    n_tips = sum(count_tips(p) for p in PAGES if p.get("special") not in ("glossary", "quiz"))
    n_terms = sum(count_tips(p) for p in PAGES if p.get("special") == "glossary")
    n_quiz = sum(count_tips(p) for p in PAGES if p.get("special") == "quiz")
    stats = [(n_guides, "أدلة تفاعلية"), (n_tips, "نصيحة عملية"), (n_terms, "مصطلحًا"), (n_quiz, "رسائل لتختبر نفسك")]

    out = head(SITE_AR + " | دليل الأمن السيبراني بالعربية", desc, "style.css")
    out += topbar("./", [("المستودع", "https://github.com/" + REPO)])
    out += '<main class="wrap">\n<section class="hero">\n'
    out += '<span class="kicker">\U0001F6E1\uFE0F توعية بالأمن السيبراني</span>\n'
    out += '<h1 class="bigname">' + SITE_AR + "</h1>\n"
    out += '<p class="lede">' + esc(SITE_TAGLINE) + "</p>\n"
    out += "</section>\n"
    out += ('<div class="banner reveal">'
            '<span class="tag">أكتوبر</span>'
            '<h2>أكتوبر شهر التوعية بالأمن السيبراني</h2>'
            '<p>شهر يذكّرنا أن حماية أنفسنا على الإنترنت عادة يومية لا تحتاج إلى خبرة تقنية، فابدأ هذا الشهر بسبع خطوات بسيطة تحمي حساباتك وأجهزتك وبياناتك.</p>'
            '<div class="banner-cta">'
            '<a class="cta" href="content/october-awareness.html">ابدأ بأساسيات أكتوبر &larr;</a>'
            '<a class="cta ghost" href="content/october-checklist.html">\U0001F4CB اطبع قائمة أكتوبر</a>'
            '</div></div>\n')
    out += '<div class="stats reveal">'
    for c, lbl in stats:
        out += ('<div class="stat"><div class="snum" data-count="' + str(c) + '">' + ar(c) + "</div>"
                '<div class="slbl">' + lbl + "</div></div>")
    out += "</div>\n"
    out += '<div class="sec-head"><h2 class="sec-title">تصفّح الأدلة</h2></div>\n'
    out += '<section class="cards">\n'
    for p in PAGES:
        cls = "card reveal"
        pill = ""
        if p.get("featured"):
            cls += " feat"
            pill = '<span class="tagpill amber">أكتوبر</span>'
        if p.get("game"):
            cls += " game"
            pill = '<span class="tagpill rose">\U0001F3AE لعبة</span>'
        out += ('<a class="' + cls + '" style="--cat:' + p["color"] + '" href="content/' + p["slug"] + '.html">'
                '<span class="chip">' + p["emoji"] + "</span>"
                "<h3>" + pill + esc(p["title"]) + "</h3>"
                "<p>" + esc(p["desc"]) + "</p>"
                '<span class="go">' + ar(count_tips(p)) + " " + p["unit"] + " &larr;</span>"
                "</a>\n")
    out += "</section>\n</main>\n" + site_footer() + "</body></html>\n"
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(out)


def build_checklist():
    items = [ln.strip() for ln in open(os.path.join(HERE, "content", "october-checklist.md"), encoding="utf-8").read().splitlines() if ln.strip()]
    out = head("قائمة أكتوبر للأمن السيبراني | " + SITE_AR,
               "قائمة تحقق تفاعلية وقابلة للطباعة لشهر التوعية بالأمن السيبراني: ثماني خطوات بسيطة تحمي حساباتك وأجهزتك وبياناتك.", "../style.css")
    out += topbar("../", [("كل الأدلة", "../"), ("المستودع", "https://github.com/" + REPO)])
    out += '<main class="wrap checklist" style="--cat:#ea580c">\n'
    out += '<div class="cl-head"><span class="cl-badge">أكتوبر</span>'
    out += "<h1>قائمة أكتوبر للأمن السيبراني</h1>"
    out += '<p class="cl-sub">ثماني خطوات بسيطة لشهر التوعية، أنجزها واحدة واحدة، أو اطبعها وعلّقها وشاركها في عملك أو مدرستك أو بيتك.</p>'
    out += '<button class="printbtn noprint" onclick="window.print()">\U0001F5A8 اطبع القائمة</button></div>\n'
    out += ('<div class="cl-progress noprint"><div class="cl-track"><span id="cl-bar"></span></div>'
            '<span class="cl-lbl" id="cl-lbl"></span></div>\n')
    out += '<ul class="cl-list" id="cl-list">\n'
    for it in items:
        out += '<li><label><input type="checkbox"><span class="box"></span><span class="txt">' + esc(it) + "</span></label></li>\n"
    out += "</ul>\n"
    out += '<div class="cl-done" id="cl-done"><span class="cl-done-emoji">\U0001F389</span><b>أحسنت!</b> أكملت قائمة أكتوبر، فأنت الآن أصعب هدفًا بكثير. شارك القائمة مع من تحب.</div>\n'
    out += '<div class="cl-foot">وعي &middot; دليل الأمن السيبراني بالعربية</div>\n'
    out += '<div class="pagefoot noprint"><div class="row"><a href="october-awareness.html">&larr; العودة إلى أساسيات أكتوبر</a></div></div>\n'
    out += "</main>\n" + site_footer().replace('<footer class="sitefoot">', '<footer class="sitefoot noprint">') + "</body></html>\n"
    with open(os.path.join(HERE, "content", "october-checklist.html"), "w", encoding="utf-8") as fh:
        fh.write(out)


def build():
    for p in PAGES:
        if p.get("special") == "quiz":
            build_quiz(p)
        else:
            build_page(p)
    build_index()
    build_checklist()
    total = sum(count_tips(p) for p in PAGES)
    print("built index.html and", len(PAGES), "pages,", total, "items total")


if __name__ == "__main__":
    build()
