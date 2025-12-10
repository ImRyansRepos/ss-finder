# ssFinder 🖼️

Search your screenshots and images on your computer by **describing them in plain text**.

> “A smiley face screenshot from 6 months ago”  
> → ssFinder searches your indexed `.png` and `.jpg` files and shows the best matches with full file paths.

---

## Features

- 🔍 Search screenshots by natural language
- 🧠 Uses image captions + text embeddings for semantic search
- 🗂 Works across multiple folders (Desktop, Downloads, Pictures, etc) in one index
- 🕒 Rough time filtering from phrases like “from 6 months ago”
- ⚡ Parallel indexing with worker threads for faster processing

---

## How it works

1. **Indexing phase**
   - Walks the directories you choose
   - For each `.png` / `.jpg`:
     - Generates a short caption with a vision model
     - Creates a text embedding from that caption
   - Stores: file path, caption, created time, embedding in a local SQLite database (`images.db`)

2. **Search phase**
   - You describe the image you remember
   - The query is embedded with the same embedding model
   - Cosine similarity is computed between the query and all stored image embeddings
   - Returns the top matches with paths, scores, and timestamps

---

## Setup

Clone the repo:

```bash
git clone https://github.com/YOUR_USERNAME/ssfinder.git
cd ssfinder
