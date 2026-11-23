#!/usr/bin/env python3
"""Optional, dependency-free authoring helper. Generated HTML is committed."""

from html import escape
from datetime import date
import json
from pathlib import Path
import re
from string import Template
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://sehi.li"
NAV_PRIMARY = [("Home", "/"), ("About", "/about/"), ("Projects", "/projects/"), ("CV", "/cv/")]
NAV_MORE = [("Video Games & Competitions", "/gaming/"), ("Mountains & Sports", "/mountains/"), ("Music & Films", "/music/"), ("Contact", "/contact/")]


def read_page(source):
    text = source.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{source}: missing front matter")
    header, separator, content = text[4:].partition("\n---\n")
    if not separator:
        raise ValueError(f"{source}: unclosed front matter")
    meta = {}
    for line in header.splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{source}: invalid metadata: {line}")
        meta[key.strip()] = value.strip()
    for key in ("path", "title", "description", "section"):
        if not meta.get(key):
            raise ValueError(f"{source}: missing {key}")
    path = meta["path"]
    if not path.startswith("/") or ".." in path or "?" in path or "#" in path:
        raise ValueError(f"{source}: invalid path")
    if path != "/404.html" and not path.endswith("/"):
        raise ValueError(f"{source}: use a directory URL ending in /")
    return meta, content.rstrip() + "\n"


def nav_link(label, path, section):
    active = ' aria-current="page"' if (path == "/" and section == "home") or path.strip("/") == section else ""
    return f'<a href="{path}"{active}>{escape(label)}</a>'


def navigation(section):
    primary = "\n        ".join(nav_link(label, path, section) for label, path in NAV_PRIMARY)
    more = "\n            ".join(nav_link(label, path, section) for label, path in NAV_MORE)
    active = ' class="has-current"' if any(path.strip("/") == section for _, path in NAV_MORE) else ""
    return f'''{primary}
        <details class="more-menu">
          <summary{active}>More <span class="chevron" aria-hidden="true"></span></summary>
          <div class="more-links">
            {more}
          </div>
        </details>'''


def external_url(value):
    if value and (urlsplit(value).scheme != "https" or not urlsplit(value).netloc):
        raise ValueError(f"Expected an HTTPS listening or video URL: {value}")
    return escape(value, quote=True)


def render_clips():
    """Generate static markup; site.js enhances YouTube links after a click."""
    clips = json.loads((ROOT / "_data/clips.json").read_text(encoding="utf-8"))
    figures = []
    for clip in clips:
        game = escape(clip["game"])
        title = escape(clip.get("title") or clip["game"])
        video_id = clip.get("youtube_id", "")
        if video_id and not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            raise ValueError(f"Invalid YouTube ID for {clip['game']}")
        url = external_url(f"https://www.youtube.com/watch?v={video_id}" if video_id else clip.get("url", ""))
        thumbnail = clip.get("thumbnail")
        if thumbnail:
            if not thumbnail.startswith("/assets/images/") or ".." in thumbnail:
                raise ValueError("Clip thumbnails must be local images under /assets/images/")
            alt = escape(clip.get("thumbnail_alt") or clip.get("title") or clip["game"], quote=True)
            preview = f'<img src="{escape(thumbnail, quote=True)}" width="640" height="360" loading="lazy" decoding="async" alt="{alt}">'
        else:
            label = '' if url else '<span class="placeholder-meta">Clip: TODO</span>'
            preview = f'<div class="media-placeholder"><span class="placeholder-title">{game}</span>{label}</div>'
        if url:
            attribute = f' data-youtube="{video_id}"' if video_id else ""
            preview = f'<a class="clip-play" href="{url}"{attribute} aria-label="Play: {title}">{preview}<span class="play-label">Play clip</span></a>'
        else:
            preview = f'<div role="img" aria-label="{game} clip: TODO">{preview}</div>'
        caption = ""
        if url or clip.get("title") or clip.get("caption") or clip.get("date"):
            game_label = f' <span class="quiet">· {game}</span>' if title != game else ""
            caption = f'<figcaption><strong>{title}</strong>{game_label}'
            if clip.get("date"):
                value = date.fromisoformat(clip["date"]).isoformat()
                caption += f' <time datetime="{value}">{value}</time>'
            if clip.get("caption"):
                caption += f'<p>{escape(clip["caption"])}</p>'
            caption += '</figcaption>'
        figures.append(f'          <figure class="clip">{preview}{caption}</figure>')
    return "\n".join(figures)


def render_tracks():
    tracks = json.loads((ROOT / "_data/music.json").read_text(encoding="utf-8"))
    items = []
    for track in tracks:
        title = escape(track.get("title") or "TODO")
        artist = escape(track.get("artist") or ("" if track.get("title") else "Artist / composer: TODO"))
        url = external_url(track.get("url", ""))
        title = f'<a href="{url}">{title}</a>' if url else title
        note = f'<p>{escape(track["note"])}</p>' if track.get("note") else ""
        credit = f'<p class="quiet">{artist}</p>' if artist else ''
        items.append(f'          <li><h3>{title}</h3>{credit}{note}</li>')
    return "\n".join(items)


def build_outputs():
    base = Template((ROOT / "_templates/base.html").read_text(encoding="utf-8"))
    project = Template((ROOT / "_templates/project.html").read_text(encoding="utf-8"))
    outputs = {}
    urls = []
    for source in sorted((ROOT / "_pages").glob("*.html")):
        meta, content = read_page(source)
        if "{{clip_gallery}}" in content:
            content = content.replace("{{clip_gallery}}", render_clips())
        if "{{music_tracks}}" in content:
            content = content.replace("{{music_tracks}}", render_tracks())
        path = meta["path"]
        is_project = meta.get("layout") == "project"
        if is_project:
            for key in ("category", "status", "technologies"):
                if not meta.get(key):
                    raise ValueError(f"{source}: missing project field {key}")
            content = project.substitute(
                heading=escape(meta["title"]), description=escape(meta["description"]),
                category=escape(meta["category"]), status=escape(meta["status"]),
                technologies=escape(meta["technologies"]), content=content)
        title = "Lyes Sehili" if path == "/" else f'{meta["title"]} — Lyes Sehili'
        rendered = base.substitute(
            title=escape(title), description=escape(meta["description"], quote=True),
            canonical=DOMAIN + path, og_type="article" if is_project else "website",
            robots='<meta name="robots" content="noindex">' if path == "/404.html" else "",
            body_class="home" if path == "/" else ("cv-page" if path == "/cv/" else "interior"),
            home_current=' aria-current="page"' if path == "/" else "",
            navigation=navigation(meta["section"]), content=content.rstrip())
        destination = "404.html" if path == "/404.html" else path.lstrip("/") + "index.html"
        if destination in outputs:
            raise ValueError(f"Duplicate output: {destination}")
        outputs[destination] = rendered
        if path != "/404.html":
            urls.append(DOMAIN + path)
    outputs["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{xml_escape(url)}</loc></url>\n" for url in sorted(urls))
        + '</urlset>\n')
    return outputs


if __name__ == "__main__":
    outputs = build_outputs()
    for relative, content in outputs.items():
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    print(f"Generated {len(outputs) - 1} pages and sitemap.xml. No deployment performed.")
