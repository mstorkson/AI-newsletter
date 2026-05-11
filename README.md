# 🤖 Daglig AI-digest

Automatisk daglig epost med de viktigste AI-nyhetene, generert av GitHub Models AI og levert via Gmail.

**Helt gratis å kjøre.**

---

## Slik setter du det opp (ca. 15 min)

### Steg 1 – Opprett GitHub-konto og repository

1. Gå til [github.com](https://github.com) og opprett en gratis konto
2. Klikk **New repository**
3. Gi det et navn, f.eks. `ai-digest`
4. Velg **Private**
5. Klikk **Create repository**

### Steg 2 – Last opp filene

Last opp disse filene til repositoriet ditt:
- `news_digest.py`
- `requirements.txt`
- `.github/workflows/daily_digest.yml`

Du kan gjøre dette direkte i GitHub-nettleseren via **Add file → Upload files**.

> ⚠️ Viktig: Mappen `.github/workflows/` må eksistere. Opprett den ved å skrive `daily_digest.yml` og skriv `.github/workflows/` foran filnavnet i opplastingsdialogen.

### Steg 3 – Sett opp Gmail App Password

Gmail krever et eget "app-passord" for automatisk sending (ikke ditt vanlige passord).

1. Gå til [myaccount.google.com/security](https://myaccount.google.com/security)
2. Aktiver **2-trinnsbekreftelse** hvis ikke allerede gjort
3. Søk etter **App passwords** (App-passord) øverst på siden
4. Velg app: **Mail**, enhet: **Other** → skriv "AI Digest"
5. Klikk **Generate** – du får et 16-tegns passord. Kopier det.

### Steg 4 – Legg inn hemmelige nøkler i GitHub

1. I ditt GitHub-repository, gå til **Settings → Secrets and variables → Actions**
2. Klikk **New repository secret** for hver av disse:

| Navn | Verdi |
|------|-------|
| `GMAIL_ADDRESS` | Din Gmail-adresse (f.eks. `ditt.navn@gmail.com`) |
| `GMAIL_APP_PASSWORD` | App-passordet fra Steg 3 (uten mellomrom) |
| `RECIPIENT_EMAIL` | E-postadressen du vil motta digest på |

> `RECIPIENT_EMAIL` kan være samme Gmail-adresse, eller en annen adresse.

### Steg 5 – Test at det fungerer

1. Gå til **Actions**-fanen i ditt repository
2. Klikk på **Daglig AI-digest** i listen til venstre
3. Klikk **Run workflow → Run workflow**
4. Vent 1–2 minutter – sjekk innboksen din!

---

## Tidspunkt for utsending

Scriptet er satt til å kjøre kl. **06:00 UTC**, som tilsvarer:
- 🌙 **07:00 norsk vintertid** (CET)
- ☀️ **08:00 norsk sommertid** (CEST)

For å endre tidspunkt, rediger `cron`-linjen i `.github/workflows/daily_digest.yml`.

**Eksempler:**
```
"0 5 * * *"   → 06:00 / 07:00 norsk tid
"0 6 * * *"   → 07:00 / 08:00 norsk tid  ← standard
"30 6 * * *"  → 07:30 / 08:30 norsk tid
```

---

## Tilpasninger

**Legge til eller fjerne nyhetskilder:**
Rediger `FEEDS`-listen i `news_digest.py`. Finn RSS-feeder ved å legge `/feed/` eller `/rss/` bak nettstedsadressen.

**Endre antall artikler per kilde:**
Juster `MAX_ARTICLES_PER_FEED` i toppen av `news_digest.py`.

**Endre språk eller tone på sammendraget:**
Rediger `prompt`-variabelen i `generate_digest()`-funksjonen.

---

## Kostnader

| Komponent | Kostnad |
|-----------|---------|
| GitHub Actions | Gratis (langt under kvoten) |
| GitHub Models AI | Gratis (inkludert i GitHub) |
| Gmail SMTP | Gratis |
| **Totalt** | **0 kr** |
