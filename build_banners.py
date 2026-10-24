from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).parent / "assets"
NAVY = (7, 11, 22)
CARD = (12, 18, 32)
STROKE = (27, 39, 64)
BLUE = (36, 123, 255)
CRIMSON = (255, 53, 79)
WHITE = (244, 247, 251)
MUTED = (154, 166, 184)
MONO = (125, 141, 163)
BAR_BG = (22, 32, 51)


def font(size, bold=False):
    names = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def mono(size):
    for n in ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/cour.ttf"]:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(draw, box, r, fill, outline=None):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=1)


def banner(h):
    img = Image.new("RGB", (880, h), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 880, 4), fill=BLUE)
    d.rectangle((440, 0, 880, 4), fill=CRIMSON)
    return img, d


def heroo():
    img, d = banner(300)
    d.text((36, 22), "vaibhav-singh05 / profile", font=mono(16), fill=MONO)
    d.text((36, 58), "Hi. I am", font=font(24), fill=MUTED)
    d.text((36, 92), "VAIBHAV SINGH", font=font(46, True), fill=WHITE)
    d.text((36, 156), "Senior AI Software Engineer", font=font(22, True), fill=BLUE)
    d.text((36, 196), "I build AI-powered, scalable backends with Python, Django REST and APIs.", font=font(16), fill=MUTED)
    d.rounded_rectangle((36, 232, 44, 240), 2, fill=BLUE)
    d.text((54, 226), "Gorakhpur, Uttar Pradesh  |  Bengaluru Remote", font=font(15), fill=MUTED)
    d.rounded_rectangle((36, 260, 44, 268), 2, fill=CRIMSON)
    d.text((54, 254), "Spoto.in  |  Senior AI Software Engineer", font=font(15), fill=MUTED)
    img.save(OUT / "heroo.png", "PNG")


def about():
    img, d = banner(250)
    d.text((36, 24), "01  /  ABOUT LIFE", font=font(14, True), fill=BLUE)
    d.text((36, 52), "What I actually ship.", font=font(28, True), fill=WHITE)
    d.text((36, 90), "Backend systems, payments, and APIs that stay up in production.", font=font(15), fill=MUTED)

    bars = [
        ("DJANGO REST  |  APIS", 342),
        ("PYTHON  |  POSTGRESQL", 318),
        ("AWS  |  NGINX  |  PAYMENTS", 296),
    ]
    y = 128
    for label, w in bars:
        d.text((36, y), label, font=font(12), fill=MUTED)
        d.rounded_rectangle((36, y + 20, 416, y + 28), 4, fill=BAR_BG)
        d.rounded_rectangle((36, y + 20, 36 + w, y + 28), 4, fill=BLUE)
        y += 40

    rounded(d, (460, 36, 844, 214), 16, CARD, STROKE)
    d.text((484, 56), "INTERESTS", font=font(13, True), fill=BLUE)
    d.text((484, 88), "Backend Systems", font=font(22, True), fill=WHITE)
    d.text((484, 128), "Django | Razorpay | Juspay | AWS", font=font(14), fill=MUTED)
    d.text((484, 156), "B.Tech CSE | IKGPTU | CGPA 7.8 / 10", font=font(14), fill=MUTED)
    d.text((484, 184), "Currently shipping at Spoto.in", font=font(13), fill=MUTED)
    img.save(OUT / "about-life.png", "PNG")


def stack():
    img, d = banner(210)
    d.text((36, 22), "02  /  STACK", font=font(14, True), fill=BLUE)
    d.text((36, 50), "Tools I keep close.", font=font(28, True), fill=WHITE)
    chips = [
        (36, 100, ["Python", "Django", "DRF", "PostgreSQL", "AWS", "JavaScript", "Linux"]),
        (36, 150, ["Nginx", "Gunicorn", "Razorpay", "Juspay", "Postman", "C/C++", "MySQL"]),
    ]
    f = font(14, True)
    for x0, y, row in chips:
        x = x0
        for t in row:
            tw = int(d.textlength(t, font=f))
            w = tw + 28
            rounded(d, (x, y, x + w, y + 36), 18, CARD, BLUE)
            d.text((x + 14, y + 8), t, font=f, fill=WHITE)
            x += w + 10
    img.save(OUT / "stack.png", "PNG")


def identity():
    img, d = banner(230)
    d.text((36, 22), "03  /  IDENTITY", font=font(14, True), fill=BLUE)
    d.text((36, 50), "Engineer on file.", font=font(24, True), fill=WHITE)
    cards = [
        (36, "LEETCODE", "100+"),
        (250, "EXPERIENCE", "2+ yrs"),
        (464, "CGPA", "7.8 / 10"),
        (678, "ROLE", "Spoto.in"),
    ]
    for x, k, v in cards:
        rounded(d, (x, 96, x + 196, 206), 14, CARD, STROKE)
        d.text((x + 20, 116), k, font=font(13, True), fill=BLUE)
        d.text((x + 20, 150), v, font=font(28, True), fill=WHITE)
    img.save(OUT / "id-dashboard.png", "PNG")


def connect():
    img, d = banner(210)
    d.text((36, 22), "04  /  CONNECT", font=font(14, True), fill=BLUE)
    d.text((36, 50), "This way.", font=font(28, True), fill=WHITE)
    d.text((36, 88), "LinkedIn, email, GitHub, and the live portfolio.", font=font(15), fill=MUTED)
    rounded(d, (36, 122, 426, 186), 12, CARD, STROKE)
    d.text((56, 146), "LinkedIn  |  vaibhav-singh", font=font(16, True), fill=WHITE)
    rounded(d, (446, 122, 844, 186), 12, CARD, STROKE)
    d.text((466, 146), "Email  |  vaibhavsingh273010", font=font(16, True), fill=WHITE)
    img.save(OUT / "connect.png", "PNG")


if __name__ == "__main__":
    heroo()
    about()
    stack()
    identity()
    connect()
    print("banners ready")
