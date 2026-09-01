#!/usr/bin/env python3
"""Build the Wa3i (وعي) Arabic cybersecurity awareness site from content/.

Renders every Arabic collection to a clean right to left HTML page and builds the
landing index, with the October Cybersecurity Awareness Month highlighted. The
glossary is rendered as a searchable bilingual list. Markdown is the source of truth.

    python3 build.py
"""
import html
import os
import re

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "SiteQ8/Wa3i"
AUTHOR_AR = "علي العنزي"

ARABIC_DIGITS = str.maketrans("0123456789", "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669")

SITE_AR = "وعي"
SITE_LAT = "Wa3i"
SITE_TAGLINE = "دليل عربي مبسّط للأمن السيبراني: عادات تحميك، ومفاهيم تفهمها، وأطر الخليج التنظيمية، بلغة واضحة للجميع."

# slug, file, emoji, title, one line desc, unit noun, featured, special
PAGES = [
    {"slug": "october-awareness", "file": "october-awareness.md", "emoji": "\U0001F4C5",
     "title": "شهر التوعية بالأمن السيبراني",
     "desc": "أكتوبر شهر التوعية بالأمن السيبراني. سبع عادات أساسية يبدأ بها كل شخص هذا الشهر ليحمي حساباته وأجهزته وبياناته.",
     "unit": "توصية", "featured": True},
    {"slug": "personal-security", "file": "personal-security.md", "emoji": "\U0001F512",
     "title": "الأمن الشخصي على الإنترنت",
     "desc": "ثماني نصائح عملية لحماية حساباتك وهاتفك وخصوصيتك، من كلمات المرور والمصادقة الثنائية إلى الروابط المشبوهة وشبكات الواي فاي العامة.",
     "unit": "نصيحة"},
    {"slug": "concepts", "file": "concepts.md", "emoji": "\U0001F4A1",
     "title": "مفاهيم الأمن السيبراني",
     "desc": "شرح مبسّط لأهم عشرة مفاهيم في الأمن السيبراني، من جدار الحماية والتشفير إلى الثقة الصفرية والدفاع في العمق، مع المصطلح الإنجليزي لكل منها.",
     "unit": "مفهوم"},
    {"slug": "small-business", "file": "small-business.md", "emoji": "\U0001F3E2",
     "title": "الأمن للمؤسسات الصغيرة",
     "desc": "سبع أساسيات تحمي أي عمل صغير دون ميزانية كبيرة: من الأساسيات المجانية والحد الأدنى من الصلاحيات إلى الاستعداد لبرامج الفدية وخطة الاستجابة للحوادث.",
     "unit": "أساسية"},
    {"slug": "gulf-frameworks", "file": "gulf-frameworks.md", "emoji": "\U0001F4CB",
     "title": "الأطر التنظيمية في الخليج",
     "desc": "نظرة مبسّطة على أبرز الأطر التنظيمية للأمن السيبراني في الخليج: CBK CORF و SAMA CSF و NCA ECC و CITRA والمعايير الدولية.",
     "unit": "إطار"},
    {"slug": "glossary", "file": "glossary.md", "emoji": "\U0001F4D6",
     "title": "مسرد المصطلحات",
     "desc": "قاموس ثنائي اللغة لأهم مصطلحات الأمن السيبراني، إنجليزي وعربي مع شرح مختصر، قابل للبحث كي لا تحتار في الترجمة.",
     "unit": "مصطلح", "special": "glossary"},
]


def esc(s):
    return html.escape(str(s))


def head(title, desc, css):
    return (
        "<!doctype html>\n<html lang=\"ar\" dir=\"rtl\"><head>\n"
        "<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>" + esc(title) + "</title>\n"
        "<meta name=\"description\" content=\"" + esc(desc) + "\">\n"
        "<meta property=\"og:title\" content=\"" + esc(title) + "\">\n"
        "<meta property=\"og:description\" content=\"" + esc(desc) + "\">\n"
        "<meta property=\"og:type\" content=\"website\">\n"
        "<meta property=\"og:locale\" content=\"ar_AR\">\n"
        "<meta name=\"twitter:card\" content=\"summary\">\n"
        "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n"
        "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n"
        "<link href=\"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">\n"
        "<link rel=\"stylesheet\" href=\"" + css + "\">\n"
        "</head>\n<body>\n"
    )


def topbar(home, links):
    nav = "".join('<a href="' + href + '">' + esc(text) + "</a>" for text, href in links)
    return ('<div class="topbar"><div class="wrap">'
            '<a class="brand" href="' + home + '"><span class="ar-name">' + SITE_AR + '</span>'
            '<span class="lat">' + SITE_LAT + "</span></a>"
            '<nav class="topnav">' + nav + "</nav></div></div>\n")


def site_footer():
    return ('<footer class="sitefoot"><div class="wrap">'
            '<span>مفتوح المصدر. <a href="https://github.com/' + REPO + '">شارك في تطويره على GitHub</a>.</span>'
            '<span class="lat">By <a href="https://github.com/SiteQ8">Ali AlEnezi</a> &middot; <a href="https://3li.info">3li.info</a></span>'
            "</div></footer>\n")


def count_tips(page):
    text = open(os.path.join(HERE, "content", page["file"]), encoding="utf-8").read()
    if page.get("special") == "glossary":
        return len([ln for ln in text.splitlines() if "|" in ln])
    return len(re.findall(r"^## \d+\.", text, re.M))


def md_body(path):
    text = open(path, encoding="utf-8").read()
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    # number each tip heading with Arabic-Indic numerals in an accent span
    def num(m):
        return '<h2><span class="n">' + m.group(1).translate(ARABIC_DIGITS) + ".</span> "
    body = re.sub(r"<h2>(\d+)\.\s*", num, body)
    return body


def glossary_html(page):
    lines = [ln for ln in open(os.path.join(HERE, "content", page["file"]), encoding="utf-8").read().splitlines() if "|" in ln]
    items = ""
    for ln in lines:
        parts = [p.strip() for p in ln.split("|")]
        en, ar, dfn = (parts + ["", "", ""])[:3]
        search = (en + " " + ar + " " + dfn).lower()
        items += ('<div class="term" data-s="' + esc(search) + '">'
                  '<div class="head"><span class="en-term">' + esc(en) + "</span>"
                  '<span class="ar-term">' + esc(ar) + "</span></div>"
                  '<div class="def">' + esc(dfn) + "</div></div>\n")
    n = len(lines)
    out = '<div class="gsearch"><input id="q" type="text" placeholder="ابحث في المصطلحات بالعربية أو الإنجليزية..." autocomplete="off"></div>\n'
    out += '<div class="gcount">عرض <b id="gc">' + str(n).translate(ARABIC_DIGITS) + '</b> من ' + str(n).translate(ARABIC_DIGITS) + ' مصطلحًا</div>\n'
    out += '<div class="terms" id="terms">\n' + items + "</div>\n"
    out += '<div class="gempty" id="gempty">لا توجد نتائج مطابقة. <b>جرّب كلمة أخرى.</b></div>\n'
    return out, n


GLOSSARY_JS = """
<script>
(function(){
  function qsa(s){return Array.prototype.slice.call(document.querySelectorAll(s));}
  var q=document.getElementById('q'), terms=qsa('.term'), gc=document.getElementById('gc'), ge=document.getElementById('gempty');
  function toEn(s){var m={'\\u0660':'0','\\u0661':'1','\\u0662':'2','\\u0663':'3','\\u0664':'4','\\u0665':'5','\\u0666':'6','\\u0667':'7','\\u0668':'8','\\u0669':'9'};return s.replace(/[\\u0660-\\u0669]/g,function(d){return m[d];});}
  var arNum={'0':'\\u0660','1':'\\u0661','2':'\\u0662','3':'\\u0663','4':'\\u0664','5':'\\u0665','6':'\\u0666','7':'\\u0667','8':'\\u0668','9':'\\u0669'};
  function toAr(n){return (''+n).replace(/[0-9]/g,function(d){return arNum[d];});}
  function apply(){
    var v=(q.value||'').toLowerCase().trim(), shown=0;
    for(var i=0;i<terms.length;i++){
      var ok=v===''||terms[i].getAttribute('data-s').indexOf(v)!==-1;
      terms[i].style.display=ok?'':'none'; if(ok)shown++;
    }
    if(gc)gc.textContent=toAr(shown);
    if(ge)ge.style.display=shown===0?'block':'none';
  }
  if(q)q.addEventListener('input',apply);
  apply();
})();
</script>
"""


def build_page(page):
    edit = "https://github.com/" + REPO + "/edit/main/content/" + page["file"]
    n = count_tips(page)
    out = head(page["title"] + " | " + SITE_AR, page["desc"], "../style.css")
    out += topbar("../", [("كل الأدلة", "../"), ("GitHub", "https://github.com/" + REPO)])
    out += '<main class="wrap prose">\n'
    out += "<h1>" + esc(page["title"]) + "</h1>\n"
    out += ('<div class="byline">بقلم <a href="https://github.com/SiteQ8">' + esc(AUTHOR_AR) + "</a>"
            '<span class="dot"></span>' + str(n).translate(ARABIC_DIGITS) + " " + page["unit"]
            + (" " if page["unit"] == "مصطلح" else "") + '<span class="dot"></span><a href="../">أدلة أخرى</a></div>\n')
    if page.get("special") == "glossary":
        body, _ = glossary_html(page)
        out += body
    else:
        out += md_body(os.path.join(HERE, "content", page["file"])) + "\n"
    out += ('<div class="pagefoot"><div class="row">'
            '<span class="grow">هذه إرشادات عامة للتوعية، وليست بديلًا عن استشارة مختص عند الحاجة. خذ منها ما يناسبك.</span>'
            '</div><div class="row" style="margin-top:12px">'
            '<a href="../">&larr; كل الأدلة</a>'
            '<span class="dot" style="width:3px;height:3px;border-radius:50%;background:var(--line2)"></span>'
            '<a href="' + edit + '">حسّن هذه الصفحة</a></div></div>\n')
    out += "</main>\n"
    if page.get("special") == "glossary":
        out += GLOSSARY_JS
    out += site_footer()
    out += "</body></html>\n"
    with open(os.path.join(HERE, "content", page["slug"] + ".html"), "w", encoding="utf-8") as fh:
        fh.write(out)


def build_index():
    desc = "وعي، دليل عربي مبسّط للأمن السيبراني من علي العنزي. عادات تحميك، مفاهيم تفهمها، أمن المؤسسات الصغيرة، أطر الخليج التنظيمية، ومسرد مصطلحات ثنائي اللغة. مع تسليط الضوء على شهر التوعية بالأمن السيبراني في أكتوبر."
    out = head(SITE_AR + " | دليل الأمن السيبراني بالعربية", desc, "style.css")
    out += topbar("./", [("GitHub", "https://github.com/" + REPO)])
    out += '<main class="wrap">\n<section class="hero">\n'
    out += '<span class="kicker">توعية بالأمن السيبراني</span>\n'
    out += "<h1>" + SITE_AR + "</h1>\n"
    out += '<p class="lede">' + esc(SITE_TAGLINE) + '</p>\n'
    out += "</section>\n"
    # October awareness banner (the highlight)
    out += ('<a class="banner" href="content/october-awareness.html" style="display:block">'
            '<span class="tag">OCTOBER</span>'
            '<h2>أكتوبر شهر التوعية بالأمن السيبراني</h2>'
            '<p>شهر يذكّرنا أن حماية أنفسنا على الإنترنت عادة يومية لا تحتاج إلى خبرة تقنية. ابدأ هذا الشهر بسبع خطوات بسيطة تحمي حساباتك وأجهزتك وبياناتك.</p>'
            '<span class="cta">ابدأ بأساسيات أكتوبر &larr;</span></a>\n')
    out += '<div class="sec-head"><div class="sec-eyebrow">Guides</div><h2 class="sec-title">الأدلة</h2></div>\n'
    out += '<section class="cards">\n'
    for p in PAGES:
        feat = " feat" if p.get("featured") else ""
        pill = '<span class="featpill">أكتوبر</span>' if p.get("featured") else ""
        out += ('<a class="card' + feat + '" href="content/' + p["slug"] + '.html">'
                '<span class="emoji">' + p["emoji"] + "</span>"
                "<h3>" + pill + esc(p["title"]) + "</h3>"
                "<p>" + esc(p["desc"]) + "</p>"
                '<span class="go">' + str(count_tips(p)).translate(ARABIC_DIGITS) + " " + p["unit"]
                + ("ًا" if p["unit"] == "مصطلح" else "") + " &larr;</span>"
                "</a>\n")
    out += "</section>\n</main>\n"
    out += site_footer()
    out += "</body></html>\n"
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(out)


def build():
    for p in PAGES:
        build_page(p)
    build_index()
    total = sum(count_tips(p) for p in PAGES)
    print("built index.html and", len(PAGES), "pages,", total, "items total")


if __name__ == "__main__":
    build()
