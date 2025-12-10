<div align="center">

# 🖼️ ssFinder  
### Search Your Screenshots by Memory

Find images on your computer by **describing them in plain English**.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey)

</div>

---

### Imagine this:

> “a screenshot of a KFC receipt from around 3 months ago”  
> “my selfie with sunglasses”  
> “a meme of a cat looking at a terminal window”  
> “a crypto chart screenshot from last December”

ssFinder searches your `.png`, `.jpg`, `.jpeg` images using **computer vision + embeddings**.  
It doesn’t care about filenames — it understands **what’s in the picture**.

---

## 🔥 Preview

> Coming soon:  
> ✔ CLI screenshot previews  
> ✔ Finder auto-open demonstration  

*(You can add a GIF or screenshots here later!)*

---

## ✨ Features

| Feature | Status |
|--------|:-----:|
| Local search by description | ✅ |
| Works on multiple folders | ✅ |
| Time-based filtering (“from 6 months ago”) | ✅ |
| Parallel indexing for speed | ✅ |
| Private — images stay local | ✅ |
| Auto-skip already indexed files | ✅ |
| Auto-open result in Finder / Explorer | 🔜 |
| Inline image thumbnails | 🔜 |
| GUI desktop app | 🔜 |

---

## 🛠 Requirements

- macOS or Windows
- Python **3.11**
- OpenAI API key

---

## 🚀 Installation

```bash
git clone https://github.com/ImRyansRepos/ss-finder.git
cd ss-finder
```

# Install dependencies:

```bash
pip install -r requirements.txt
```
# 🔑 API Key Setup

Edit:
```bash
ssfinder/config.py
```
Change:
```bash
OPENAI_API_KEY = "Put your api key here"
```
