"""Quality gate for Agent 1: concept relevance, not TikTok virality prediction."""
import hashlib
import re

PROMO = re.compile(r"\b(tutorial|cara membuat|how to|prompts?|review|ulasan|software|aplikasi|platform|tools?|kursus|webinar|startup|investment|diskon|promo|pricing|harga langganan|fitur baru|fitur ai|launches|releases|unduh|download)\b",re.I)
SUBJECT = re.compile(r"\b(miniatur|miniature|tiny world|stop.motion|stop motion|figurine|figure|toys?|mainan|kartu|cards?|anime|cosplay|surreal|fantasy|fantasi|kartun|cartoon|characters?|karakter|kucing|cat|cats|dogs?|puppet|diorama|creature|dunia mini)\b",re.I)
MOTION = re.compile(r"\b(animasi|animation|animated|film pendek|short film|shorts?|video|stop.motion|stop motion|transformasi|transformation|transforms|morph|comes alive|come to life|hidup|bergerak|cgi|vfx|3d|loop)\b",re.I)
ENTERTAINMENT = re.compile(r"\b(anime|animasi|animation|game|gaming|miniatur|miniature|figurine|figure|toys?|mainan|kartu|cards?|kartun|cosplay|kucing|cat|fantasy|fantasi|stop motion|surreal)\b",re.I)
ANGLES = {
 "object_comes_alive":"Buat karakter orisinal keluar dari benda atau kartu dalam satu transisi lalu beri twist visual.",
 "miniature_world":"Ubah benda sederhana menjadi dunia mini dalam satu adegan makro.",
 "surreal_comedy":"Ciptakan kejadian absurd yang langsung dimengerti tanpa dialog.",
 "visual_transformation":"Buat satu perubahan visual jelas dengan reveal yang memuaskan."
}
def rejection(title,kind):
 if PROMO.search(title): return "tutorial_atau_promosi"
 if kind=="news" and not (SUBJECT.search(title) and MOTION.search(title)): return "tidak_spesifik_visual"
 if kind=="trends" and not ENTERTAINMENT.search(title): return "bukan_hiburan"
 return None

def title_key(title,group):
 lead=re.split(r"\s[-–|]\s",title,maxsplit=1)[0]
 normalized=re.sub(r"[^\w]+"," ",lead.casefold()).strip()
 return "TH-"+hashlib.sha256((normalized+"|"+group).encode()).hexdigest()[:12].upper()

def assess(title,group,kind,age):
 concrete=bool(SUBJECT.search(title) and MOTION.search(title))
 relevance=36 if concrete else 26
 hook={"object_comes_alive":26,"miniature_world":25,"surreal_comedy":23,"visual_transformation":18}.get(group,18)
 freshness=18 if age<=2 else (13 if age<=5 else 8)
 evidence=9 if kind=="trends" else 7
 breakdown={"relevance":relevance,"visual_hook":hook,"freshness":freshness,"source":evidence}
 return sum(breakdown.values()),breakdown
