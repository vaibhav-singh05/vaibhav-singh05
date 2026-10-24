"""Build GitHub-safe, self-contained profile SVGs (Udit-style midnight glass)."""
from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"


def data_uri(path: Path, max_w: int = 520) -> str:
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r > 236 and g > 236 and b > 236:
                px[x, y] = (r, g, b, 0)
    bbox = im.getbbox()
    if bbox:
        pad = 12
        x0, y0, x1, y1 = bbox
        im = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)))
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


PORTRAIT = data_uri(ASSETS / "id.png", 360)
POINTING = data_uri(ASSETS / "right_pointing.png", 340)


def use_photo(ref: str, x: int, y: int, w: int, h: int, meet: str = "xMidYMid meet") -> str:
    return (
        f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 360 420" overflow="hidden">'
        f'<use href="#{ref}" width="360" height="420"/>'
        f"</svg>"
    )


def style(prefix: str) -> str:
    return f"""<style>
text{{font-family:Segoe UI,Helvetica Neue,Arial,sans-serif;font-weight:700;fill:#f2f5ff}}
.mono{{font-family:Consolas,Courier New,monospace;font-weight:400}}
.enter{{animation:entry 1s cubic-bezier(.16,1,.3,1) both}}
.blink{{animation:blink 1s steps(2,end) infinite both}}
.pulse{{animation:pulse 2.4s ease-in-out infinite both}}
.nudge{{animation:nudge 2.8s ease-in-out infinite both}}
.float{{animation:float 6s ease-in-out infinite both}}
.swing{{transform-origin:268px 24px;animation:swing 5.8s ease-in-out infinite both}}
.spin-slow{{transform-origin:300px 393px;animation:spin 28s linear infinite}}
.spin-mid{{transform-origin:300px 393px;animation:spin 38s linear infinite reverse}}
.spin-fast{{transform-origin:300px 393px;animation:spin 52s linear infinite}}
@keyframes entry{{from{{opacity:0;transform:translateY(22px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
@keyframes nudge{{0%,70%,100%{{transform:translateX(0)}}85%{{transform:translateX(8px)}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
@keyframes swing{{0%,100%{{transform:rotate(-1.7deg)}}50%{{transform:rotate(1.7deg)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}.motion{{display:none}}.still{{display:inline!important}}}}
</style>"""


def defs(prefix: str, height: int, extra: str = "") -> str:
    return f"""<defs>
<linearGradient id="{prefix}-aurora" x1="0" y1="0" x2="1" y2="1">
  <stop stop-color="#8bc6ff"/><stop offset=".52" stop-color="#247bff"/><stop offset="1" stop-color="#1240bd"/>
</linearGradient>
<linearGradient id="{prefix}-hairline">
  <stop stop-color="#247bff" stop-opacity=".7"/><stop offset=".5" stop-color="#567394" stop-opacity=".25"/><stop offset="1" stop-color="#ff354f" stop-opacity=".65"/>
</linearGradient>
<radialGradient id="{prefix}-halo">
  <stop stop-color="#1266ed" stop-opacity=".38"/><stop offset="1" stop-color="#1266ed" stop-opacity="0"/>
</radialGradient>
<radialGradient id="{prefix}-red-halo">
  <stop stop-color="#ff1c3f" stop-opacity=".22"/><stop offset="1" stop-color="#ff1c3f" stop-opacity="0"/>
</radialGradient>
<linearGradient id="{prefix}-steel" x1="0" y1="0" x2="1" y2="1">
  <stop stop-color="#e7efff"/><stop offset=".2" stop-color="#526178"/><stop offset=".45" stop-color="#ecf4ff"/><stop offset=".6" stop-color="#788aa7"/><stop offset="1" stop-color="#26364d"/>
</linearGradient>
<linearGradient id="{prefix}-foil">
  <stop stop-color="#76afff" stop-opacity="0"/><stop offset=".42" stop-color="#76afff" stop-opacity="0"/><stop offset=".5" stop-color="#d2ecff" stop-opacity=".35"/><stop offset=".58" stop-color="#ff354f" stop-opacity=".1"/><stop offset="1" stop-color="#ff354f" stop-opacity="0"/>
</linearGradient>
<linearGradient id="{prefix}-shade" x1="0" y1="0" x2="0" y2="1">
  <stop stop-color="#070b16" stop-opacity="0"/><stop offset=".55" stop-color="#070b16" stop-opacity="0"/><stop offset="1" stop-color="#070b16"/>
</linearGradient>
<pattern id="{prefix}-dots" width="20" height="20" patternUnits="userSpaceOnUse">
  <circle cx="1" cy="1" r=".7" fill="#99b1db" opacity=".13"/>
</pattern>
<pattern id="{prefix}-carbon" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
  <path d="M0 0V8" stroke="#4b6d9c" stroke-opacity=".12" stroke-width="2"/>
</pattern>
<clipPath id="{prefix}-outer"><rect x="1" y="1" width="1198" height="{height - 2}" rx="24"/></clipPath>
{extra}
</defs>"""


def chevrons(x: int, y: int, color: str = "#ff354f") -> str:
    parts = []
    for i in range(3):
        cx = x + i * 12
        parts.append(f'<path d="M{cx} {y}l9 0 -7 18h-9Z" fill="{color}"/>')
    return "".join(parts)


def svg_open(name: str, height: int, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" '
        f'aria-labelledby="{name}-title {name}-desc">'
        f'<title id="{name}-title">{title}</title>'
        f'<desc id="{name}-desc">{desc}</desc>'
    )


def card_bg(prefix: str, height: int) -> str:
    return (
        f'<g clip-path="url(#{prefix}-outer)">'
        f'<rect x="1" y="1" width="1198" height="{height - 2}" rx="22" fill="#070b16" stroke="url(#{prefix}-hairline)"/>'
        f'<rect x="2" y="2" width="1196" height="{height - 4}" rx="21" fill="url(#{prefix}-dots)"/>'
    )


def icon_pin() -> str:
    return '<path d="M12 22s8-8 8-14a8 8 0 0 0-16 0c0 6 8 14 8 14Z M15 8a3 3 0 1 1-6 0a3 3 0 1 1 6 0"/>'


def icon_briefcase() -> str:
    return '<path d="M8 6V3h8v3 M3 7h18v15H3Z M3 12q9 6 18 0 M11 14h2"/>'


def icon_star() -> str:
    return '<path d="m12 2 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1Z"/>'


def icon_book() -> str:
    return '<path d="M4 3h16v18H4Z M8 3v18 M12 7h4"/>'


def icon_arrow() -> str:
    return '<path d="M3 12h18 M15 6l6 6-6 6"/>'


def icon_code() -> str:
    return '<path d="m8 5-6 7 6 7 M16 5l6 7-6 7 M14 3l-4 18"/>'


def icon_cloud() -> str:
    return '<path d="M6 19a5 5 0 0 1-1-10 7 7 0 0 1 13-1 5.5 5.5 0 0 1 0 11Z"/>'


def icon_people() -> str:
    return '<path d="M8 11a4 4 0 1 0 0-8 4 4 0 1 0 0 8 M1 22v-3a7 7 0 0 1 14 0v3 M17 4a4 4 0 1 1 0 8 M18 15a5 5 0 0 1 5 5v2"/>'


def lucide(x: int, y: int, scale: float, stroke: str, path: str) -> str:
    return (
        f'<g transform="translate({x} {y}) scale({scale})" fill="none" stroke="{stroke}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{path}</g>'
    )


def linkedin_icon(x: int, y: int, fill: str = "#247bff") -> str:
    return (
        f'<g transform="translate({x} {y}) scale(1.333)" fill="{fill}">'
        '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'
        "</g>"
    )


def github_icon(x: int, y: int, fill: str = "#f2f5ff") -> str:
    return (
        f'<g transform="translate({x} {y}) scale(1.25)" fill="{fill}">'
        '<path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>'
        "</g>"
    )


def build_hero() -> str:
    extra = f"""
<image id="hero-photo" width="360" height="420" href="{PORTRAIT}" preserveAspectRatio="xMidYMid meet"/>
<clipPath id="hero-typing"><rect x="40" y="147" width="340" height="42"/></clipPath>
<mask id="hero-reveal" maskUnits="userSpaceOnUse" x="30" y="180" width="680" height="260">
  <rect x="30" y="180" width="680" height="270" fill="white"/>
</mask>
"""
    roles = [
        ("1;1;0;0;1", "0;0.227;0.25;0.977;1", "Senior AI Engineer @ Spoto.in", "1"),
        ("0;0;1;1;0;0", "0;0.227;0.25;0.477;0.5;1", "Django REST + API Builder", "0"),
        ("0;0;1;1;0;0", "0;0.477;0.5;0.727;0.75;1", "Python · PostgreSQL · AWS", "0"),
        ("0;0;1;1;0", "0;0.727;0.75;0.977;1", "Shipping production systems", "0"),
    ]
    role_svg = []
    for values, keys, label, start in roles:
        role_svg.append(
            f'<g class="motion" opacity="{start}">'
            f'<animate attributeName="opacity" begin="0s" dur="16s" values="{values}" keyTimes="{keys}" fill="freeze" repeatCount="indefinite"/>'
            f'<text x="46" y="456" font-size="26" fill="#f2f5ff">{label}</text></g>'
        )

    return (
        svg_open("hero", 640, "Vaibhav Singh — hero", "Senior AI Software Engineer at Spoto.in. Gorakhpur / Bengaluru remote.")
        + style("hero")
        + defs("hero", 640, extra)
        + card_bg("hero", 640)
        + '<ellipse cx="925" cy="310" rx="410" ry="390" fill="url(#hero-halo)"/>'
        + '<ellipse cx="1200" cy="100" rx="280" ry="360" fill="url(#hero-red-halo)"/>'
        + '<text x="690" y="530" font-size="210" fill="#0e2244" letter-spacing="-4">05</text>'
        + "".join(
            f'<path d="M{630 + i * 84} 95 L{310 + i * 84} 640" fill="none" stroke="#193057" stroke-width="1.5" opacity=".3"/>'
            for i in range(8)
        )
        + '<g><circle cx="935" cy="329" r="222" fill="none" stroke="#247bff" opacity=".14"/>'
        + '<circle cx="935" cy="329" r="222" fill="none" stroke="#247bff" stroke-width="2" stroke-dasharray="80 1315">'
        + '<animateTransform attributeName="transform" type="rotate" dur="24s" values="0 935 329;360 935 329" repeatCount="indefinite"/>'
        + "</circle></g>"
        + '<g><circle cx="935" cy="329" r="241" fill="none" stroke="#ff354f" opacity=".14"/>'
        + '<circle cx="935" cy="329" r="241" fill="none" stroke="#ff354f" stroke-width="2" stroke-dasharray="80 1434">'
        + '<animateTransform attributeName="transform" type="rotate" dur="38s" values="0 935 329;360 935 329" repeatCount="indefinite"/>'
        + "</circle></g>"
        + '<path d="M42 76 L1158 76" fill="none" stroke="#223149" stroke-width="1.5"/>'
        + '<text x="44" y="44" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">VS / SOFTWARE ENGINEER</text>'
        + '<text x="446" y="44" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">GORAKHPUR · BENGALURU</text>'
        + chevrons(1092, 29)
        + '<rect x="44" y="104" width="169" height="28" rx="5" fill="#122c49"/>'
        + '<text x="56" y="123" font-size="10" fill="#f2f5ff" class="mono" letter-spacing="1">OPEN TO COLLABS</text>'
        + '<circle cx="228" cy="118" r="4" fill="#3d93ff" class="pulse"/>'
        + '<text x="45" y="176" font-size="18" fill="#b6c5dd" class="mono" clip-path="url(#hero-typing)">Hi there, I\'m</text>'
        + '<g mask="url(#hero-reveal)" class="enter">'
        + '<text x="39" y="278" font-size="72" fill="#f2f5ff" letter-spacing="2">VAIBHAV</text>'
        + '<text x="40" y="368" font-size="72" fill="url(#hero-aurora)" letter-spacing="2">SINGH</text>'
        + "</g>"
        + chevrons(430, 228)
        + '<text x="430" y="292" font-size="24" fill="#f2f5ff">BUILD.</text>'
        + '<text x="430" y="322" font-size="24" fill="#f2f5ff">SHIP.</text>'
        + "".join(role_svg)
        + '<g class="still" display="none"><text x="46" y="456" font-size="26">Senior AI Engineer @ Spoto.in</text></g>'
        + '<text x="46" y="496" font-size="14" fill="#adbed8" class="mono">Building AI-powered, scalable backends with</text>'
        + '<text x="46" y="518" font-size="14" fill="#adbed8" class="mono">Python, Django REST Framework &amp; APIs.</text>'
        + use_photo("hero-photo", 700, 70, 460, 538)
        + '<rect x="661" y="476" width="538" height="164" fill="url(#hero-shade)"/>'
        + '<rect x="861" y="525" width="287" height="56" rx="9" fill="#0b1323" stroke="#2d527b"/>'
        + chevrons(876, 540, "#247bff")
        + '<text x="922" y="550" font-size="18">ENGINEER / BUILDER</text>'
        + '<text x="922" y="567" font-size="10" fill="#85a4ce" class="mono">@vaibhav-singh05</text>'
        + '<path d="M44 554 L634 554" fill="none" stroke="#24334d" stroke-width="1.5"/>'
        + lucide(44, 580, 0.7, "#247bff", icon_pin())
        + '<text x="70" y="594" font-size="11" fill="#9db2d1" class="mono">Gorakhpur</text>'
        + lucide(222, 580, 0.7, "#247bff", icon_briefcase())
        + '<text x="248" y="594" font-size="11" fill="#9db2d1" class="mono">Spoto.in</text>'
        + lucide(376, 580, 0.7, "#247bff", icon_star())
        + '<text x="402" y="594" font-size="11" fill="#9db2d1" class="mono">100+ LC</text>'
        + lucide(516, 580, 0.7, "#247bff", icon_book())
        + '<text x="542" y="594" font-size="11" fill="#9db2d1" class="mono">13 repos</text>'
        + '<text x="880" y="611" font-size="10" fill="#6688b5" class="mono">01 / ENGINEERED TO SHIP</text>'
        + "</g></svg>"
    )


def build_about() -> str:
    extra = f'<image id="about-photo" width="360" height="420" href="{PORTRAIT}" preserveAspectRatio="xMidYMid meet"/>'
    waveform = []
    for i in range(48):
        x = 671 + i * 9
        h = 6 + abs(((i * 7) % 17) - 8)
        y = 406 - h
        color = "#247bff" if i < 30 else "#294565"
        waveform.append(f'<rect x="{x}" y="{y}" width="4" height="{h}" rx="1" fill="{color}"/>')

    slide1 = (
        '<g class="motion" opacity="1">'
        '<animate attributeName="opacity" begin="0s" dur="12s" values="1;1;0;0;1" keyTimes="0;0.31;0.333;0.977;1" fill="freeze" repeatCount="indefinite"/>'
        '<g><animateTransform attributeName="transform" type="translate" begin="0s" dur="12s" values="0 0;0 0;-22 0;-22 0;0 0" keyTimes="0;.31;.333;.977;1" repeatCount="indefinite"/>'
        '<rect x="634" y="144" width="529" height="302" rx="12" fill="#0d1628" stroke="#233d61"/>'
        '<ellipse cx="902" cy="283" rx="250" ry="160" fill="url(#about-halo)"/>'
        '<rect x="667" y="172" width="463" height="209" rx="9" fill="#090f1c" stroke="#2a4a73"/>'
        + use_photo("about-photo", 684, 166, 190, 220) +
        '<rect x="686" y="350" width="186" height="19" rx="4" fill="#0c2245"/>'
        '<text x="695" y="363" font-size="10" fill="#b8d9ff" class="mono">VAIBHAV / ENGINEER</text>'
        '<text x="900" y="250" font-size="28">BACKEND.</text>'
        '<text x="900" y="286" font-size="28">APIS.</text>'
        '<text x="900" y="322" font-size="28" fill="#247bff">PRODUCTION.</text>'
        + "".join(waveform)
        + "</g>"
        + '<text x="635" y="484" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">MAKE IT SHIP.</text>'
        + '<text x="633" y="533" font-size="34">Backend Systems</text>'
        + '<text x="635" y="567" font-size="13" fill="#97adcb" class="mono">Django REST · Razorpay · Juspay · AWS</text>'
        + '<text x="635" y="616" font-size="11" fill="#6686ae" class="mono">01 / 03</text>'
        + chevrons(1108, 598, "#247bff")
        + "</g>"
    )

    slide2 = (
        '<g class="motion" opacity="0">'
        '<animate attributeName="opacity" begin="0s" dur="12s" values="0;0;1;1;0;0" keyTimes="0;0.31;0.333;0.644;0.667;1" fill="freeze" repeatCount="indefinite"/>'
        '<g><animateTransform attributeName="transform" type="translate" begin="0s" dur="12s" values="22 0;22 0;0 0;0 0;-22 0;-22 0" keyTimes="0;.31;.333;.644;.667;1" repeatCount="indefinite"/>'
        '<rect x="634" y="144" width="529" height="302" rx="12" fill="#0d1628" stroke="#233d61"/>'
        '<ellipse cx="902" cy="283" rx="250" ry="160" fill="url(#about-red-halo)"/>'
        '<rect x="664" y="171" width="215" height="238" rx="10" fill="#0a1324" stroke="#254365"/>'
        + use_photo("about-photo", 678, 176, 188, 220) +
        '<text x="684" y="400" font-size="11" fill="#a6c8f4" class="mono">LIVE PRODUCTS</text>'
        '<text x="919" y="204" font-size="28" fill="#ff354f">01</text>'
        '<text x="964" y="200" font-size="11" fill="#bbcbe2" class="mono">COUNSELLING LIVE</text>'
        '<path d="M920 223 L1128 223" fill="none" stroke="#263b58" stroke-width="1.5"/>'
        '<text x="919" y="276" font-size="28" fill="#ff354f">02</text>'
        '<text x="964" y="272" font-size="11" fill="#bbcbe2" class="mono">UNIBOOK EXCHANGE</text>'
        '<path d="M920 295 L1128 295" fill="none" stroke="#263b58" stroke-width="1.5"/>'
        '<text x="919" y="348" font-size="28" fill="#ff354f">03</text>'
        '<text x="964" y="344" font-size="11" fill="#bbcbe2" class="mono">VANI COMMERCE</text>'
        '<path d="M920 367 L1128 367" fill="none" stroke="#263b58" stroke-width="1.5"/>'
        "</g>"
        + '<text x="635" y="484" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">FROM IDEA TO URL.</text>'
        + '<text x="633" y="533" font-size="34">Things I\'ve shipped</text>'
        + '<text x="635" y="567" font-size="13" fill="#97adcb" class="mono">Live Django products with payments &amp; traffic.</text>'
        + '<text x="635" y="616" font-size="11" fill="#6686ae" class="mono">02 / 03</text>'
        + chevrons(1108, 598)
        + "</g>"
    )

    slide3 = (
        '<g class="motion" opacity="0">'
        '<animate attributeName="opacity" begin="0s" dur="12s" values="0;0;1;1;0" keyTimes="0;0.644;0.667;0.977;1" fill="freeze" repeatCount="indefinite"/>'
        '<g><animateTransform attributeName="transform" type="translate" begin="0s" dur="12s" values="22 0;22 0;0 0;0 0;-22 0" keyTimes="0;.644;.667;.977;1" repeatCount="indefinite"/>'
        '<rect x="634" y="144" width="529" height="302" rx="12" fill="#0d1628" stroke="#233d61"/>'
        '<ellipse cx="902" cy="283" rx="250" ry="160" fill="url(#about-halo)"/>'
        '<text x="665" y="186" font-size="19" fill="#80b5ff" class="mono">problem.solve()</text>'
        '<rect x="1016" y="165" width="120" height="28" rx="5" fill="#12332e"/>'
        '<text x="1028" y="184" font-size="10" fill="#f2f5ff" class="mono" letter-spacing="1">ACCEPTED</text>'
        '<text x="665" y="239" font-size="10" fill="#56779f" class="mono">APPROACH</text>'
        '<text x="665" y="264" font-size="15" fill="#f2f5ff" class="mono">Understand → simplify</text>'
        '<text x="665" y="294" font-size="10" fill="#56779f" class="mono">COMPLEXITY</text>'
        '<text x="665" y="319" font-size="15" fill="#f2f5ff" class="mono">Think before you type</text>'
        '<text x="665" y="349" font-size="10" fill="#56779f" class="mono">RESULT</text>'
        '<text x="665" y="374" font-size="15" fill="#f2f5ff" class="mono">100+ LeetCode solved</text>'
        "</g>"
        '<text x="635" y="484" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">CHASE THE ELEGANT SOLUTION.</text>'
        '<text x="633" y="533" font-size="34">Problem Solving</text>'
        '<text x="635" y="567" font-size="13" fill="#97adcb" class="mono">For the joy of a problem, solved.</text>'
        '<text x="635" y="616" font-size="11" fill="#6686ae" class="mono">03 / 03</text>'
        + chevrons(1108, 598, "#247bff")
        + "</g>"
    )

    return (
        svg_open("about", 650, "Vaibhav Singh — about life", "Django REST, AI backends, and production systems.")
        + style("about")
        + defs("about", 650, extra)
        + '<g clip-path="url(#about-outer)">'
        + '<rect x="1" y="1" width="583" height="648" rx="22" fill="#070b16" stroke="url(#about-hairline)"/>'
        + '<rect x="2" y="2" width="581" height="646" rx="21" fill="url(#about-dots)"/>'
        + '<rect x="600" y="1" width="599" height="648" rx="22" fill="#070b16" stroke="url(#about-hairline)"/>'
        + '<rect x="601" y="2" width="597" height="646" rx="21" fill="url(#about-dots)"/>'
        + '<text x="34" y="37" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">01 / FROM THOUGHT TO THING</text>'
        + '<text x="32" y="92" font-size="38">IDEAS. BUILT DIFFERENT.</text>'
        + '<rect x="34" y="116" width="515" height="215" rx="10" fill="#0c1425" stroke="#294363"/>'
        + '<rect x="35" y="117" width="513" height="30" rx="9" fill="#12213a"/>'
        + '<circle cx="49" cy="132" r="3" fill="#ff354f"/><circle cx="63" cy="132" r="3" fill="#247bff"/><circle cx="77" cy="132" r="3" fill="#8cbfff"/>'
        + '<text x="102" y="136" font-size="10" fill="#92afd5" class="mono">github.com / vaibhav-singh05 / build</text>'
        + '<text x="57" y="184" font-size="14" fill="#91baff" class="mono">&gt; turn_curiosity_into_impact()</text>'
        + '<rect x="390" y="173" width="6" height="14" fill="#247bff" class="blink"/>'
        + '<rect x="57" y="216" width="135" height="79" rx="8" fill="#0d1d35" stroke="#247bff"/>'
        + '<text x="69" y="245" font-size="29" fill="#247bff">01</text>'
        + '<text x="69" y="276" font-size="11" fill="#cedbf0" class="mono">IDEATE</text>'
        + lucide(196, 241, 0.8, "#527ba9", icon_arrow())
        + '<rect x="224" y="216" width="135" height="79" rx="8" fill="#0d1d35" stroke="#579dff"/>'
        + '<text x="236" y="245" font-size="29" fill="#579dff">02</text>'
        + '<text x="236" y="276" font-size="11" fill="#cedbf0" class="mono">ENGINEER</text>'
        + lucide(363, 241, 0.8, "#527ba9", icon_arrow())
        + '<rect x="391" y="216" width="135" height="79" rx="8" fill="#0d1d35" stroke="#ff354f"/>'
        + '<text x="403" y="245" font-size="29" fill="#ff354f">03</text>'
        + '<text x="403" y="276" font-size="11" fill="#cedbf0" class="mono">SHIP</text>'
        + '<path d="M34 430 L548 430" fill="none" stroke="#1e2e45" stroke-width="1.5"/>'
        + lucide(43, 373, 1.15, "#247bff", icon_code())
        + '<text x="91" y="389" font-size="24">Django REST &amp; APIs</text>'
        + '<text x="92" y="413" font-size="11" fill="#849dbf" class="mono">From first request to production traffic.</text>'
        + '<path d="M34 519 L548 519" fill="none" stroke="#1e2e45" stroke-width="1.5"/>'
        + lucide(43, 462, 1.15, "#247bff", icon_cloud())
        + '<text x="91" y="478" font-size="24">AI &amp; Cloud Backends</text>'
        + '<text x="92" y="502" font-size="11" fill="#849dbf" class="mono">Scalable systems. Useful intelligence.</text>'
        + '<path d="M34 608 L548 608" fill="none" stroke="#1e2e45" stroke-width="1.5"/>'
        + lucide(43, 551, 1.15, "#ff354f", icon_people())
        + '<text x="91" y="567" font-size="24">Full-stack shipping</text>'
        + '<text x="92" y="591" font-size="11" fill="#849dbf" class="mono">Payments, Nginx, AWS — products that stay up.</text>'
        + '<text x="634" y="37" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">02 / LIFE OUTSIDE THE COMMIT</text>'
        + '<text x="632" y="92" font-size="38">MORE THAN A JOB TITLE.</text>'
        + '<rect x="634" y="112" width="157" height="4" rx="2" fill="#22324a"/>'
        + '<rect x="634" y="112" width="157" height="4" rx="2" fill="#247bff"><animate attributeName="width" dur="12s" values="0;157;157" keyTimes="0;.333;1" fill="freeze" repeatCount="indefinite"/></rect>'
        + '<rect x="810" y="112" width="157" height="4" rx="2" fill="#22324a"/>'
        + '<rect x="810" y="112" width="157" height="4" rx="2" fill="#ff354f"><animate attributeName="width" dur="12s" values="0;0;157;157" keyTimes="0;.333;.667;1" fill="freeze" repeatCount="indefinite"/></rect>'
        + '<rect x="986" y="112" width="157" height="4" rx="2" fill="#22324a"/>'
        + '<rect x="986" y="112" width="157" height="4" rx="2" fill="#247bff"><animate attributeName="width" dur="12s" values="0;0;157" keyTimes="0;.667;1" fill="freeze" repeatCount="indefinite"/></rect>'
        + slide1
        + slide2
        + slide3
        + '<g class="still" display="none">'
        + '<text x="639" y="217" font-size="34">Backend Systems</text>'
        + '<text x="639" y="282" font-size="34">Things I\'ve shipped</text>'
        + '<text x="639" y="347" font-size="34">Problem Solving</text>'
        + "</g></g></svg>"
    )


def orbit_node(label: str, color: str, angle: int, radius: int = 168) -> str:
    import math

    rad = math.radians(angle)
    x = 300 + radius * math.cos(rad)
    y = 393 + radius * math.sin(rad)
    return (
        f'<g transform="translate({x:.1f} {y:.1f})">'
        f'<circle r="29" fill="#0d1729" stroke="{color}" stroke-opacity=".7"/>'
        f'<text x="0" y="5" font-size="11" fill="{color}" text-anchor="middle" class="mono">{label}</text>'
        "</g>"
    )


def build_stack() -> str:
    chips = [
        (625, 208, "01 / LANGUAGES", [("Python", "#247bff"), ("JavaScript", "#247bff"), ("C / C++", "#247bff")]),
        (340, "02 / BACKEND &amp; DATA", [("Django", "#247bff"), ("DRF", "#247bff"), ("PostgreSQL", "#247bff")]),
        (472, "03 / CLOUD &amp; PAYMENTS", [("AWS", "#ff354f"), ("Nginx", "#ff354f"), ("Razorpay", "#ff354f")]),
    ]
    chip_svg = []
    rows = [
        (226, "01 / LANGUAGES", [("Python", "#247bff"), ("JavaScript", "#247bff"), ("C / C++", "#247bff")]),
        (358, "02 / BACKEND &amp; DATA", [("Django", "#247bff"), ("DRF", "#247bff"), ("PostgreSQL", "#247bff")]),
        (490, "03 / CLOUD &amp; PAYMENTS", [("AWS", "#ff354f"), ("Nginx", "#ff354f"), ("Razorpay", "#ff354f")]),
    ]
    for y, label, items in rows:
        chip_svg.append(f'<text x="625" y="{y - 18}" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">{label}</text>')
        for i, (name, accent) in enumerate(items):
            x = 625 + i * 177
            chip_svg.append(
                f'<rect x="{x}" y="{y}" width="162" height="81" rx="9" fill="#0d182c" stroke="#284465"/>'
                f'<path d="M{x + 12} {y + 80} L{x + 72} {y + 80}" fill="none" stroke="{accent}" stroke-width="1.5"/>'
                f'<text x="{x + 14}" y="{y + 48}" font-size="22">{name}</text>'
            )

    nodes_slow = "".join(
        [
            orbit_node("PY", "#247bff", -20, 168),
            orbit_node("JS", "#247bff", 70, 168),
            orbit_node("DJ", "#247bff", 160, 168),
            orbit_node("SQL", "#247bff", 250, 168),
        ]
    )
    nodes_mid = "".join(
        [
            orbit_node("AWS", "#ff354f", 20, 210),
            orbit_node("NGX", "#ff354f", 140, 210),
            orbit_node("PAY", "#ff354f", 260, 210),
        ]
    )
    nodes_fast = "".join(
        [
            orbit_node("DRF", "#a0caff", 50, 248),
            orbit_node("API", "#a0caff", 170, 248),
            orbit_node("LIN", "#a0caff", 300, 248),
        ]
    )

    return (
        svg_open("stack", 680, "Vaibhav Singh — stack", "Python, Django, JavaScript, AWS, PostgreSQL, Nginx, Razorpay.")
        + style("stack")
        + defs("stack", 680)
        + card_bg("stack", 680)
        + '<text x="42" y="39" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">03 / MY ENGINE ROOM</text>'
        + '<text x="39" y="102" font-size="40">TOOLS CHANGE. CURIOSITY DOESN&apos;T.</text>'
        + '<text x="42" y="135" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">LANGUAGES / SYSTEMS / INTELLIGENCE</text>'
        + chevrons(1090, 73)
        + '<ellipse cx="300" cy="388" rx="300" ry="245" fill="url(#stack-halo)"/>'
        + '<circle cx="300" cy="393" r="168" fill="none" stroke="#247bff" opacity=".28"/>'
        + '<circle cx="300" cy="393" r="168" fill="none" stroke="#247bff" stroke-width="2" stroke-dasharray="80 976">'
        + '<animate attributeName="stroke-dashoffset" dur="11s" values="0;-1056" repeatCount="indefinite"/>'
        + "</circle>"
        + '<circle cx="300" cy="393" r="210" fill="none" stroke="#ff354f" opacity=".22"/>'
        + '<circle cx="300" cy="393" r="210" fill="none" stroke="#ff354f" stroke-width="2" stroke-dasharray="80 1240">'
        + '<animate attributeName="stroke-dashoffset" dur="14s" values="0;-1320" repeatCount="indefinite"/>'
        + "</circle>"
        + '<circle cx="300" cy="393" r="248" fill="none" stroke="#5b9fff" opacity=".16"/>'
        + '<g class="spin-slow">' + nodes_slow + "</g>"
        + '<g class="spin-mid">' + nodes_mid + "</g>"
        + '<g class="spin-fast">' + nodes_fast + "</g>"
        + '<circle cx="300" cy="393" r="76" fill="#0c1b36" stroke="#285cb1"/>'
        + '<circle cx="300" cy="393" r="85" fill="none" stroke="#287dff" opacity=".2" class="pulse"/>'
        + '<path d="m300 338 45 26v53l-45 26-45-26v-53Z" fill="#123365" stroke="#438fff"/>'
        + '<path d="m300 338 45 26-45 26-45-26Z" fill="#245caf"/>'
        + '<path d="M300 390v53 M255 364l45 26 45-26" fill="none" stroke="#83b7ff"/>'
        + '<text x="278" y="401" font-size="32">VS</text>'
        + '<text x="70" y="628" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">CODE IS THE TOOL. IMPACT IS THE POINT.</text>'
        + '<path d="M580 184 L580 631" fill="none" stroke="#223c60" stroke-width="1.5"/>'
        + "".join(chip_svg)
        + '<text x="625" y="629" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">BUILD / SHIP / LEARN / REPEAT</text>'
        + "</g></svg>"
    )


def barcode(x: int = 116, y: int = 582) -> str:
    bars = []
    pos = x
    pattern = [2.5, 1, 1, 2.5, 1, 1, 2.5, 1]
    for i in range(72):
        w = pattern[i % len(pattern)]
        h = 41 if i % 7 == 0 else 35
        bars.append(f'<rect x="{pos:.2f}" y="{y}" width="{w}" height="{h}" fill="#9cb2d2"/>')
        pos += w + 1.35
    return "".join(bars)


def ticker(x: int, y: int, final: str, color: str, steps: list[str]) -> str:
    texts = []
    for i, val in enumerate(steps):
        texts.append(f'<text x="{x}" y="{y + i * 70}" font-size="54" fill="{color}">{val}</text>')
    return (
        f'<g transform="translate(0 -280)">'
        f'<animateTransform attributeName="transform" type="translate" dur="2.4s" '
        f'values="0 0;0 0;0 -70;0 -140;0 -210;0 -280" keyTimes="0;.2;.4;.6;.8;1" calcMode="discrete" fill="freeze"/>'
        + "".join(texts)
        + "</g>"
    )


def build_id() -> str:
    extra = f"""
<image id="id-photo" width="360" height="420" href="{PORTRAIT}" preserveAspectRatio="xMidYMid slice"/>
<clipPath id="id-badge-photo"><rect x="115" y="253" width="306" height="235" rx="12"/></clipPath>
<clipPath id="id-badge-clip"><rect x="93" y="191" width="350" height="473" rx="20"/></clipPath>
<clipPath id="id-count-0"><rect x="535" y="196" width="150" height="56"/></clipPath>
<clipPath id="id-count-1"><rect x="752" y="196" width="150" height="56"/></clipPath>
<clipPath id="id-count-2"><rect x="969" y="196" width="150" height="56"/></clipPath>
"""
    repos = [
        (376, "Medical Counselling Center", 560, "LIVE"),
        (441, "Unibook", 420, "LIVE"),
        (506, "Vani E-commerce", 360, "LIVE"),
        (571, "Task Manager Pro", 280, "LIVE"),
    ]
    repo_svg = []
    for y, name, width, tag in repos:
        repo_svg.append(
            f'<text x="520" y="{y}" font-size="12" fill="#a9c0df" class="mono">{name}</text>'
            f'<rect x="520" y="{y + 13}" width="575" height="12" rx="3" fill="#132842"/>'
            f'<rect x="520" y="{y + 13}" width="{width}" height="12" rx="3" fill="#247bff">'
            f'<animate attributeName="width" dur="2s" values="0;0;{width}" keyTimes="0;.25;1" fill="freeze"/></rect>'
            f'<text x="1110" y="{y + 23}" font-size="14" fill="#73b0ff" class="mono">{tag}</text>'
        )

    badge = (
        '<g class="motion">'
        '<animateTransform attributeName="transform" type="translate" dur="1.65s" values="0 -720;0 -720;0 9;0 -3;0 0" keyTimes="0;.06;.74;.88;1" fill="freeze"/>'
        '<g class="swing">'
        '<rect x="244" y="-55" width="48" height="217" rx="7" fill="#153f83" stroke="#367be0"/>'
        '<rect x="247" y="-54" width="42" height="215" rx="5" fill="url(#id-carbon)"/>'
        '<path d="M249 -20 L249 155" fill="none" stroke="#689ddd" stroke-width="1.5"/>'
        '<path d="M287 -20 L287 155" fill="none" stroke="#071d40" stroke-width="1.5"/>'
        '<text x="276" y="-17" font-size="10" fill="#d8e8ff" class="mono" transform="rotate(90 276 -17)">VAIBHAV SINGH // VS05</text>'
        '<rect x="246" y="147" width="44" height="42" rx="8" fill="url(#id-steel)" stroke="#b7c9e1"/>'
        '<rect x="255" y="156" width="26" height="20" rx="4" fill="#070e1c" stroke="#193451"/>'
        '<rect x="251" y="177" width="34" height="29" rx="8" fill="url(#id-steel)" stroke="#a9b9d0"/>'
        '<rect x="93" y="191" width="350" height="473" rx="20" fill="#101c30" stroke="#518fea"/>'
        '<rect x="96" y="194" width="344" height="467" rx="18" fill="url(#id-carbon)"/>'
        '<rect x="95" y="193" width="346" height="7" rx="3" fill="#ff354f"/>'
        '<rect x="242" y="202" width="51" height="8" rx="4" fill="#030711" stroke="#223b5b"/>'
        '<text x="116" y="236" font-size="20">VS / BUILDER PASS</text>'
        '<text x="368" y="235" font-size="15" fill="#247bff" class="mono">05</text>'
        '<rect x="115" y="253" width="306" height="235" rx="12" fill="#091224" stroke="#28558b"/>'
        + '<g clip-path="url(#id-badge-photo)">'
        + use_photo("id-photo", 128, 230, 280, 330)
        + "</g>"
        +
        '<rect x="116" y="254" width="304" height="233" rx="11" fill="none" stroke="#8cc3ff" stroke-width="2" stroke-dasharray="60 1014">'
        '<animate attributeName="stroke-dashoffset" dur="5.5s" values="0;-1074" repeatCount="indefinite"/></rect>'
        '<rect x="126" y="450" width="168" height="28" rx="5" fill="#247bff"/>'
        '<text x="138" y="469" font-size="10" fill="#f2f5ff" class="mono" letter-spacing="1">SENIOR AI @ SPOTO</text>'
        '<text x="115" y="533" font-size="32">VAIBHAV SINGH</text>'
        '<text x="116" y="556" font-size="10" fill="#83a0c5" class="mono">GORAKHPUR / INDIA</text>'
        '<rect x="366" y="510" width="49" height="39" rx="7" fill="#d2ad60" stroke="#f8d894"/>'
        '<path d="M367 523 L414 523" fill="none" stroke="#917539" stroke-width="1.5"/>'
        '<path d="M367 536 L414 536" fill="none" stroke="#917539" stroke-width="1.5"/>'
        '<path d="M381 511 L381 548" fill="none" stroke="#917539" stroke-width="1.5"/>'
        '<path d="M400 511 L400 548" fill="none" stroke="#917539" stroke-width="1.5"/>'
        + barcode()
        + '<text x="116" y="644" font-size="9" fill="#7998bf" class="mono">INDEPENDENT ENGINEER ID · VS05</text>'
        + '<g clip-path="url(#id-badge-clip)">'
        + '<rect x="-500" y="191" width="330" height="473" fill="url(#id-foil)" transform="skewX(-18)">'
        + '<animate attributeName="x" dur="9s" values="-500;-500;900;900" keyTimes="0;.22;.62;1" fill="freeze" repeatCount="indefinite"/>'
        + "</rect></g></g></g>"
    )

    return (
        svg_open("id", 800, "Vaibhav Singh — builder credentials", "Public snapshot of work and impact.")
        + style("id")
        + defs("id", 800, extra)
        + card_bg("id", 800)
        + '<ellipse cx="241" cy="417" rx="290" ry="360" fill="url(#id-halo)"/>'
        + '<ellipse cx="450" cy="735" rx="260" ry="280" fill="url(#id-red-halo)"/>'
        + '<text x="37" y="178" font-size="100" fill="#11264a">THE</text>'
        + '<text x="37" y="266" font-size="100" fill="#11264a">HUMAN.</text>'
        + '<text x="38" y="729" font-size="44" fill="#183153">BEHIND THE CODE.</text>'
        + '<text x="520" y="42" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">04 / BUILDER CREDENTIALS</text>'
        + '<text x="516" y="104" font-size="40">REAL WORK. REAL IMPACT.</text>'
        + '<text x="520" y="132" font-size="11" fill="#8e9db9" class="mono">PUBLIC SNAPSHOT / 24 OCT 2026</text>'
        + badge
        + '<rect x="520" y="164" width="198" height="127" rx="9" fill="#101c31" stroke="#28476d"/>'
        + '<text x="536" y="188" font-size="10" fill="#8aa7cf" class="mono">LEETCODE</text>'
        + '<g clip-path="url(#id-count-0)">'
        + ticker(536, 246, "100+", "#ff354f", ["0", "25", "50", "80", "100+"])
        + "</g>"
        + '<text x="537" y="274" font-size="9" fill="#688ab5" class="mono">PROBLEMS SOLVED</text>'
        + '<rect x="737" y="164" width="198" height="127" rx="9" fill="#101c31" stroke="#28476d"/>'
        + '<text x="753" y="188" font-size="10" fill="#8aa7cf" class="mono">REPOSITORIES</text>'
        + '<g clip-path="url(#id-count-1)">'
        + ticker(753, 246, "13", "#73b0ff", ["0", "4", "7", "10", "13"])
        + "</g>"
        + '<text x="754" y="274" font-size="9" fill="#688ab5" class="mono">PUBLIC GITHUB</text>'
        + '<rect x="954" y="164" width="198" height="127" rx="9" fill="#101c31" stroke="#28476d"/>'
        + '<text x="970" y="188" font-size="10" fill="#8aa7cf" class="mono">EXPERIENCE</text>'
        + '<g clip-path="url(#id-count-2)">'
        + ticker(970, 246, "2+", "#73b0ff", ["0", "1", "1+", "2", "2+"])
        + "</g>"
        + '<text x="971" y="274" font-size="9" fill="#688ab5" class="mono">YEARS SHIPPING</text>'
        + '<text x="520" y="334" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">MOST-SHIPPED / LIVE PRODUCTS</text>'
        + lucide(1128, 318, 0.75, "#ff354f", icon_star())
        + "".join(repo_svg)
        + '<rect x="520" y="635" width="632" height="117" rx="10" fill="#0b1b33" stroke="#2c5b96"/>'
        + '<rect x="537" y="652" width="76" height="28" rx="5" fill="#ff354f"/>'
        + '<text x="549" y="671" font-size="10" fill="#f2f5ff" class="mono" letter-spacing="1">NOW</text>'
        + '<text x="537" y="706" font-size="26">Building AI-powered software at Spoto.in</text>'
        + '<text x="537" y="731" font-size="11" fill="#88a9d3" class="mono">Django REST · APIs · Bengaluru remote.</text>'
        + "</g></svg>"
    )


def social_row(y: int, href: str, accent: str, title: str, subtitle: str, icon: str) -> str:
    return (
        f'<a href="{href}" target="_blank">'
        f'<rect x="507" y="{y}" width="647" height="86" rx="10" fill="#101c30" stroke="#294e79"/>'
        f'<rect x="507" y="{y}" width="4" height="86" rx="2" fill="{accent}"/>'
        + icon
        + f'<text x="584" y="{y + 37}" font-size="28">{title}</text>'
        + f'<text x="585" y="{y + 62}" font-size="12" fill="#8facd4" class="mono">{subtitle}</text>'
        + f'<g class="nudge">{lucide(1100, y + 30, 1.1, accent, icon_arrow())}</g>'
        + "</a>"
    )


def build_connect() -> str:
    extra = f'<image id="connect-photo" width="360" height="420" href="{POINTING}" preserveAspectRatio="xMidYMid meet"/>'
    return (
        svg_open("connect", 640, "Vaibhav Singh — connect", "LinkedIn, GitHub, email, and portfolio.")
        + style("connect")
        + defs("connect", 640, extra)
        + card_bg("connect", 640)
        + '<ellipse cx="215" cy="315" rx="335" ry="290" fill="url(#connect-halo)"/>'
        + '<ellipse cx="421" cy="403" rx="190" ry="260" fill="url(#connect-red-halo)"/>'
        + '<text x="37" y="38" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">05 / START A CONVERSATION</text>'
        + '<text x="36" y="125" font-size="72" fill="#f2f5ff">LET\'S</text>'
        + '<text x="36" y="194" font-size="72" fill="#183b6e">CONNECT.</text>'
        + use_photo("connect-photo", 40, 190, 430, 430)
        + '<rect x="45" y="545" width="450" height="94" fill="url(#connect-shade)"/>'
        + '<text x="507" y="79" font-size="42">BUILD SOMETHING GREAT.</text>'
        + '<text x="509" y="112" font-size="13" fill="#9cb6da" class="mono">Ideas. Opportunities. Your next move.</text>'
        + chevrons(1107, 91)
        + social_row(148, "https://www.linkedin.com/in/vaibhav-singh-2a5991229/", "#247bff", "LinkedIn", "Connect &amp; exchange ideas", linkedin_icon(530, 174))
        + social_row(255, "https://github.com/vaibhav-singh05", "#f2f5ff", "GitHub", "github.com/vaibhav-singh05", github_icon(530, 281))
        + social_row(362, "mailto:vaibhavsingh273010@gmail.com", "#ff354f", "Email", "vaibhavsingh273010@gmail.com", lucide(530, 388, 1.4, "#ff354f", '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/>'))
        + social_row(469, "https://vaibhav-singh05.github.io/Portfolio-Website/", "#247bff", "Portfolio", "vaibhav-singh05.github.io", lucide(530, 495, 1.4, "#247bff", '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'))
        + '<text x="511" y="609" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">GOOD PEOPLE. GOOD IDEAS. LET\'S TALK.</text>'
        + "</g></svg>"
    )


def write_readme() -> None:
    (ROOT / "README.md").write_text(
        """<p align="center">
  <img src="./assets/hero.svg?v=6" width="100%" alt="Hi, I'm Vaibhav Singh — Senior AI Software Engineer at Spoto.in. Building AI-powered, scalable backends with Python, Django REST and APIs." />
</p>

<img src="./assets/about-life.svg?v=6" width="100%" alt="Django REST and APIs, AI and cloud backends, full-stack shipping. Backend systems, live products, and problem solving." />

<img src="./assets/stack.svg?v=6" width="100%" alt="My stack: Python, JavaScript, C/C++, Django, DRF, PostgreSQL, AWS, Nginx, and Razorpay." />

### Things I've built

| Project | What it does | Focus |
| :--- | :--- | :--- |
| [**Medical Counselling Center**](https://medicalcounsellingcenter.com/) | Live counselling platform with payments and admin workflows | Django + Payments |
| [**Unibook**](https://unibook-krly.onrender.com) | Student book exchange for campus | Full-stack Django |
| [**Vani**](https://vani-6hcu.onrender.com) | E-commerce storefront with cart and checkout | Commerce + Django |
| [**Task Manager Pro**](https://task-manager-a4jc.onrender.com) | Productivity app for tasks and tracking | Product + Django |
| [**Quora Clone**](https://quora-phjc.onrender.com) | Q&A platform with voting and search | Community + Django |
| [**Educa**](https://vaibhav-singh05.github.io/Educa-Web/) | Education landing and course pages | Frontend |

<img src="./assets/id-dashboard.svg?v=6" width="100%" alt="Vaibhav's builder ID and public dashboard. 100+ LeetCode, 13 public repositories, 2+ years shipping. Snapshot: October 24, 2026." />

<img src="./assets/connect.svg?v=6" width="100%" alt="Let's build what's next. Connect on LinkedIn, GitHub, email, or the live portfolio." />

<p align="center">
  <a href="https://www.linkedin.com/in/vaibhav-singh-2a5991229/">LinkedIn</a> &nbsp;·&nbsp;
  <a href="https://github.com/vaibhav-singh05">GitHub</a> &nbsp;·&nbsp;
  <a href="mailto:vaibhavsingh273010@gmail.com">Email</a> &nbsp;·&nbsp;
  <a href="https://vaibhav-singh05.github.io/Portfolio-Website/">Portfolio</a>
</p>

<p align="center"><sub>Curious by default. Building with intent.</sub></p>
""",
        encoding="utf-8",
    )


def write_preview() -> None:
    (ROOT / "preview.html").write_text(
        """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Vaibhav profile preview</title>
  <style>
    body { margin: 0; background: #0d1117; color: #c9d1d9; font-family: Segoe UI, sans-serif; }
    main { max-width: 980px; margin: 32px auto; padding: 0 16px 64px; }
    img { width: 100%; display: block; margin: 18px 0; }
    table { width: 100%; border-collapse: collapse; color: #c9d1d9; }
    td, th { border: 1px solid #30363d; padding: 10px; text-align: left; }
    a { color: #58a6ff; }
  </style>
</head>
<body>
  <main>
    <img src="./assets/hero.svg" alt="hero"/>
    <img src="./assets/about-life.svg" alt="about"/>
    <img src="./assets/stack.svg" alt="stack"/>
    <img src="./assets/id-dashboard.svg" alt="id"/>
    <img src="./assets/connect.svg" alt="connect"/>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    mapping = {
        "hero.svg": build_hero(),
        "about-life.svg": build_about(),
        "stack.svg": build_stack(),
        "id-dashboard.svg": build_id(),
        "connect.svg": build_connect(),
    }
    for name, markup in mapping.items():
        dest = ASSETS / name
        dest.write_text(markup, encoding="utf-8")
        print(f"{name:20} {dest.stat().st_size / 1024:.1f} KB")
    write_readme()
    write_preview()
    print("profile assets ready")


if __name__ == "__main__":
    main()
