import os, re, glob
from PIL import Image, ImageDraw

res = "android/app/src/main/res"
fg = Image.open("icon-foreground.png").convert("RGBA")
full = Image.open("icon.png").convert("RGBA")

# remove any old launcher icons in other formats to avoid duplicate resources
for f in glob.glob(res + "/mipmap-*/ic_launcher*"):
    if f.endswith(".webp"):
        os.remove(f)

dens = {"mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216),
        "xxhdpi": (144, 324), "xxxhdpi": (192, 432)}
for d, (l, f) in dens.items():
    p = f"{res}/mipmap-{d}"
    os.makedirs(p, exist_ok=True)
    sq = full.resize((l, l), Image.LANCZOS)
    sq.save(f"{p}/ic_launcher.png")
    mask = Image.new("L", (l, l), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, l - 1, l - 1), fill=255)
    rd = Image.new("RGBA", (l, l), (0, 0, 0, 0))
    rd.paste(sq, (0, 0), mask)
    rd.save(f"{p}/ic_launcher_round.png")
    fg.resize((f, f), Image.LANCZOS).save(f"{p}/ic_launcher_foreground.png")

os.makedirs(res + "/values", exist_ok=True)
with open(res + "/values/ic_launcher_background.xml", "w") as fh:
    fh.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
             '    <color name="ic_launcher_background">#0F7A4A</color>\n</resources>\n')

# plain colour splash instead of the default image
for f in glob.glob(res + "/drawable*/splash.png"):
    os.remove(f)
os.makedirs(res + "/drawable", exist_ok=True)
with open(res + "/drawable/splash.xml", "w") as fh:
    fh.write('<?xml version="1.0" encoding="utf-8"?>\n'
             '<layer-list xmlns:android="http://schemas.android.com/apk/res/android">\n'
             '    <item><shape android:shape="rectangle"><solid android:color="#0F7A4A"/></shape></item>\n'
             '</layer-list>\n')

gp = "android/app/build.gradle"
g = open(gp).read()
g = re.sub(r"versionCode\s*=?\s*\d+", "versionCode " + os.environ.get("GITHUB_RUN_NUMBER", "1"), g)
if os.environ.get("KEYSTORE_PASSWORD"):
    g += '''
android {
    signingConfigs {
        release {
            storeFile file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS")
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
'''
open(gp, "w").write(g)
print("prepared")
