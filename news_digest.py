"""
AI News Digest – daglig epostsammendrag med Gemini AI
Kjøres automatisk via GitHub Actions hver morgen.
"""

import feedparser
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from openai import OpenAI

# ── Nyhetskilder ────────────────────────────────────────────────────────────
FEEDS = [
    ("TechCrunch AI",        "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI",       "https://venturebeat.com/category/ai/feed/"),
    ("The Verge AI",         "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("MIT Technology Review","https://www.technologyreview.com/feed/"),
    ("Ars Technica",         "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("Hugging Face Blog",    "https://huggingface.co/blog/feed.xml"),
    ("OpenAI Blog",          "https://openai.com/blog/rss.xml"),
]

MAX_ARTICLES_PER_FEED = 4   # Maks artikler å hente per kilde
HOURS_LOOKBACK       = 28   # Hvor mange timer tilbake vi ser (litt buffer)


# ── Hent nyheter fra RSS ────────────────────────────────────────────────────
def fetch_articles():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_LOOKBACK)
    articles = []

    for source_name, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= MAX_ARTICLES_PER_FEED:
                    break

                # Sjekk publiseringsdato
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                if published and published < cutoff:
                    continue  # For gammel

                title   = entry.get("title", "Ingen tittel")
                summary = entry.get("summary", entry.get("description", ""))
                link    = entry.get("link", "")

                # Rens HTML-tags fra summary
                import re
                summary = re.sub(r"<[^>]+>", "", summary)[:600]

                articles.append({
                    "source":  source_name,
                    "title":   title,
                    "summary": summary,
                    "link":    link,
                    "date":    published.strftime("%d.%m.%Y %H:%M") if published else "Ukjent dato",
                })
                count += 1

        except Exception as e:
            print(f"Feil ved henting fra {source_name}: {e}")

    print(f"Hentet {len(articles)} artikler totalt.")
    return articles


# ── Lag AI-sammendrag med Gemini ────────────────────────────────────────────
def generate_digest(articles):
    if not articles:
        return "Ingen nye AI-nyheter funnet i dag."

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"""
Artikkel {i} – {a['source']} ({a['date']})
Tittel: {a['title']}
Sammendrag: {a['summary']}
Lenke: {a['link']}
"""

    prompt = f"""
Du er en AI-nyhetsanalytiker. Nedenfor er dagens AI-nyheter fra ulike kilder.

Din oppgave:
1. Velg de 6 viktigste og mest interessante sakene
2. Skriv et kort, presist norsk sammendrag for hver (3–4 setninger)
3. Forklar kort HVORFOR saken er viktig for AI-feltet
4. Sorter fra mest til minst viktig
5. Avslutt med én setning om dagens overordnede AI-trend

Bruk dette formatet for hver sak:
### [Nummer]. [Tittel]
📰 Kilde: [Kilde] | [Dato]
[Sammendrag på norsk]
💡 Hvorfor det er viktig: [1–2 setninger]
🔗 [Lenke]

---

{articles_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return response.choices[0].message.content


# ── Bygg HTML-epost ─────────────────────────────────────────────────────────
def build_email_html(digest_text, article_count):
    today = datetime.now().strftime("%A %d. %B %Y").capitalize()

    # Konverter markdown-lignende tekst til enkel HTML
    import re
    html_body = digest_text
    html_body = re.sub(r"### (.+)", r"<h3>\1</h3>", html_body)
    html_body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html_body)
    html_body = re.sub(r"\n---\n", r"<hr>", html_body)
    html_body = re.sub(r"\n", r"<br>", html_body)

    return f"""
<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <style>
    body      {{ font-family: Georgia, serif; max-width: 680px; margin: 0 auto; color: #1a1a1a; background: #f9f9f7; }}
    .header   {{ background: #1a1a2e; color: white; padding: 24px 32px; border-radius: 8px 8px 0 0; }}
    .header h1{{ margin: 0; font-size: 22px; letter-spacing: 0.5px; }}
    .header p {{ margin: 6px 0 0; color: #aaa; font-size: 14px; }}
    .content  {{ background: white; padding: 28px 32px; border-radius: 0 0 8px 8px; border: 1px solid #e5e5e5; }}
    h3        {{ color: #1a1a2e; font-size: 17px; margin-top: 24px; margin-bottom: 6px; }}
    hr        {{ border: none; border-top: 1px solid #eee; margin: 20px 0; }}
    .footer   {{ text-align: center; color: #999; font-size: 12px; margin-top: 24px; }}
    a         {{ color: #4a6fa5; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🤖 Daglig AI-digest</h1>
    <p>{today} &nbsp;·&nbsp; {article_count} artikler analysert</p>
  </div>
  <div class="content">
    {html_body}
  </div>
  <div class="footer">
    Generert automatisk med Gemini AI og GitHub Actions
  </div>
</body>
</html>
"""


# ── Send epost via Gmail ─────────────────────────────────────────────────────
def send_email(html_content):
    sender    = os.environ["GMAIL_ADDRESS"]
    password  = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]
    today     = datetime.now().strftime("%d.%m.%Y")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🤖 AI-digest {today}"
    msg["From"]    = f"AI Digest <{sender}>"
    msg["To"]      = recipient

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Epost sendt til {recipient}")


# ── Hovedprogram ─────────────────────────────────────────────────────────────
def main():
    print("=== AI News Digest starter ===")

    articles = fetch_articles()
    digest   = generate_digest(articles)
    html     = build_email_html(digest, len(articles))
    send_email(html)

    print("=== Ferdig ===")


if __name__ == "__main__":
    main()
