# Data Science Projekt

## LLM - Zusammenfassung

Der LLM-Teil nutzt die Groq API mit dem Modell `llama-3.3-70b-versatile` 
um gescrapte Artikel automatisch zusammenzufassen.

### Setup

1. Kostenlosen Groq API Key erstellen auf [console.groq.com](https://console.groq.com)

2. Dependencies installieren:
```bash
   pip install groq python-dotenv
```

3. `.env` Datei erstellen (wichtig: ohne BOM-Encoding!):
```powershell
   # Windows
   [System.IO.File]::WriteAllText(".env", "GROQ_API_KEY=dein_key_hier", (New-Object System.Text.UTF8Encoding $false))
   
   # Mac/Linux
   echo "GROQ_API_KEY=dein_key_hier" > .env
```

### Hinweise
- Die `.env` Datei niemals committen
- Den API Key auf [console.groq.com](https://console.groq.com) generieren und einfügen
- Groq ist kostenlos mit 14.400 Anfragen pro Tag