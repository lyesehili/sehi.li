#!/usr/bin/env python3
"""Check the static site without packages or external network access."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from build import DOMAIN, NAV_MORE, NAV_PRIMARY, ROOT, build_outputs

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.ids = []
        self.refs = []
        self.errors = []
        self.stack = []
        self.feed(text)
        if self.stack:
            self.errors.append(f"Unclosed elements: {self.stack}")

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src", "poster"):
            if key in attrs:
                self.refs.append(attrs[key])
        if "srcset" in attrs:
            self.refs.extend(item.strip().split()[0] for item in attrs["srcset"].split(","))
        if tag == "img" and not all(key in attrs for key in ("alt", "width", "height")):
            self.errors.append("Image missing alt text or explicit dimensions")
        if tag == "iframe" and "title" not in attrs:
            self.errors.append("Iframe missing title")
        if tag in {"audio", "video"} and "autoplay" in attrs:
            self.errors.append("Media must not autoplay")
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing tag: {tag}")
        else:
            self.stack.pop()

    def find(self, tag, **attributes):
        return [attrs for name, attrs in self.elements if name == tag and
                all(attrs.get(key) == value for key, value in attributes.items())]


def main():
    errors = []
    expected = build_outputs()
    pages = {}
    titles = []
    for relative, text in expected.items():
        file = ROOT / relative
        if not file.is_file() or file.read_text(encoding="utf-8") != text:
            errors.append(f"{relative}: generated output is stale; run scripts/build.py")
        if not relative.endswith(".html"):
            continue
        page = Page(text)
        pages[file] = page
        errors.extend(f"{relative}: {message}" for message in page.errors)
        if len(page.find("h1")) != 1 or len(page.find("main")) != 1:
            errors.append(f"{relative}: needs exactly one h1 and main")
        if page.find("html", lang="en") == []:
            errors.append(f"{relative}: missing document language")
        if len(page.find("title")) != 1:
            errors.append(f"{relative}: needs one title")
        else:
            titles.append(text.partition("<title>")[2].partition("</title>")[0])
        for name in ("description", "viewport"):
            if not any(attrs.get("content") for attrs in page.find("meta", name=name)):
                errors.append(f"{relative}: missing {name}")
        for prop in ("og:title", "og:description", "og:url", "og:image", "og:image:alt"):
            if not any(attrs.get("content") for attrs in page.find("meta", property=prop)):
                errors.append(f"{relative}: missing {prop}")
        if not page.find("link", rel="canonical"):
            errors.append(f"{relative}: missing canonical URL")
        if not page.find("nav", **{"aria-label": "Main navigation"}):
            errors.append(f"{relative}: missing shared navigation")
        for _, path in NAV_PRIMARY + NAV_MORE:
            if path not in page.refs:
                errors.append(f"{relative}: missing navigation link to {path}")
        if "/" not in page.refs or "#main" not in page.refs:
            errors.append(f"{relative}: missing home or skip link")
        duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
        if duplicates:
            errors.append(f"{relative}: duplicate IDs {duplicates}")
    if len(titles) != len(set(titles)):
        errors.append("Page titles must be unique")

    checked_links = 0
    for file, page in pages.items():
        for ref in page.refs:
            parts = urlsplit(ref)
            if parts.scheme in {"mailto", "tel", "data"}:
                continue
            if parts.netloc and parts.netloc != urlsplit(DOMAIN).netloc:
                continue
            if parts.scheme and parts.scheme not in {"http", "https"}:
                errors.append(f"{file.relative_to(ROOT)}: unsupported URL {ref}")
                continue
            path = unquote(parts.path)
            target = (ROOT / path.lstrip("/")) if path.startswith("/") else (file.parent / path)
            if not path:
                target = file
            if target.is_dir():
                target /= "index.html"
            checked_links += 1
            if not target.is_file():
                errors.append(f"{file.relative_to(ROOT)}: missing local target {ref}")
            elif parts.fragment and target.suffix == ".html":
                parsed = pages.get(target) or Page(target.read_text(encoding="utf-8"))
                if unquote(parts.fragment) not in parsed.ids:
                    errors.append(f"{file.relative_to(ROOT)}: missing fragment {ref}")
    if (ROOT / "CNAME").read_text().strip() != "sehi.li":
        errors.append("CNAME must remain sehi.li")
    if not (ROOT / ".nojekyll").is_file():
        errors.append("Missing .nojekyll")
    sitemap = ElementTree.fromstring(expected["sitemap.xml"])
    if len(sitemap) != len(pages) - 1:
        errors.append("Sitemap must include every page except 404")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(pages)} pages, {checked_links} local references, HTML structure, SEO, navigation, sitemap, and CNAME.")


if __name__ == "__main__":
    main()
