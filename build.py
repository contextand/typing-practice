#!/usr/bin/env python3
import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "책")

def parse_md(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    title = ""
    author = ""
    genre = ""
    publisher = ""
    body_start = 0

    # Detect YAML frontmatter format (--- ... ---)
    if lines and lines[0].strip() == "---":
        end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
        if end:
            for line in lines[1:end]:
                line = line.strip()
                if line.startswith("title:"):
                    title = line[6:].strip().strip('"\'')
                elif line.startswith("author:"):
                    author = line[7:].strip().strip('"\'')
                elif line.startswith("genre:"):
                    genre = line[6:].strip().strip('"\'')
                elif line.startswith("publisher:"):
                    publisher = line[10:].strip().strip('"\'')
            body_start = end + 1
    else:
        # Legacy format: # title + key: value metadata
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("글쓴이:"):
                author = line[4:].strip()
            elif line.startswith("장르:"):
                genre = line[3:].strip()
            elif line.startswith("출판사:"):
                publisher = line[4:].strip()

    passages = []
    current_lines = []
    in_metadata = (body_start == 0)

    for line in lines[body_start:]:
        stripped = line.strip()

        if stripped.startswith("!["):
            in_metadata = False
            continue

        if in_metadata:
            if stripped.startswith("# ") or stripped.startswith("글쓴이:") or \
               stripped.startswith("장르:") or stripped.startswith("정리한 날:") or \
               stripped.startswith("출판사:") or stripped == "":
                continue
            else:
                in_metadata = False

        if re.match(r"^\d+$", stripped):
            if current_lines:
                text = "\n".join(current_lines).strip()
                if text:
                    passages.append(text)
            current_lines = []
            continue

        current_lines.append(line)

    if current_lines:
        text = "\n".join(current_lines).strip()
        if text:
            passages.append(text)

    def clean(text):
        # Replace newlines with space so text flows naturally
        text = re.sub(r'\n+', ' ', text)
        # Remove leading / markers (list-style quotes in some books)
        text = re.sub(r'(?<!\w)/\s*', '', text)
        # Remove .. or ... separators
        text = re.sub(r'\.\.+', '', text)
        # Normalize whitespace
        text = re.sub(r'  +', ' ', text).strip()
        return text

    cleaned = [clean(p) for p in passages]
    return {
        "title": title,
        "author": author,
        "genre": genre,
        "publisher": publisher,
        "passages": [p for p in cleaned if len(p) > 10]
    }


def main():
    books = []
    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(DATA_DIR, filename)
        try:
            book = parse_md(filepath)
            if book["passages"]:
                books.append(book)
        except Exception as e:
            print(f"Error parsing {filename}: {e}")

    print(f"Parsed {len(books)} books")
    total_passages = sum(len(b["passages"]) for b in books)
    print(f"Total passages: {total_passages}")

    # Load quotes
    quotes_path = os.path.join(os.path.dirname(__file__), "data", "quotes.json")
    with open(quotes_path, encoding="utf-8") as f:
        quotes = json.load(f)
    quotes_json = json.dumps([q["text"] for q in quotes], ensure_ascii=False)

    # Generate HTML
    data_json = json.dumps(books, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>타이핑</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Asta+Sans:wght@300..800&family=Chiron+GoRound+TC:wght@200..900&family=Chiron+Hei+HK:ital,wght@0,200..900;1,200..900&family=Diphylleia&family=Gowun+Dodum&family=Hahmlet:wght@100..900&family=Nanum+Gothic+Coding&family=Nanum+Myeongjo&family=Noto+Sans+KR:wght@100..900&family=Song+Myung&family=Sunflower:wght@300&display=swap" rel="stylesheet">
<style>
  @import url('https://cdn.jsdelivr.net/gh/wanteddev/wanted-sans@v1.0.1/packages/wanted-sans/fonts/webfonts/variable/split/WantedSansVariable.min.css');

  @font-face {{
    font-family: 'ChosunIlboMyungjo';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_one@1.0/Chosunilbo_myungjo.woff') format('woff');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'Giants';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2307-1@1.1/Giants-Regular.woff2') format('woff2');
    font-weight: 400; font-display: swap;
  }}
  @font-face {{
    font-family: 'Giants';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2307-1@1.1/Giants-Bold.woff2') format('woff2');
    font-weight: 700; font-display: swap;
  }}
  @font-face {{
    font-family: 'Independent';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_twelve@1.1/Dokrip.woff') format('woff');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'PyeojinGothic';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2504-1@1.0/PyeojinGothic-Light.woff2') format('woff2');
    font-weight: 300; font-display: swap;
  }}
  @font-face {{
    font-family: 'PyeojinGothic';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2504-1@1.0/PyeojinGothic-Regular.woff2') format('woff2');
    font-weight: 400; font-display: swap;
  }}
  @font-face {{
    font-family: 'PyeojinGothic';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2504-1@1.0/PyeojinGothic-Bold.woff2') format('woff2');
    font-weight: 700; font-display: swap;
  }}
  @font-face {{
    font-family: 'Ridibatang';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_twelve@1.0/RIDIBatang.woff') format('woff');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'SchoolSafetyNotification';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-5@1.0/HakgyoansimAllimjangTTF-R.woff2') format('woff2');
    font-weight: 400; font-display: swap;
  }}
  @font-face {{
    font-family: 'SchoolSafetyNotification';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-5@1.0/HakgyoansimAllimjangTTF-B.woff2') format('woff2');
    font-weight: 700; font-display: swap;
  }}
  @font-face {{
    font-family: 'SchoolSafetyRoundedSmile';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-5@1.0/HakgyoansimDunggeunmisoTTF-R.woff2') format('woff2');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'SchoolSafetyRoundedSmile';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-5@1.0/HakgyoansimDunggeunmisoTTF-B.woff2') format('woff2');
    font-weight: 700; font-display: swap;
  }}
  @font-face {{
    font-family: 'Taenada';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2210-2@1.0/Tenada.woff2') format('woff2');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'Yeongwol';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2507-2@1.0/YeongwolTTF-Regular.woff2') format('woff2');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'Aggravo';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2108@1.1/SBAggroL.woff') format('woff');
    font-weight: 300; font-display: swap;
  }}
  @font-face {{
    font-family: 'Aggravo';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2108@1.1/SBAggroM.woff') format('woff');
    font-weight: 500; font-display: swap;
  }}
  @font-face {{
    font-family: 'Aggravo';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2108@1.1/SBAggroB.woff') format('woff');
    font-weight: 700; font-display: swap;
  }}
  @font-face {{
    font-family: 'Cafe24Surround';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2105_2@1.0/Cafe24Ssurround.woff') format('woff');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-1Thin.woff2') format('woff2');
    font-weight: 100; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-2ExtraLight.woff2') format('woff2');
    font-weight: 200; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-3Light.woff2') format('woff2');
    font-weight: 300; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-4Regular.woff2') format('woff2');
    font-weight: 400; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-5Medium.woff2') format('woff2');
    font-weight: 500; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-6SemiBold.woff2') format('woff2');
    font-weight: 600; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-7Bold.woff2') format('woff2');
    font-weight: 700; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-8ExtraBold.woff2') format('woff2');
    font-weight: 800; font-display: swap;
  }}
  @font-face {{
    font-family: 'A2z';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2601-6@1.0/에이투지체-9Black.woff2') format('woff2');
    font-weight: 900; font-display: swap;
  }}
  @font-face {{
    font-family: 'GangwonEducationTteontteon';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2201-2@1.0/GangwonEduPowerExtraBoldA.woff') format('woff');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'JoseonPalace';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_20-04@1.0/ChosunGs.woff') format('woff');
    font-weight: normal; font-display: swap;
  }}
  @font-face {{
    font-family: 'SeoulNotice';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2505-1@1.0/SeoulAlrimTTF-Medium.woff2') format('woff2');
    font-weight: 500; font-display: swap;
  }}
  @font-face {{
    font-family: 'SeoulNotice';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2505-1@1.0/SeoulAlrimTTF-Bold.woff2') format('woff2');
    font-weight: 700; font-display: swap;
  }}
  @font-face {{
    font-family: 'SeoulNotice';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2505-1@1.0/SeoulAlrimTTF-ExtraBold.woff2') format('woff2');
    font-weight: 800; font-display: swap;
  }}
  @font-face {{
    font-family: 'SeoulNotice';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2505-1@1.0/SeoulAlrimTTF-Heavy.woff2') format('woff2');
    font-weight: 900; font-display: swap;
  }}

  @font-face {{
    font-family: 'Library';
    src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408@1.0/LibraryK.woff2') format('woff2');
    font-weight: normal;
    font-display: swap;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: #fff;
    color: #1a1a1a;
    font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
  }}

  /* ── Shared char styles ─────────────────────────── */
  .passage-text {{
    font-size: 30px;
    font-weight: 900;
    line-height: 1.8;
    letter-spacing: 0.02em;
    white-space: pre-wrap;
    word-break: keep-all;
    user-select: text;
  }}

  .char {{
    display: inline-block;
    vertical-align: baseline;
    position: relative;
    color: #ddd;
  }}
  .char.correct {{ color: #1a1a1a; }}
  .char.wrong {{ color: #ddd; }}
  .char.wrong::before {{
    content: attr(data-typed);
    position: absolute; top: 0; left: 0;
    width: 100%; line-height: inherit;
    color: #e07070; pointer-events: none;
  }}
  .char.composing {{ color: #ddd; }}
  .char.composing::before {{
    content: attr(data-composing);
    position: absolute; top: 0; left: 0;
    width: 100%; line-height: inherit;
    color: #1a1a1a; pointer-events: none;
  }}
  .char.cursor-after::after {{
    content: '';
    position: absolute; right: -1px; top: 50%;
    transform: translateY(-50%);
    width: 2px; height: 1.1em;
    background: #1a1a1a;
    animation: blink 0.8s step-end infinite;
  }}
  .char.cursor-before::before {{
    content: '';
    position: absolute; left: -1px; top: 50%;
    transform: translateY(-50%);
    width: 2px; height: 1.1em;
    background: #1a1a1a;
    animation: blink 0.8s step-end infinite;
  }}
  @keyframes blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0; }}
  }}

  /* ── MOBILE LAYOUT ──────────────────────────────── */
  .mobile-layout {{
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 32px 20px;
    user-select: none;
    overflow: hidden;
    background: #fff;
  }}

  .mobile-card {{
    width: 100%;
    max-width: 480px;
    border: none;
    padding: 20px;
    box-sizing: border-box;
    background: #fff;
    will-change: transform;
  }}

  @media (max-width: 1000px) {{
    .passage-text {{ font-size: 16px; line-height: 1.9; color: #444; font-weight: 500; }}
    .type-page {{ display: none !important; }}
  }}

  .mobile-card-footer {{
    border-top: 1px solid #000;
    padding-top: 28px;
    margin-top: 28px;
  }}

  .mobile-book-title {{
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 6px;
    color: #222;
  }}

  .mobile-book-meta {{
    font-size: 12px;
    color: #999;
    line-height: 1.6;
  }}

  /* ── PC LAYOUT ──────────────────────────────────── */
  .pc-layout {{ display: none; }}

  @media (min-width: 1001px) {{
    body {{ overflow: hidden; height: 100vh; }}

    .mobile-layout {{ display: none; }}

    .pc-layout {{
      display: flex;
      width: 100vw;
      height: 100vh;
      position: relative;
    }}

    /* Outer border 1px inset */
    .pc-layout {{
      box-shadow: inset 0 0 0 1px #1a1a1a;
    }}

    .pc-layout::after {{
      content: '';
      position: absolute;
      left: 50%;
      top: 0;
      height: 100%;
      width: 1px;
      background: #1a1a1a;
      pointer-events: none;
    }}

    /* Left sidebar — exactly 50% width */
    .pc-sidebar {{
      width: 50%;
      flex-shrink: 0;
      height: 100vh;
      padding: 25px 0 35px 36px;
      display: flex;
      flex-direction: column;
      position: relative;
      background: #fff;
      transition: background 0.2s;
    }}

    .pc-book {{
      margin-top: 0;
    }}

    .pc-book-title {{
      font-size: 30px;
      font-weight: 300;
      color: #222;
      line-height: 2;
    }}

    .pc-book-lock {{
      background: none;
      border: none;
      cursor: pointer;
      padding: 0;
      color: #222;
      line-height: 0;
      flex-shrink: 0;
      transition: color 0.15s;
      position: relative;
    }}
    .pc-book-lock:hover {{ color: #999; }}
    .pc-book-lock svg circle {{ fill: none; transition: fill 0.15s; }}
    .pc-book-lock.locked svg circle {{ fill: currentColor; }}
    .pc-book-lock:not(.locked)::after {{
      content: attr(data-tooltip);
      position: absolute;
      left: calc(100% + 10px);
      top: 50%;
      transform: translateY(-50%);
      white-space: nowrap;
      font-size: 15px;
      font-weight: 300;
      color: #222;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.15s;
      z-index: 200;
    }}
    .pc-book-lock:not(.locked):hover::after {{ opacity: 1; }}

    .pc-book-meta {{
      font-size: 15px;
      font-weight: 300;
      color: #222;
      line-height: 2;
      margin-bottom: 15px;
    }}

    .pc-sidebar-content {{
      height: 100%;
      position: relative;
    }}

    .pc-font-info {{
      position: absolute;
      bottom: 35px;
      left: 44px;
      font-size: 30px;
      font-weight: 300;
      color: #222;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 0;
      z-index: 101;
    }}

    .pc-font-info a {{
      color: #222;
      text-decoration: none;
      font-size: 30px;
      font-weight: 300;
      transition: color 0.15s;
    }}

    .pc-font-info a:hover {{ color: #999; }}

    .pc-font-lock {{
      background: none;
      border: none;
      cursor: pointer;
      padding: 0;
      color: #222;
      line-height: 0;
      flex-shrink: 0;
      transition: color 0.15s;
      margin-bottom: 18px;
      position: relative;
    }}
    .pc-font-lock:hover {{ color: #999; }}
    .pc-font-lock svg circle {{ fill: none; transition: fill 0.15s; }}
    .pc-font-lock.locked svg circle {{ fill: currentColor; }}
    .pc-font-lock:not(.locked)::after {{
      content: attr(data-tooltip);
      position: absolute;
      left: calc(100% + 10px);
      top: 50%;
      transform: translateY(-50%);
      white-space: nowrap;
      font-size: 15px;
      font-weight: 300;
      color: #222;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.15s;
      z-index: 200;
    }}
    .pc-font-lock:not(.locked):hover::after {{ opacity: 1; }}

    .pc-sliders {{
      position: absolute;
      bottom: 35px;
      left: 44px;
      right: 54px;
      display: none;
      flex-direction: column;
      gap: 7px;
      z-index: 101;
    }}
    .pc-slider-row {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .pc-slider-val {{
      font-size: 15px;
      font-weight: 300;
      color: #222;
      white-space: nowrap;
      width: 60px;
      flex-shrink: 0;
      text-align: left;
    }}
    .pc-slider {{
      -webkit-appearance: none;
      appearance: none;
      flex: 1;
      width: 0;
      height: 1px;
      background: linear-gradient(to right, #222 50%, #ddd 50%);
      outline: none;
      border: none;
      cursor: ew-resize;
      margin: 8px 0;
    }}
    .pc-slider::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 1px;
      height: 16px;
      background: transparent;
      cursor: ew-resize;
    }}
    .pc-slider::-moz-range-thumb {{
      width: 1px;
      height: 16px;
      background: transparent;
      border: none;
      cursor: ew-resize;
    }}

    /* Right panel — fills remaining 50% */
    .pc-right {{
      flex: 1;
      height: 100vh;
      overflow-y: auto;
      overflow-x: hidden;
      position: relative;
      background: #fff;
      transition: background 0.2s;
    }}

    /* Invisible textarea covers right panel for click-to-type */
    .pc-input {{
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      opacity: 0;
      cursor: text;
      resize: none;
      border: none;
      background: transparent;
      font-size: 18px;
      z-index: 10;
    }}

    .pc-passages-track {{
      padding-top: 27px;
      padding-bottom: 35px;
      padding-left: 54px;
      padding-right: 60px;
    }}

    .pc-preview-slot {{ display: none; }}

    /* Slide animation on passage change */
    .pc-passages-track {{
      will-change: transform;
    }}

    @keyframes slideOutUp   {{ from {{ transform: translateY(0);     opacity: 1; }} to {{ transform: translateY(-60px); opacity: 0; }} }}
    @keyframes slideInUp    {{ from {{ transform: translateY(60px);  opacity: 0; }} to {{ transform: translateY(0);     opacity: 1; }} }}
    @keyframes slideOutDown {{ from {{ transform: translateY(0);     opacity: 1; }} to {{ transform: translateY(60px);  opacity: 0; }} }}
    @keyframes slideInDown  {{ from {{ transform: translateY(-60px); opacity: 0; }} to {{ transform: translateY(0);     opacity: 1; }} }}

    /* Type button in sidebar bottom-right */
    .pc-type-btn {{
      position: absolute;
      bottom: 35px;
      right: 54px;
      font-size: 30px;
      font-weight: 300;
      color: #222;
      background: none;
      border: none;
      cursor: pointer;
      padding: 0;
      font-family: inherit;
      z-index: 101;
      transition: color 0.15s;
    }}
    .pc-type-btn:hover {{ color: #999; }}

    /* BookList button */
    .pc-booklist-btn {{
      position: absolute;
      left: 44px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 15px;
      font-weight: 300;
      letter-spacing: 80px;
      color: #222;
      background: none;
      border: none;
      cursor: pointer;
      padding: 0;
      font-family: inherit;
      transition: color 0.15s;
      z-index: 101;
      display: none;
    }}
    .pc-booklist-btn:hover {{ color: #999; }}

    /* BookList overlay */
    .pc-booklist-overlay {{
      display: none;
      position: fixed;
      top: 0; left: 0;
      width: 100vw; height: 100vh;
      z-index: 300;
      align-items: center;
      justify-content: center;
      background: rgba(255,255,255,0.85);
    }}
    .pc-booklist-overlay.open {{ display: flex; }}
    .pc-booklist-inner {{
      max-height: 80vh;
      overflow-y: scroll;
      text-align: center;
      scrollbar-width: none;
    }}
    .pc-booklist-inner::-webkit-scrollbar {{ display: none; }}
    .pc-booklist-item {{
      font-size: 15px;
      font-weight: 300;
      color: #222;
      cursor: pointer;
      padding: 6px 0;
      line-height: 1.6;
      transition: color 0.15s;
      display: block;
      background: none;
      border: none;
      font-family: inherit;
      outline: none;
      width: 100%;
    }}
    .pc-booklist-item:hover {{ color: #999; }}

    /* Type page overlay */
    .type-page {{
      display: none;
      position: fixed;
      top: 0; left: 0;
      width: 100vw; height: 100vh;
      background: #fff;
      box-shadow: inset 0 0 0 1px #1a1a1a;
      z-index: 200;
      flex-direction: column;
    }}
    .type-page.open {{ display: flex; }}

    .type-header {{
      flex-shrink: 0;
      display: flex;
      align-items: center;
      padding: 0 54px 0 44px;
      min-height: 104px;
      border-bottom: 1px solid #1a1a1a;
      gap: 54px;
    }}

    .type-title {{
      font-size: 30px;
      font-weight: 300;
      color: #222;
      width: 200px;
      flex-shrink: 0;
    }}

    .type-close {{
      position: absolute;
      top: 35px;
      right: 35px;
      background: none;
      border: none;
      cursor: pointer;
      color: #222;
      padding: 0;
      line-height: 1;
      font-size: 30px;
      font-weight: 300;
      font-family: inherit;
      transition: color 0.15s;
    }}
    .type-close:hover {{ color: #999; }}

    .type-input {{
      flex: 1;
      font-size: 30px;
      font-weight: 900;
      color: #1a1a1a;
      border: none;
      outline: none;
      background: transparent;
      font-family: 'Noto Sans KR', sans-serif;
    }}
    .type-input::placeholder {{ color: #ddd; }}

    .type-list {{
      flex: 1;
      overflow-y: auto;
    }}

    .type-row {{
      display: flex;
      align-items: center;
      padding: 0 54px 0 44px;
      min-height: 104px;
      border-bottom: 1px solid #1a1a1a;
      gap: 54px;
    }}

    .type-row-name {{
      font-size: 15px;
      font-weight: 300;
      color: #222;
      width: 200px;
      flex-shrink: 0;
      line-height: 2;
    }}

    .type-row-name a {{
      color: #222;
      text-decoration: none;
      transition: color 0.15s;
    }}
    .type-row-name a:hover {{ color: #999; }}

    .type-row-text {{
      flex: 1;
      font-size: 30px;
      font-weight: 900;
      color: #ddd;
      line-height: 2;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .pc-passages-track.slide-out-up,
    .pc-sidebar-content.slide-out-up   {{ animation: slideOutUp   0.18s ease-in  forwards; }}
    .pc-passages-track.slide-in-up,
    .pc-sidebar-content.slide-in-up    {{ animation: slideInUp    0.22s ease-out forwards; }}
    .pc-passages-track.slide-out-down,
    .pc-sidebar-content.slide-out-down {{ animation: slideOutDown 0.18s ease-in  forwards; }}
    .pc-passages-track.slide-in-down,
    .pc-sidebar-content.slide-in-down  {{ animation: slideInDown  0.22s ease-out forwards; }}

    /* Dark mode button */
    .pc-dark-btn {{
      position: absolute;
      top: 12px;
      right: 16px;
      font-size: 15px;
      font-weight: 300;
      color: #222;
      background: none;
      border: none;
      cursor: pointer;
      padding: 0;
      font-family: inherit;
      transition: color 0.15s;
      z-index: 101;
    }}
    .pc-dark-btn:hover {{ color: #999; }}
    .pc-right-dark-btn {{
      position: fixed;
      top: 12px;
      left: calc(50% + 16px);
      font-size: 15px;
      font-weight: 300;
      color: #222;
      background: none;
      border: none;
      cursor: pointer;
      padding: 0;
      font-family: inherit;
      transition: color 0.15s;
      z-index: 101;
    }}
    .pc-right-dark-btn:hover {{ color: #999; }}
  }}

  /* ── DARK MODE ────────────────────────────────────── */
  @media (min-width: 1001px) {{
    /* ── LEFT dark mode ───────────────────────────── */
    body.left-dark .pc-sidebar {{ background: #1a1a1a; }}
    body.left-dark .pc-layout {{ box-shadow: inset 0 0 0 1px #333; }}
    body.left-dark .pc-layout::after {{ background: #333; }}
    body.left-dark .pc-book-title,
    body.left-dark .pc-book-meta,
    body.left-dark .pc-book-lock {{ color: #ccc; }}
    body.left-dark .pc-book-lock:not(.locked)::after,
    body.left-dark .pc-font-lock:not(.locked)::after {{ color: #ccc; }}
    body.left-dark .pc-font-info,
    body.left-dark .pc-font-info a,
    body.left-dark .pc-font-lock,
    body.left-dark .pc-type-btn,
    body.left-dark .pc-dark-btn,
    body.left-dark .pc-booklist-btn {{ color: #ccc; }}
    body.left-dark .pc-font-info a:hover,
    body.left-dark .pc-type-btn:hover,
    body.left-dark .pc-dark-btn:hover,
    body.left-dark .pc-booklist-btn:hover {{ color: #666; }}
    body.left-dark .pc-slider-val {{ color: #ccc; }}
    body.left-dark .type-page {{ background: #1a1a1a; box-shadow: inset 0 0 0 1px #333; }}
    body.left-dark .type-header {{ border-bottom-color: #333; }}
    body.left-dark .type-title,
    body.left-dark .type-close {{ color: #ccc; }}
    body.left-dark .type-close:hover {{ color: #666; }}
    body.left-dark .type-input {{ color: #ddd; }}
    body.left-dark .type-input::placeholder {{ color: #444; }}
    body.left-dark .type-row {{ border-bottom-color: #333; }}
    body.left-dark .type-row-name a {{ color: #888; }}
    body.left-dark .type-row-name a:hover {{ color: #666; }}

    /* ── RIGHT dark mode ──────────────────────────── */
    body.right-dark .pc-right {{ background: #1a1a1a; }}
    body.right-dark .pc-right-dark-btn {{ color: #ccc; }}
    body.right-dark .pc-right-dark-btn:hover {{ color: #666; }}
    body.right-dark .char {{ color: #555; }}
    body.right-dark .char.correct {{ color: #ddd; }}
    body.right-dark .char.composing::before {{ color: #ddd; }}
    body.right-dark .char.cursor-after::after,
    body.right-dark .char.cursor-before::before {{ background: #ddd; }}

    /* ── LEFT quotes mode ─────────────────────────── */
    body.left-yellow .pc-sidebar {{ background: #ffde59; }}
    body.left-green  .pc-sidebar {{ background: #7ed957; }}
    body.left-yellow .pc-book-title,
    body.left-yellow .pc-book-meta,
    body.left-yellow .pc-book-lock,
    body.left-yellow .pc-font-info,
    body.left-yellow .pc-font-info a,
    body.left-yellow .pc-font-lock,
    body.left-yellow .pc-type-btn,
    body.left-yellow .pc-dark-btn,
    body.left-yellow .pc-booklist-btn,
    body.left-yellow .pc-slider-val {{ color: #222; }}
    body.left-green  .pc-book-title,
    body.left-green  .pc-book-meta,
    body.left-green  .pc-book-lock,
    body.left-green  .pc-font-info,
    body.left-green  .pc-font-info a,
    body.left-green  .pc-font-lock,
    body.left-green  .pc-type-btn,
    body.left-green  .pc-dark-btn,
    body.left-green  .pc-booklist-btn,
    body.left-green  .pc-slider-val {{ color: #222; }}
    body.left-yellow .pc-layout {{ box-shadow: inset 0 0 0 1px rgba(0,0,0,0.15); }}
    body.left-green  .pc-layout {{ box-shadow: inset 0 0 0 1px rgba(0,0,0,0.15); }}
    body.left-yellow .pc-layout::after {{ background: rgba(0,0,0,0.15); }}
    body.left-green  .pc-layout::after {{ background: rgba(0,0,0,0.15); }}
    body.left-yellow .pc-slider,
    body.left-green  .pc-slider {{ background: linear-gradient(to right, #222 50%, rgba(0,0,0,0.2) 50%); }}
    body.left-yellow .type-page {{ background: #ffde59; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.15); }}
    body.left-green  .type-page {{ background: #7ed957; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.15); }}
    body.left-yellow .type-header,
    body.left-green  .type-header {{ border-bottom-color: rgba(0,0,0,0.15); }}
    body.left-yellow .type-row,
    body.left-green  .type-row {{ border-bottom-color: rgba(0,0,0,0.15); }}
    body.left-yellow .type-input::placeholder,
    body.left-green  .type-input::placeholder {{ color: rgba(0,0,0,0.25); }}
    body.left-yellow .type-row-name a,
    body.left-green  .type-row-name a {{ color: rgba(0,0,0,0.4); }}

    /* ── RIGHT quotes mode ────────────────────────── */
    body.right-yellow .pc-right {{ background: #ffde59; }}
    body.right-green  .pc-right {{ background: #7ed957; }}
    body.right-yellow .pc-right-dark-btn,
    body.right-green  .pc-right-dark-btn {{ color: #222; }}
    body.right-yellow .char,
    body.right-green  .char {{ color: rgba(0,0,0,0.2); }}
    body.right-yellow .char.correct,
    body.right-green  .char.correct {{ color: #1a1a1a; }}
    body.right-yellow .char.wrong,
    body.right-green  .char.wrong {{ color: rgba(0,0,0,0.2); }}
    body.right-yellow .char.composing::before,
    body.right-green  .char.composing::before {{ color: #1a1a1a; }}
    body.right-yellow .char.cursor-after::after,
    body.right-yellow .char.cursor-before::before,
    body.right-green  .char.cursor-after::after,
    body.right-green  .char.cursor-before::before {{ background: #1a1a1a; }}
  }}

</style>
</head>
<body>

<!-- ── PC LAYOUT ─────────────────────────────────────── -->
<div class="pc-layout">
  <aside class="pc-sidebar">
    <div class="pc-sidebar-content" id="pcSidebarContent">
      <div class="pc-book">
        <div class="pc-book-title" id="pcBookTitle"></div>
        <div class="pc-book-meta" id="pcBookMeta"></div>
        <button class="pc-book-lock" id="pcBookLock" data-tooltip="해당 책의 내용만 고정해서 봅니다.">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor"/></svg>
        </button>
      </div>
    </div>
    <button class="pc-dark-btn" id="pcDarkBtn">D</button>
    <div class="pc-sliders" id="pcSliders">
      <div class="pc-slider-row">
        <input type="range" class="pc-slider" id="pcSliderFS" min="0" max="100" value="50">
        <span class="pc-slider-val" id="pcSliderFSVal">30px</span>
      </div>
      <div class="pc-slider-row">
        <input type="range" class="pc-slider" id="pcSliderLH" min="0" max="100" value="50">
        <span class="pc-slider-val" id="pcSliderLHVal">2.0</span>
      </div>
      <div class="pc-slider-row">
        <input type="range" class="pc-slider" id="pcSliderLS" min="0" max="100" value="50">
        <span class="pc-slider-val" id="pcSliderLSVal">0.02em</span>
      </div>
    </div>
    <div class="pc-font-info" id="pcFontInfo">
      <button class="pc-font-lock" id="pcFontLock" data-tooltip="해당 폰트가 고정되어 적용됩니다.">
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="7.5" cy="7.5" r="6.5" stroke="currentColor"/></svg>
      </button>
      <a id="pcFontLink" target="_blank" rel="noopener"></a>
    </div>
    <button class="pc-type-btn" id="pcTypeBtn">Type</button>
    <button class="pc-booklist-btn" id="pcBookListBtn">BookList</button>
  </aside>

  <!-- BookList overlay -->
  <div class="pc-booklist-overlay" id="pcBookListOverlay">
    <div class="pc-booklist-inner" id="pcBookListInner"></div>
  </div>

  <div class="pc-right" id="pcRight">
    <button class="pc-right-dark-btn" id="pcRightDarkBtn">D</button>
    <div class="pc-passages-track" id="pcPassagesTrack">
      <div class="pc-current-slot" id="pcCurrentSlot">
        <div class="passage-text" id="passageText"></div>
      </div>
      <div class="pc-preview-slot" id="pcPreviewSlot">
        <div class="passage-text" id="previewText"></div>
      </div>
    </div>
    <textarea class="pc-input" id="inputArea" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></textarea>
  </div>
</div>

<!-- ── TYPE PAGE OVERLAY (PC only) ───────────────────── -->
<div class="type-page" id="typePage">
  <button class="type-close" id="typeClose"><svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M31.9058 30.4919L31.1987 31.199L0.706829 0.707107L1.41394 0L31.9058 30.4919Z" fill="currentColor"/><path d="M0 30.4919L0.707107 31.199L31.199 0.707107L30.4919 0L0 30.4919Z" fill="currentColor"/></svg></button>
  <div class="type-header">
    <span class="type-title">Type</span>
    <input class="type-input" id="typeInput" placeholder="" autocomplete="off" spellcheck="false">
  </div>
  <div class="type-list" id="typeList"></div>
</div>

<!-- ── MOBILE LAYOUT ─────────────────────────────────── -->
<div class="mobile-layout">
  <div class="mobile-card" id="mCard">
    <div class="passage-text" id="mPassageText"></div>
    <div class="mobile-card-footer">
      <div class="mobile-book-title" id="mBookTitle"></div>
      <div class="mobile-book-meta" id="mBookMeta"></div>
    </div>
  </div>
</div>
<!-- 숨김 요소 (JS 호환성 유지) -->
<textarea id="mInputArea" style="display:none"></textarea>
<button id="mPrevBtn" style="display:none"></button>
<button id="mNextBtn" style="display:none"></button>

<script>
const BOOKS = {data_json};

const ALL = [];
BOOKS.forEach(book => {{
  book.passages.forEach(p => {{
    ALL.push({{ text: p, book }});
  }});
}});

let current = null;
let typed = "";
let isComposing = false;
let composingChar = "";
const passageHistory = [];
let historyIdx = -1;

const isPc = () => window.innerWidth > 1000;

// PC elements
const passageText = document.getElementById('passageText');
const pcBookTitle = document.getElementById('pcBookTitle');
const pcBookMeta  = document.getElementById('pcBookMeta');
const pcFontInfo  = document.getElementById('pcFontInfo');
const pcRight     = document.getElementById('pcRight');
const inputArea   = document.getElementById('inputArea');

// Mobile elements
const mPassageText = document.getElementById('mPassageText');
const mBookTitle   = document.getElementById('mBookTitle');
const mBookMeta    = document.getElementById('mBookMeta');
const mInputArea   = document.getElementById('mInputArea');

let bookLocked = false;
let lockedBook  = null;

const pcBookLock = document.getElementById('pcBookLock');
pcBookLock.addEventListener('click', () => {{
  bookLocked = !bookLocked;
  lockedBook = bookLocked ? (current ? current.book : null) : null;
  pcBookLock.classList.toggle('locked', bookLocked);
}});

// ── BookList ──────────────────────────────────────────
const pcBookListBtn = document.getElementById('pcBookListBtn');
const pcBookListOverlay = document.getElementById('pcBookListOverlay');
const pcBookListInner = document.getElementById('pcBookListInner');

function openBookList() {{
  pcBookListInner.innerHTML = '';
  BOOKS.forEach(book => {{
    const btn = document.createElement('button');
    btn.className = 'pc-booklist-item';
    btn.textContent = book.title;
    btn.addEventListener('click', (e) => {{
      e.stopPropagation();
      bookLocked = true;
      lockedBook = book;
      pcBookLock.classList.add('locked');
      current = pick();
      passageHistory.push(current);
      historyIdx = passageHistory.length - 1;
      applyPassage();
      closeBookList();
    }});
    pcBookListInner.appendChild(btn);
  }});
  pcBookListOverlay.classList.add('open');
}}

function closeBookList() {{
  pcBookListOverlay.classList.remove('open');
}}

pcBookListBtn.addEventListener('click', (e) => {{
  e.stopPropagation();
  if (pcBookListOverlay.classList.contains('open')) {{
    closeBookList();
  }} else {{
    openBookList();
  }}
}});

pcBookListOverlay.addEventListener('click', (e) => {{
  if (e.target === pcBookListOverlay) closeBookList();
}});

function pick() {{
  if (bookLocked && lockedBook) {{
    const pool = ALL.filter(p => p.book === lockedBook);
    return pool[Math.floor(Math.random() * pool.length)];
  }}
  return ALL[Math.floor(Math.random() * ALL.length)];
}}

function escAttr(s) {{
  return s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
}}

function buildPassageHtml(target) {{
  let html = '';
  const lastIsSpace = !isComposing && typed.length > 0 && typed[typed.length - 1] === ' ';
  for (let i = 0; i < target.length; i++) {{
    const ch = target[i];
    let cls = 'pending', extra = '';
    if (i < typed.length) {{
      const ok = typed[i] === target[i];
      cls = ok ? 'correct' : 'wrong';
      if (!ok) extra = ` data-typed="${{escAttr(typed[i])}}"`;
      if (i === typed.length - 1 && !isComposing && !lastIsSpace) cls += ' cursor-after';
    }} else if (isComposing && i === typed.length) {{
      cls = 'composing cursor-after';
      extra = ` data-composing="${{escAttr(composingChar)}}"`;
    }} else if (i === typed.length && (typed.length === 0 || lastIsSpace)) {{
      cls += ' cursor-before';
    }}
    html += `<span class="char ${{cls}}"${{extra}}>${{ch.replace(/&/g,'&amp;').replace(/</g,'&lt;')}}</span>`;
  }}
  return html;
}}

function render() {{
  if (!isPc()) return;
  const target = current.text;
  passageText.innerHTML = buildPassageHtml(target);
  if (!isComposing && typed.length >= target.length && typed === target) {{
    setTimeout(loadNext, 500);
  }}
}}

function resetState() {{
  typed = "";
  isComposing = false;
  composingChar = "";
  inputArea.value = "";
  mInputArea.value = "";
}}

const FONTS = [
  'A2z', 'Aggravo', 'Asta Sans', 'Cafe24Surround', 'Chiron GoRound TC',
  'ChosunIlboMyungjo', 'Diphylleia', 'GangwonEducationTteontteon', 'Giants',
  'Gowun Dodum', 'Hahmlet', 'Independent', 'JoseonPalace',
  'Library', 'Nanum Myeongjo', 'Noto Sans KR', 'PyeojinGothic', 'Ridibatang',
  'SchoolSafetyNotification', 'SchoolSafetyRoundedSmile', 'SeoulNotice',
  'Song Myung', 'Sunflower', 'Taenada', 'Wanted Sans', 'Yeongwol',
];
const FONT_LINKS = {{
  'A2z': 'https://freesentation.blog/a2z',
  'Aggravo': 'https://sandbox.co.kr/font',
  'Cafe24Surround': 'https://fonts.cafe24.com/',
  'ChosunIlboMyungjo': 'https://event.chosun.com/100/100font.html',
  'GangwonEducationTteontteon': 'https://www.gwe.go.kr/main/content.do?key=m2307211207715',
  'Giants': 'https://www.giantsclub.com/html/?pcode=1007',
  'Independent': 'https://font.co.kr/collection/freeFont?page=1&page_move=1&cate_idx=&pd_idx=&lc_font=&lc_users=&lc_range=&lc_term=&lc_scale=&price_users=&view_mode=list&view_image_mode=&stx=Yoon%C2%AE&filter_range=32&ordby=regdate&ex_txt=1',
  'JoseonPalace': 'https://event.chosun.com/100/100font.html',
  'Library': 'https://www.nl.go.kr/NL/contents/N50104020000.do',
  'PyeojinGothic': 'https://notforall.tistory.com/m/7',
  'Ridibatang': 'https://ridicorp.com/ridibatang/',
  'SchoolSafetyNotification': 'https://copyright.keris.or.kr/wft/fntDwnldView?fntGrpId=GFT202408200000000000007',
  'SchoolSafetyRoundedSmile': 'https://copyright.keris.or.kr/wft/fntDwnldView?fntGrpId=GFT202408200000000000003',
  'SeoulNotice': 'https://www.seoul.go.kr/seoul/font.do',
  'Taenada': 'https://blog.naver.com/tenada/222849825644',
  'Wanted Sans': 'https://github.com/wanteddev/wanted-sans',
  'Yeongwol': 'https://www.yw.go.kr/www/contents.do?key=1500',
}};

const pcSidebarContent = document.getElementById('pcSidebarContent');

let currentFont = null;
let fontLocked = false;
let lockedFont = null;
let preQuotesLeftDark = false;
let preQuotesRightDark = false;

const pcFontLink = document.getElementById('pcFontLink');
const pcFontLock = document.getElementById('pcFontLock');

function setPassageFont(font) {{
  passageText.style.fontFamily = `'${{font}}', sans-serif`;
  passageText.style.fontWeight = font === 'A2z' ? '800' : '900';
}}

function applyFont(font) {{
  currentFont = font;
  if (fontLocked) lockedFont = font;
  setPassageFont(font);
  const url = FONT_LINKS[font] || 'https://fonts.google.com/specimen/' + font.replace(/ /g, '+');
  pcFontLink.href = url;
  pcFontLink.textContent = font;
}}

// Lock button (toggle unlock)
pcFontLock.addEventListener('click', (e) => {{
  e.stopPropagation();
  fontLocked = !fontLocked;
  lockedFont = fontLocked ? currentFont : null;
  pcFontLock.classList.toggle('locked', fontLocked);
}});

function applyPassage() {{
  resetState();
  if (current.book === quotesBook) {{
    const alreadyInQuotes = document.body.classList.contains('left-yellow') || document.body.classList.contains('left-green');
    if (!alreadyInQuotes) {{
      preQuotesLeftDark = document.body.classList.contains('left-dark');
      preQuotesRightDark = document.body.classList.contains('right-dark');
      document.body.classList.remove('left-dark', 'right-dark');
      document.body.classList.add(preQuotesLeftDark ? 'left-green' : 'left-yellow');
      document.body.classList.add(preQuotesRightDark ? 'right-green' : 'right-yellow');
      pcDarkBtn.textContent = preQuotesLeftDark ? 'Y' : 'G';
      pcRightDarkBtn.textContent = preQuotesRightDark ? 'Y' : 'G';
    }}
  }} else {{
    document.body.classList.remove('left-yellow', 'left-green', 'right-yellow', 'right-green');
    if (preQuotesLeftDark) document.body.classList.add('left-dark');
    if (preQuotesRightDark) document.body.classList.add('right-dark');
    preQuotesLeftDark = false;
    preQuotesRightDark = false;
    pcDarkBtn.textContent = document.body.classList.contains('left-dark') ? 'L' : 'D';
    pcRightDarkBtn.textContent = document.body.classList.contains('right-dark') ? 'L' : 'D';
  }}
  updateSliderBg(pcSliderFS);
  updateSliderBg(pcSliderLH);
  updateSliderBg(pcSliderLS);

  if (isPc()) {{
    const font = fontLocked ? lockedFont : FONTS[Math.floor(Math.random() * FONTS.length)];
    applyFont(font);
    pcBookTitle.textContent = current.book.title;
    pcBookMeta.textContent = [current.book.author, current.book.genre, current.book.publisher].filter(Boolean).join(' · ');
    render();
    inputArea.focus();
  }} else {{
    mPassageText.textContent = current.text;
    mBookTitle.textContent = current.book.title;
    mBookMeta.textContent = [current.book.author, current.book.genre, current.book.publisher].filter(Boolean).join(' · ');
  }}
}}

function mobileSlide(dir, callback) {{
  if (isAnimating) return;
  isAnimating = true;
  const card = document.getElementById('mCard');
  const outX = dir === 'next' ? '-110%' : '110%';
  const inX  = dir === 'next' ? '110%'  : '-110%';
  card.style.transition = 'transform 0.25s cubic-bezier(0.4,0,0.2,1), opacity 0.25s ease';
  card.style.transform = `translateX(${{outX}})`;
  card.style.opacity = '0';
  setTimeout(() => {{
    card.style.transition = 'none';
    card.style.transform = `translateX(${{inX}})`;
    card.style.opacity = '0';
    callback();
    requestAnimationFrame(() => {{
      requestAnimationFrame(() => {{
        card.style.transition = 'transform 0.3s cubic-bezier(0.25,0.46,0.45,0.94), opacity 0.3s ease';
        card.style.transform = 'translateX(0)';
        card.style.opacity = '1';
        setTimeout(() => {{ isAnimating = false; }}, 320);
      }});
    }});
  }}, 270);
}}

let isAnimating = false;
const pcTrack = document.getElementById('pcPassagesTrack');

function pageSlide(dir, callback) {{
  if (!isPc()) {{ mobileSlide(dir, callback); return; }}
  if (isAnimating) return;
  isAnimating = true;

  const outClass = dir === 'next' ? 'slide-out-up'   : 'slide-out-down';
  const inClass  = dir === 'next' ? 'slide-in-up'    : 'slide-in-down';

  pcTrack.classList.add(outClass);

  pcTrack.addEventListener('animationend', function onOut() {{
    pcTrack.classList.remove(outClass);
    callback();
    pcTrack.classList.add(inClass);
    pcTrack.addEventListener('animationend', function onIn() {{
      pcTrack.classList.remove(inClass);
      isAnimating = false;
    }}, {{ once: true }});
  }}, {{ once: true }});
}}

function loadNext() {{
  function go() {{
    if (historyIdx < passageHistory.length - 1) {{
      let targetIdx = historyIdx + 1;
      while (targetIdx < passageHistory.length - 1 && bookLocked && lockedBook && passageHistory[targetIdx].book !== lockedBook) {{
        targetIdx++;
      }}
      if (bookLocked && lockedBook && passageHistory[targetIdx].book !== lockedBook) {{
        current = pick();
        passageHistory.push(current);
        historyIdx = passageHistory.length - 1;
      }} else {{
        historyIdx = targetIdx;
        current = passageHistory[historyIdx];
      }}
    }} else {{
      current = pick();
      passageHistory.push(current);
      historyIdx = passageHistory.length - 1;
    }}
    applyPassage();
  }}
  pageSlide('next', go);
}}

function loadPrev() {{
  if (historyIdx <= 0) return;
  // When book is locked, skip history entries from other books
  let targetIdx = historyIdx - 1;
  while (targetIdx > 0 && bookLocked && lockedBook && passageHistory[targetIdx].book !== lockedBook) {{
    targetIdx--;
  }}
  if (bookLocked && lockedBook && passageHistory[targetIdx].book !== lockedBook) return;
  pageSlide('prev', () => {{
    historyIdx = targetIdx;
    current = passageHistory[historyIdx];
    applyPassage();
  }});
}}

// ── IME & input handling (attached to both textareas) ──
let rafPending = false;
function scheduleRender() {{
  if (!rafPending) {{
    rafPending = true;
    requestAnimationFrame(() => {{ rafPending = false; render(); }});
  }}
}}

function addInputListeners(el) {{
  el.addEventListener('compositionstart', () => {{ isComposing = true; }});
  el.addEventListener('compositionupdate', (e) => {{
    const d = e.data || '';
    composingChar = d[d.length - 1] || '';
    scheduleRender();
  }});
  el.addEventListener('compositionend', () => {{
    isComposing = false; composingChar = '';
    const raw = el.value;
    const target = current.text;
    typed = raw.length > target.length ? raw.slice(0, target.length) : raw;
    el.value = typed;
    scheduleRender();
  }});
  el.addEventListener('input', () => {{
    const raw = el.value;
    const target = current.text;
    const completed = isComposing ? raw.slice(0, raw.length - 1) : raw;
    if (!isComposing && completed.length > target.length) {{
      typed = completed.slice(0, target.length);
      el.value = typed;
    }} else {{
      typed = completed;
    }}
    scheduleRender();
  }});
  el.addEventListener('keydown', (e) => {{
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === 'Tab' || e.key === 'Enter') {{
      e.preventDefault(); loadNext();
    }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {{
      e.preventDefault(); loadPrev();
    }}
  }});
}}

addInputListeners(inputArea);
addInputListeners(mInputArea);

// ── Type page (declared early so keydown handler can reference it) ────────
const typePage  = document.getElementById('typePage');

// ── PC: document-level keydown so arrows always work regardless of focus ──
document.addEventListener('keydown', (e) => {{
  if (!isPc()) return;
  if (typePage.classList.contains('open')) return;
  if (document.activeElement === inputArea) return; // handled by textarea listener
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === 'Tab' || e.key === 'Enter') {{
    e.preventDefault(); loadNext();
  }} else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {{
    e.preventDefault(); loadPrev();
  }}
}});

// ── Click / double-tap to focus ───────────────────────
document.addEventListener('click', (e) => {{
  if (isPc() && !typePage.classList.contains('open') && !e.target.closest('a')) inputArea.focus();
}});
window.addEventListener('focus', () => {{ if (isPc()) inputArea.focus(); }});

(function() {{
  let touchStartX = 0;
  let touchStartY = 0;

  document.addEventListener('touchstart', (e) => {{
    if (isPc()) return;
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }}, {{ passive: true }});

  document.addEventListener('touchend', (e) => {{
    if (isPc() || isAnimating) return;
    const dx = e.changedTouches[0].clientX - touchStartX;
    const dy = e.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dx) > 10 || Math.abs(dy) > 10) return;
    const x = e.changedTouches[0].clientX;
    const w = window.innerWidth;
    if (x < w / 4) {{
      loadPrev();
    }} else if (x > w * 3 / 4) {{
      loadNext();
    }}
  }});
}})();

// ── Button listeners ──────────────────────────────────
document.getElementById('mPrevBtn').addEventListener('click', loadPrev);
document.getElementById('mNextBtn').addEventListener('click', loadNext);

// ── Type page ─────────────────────────────────────────
const typeInput = document.getElementById('typeInput');
const typeList  = document.getElementById('typeList');
const QUOTES = {quotes_json};
const quotesBook = {{
  title: '발췌의 발췌',
  author: '한 번 더 발췌한 문장들, 출처 정리 못함 ㅈㅅ',
  genre: '', publisher: ''
}};
QUOTES.forEach(text => ALL.push({{ text, book: quotesBook }}));
let PLACEHOLDER = QUOTES[Math.floor(Math.random() * QUOTES.length)];

function buildTypeList() {{
  typeList.innerHTML = '';
  FONTS.forEach(font => {{
    const row = document.createElement('div');
    row.className = 'type-row';

    const name = document.createElement('div');
    name.className = 'type-row-name';
    const fontUrl = FONT_LINKS[font] || 'https://fonts.google.com/specimen/' + font.replace(/ /g, '+');
    name.innerHTML = `<a href="${{fontUrl}}" target="_blank" rel="noopener">${{font}}&nbsp;↗</a>`;

    const text = document.createElement('div');
    text.className = 'type-row-text';
    text.style.fontFamily = `'${{font}}', sans-serif`;
    text.style.fontWeight = font === 'A2z' ? '800' : '900';
    text.textContent = PLACEHOLDER;
    text.dataset.font = font;

    row.appendChild(name);
    row.appendChild(text);
    typeList.appendChild(row);
  }});
}}

function updateTypeRows() {{
  const val = typeInput.value;
  const isDark = document.body.classList.contains('left-dark');
  const isQuotes = document.body.classList.contains('left-yellow') || document.body.classList.contains('left-green');
  typeList.querySelectorAll('.type-row-text').forEach(el => {{
    el.textContent = val || PLACEHOLDER;
    if (isQuotes) {{
      el.style.color = val ? '#1a1a1a' : 'rgba(0,0,0,0.25)';
    }} else {{
      el.style.color = val ? (isDark ? '#ddd' : '#1a1a1a') : (isDark ? '#444' : '#ddd');
    }}
  }});
}}

function openTypePage() {{
  PLACEHOLDER = QUOTES[Math.floor(Math.random() * QUOTES.length)];
  typeInput.placeholder = PLACEHOLDER;
  buildTypeList();
  updateTypeRows();
  typePage.classList.add('open');
  typeInput.focus();
  if (location.hash !== '#type') location.hash = 'type';
}}

function closeTypePage() {{
  typePage.classList.remove('open');
  typeInput.value = '';
  updateTypeRows();
  if (location.hash === '#type') location.hash = '';
}}

window.addEventListener('hashchange', () => {{
  if (location.hash === '#type') {{
    if (!typePage.classList.contains('open')) openTypePage();
  }} else {{
    if (typePage.classList.contains('open')) closeTypePage();
  }}
}});

document.getElementById('pcTypeBtn').addEventListener('click', openTypePage);
document.getElementById('typeClose').addEventListener('click', closeTypePage);
typeInput.addEventListener('input', updateTypeRows);
document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape' && typePage.classList.contains('open')) closeTypePage();
}});

if (location.hash === '#type') openTypePage();

// ── Dark mode ─────────────────────────────────────────
const pcDarkBtn = document.getElementById('pcDarkBtn');
const pcRightDarkBtn = document.getElementById('pcRightDarkBtn');

pcDarkBtn.addEventListener('click', () => {{
  if (document.body.classList.contains('left-yellow')) {{
    document.body.classList.replace('left-yellow', 'left-green');
    pcDarkBtn.textContent = 'Y';
    updateSliderBg(pcSliderFS); updateSliderBg(pcSliderLH); updateSliderBg(pcSliderLS);
  }} else if (document.body.classList.contains('left-green')) {{
    document.body.classList.replace('left-green', 'left-yellow');
    pcDarkBtn.textContent = 'G';
    updateSliderBg(pcSliderFS); updateSliderBg(pcSliderLH); updateSliderBg(pcSliderLS);
  }} else {{
    const isLeftDark = document.body.classList.toggle('left-dark');
    pcDarkBtn.textContent = isLeftDark ? 'L' : 'D';
    updateTypeRows();
    updateSliderBg(pcSliderFS); updateSliderBg(pcSliderLH); updateSliderBg(pcSliderLS);
  }}
}});

pcRightDarkBtn.addEventListener('click', () => {{
  if (document.body.classList.contains('right-yellow')) {{
    document.body.classList.replace('right-yellow', 'right-green');
    pcRightDarkBtn.textContent = 'Y';
  }} else if (document.body.classList.contains('right-green')) {{
    document.body.classList.replace('right-green', 'right-yellow');
    pcRightDarkBtn.textContent = 'G';
  }} else {{
    const isRightDark = document.body.classList.toggle('right-dark');
    pcRightDarkBtn.textContent = isRightDark ? 'L' : 'D';
  }}
}});

// Sliders — line-height & letter-spacing
const pcSliderFS = document.getElementById('pcSliderFS');
const pcSliderLH = document.getElementById('pcSliderLH');
const pcSliderLS = document.getElementById('pcSliderLS');

function updateSliderBg(slider) {{
  if (!slider) return;
  const pct = slider.value;
  const dark = document.body.classList.contains('left-dark');
  const quotes = document.body.classList.contains('left-yellow') || document.body.classList.contains('left-green');
  const filled = dark ? '#ccc' : '#222';
  const empty  = dark ? '#444' : quotes ? 'rgba(0,0,0,0.2)' : '#ddd';
  slider.style.background = `linear-gradient(to right, ${{filled}} ${{pct}}%, ${{empty}} ${{pct}}%)`;
}}

const pcSliderFSVal = document.getElementById('pcSliderFSVal');
const pcSliderLHVal = document.getElementById('pcSliderLHVal');
const pcSliderLSVal = document.getElementById('pcSliderLSVal');
function applySliders() {{
  const fs = 16 + (pcSliderFS.value / 100) * 28;
  const lh = 1.0 + (pcSliderLH.value / 100) * 2.0;
  const ls = -0.08 + (pcSliderLS.value / 100) * 0.20;
  passageText.style.fontSize = fs + 'px';
  passageText.style.lineHeight = lh;
  passageText.style.letterSpacing = ls + 'em';
  pcSliderFSVal.textContent = Math.round(fs) + 'px';
  pcSliderLHVal.textContent = lh.toFixed(1);
  pcSliderLSVal.textContent = ls.toFixed(2) + 'em';
}}

pcSliderFS.addEventListener('input', () => {{ updateSliderBg(pcSliderFS); applySliders(); }});
pcSliderLH.addEventListener('input', () => {{ updateSliderBg(pcSliderLH); applySliders(); }});
pcSliderLS.addEventListener('input', () => {{ updateSliderBg(pcSliderLS); applySliders(); }});
updateSliderBg(pcSliderFS);
updateSliderBg(pcSliderLH);
updateSliderBg(pcSliderLS);

// ── Init ──────────────────────────────────────────────
current = pick();
passageHistory.push(current);
historyIdx = 0;
fontLocked = true;
lockedFont = 'Asta Sans';
applyPassage();
pcFontLock.classList.add('locked');
</script>
</body>
</html>
"""

    out_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated index.html")


if __name__ == "__main__":
    main()
