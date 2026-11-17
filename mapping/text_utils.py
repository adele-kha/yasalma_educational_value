"""Conservative URL keys, Markdown-visible text, and reference leakage screening."""
from collections import defaultdict
import hashlib
import html
from html.parser import HTMLParser
import re
import unicodedata
from urllib.parse import quote, urlsplit, urlunsplit

import ahocorasick
from markdown_it import MarkdownIt
from rapidfuzz.fuzz import ratio

MARKDOWN = MarkdownIt('commonmark', {'html': True}).enable(['table', 'strikethrough'])
WORDS = re.compile(r'[^\W_]+', re.UNICODE)
LINK = re.compile(r'!?\[([^\]\n]*)\]\([^\n)]*\)')
TAGS = re.compile(r'<[^>]*>')
MARKUP = re.compile(r'[\[\]<>*_`#\\|~]|(?m:^[ ]{0,3}(?:[-+]|[0-9]+[.)])[ \t]+)')


def canonical(text):
    """Visible word/number sequence; ignore casing, Unicode presentation and punctuation."""
    return ' '.join(WORDS.findall(unicodedata.normalize('NFKC', html.unescape(text)).casefold()))


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def fast_markdown(text):
    """Cheap leakage screen only; never sufficient to accept a training pair."""
    return canonical(TAGS.sub(' ', LINK.sub(r'\1', text)))


class VisibleHTML(HTMLParser):
    BLOCKS = {'p','div','br','li','tr','td','th','h1','h2','h3','h4','h5','h6',
              'pre','blockquote','ul','ol','table','thead','tbody','tfoot','hr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if tag in self.BLOCKS:
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)
        if tag in self.BLOCKS:
            self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def visible_markdown(text):
    # Plain paragraphs need no parser. Ordered-list markers must still be
    # rendered because their numbers are not part of the visible body text.
    if not MARKUP.search(text):
        return canonical(text)
    parser = VisibleHTML()
    parser.feed(MARKDOWN.render(text))
    return canonical(''.join(parser.parts))


def url_key(url):
    """Candidate key only. Preserve query order/values, path case and reserved escapes."""
    if not isinstance(url, str):
        return None
    try:
        parsed = urlsplit(url.strip())
        if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname or parsed.username:
            return None
        host = parsed.hostname.encode('idna').decode().lower().rstrip('.')
        port = parsed.port
        if ':' in host:
            host = '[' + host + ']'
        if port and (parsed.scheme.lower(), port) not in (('http', 80), ('https', 443)):
            host += ':' + str(port)
        path = quote(parsed.path or '/', safe="/%:@!$&'()*+,;=-._~")
        path = re.sub(r'%([0-9a-fA-F]{2})', lambda m: chr(int(m[1], 16)) if chr(int(m[1], 16)) in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' else '%'+m[1].upper(), path)
        query = quote(parsed.query, safe="%=&/?+:;,@!$'()*-._~")
        query = re.sub(r'%[0-9a-fA-F]{2}', lambda m: m[0].upper(), query)
        # HTTP/HTTPS aliases are candidates; text equivalence is still mandatory.
        return urlunsplit(('', host, path, query, ''))
    except (ValueError, UnicodeError):
        return None


class ReferenceGuard:
    """Exact canonical hashes plus bounded anchor retrieval and full-text verification."""
    def __init__(self, variants, policy):
        self.variants = variants
        self.policy = policy
        self.hashes = defaultdict(set)
        anchors = defaultdict(set)
        size = policy['reference_anchor_chars']
        count = policy['reference_anchor_count']
        for index, (reference_id, text) in enumerate(variants):
            self.hashes[digest(text)].add(reference_id)
            if len(text) < size:
                continue
            for step in range(count):
                offset = (len(text) - size) * step // max(1, count - 1)
                anchors[text[offset:offset+size]].add(index)
        self.automaton = ahocorasick.Automaton()
        for anchor, indices in anchors.items():
            self.automaton.add_word(anchor, tuple(sorted(indices)))
        self.automaton.make_automaton()

    def matches(self, text):
        found = set(self.hashes.get(digest(text), ()))
        candidates = set()
        if not self.automaton:
            return sorted(found)
        for _, indices in self.automaton.iter(text):
            candidates.update(indices)
        threshold = self.policy['reference_near_similarity'] * 100
        for index in candidates:
            reference_id, other = self.variants[index]
            if reference_id in found:
                continue
            if other in text or ratio(text, other, score_cutoff=threshold) >= threshold:
                found.add(reference_id)
        return sorted(found)
