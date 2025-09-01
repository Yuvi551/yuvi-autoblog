import os, time, argparse, feedparser
from slugify import slugify
from datetime import datetime, timezone

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
RSS_DEFAULT = "https://news.google.com/rss/search?q=artificial%20intelligence&hl=en-IN&gl=IN&ceid=IN:en"

def gen_with_openai(title, link):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    prompt = f"Write a 900-word SEO article with H2/H3 and bullets. Topic: {title}. Cite the source at end: {link}. Indian audience, simple English."
    r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
    return r.choices[0].message.content

def gen_with_local(title, link):
    return f"## {title}\n\nSummary of {title}. Source: {link}\n\n- Key point 1\n- Key point 2\n"

def write_post(title, body):
    slug = slugify(title)[:60]
    path = f"content/posts/{slug}.md"
    if os.path.exists(path): return
    fm = f"---\ntitle: \"{title}\"\ndate: {datetime.now(timezone.utc).isoformat()}\n---\n\n"
    with open(path,"w") as f: f.write(fm+body+"\n")
    print("✓", path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rss", default=RSS_DEFAULT)
    ap.add_argument("--max", type=int, default=3)
    args = ap.parse_args()
    feed = feedparser.parse(args.rss)
    for e in feed.entries[:args.max]:
        title, link = e.title, getattr(e,"link","")
        try:
            body = gen_with_openai(title, link) if OPENAI_KEY else gen_with_local(title, link)
        except:
            body = gen_with_local(title, link)
        write_post(title, body); time.sleep(1)

if __name__=="__main__": main()
