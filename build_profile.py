"""Build GitHub-safe, self-contained profile SVGs (Udit-style midnight glass)."""
from __future__ import annotations

import base64
import io
import math
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


def ellipse_pts(cx: float, cy: float, rx: float, ry: float, rot_deg: float, n: int = 100) -> list[tuple[float, float]]:
    rot = math.radians(rot_deg)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = rx * math.cos(t)
        y = ry * math.sin(t)
        pts.append(
            (
                cx + x * math.cos(rot) - y * math.sin(rot),
                cy + x * math.sin(rot) + y * math.cos(rot),
            )
        )
    return pts


def ellipse_d(pts: list[tuple[float, float]]) -> str:
    bits = [f"M{pts[0][0]:.2f} {pts[0][1]:.2f}"]
    bits.extend(f"L{x:.2f} {y:.2f}" for x, y in pts[1:])
    bits.append("Z")
    return " ".join(bits)


def motion_from(pts: list[tuple[float, float]], start_idx: int) -> tuple[str, tuple[float, float]]:
    ordered = pts[start_idx:] + pts[: start_idx + 1]
    x0, y0 = ordered[0]
    bits = ["M0.00 0.00"]
    bits.extend(f"L{x - x0:.2f} {y - y0:.2f}" for x, y in ordered[1:])
    return " ".join(bits), ordered[0]


def brand_mark(name: str, fill: str) -> str:
    # Official Simple Icons 24x24 marks — same family Udit uses on the orbit.
    paths = {
        "python": "M14.25.18l.9.2.73.26.59.3.45.32.34.34.25.34.16.33.1.3.04.26.02.2-.01.13V8.5l-.05.63-.13.55-.21.46-.26.38-.3.31-.33.25-.35.19-.35.14-.33.1-.3.07-.26.04-.21.02H8.77l-.69.05-.59.14-.5.22-.41.27-.33.32-.27.35-.2.36-.15.37-.1.35-.07.32-.04.27-.02.21v3.06H3.17l-.21-.03-.28-.07-.32-.12-.35-.18-.36-.26-.36-.36-.35-.46-.32-.59-.28-.73-.21-.88-.14-1.05-.05-1.23.06-1.22.16-1.04.24-.87.32-.71.36-.57.4-.44.42-.33.42-.24.4-.16.36-.1.32-.05.24-.01h.16l.06.01h8.16v-.83H6.18l-.01-2.75-.02-.37.05-.34.11-.31.17-.28.25-.26.31-.23.38-.2.44-.18.51-.15.58-.12.64-.1.71-.06.77-.04.84-.02 1.27.05zm-6.3 1.98l-.23.33-.08.41.08.41.23.34.33.22.41.09.41-.09.33-.22.23-.34.08-.41-.08-.41-.23-.33-.33-.22-.41-.09-.41.09zm13.09 3.95l.28.06.32.12.35.18.36.27.36.35.35.47.32.59.28.73.21.88.14 1.04.05 1.23-.06 1.23-.16 1.04-.24.86-.32.71-.36.57-.4.45-.42.33-.42.24-.4.16-.36.09-.32.05-.24.02-.16-.01h-8.22v.82h5.84l.01 2.76.02.36-.05.34-.11.31-.17.29-.25.25-.31.24-.38.2-.44.17-.51.15-.58.13-.64.09-.71.07-.77.04-.84.01-1.27-.04-1.07-.14-.9-.2-.73-.25-.59-.3-.45-.33-.34-.34-.25-.34-.16-.33-.1-.3-.04-.25-.02-.2.01-.13v-5.34l.05-.64.13-.54.21-.46.26-.38.3-.32.33-.24.35-.2.35-.14.33-.1.3-.06.26-.04.21-.02.13-.01h5.84l.69-.05.59-.14.5-.21.41-.28.33-.32.27-.35.2-.36.15-.36.1-.35.07-.32.04-.28.02-.21V6.07h2.09l.14.01zm-6.47 14.25l-.23.33-.08.41.08.41.23.33.33.23.41.08.41-.08.33-.23.23-.33.08-.41-.08-.41-.23-.33-.33-.23-.41-.08-.41.08z",
        "js": "M0 0h24v24H0V0zm22.034 18.276c-.175-1.095-.888-2.015-3.003-2.873-.736-.345-1.554-.585-1.797-1.14-.091-.33-.105-.51-.046-.705.15-.646.915-.84 1.515-.66.39.12.75.42.976.9 1.034-.676 1.034-.676 1.755-1.125-.27-.42-.404-.601-.586-.78-.63-.705-1.469-1.065-2.834-1.034l-.705.089c-.676.165-1.32.525-1.71 1.005-1.14 1.291-.811 3.541.569 4.471 1.365 1.02 3.361 1.244 3.616 2.205.24 1.17-.87 1.545-1.966 1.41-.811-.18-1.26-.586-1.755-1.336l-1.83 1.051c.21.48.45.689.81 1.109 1.74 1.756 6.09 1.666 6.871-1.004.029-.09.24-.705.074-1.65l.046.067zm-8.983-7.245h-2.248c0 1.938-.009 3.864-.009 5.805 0 1.232.063 2.363-.138 2.711-.33.689-1.18.601-1.566.48-.396-.196-.597-.466-.83-.855-.063-.105-.11-.196-.127-.196l-1.825 1.125c.305.63.75 1.172 1.324 1.517.855.51 2.004.675 3.207.405.783-.226 1.458-.691 1.811-1.411.51-.93.402-2.07.397-3.346.012-2.054 0-4.109 0-6.179l.004-.056z",
        "django": "M11.146 0h3.924v18.166c-2.013.382-3.491.535-5.096.535-4.791 0-7.288-2.166-7.288-6.32 0-4.002 2.65-6.6 6.753-6.6.637 0 1.121.05 1.707.203zm0 9.143a3.894 3.894 0 00-1.325-.204c-1.988 0-3.134 1.223-3.134 3.365 0 2.09 1.096 3.236 3.109 3.236.433 0 .79-.025 1.35-.102V9.142zM21.314 6.06v9.098c0 3.134-.229 4.638-.917 5.937-.637 1.249-1.478 2.039-3.211 2.905l-3.644-1.733c1.733-.815 2.574-1.53 3.109-2.625.561-1.121.739-2.421.739-5.835V6.059h3.924zM17.39.021h3.924v4.026H17.39z",
        "postgres": "M23.5594 14.7228a.5269.5269 0 0 0-.0563-.1191c-.139-.2632-.4768-.3418-1.0074-.2321-1.6533.3411-2.2935.1312-2.5256-.0191 1.342-2.0482 2.445-4.522 3.0411-6.8297.2714-1.0507.7982-3.5237.1222-4.7316a1.5641 1.5641 0 0 0-.1509-.235C21.6931.9086 19.8007.0248 17.5099.0005c-1.4947-.0158-2.7705.3461-3.1161.4794a9.449 9.449 0 0 0-.5159-.0816 8.044 8.044 0 0 0-1.3114-.1278c-1.1822-.0184-2.2038.2642-3.0498.8406-.8573-.3211-4.7888-1.645-7.2219.0788C.9359 2.1526.3086 3.8733.4302 6.3043c.0409.818.5069 3.334 1.2423 5.7436.4598 1.5065.9387 2.7019 1.4334 3.582.553.9942 1.1259 1.5933 1.7143 1.7895.4474.1491 1.1327.1441 1.8581-.7279.8012-.9635 1.5903-1.8258 1.9446-2.2069.4351.2355.9064.3625 1.39.3772a.0569.0569 0 0 0 .0004.0041 11.0312 11.0312 0 0 0-.2472.3054c-.3389.4302-.4094.5197-1.5002.7443-.3102.064-1.1344.2339-1.1464.8115-.0025.1224.0329.2309.0919.3268.2269.4231.9216.6097 1.015.6331 1.3345.3335 2.5044.092 3.3714-.6787-.017 2.231.0775 4.4174.3454 5.0874.2212.5529.7618 1.9045 2.4692 1.9043.2505 0 .5263-.0291.8296-.0941 1.7819-.3821 2.5557-1.1696 2.855-2.9059.1503-.8707.4016-2.8753.5388-4.1012.0169-.0703.0357-.1207.057-.1362.0007-.0005.0697-.0471.4272.0307a.3673.3673 0 0 0 .0443.0068l.2539.0223.0149.001c.8468.0384 1.9114-.1426 2.5312-.4308.6438-.2988 1.8057-1.0323 1.5951-1.6698zM2.371 11.8765c-.7435-2.4358-1.1779-4.8851-1.2123-5.5719-.1086-2.1714.4171-3.6829 1.5623-4.4927 1.8367-1.2986 4.8398-.5408 6.108-.13-.0032.0032-.0066.0061-.0098.0094-2.0238 2.044-1.9758 5.536-1.9708 5.7495-.0002.0823.0066.1989.0162.3593.0348.5873.0996 1.6804-.0735 2.9184-.1609 1.1504.1937 2.2764.9728 3.0892.0806.0841.1648.1631.2518.2374-.3468.3714-1.1004 1.1926-1.9025 2.1576-.5677.6825-.9597.5517-1.0886.5087-.3919-.1307-.813-.5871-1.2381-1.3223-.4796-.839-.9635-2.0317-1.4155-3.5126zm6.0072 5.0871c-.1711-.0428-.3271-.1132-.4322-.1772.0889-.0394.2374-.0902.4833-.1409 1.2833-.2641 1.4815-.4506 1.9143-1.0002.0992-.126.2116-.2687.3673-.4426a.3549.3549 0 0 0 .0737-.1298c.1708-.1513.2724-.1099.4369-.0417.156.0646.3078.26.3695.4752.0291.1016.0619.2945-.0452.4444-.9043 1.2658-2.2216 1.2494-3.1676 1.0128zm2.094-3.988-.0525.141c-.133.3566-.2567.6881-.3334 1.003-.6674-.0021-1.3168-.2872-1.8105-.8024-.6279-.6551-.9131-1.5664-.7825-2.5004.1828-1.3079.1153-2.4468.079-3.0586-.005-.0857-.0095-.1607-.0122-.2199.2957-.2621 1.6659-.9962 2.6429-.7724.4459.1022.7176.4057.8305.928.5846 2.7038.0774 3.8307-.3302 4.7363-.084.1866-.1633.3629-.2311.5454zm7.3637 4.5725c-.0169.1768-.0358.376-.0618.5959l-.146.4383a.3547.3547 0 0 0-.0182.1077c-.0059.4747-.054.6489-.115.8693-.0634.2292-.1353.4891-.1794 1.0575-.11 1.4143-.8782 2.2267-2.4172 2.5565-1.5155.3251-1.7843-.4968-2.0212-1.2217a6.5824 6.5824 0 0 0-.0769-.2266c-.2154-.5858-.1911-1.4119-.1574-2.5551.0165-.5612-.0249-1.9013-.3302-2.6462.0044-.2932.0106-.5909.019-.8918a.3529.3529 0 0 0-.0153-.1126 1.4927 1.4927 0 0 0-.0439-.208c-.1226-.4283-.4213-.7866-.7797-.9351-.1424-.059-.4038-.1672-.7178-.0869.067-.276.1831-.5875.309-.9249l.0529-.142c.0595-.16.134-.3257.213-.5012.4265-.9476 1.0106-2.2453.3766-5.1772-.2374-1.0981-1.0304-1.6343-2.2324-1.5098-.7207.0746-1.3799.3654-1.7088.5321a5.6716 5.6716 0 0 0-.1958.1041c.0918-1.1064.4386-3.1741 1.7357-4.4823a4.0306 4.0306 0 0 1 .3033-.276.3532.3532 0 0 0 .1447-.0644c.7524-.5706 1.6945-.8506 2.802-.8325.4091.0067.8017.0339 1.1742.081 1.939.3544 3.2439 1.4468 4.0359 2.3827.8143.9623 1.2552 1.9315 1.4312 2.4543-1.3232-.1346-2.2234.1268-2.6797.779-.9926 1.4189.543 4.1729 1.2811 5.4964.1353.2426.2522.4522.2889.5413.2403.5825.5515.9713.7787 1.2552.0696.087.1372.1714.1885.245-.4008.1155-1.1208.3825-1.0552 1.717-.0123.1563-.0423.4469-.0834.8148-.0461.2077-.0702.4603-.0994.7662zm.8905-1.6211c-.0405-.8316.2691-.9185.5967-1.0105a2.8566 2.8566 0 0 0 .135-.0406 1.202 1.202 0 0 0 .1342.103c.5703.3765 1.5823.4213 3.0068.1344-.2016.1769-.5189.3994-.9533.6011-.4098.1903-1.0957.333-1.7473.3636-.7197.0336-1.0859-.0807-1.1721-.151zm.5695-9.2712c-.0059.3508-.0542.6692-.1054 1.0017-.055.3576-.112.7274-.1264 1.1762-.0142.4368.0404.8909.0932 1.3301.1066.887.216 1.8003-.2075 2.7014a3.5272 3.5272 0 0 1-.1876-.3856c-.0527-.1276-.1669-.3326-.3251-.6162-.6156-1.1041-2.0574-3.6896-1.3193-4.7446.3795-.5427 1.3408-.5661 2.1781-.463zm.2284 7.0137a12.3762 12.3762 0 0 0-.0853-.1074l-.0355-.0444c.7262-1.1995.5842-2.3862.4578-3.4385-.0519-.4318-.1009-.8396-.0885-1.2226.0129-.4061.0666-.7543.1185-1.0911.0639-.415.1288-.8443.1109-1.3505.0134-.0531.0188-.1158.0118-.1902-.0457-.4855-.5999-1.938-1.7294-3.253-.6076-.7073-1.4896-1.4972-2.6889-2.0395.5251-.1066 1.2328-.2035 2.0244-.1859 2.0515.0456 3.6746.8135 4.8242 2.2824a.908.908 0 0 1 .0667.1002c.7231 1.3556-.2762 6.2751-2.9867 10.5405zm-8.8166-6.1162c-.025.1794-.3089.4225-.6211.4225a.5821.5821 0 0 1-.0809-.0056c-.1873-.026-.3765-.144-.5059-.3156-.0458-.0605-.1203-.178-.1055-.2844.0055-.0401.0261-.0985.0925-.1488.1182-.0894.3518-.1226.6096-.0867.3163.0441.6426.1938.6113.4186zm7.9305-.4114c.0111.0792-.049.201-.1531.3102-.0683.0717-.212.1961-.4079.2232a.5456.5456 0 0 1-.075.0052c-.2935 0-.5414-.2344-.5607-.3717-.024-.1765.2641-.3106.5611-.352.297-.0414.6111.0088.6356.1851z",
        "aws": "M6.763 10.036c0 .296.032.535.088.71.064.176.144.368.256.576.04.063.056.127.056.183 0 .08-.048.16-.152.24l-.503.335a.383.383 0 0 1-.208.072c-.08 0-.16-.04-.239-.112a2.47 2.47 0 0 1-.287-.375 6.18 6.18 0 0 1-.248-.471c-.622.734-1.405 1.101-2.347 1.101-.67 0-1.205-.191-1.596-.574-.391-.384-.59-.894-.59-1.533 0-.678.239-1.23.726-1.644.487-.415 1.133-.623 1.955-.623.272 0 .551.024.846.064.296.04.6.104.918.176v-.583c0-.607-.127-1.03-.375-1.277-.255-.248-.686-.367-1.3-.367-.28 0-.568.031-.863.103-.295.072-.583.16-.862.272a2.287 2.287 0 0 1-.28.104.488.488 0 0 1-.127.023c-.112 0-.168-.08-.168-.247v-.391c0-.128.016-.224.056-.28a.597.597 0 0 1 .224-.167c.279-.144.614-.264 1.005-.36a4.84 4.84 0 0 1 1.246-.151c.95 0 1.644.216 2.091.647.439.43.662 1.085.662 1.963v2.586zm-3.24 1.214c.263 0 .534-.048.822-.144.287-.096.543-.271.758-.51.128-.152.224-.32.272-.512.047-.191.08-.423.08-.694v-.335a6.66 6.66 0 0 0-.735-.136 6.02 6.02 0 0 0-.75-.048c-.535 0-.926.104-1.19.32-.263.215-.39.518-.39.917 0 .375.095.655.295.846.191.2.47.296.838.296zm6.41.862c-.144 0-.24-.024-.304-.08-.064-.048-.12-.16-.168-.311L7.586 5.55a1.398 1.398 0 0 1-.072-.32c0-.128.064-.2.191-.2h.783c.151 0 .255.025.31.08.065.048.113.16.16.312l1.342 5.284 1.245-5.284c.04-.16.088-.264.151-.312a.549.549 0 0 1 .32-.08h.638c.152 0 .256.025.32.08.063.048.12.16.151.312l1.261 5.348 1.381-5.348c.048-.16.104-.264.16-.312a.52.52 0 0 1 .311-.08h.743c.127 0 .2.065.2.2 0 .04-.009.08-.017.128a1.137 1.137 0 0 1-.056.2l-1.923 6.17c-.048.16-.104.263-.168.311a.51.51 0 0 1-.303.08h-.687c-.151 0-.255-.024-.32-.08-.063-.056-.119-.16-.15-.32l-1.238-5.148-1.23 5.14c-.04.16-.087.264-.15.32-.065.056-.177.08-.32.08zm10.256.215c-.415 0-.83-.048-1.229-.143-.399-.096-.71-.2-.918-.32-.128-.071-.215-.151-.247-.223a.563.563 0 0 1-.048-.224v-.407c0-.167.064-.247.183-.247.048 0 .096.008.144.024.048.016.12.048.2.08.271.12.566.215.878.279.319.064.63.096.95.096.502 0 .894-.088 1.165-.264a.86.86 0 0 0 .415-.758.777.777 0 0 0-.215-.559c-.144-.151-.416-.287-.807-.415l-1.157-.36c-.583-.183-1.014-.454-1.277-.813a1.902 1.902 0 0 1-.4-1.158c0-.335.073-.63.216-.886.144-.255.335-.479.575-.654.24-.184.51-.32.83-.415.32-.096.655-.136 1.006-.136.175 0 .359.008.535.032.183.024.35.056.518.088.16.04.312.08.455.127.144.048.256.096.336.144a.69.69 0 0 1 .24.2.43.43 0 0 1 .071.263v.375c0 .168-.064.256-.184.256a.83.83 0 0 1-.303-.096 3.652 3.652 0 0 0-1.532-.311c-.455 0-.815.071-1.062.223-.248.152-.375.383-.375.71 0 .224.08.416.24.567.159.152.454.304.877.44l1.134.358c.574.184.99.44 1.237.767.247.327.367.702.367 1.117 0 .343-.072.655-.207.926-.144.272-.336.511-.583.703-.248.2-.543.343-.886.447-.36.111-.734.167-1.142.167zM21.698 16.207c-2.626 1.94-6.442 2.969-9.722 2.969-4.598 0-8.74-1.7-11.87-4.526-.247-.223-.024-.527.272-.351 3.384 1.963 7.559 3.153 11.877 3.153 2.914 0 6.114-.607 9.06-1.852.439-.2.814.287.383.607zM22.792 14.961c-.336-.43-2.22-.207-3.074-.103-.255.032-.295-.192-.063-.36 1.5-1.053 3.967-.75 4.254-.399.287.36-.08 2.826-1.485 4.007-.215.184-.423.088-.327-.151.32-.79 1.03-2.57.695-2.994z",
        "nginx": "M12 0L1.605 6v12L12 24l10.395-6V6L12 0zm6 16.59c0 .705-.646 1.29-1.529 1.29-.631 0-1.351-.255-1.801-.81l-6-7.141v6.66c0 .721-.57 1.29-1.274 1.29H7.32c-.721 0-1.29-.6-1.29-1.29V7.41c0-.705.63-1.29 1.5-1.29.646 0 1.38.255 1.83.81l5.97 7.141V7.41c0-.721.6-1.29 1.29-1.29h.075c.72 0 1.29.6 1.29 1.29v9.18H18z",
        "cpp": "M22.394 6c-.167-.29-.398-.543-.652-.69L12.926.22c-.509-.294-1.34-.294-1.848 0L2.26 5.31c-.508.293-.923 1.013-.923 1.6v10.18c0 .294.104.62.271.91.167.29.398.543.652.69l8.816 5.09c.508.293 1.34.293 1.848 0l8.816-5.09c.254-.147.485-.4.652-.69.167-.29.27-.616.27-.91V6.91c.003-.294-.1-.62-.268-.91zM12 19.11c-3.92 0-7.109-3.19-7.109-7.11 0-3.92 3.19-7.11 7.11-7.11a7.133 7.133 0 016.156 3.553l-3.076 1.78a3.567 3.567 0 00-3.08-1.78A3.56 3.56 0 008.444 12 3.56 3.56 0 0012 15.555a3.57 3.57 0 003.08-1.778l3.078 1.78A7.135 7.135 0 0112 19.11zm7.11-6.715h-.79v.79h-.79v-.79h-.79v-.79h.79v-.79h.79v.79h.79zm2.962 0h-.79v.79h-.79v-.79h-.79v-.79h.79v-.79h.79v.79h.79z",
        "linux": "M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139z",
        "html": "M1.5 0h21l-1.91 21.563L11.977 24l-8.564-2.438L1.5 0zm7.031 9.75l-.232-2.718 10.059.003.23-2.622L5.412 4.41l.698 8.01h9.126l-.326 3.426-2.91.804-2.955-.81-.188-2.11H6.248l.33 4.171L12 19.351l5.379-1.443.744-8.157H8.531z",
        "razorpay": "M22.436 0l-11.91 7.773-1.174 4.276 6.625-4.297L11.65 24h4.391l6.395-24zM14.26 10.098L3.389 17.166 1.564 24h9.008l3.688-13.902Z",
    }
    rule = ' fill-rule="evenodd"' if name in {"js", "html", "postgres"} else ""
    return f'<g fill="{fill}"><path d="{paths[name]}"{rule}/></g>'


def traveling_icon(pts: list[tuple[float, float]], phase: float, dur: int, color: str, icon: str, radius: float = 29.5) -> str:
    idx = int(phase * len(pts)) % len(pts)
    motion, (x0, y0) = motion_from(pts, idx)
    mark = f'<g transform="translate(-16.5 -16.5) scale(1.375)">{brand_mark(icon, color)}</g>'
    return (
        f'<g transform="translate({x0:.2f} {y0:.2f})">'
        f'<g class="motion">'
        f'<animateMotion path="{motion}" dur="{dur}s" rotate="0" repeatCount="indefinite"/>'
        f'<circle r="{radius}" fill="#0d1729" stroke="{color}" stroke-opacity=".65"/>'
        f"{mark}"
        "</g>"
        f'<g class="still" display="none">'
        f'<circle r="{radius}" fill="#0d1729" stroke="{color}" stroke-opacity=".65"/>'
        f"{mark}"
        "</g></g>"
    )


def orbit_ring(pts: list[tuple[float, float]], color: str, dash_dur: int) -> str:
    d = ellipse_d(pts)
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity=".3"/>'
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="80 1300">'
        f'<animate attributeName="stroke-dashoffset" dur="{dash_dur}s" values="0;-1380" repeatCount="indefinite"/>'
        "</path>"
    )


def build_stack() -> str:
    chip_svg = []
    rows = [
        (226, "01 / LANGUAGES", [("Python", "python"), ("JavaScript", "js"), ("C / C++", "cpp")]),
        (358, "02 / BACKEND &amp; DATA", [("Django", "django"), ("DRF", "django"), ("PostgreSQL", "postgres")]),
        (490, "03 / CLOUD &amp; PAYMENTS", [("AWS", "aws"), ("Nginx", "nginx"), ("Razorpay", "razorpay")]),
    ]
    for y, label, items in rows:
        chip_svg.append(f'<text x="625" y="{y - 18}" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">{label}</text>')
        for i, (name, icon) in enumerate(items):
            x = 625 + i * 177
            accent = "#ff354f" if y == 490 else "#247bff"
            chip_svg.append(
                f'<rect x="{x}" y="{y}" width="162" height="81" rx="9" fill="#0d182c" stroke="#284465"/>'
                f'<path d="M{x + 12} {y + 80} L{x + 72} {y + 80}" fill="none" stroke="{accent}" stroke-width="1.5"/>'
                f'<g transform="translate({x + 14} {y + 18}) scale(0.958)">{brand_mark(icon, "#7db5ff")}</g>'
                f'<text x="{x + 14}" y="{y + 64}" font-size="24">{name}</text>'
            )

    inner = ellipse_pts(300, 393, 203, 111.5, -32, 120)
    mid = ellipse_pts(300, 393, 188, 140, 48, 120)
    outer = ellipse_pts(300, 393, 138, 180, -8, 120)

    travelers = (
        traveling_icon(inner, 0.00, 34, "#247bff", "python")
        + traveling_icon(inner, 0.25, 34, "#247bff", "js")
        + traveling_icon(inner, 0.50, 34, "#247bff", "django")
        + traveling_icon(inner, 0.75, 34, "#247bff", "postgres")
        + traveling_icon(mid, 0.08, 43, "#ff354f", "aws")
        + traveling_icon(mid, 0.33, 43, "#ff354f", "nginx")
        + traveling_icon(mid, 0.58, 43, "#ff354f", "html")
        + traveling_icon(mid, 0.83, 43, "#ff354f", "razorpay")
        + traveling_icon(outer, 0.12, 52, "#a0caff", "cpp")
        + traveling_icon(outer, 0.45, 52, "#a0caff", "linux")
        + traveling_icon(outer, 0.80, 52, "#a0caff", "js", 26.5)
    )

    return (
        svg_open("stack", 680, "Vaibhav Singh — stack", "Python, Django, JavaScript, AWS, PostgreSQL, Nginx, Razorpay.")
        + style("stack")
        + defs("stack", 680)
        + card_bg("stack", 680)
        + '<text x="42" y="39" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">03 / MY ENGINE ROOM</text>'
        + '<text x="39" y="102" font-size="47">TOOLS CHANGE. CURIOSITY DOESN&apos;T.</text>'
        + '<text x="42" y="135" font-size="11" fill="#8e9db9" class="mono" letter-spacing="1.6">LANGUAGES / SYSTEMS / INTELLIGENCE</text>'
        + chevrons(1090, 73)
        + '<ellipse cx="300" cy="388" rx="300" ry="245" fill="url(#stack-halo)"/>'
        + orbit_ring(inner, "#247bff", 11)
        + orbit_ring(mid, "#ff354f", 14)
        + orbit_ring(outer, "#5b9fff", 17)
        + travelers
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
  <img src="./assets/hero.svg?v=10" width="100%" alt="Hi, I'm Vaibhav Singh — Senior AI Software Engineer at Spoto.in. Building AI-powered, scalable backends with Python, Django REST and APIs." />
</p>

<img src="./assets/about-life.svg?v=10" width="100%" alt="Django REST and APIs, AI and cloud backends, full-stack shipping. Backend systems, live products, and problem solving." />

<img src="./assets/stack.svg?v=10" width="100%" alt="My stack: Python, JavaScript, C/C++, Django, DRF, PostgreSQL, AWS, Nginx, and Razorpay." />

<img src="./assets/id-dashboard.svg?v=10" width="100%" alt="Vaibhav's builder ID and public dashboard. 100+ LeetCode, 13 public repositories, 2+ years shipping. Snapshot: October 24, 2026." />

<img src="./assets/connect.svg?v=10" width="100%" alt="Let's build what's next. Connect on LinkedIn, GitHub, email, or the live portfolio." />

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
