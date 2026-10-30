import html


def report_text_to_html(title, text):
    safe_title = html.escape(title or "LEAF Report")
    safe_text = html.escape(text or "")

    lines = safe_text.splitlines()

    body_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            body_lines.append("<br>")
            continue

        if set(stripped) in ({"="}, {"-"}):
            continue

        if stripped.startswith("LEAF ") or stripped.endswith("REPORT") or stripped.endswith("ANALYSIS"):
            body_lines.append(f"<h2>{stripped}</h2>")
        elif stripped.startswith("Attempt "):
            body_lines.append(f"<h3>{stripped}</h3>")
        elif stripped.startswith("Cause "):
            body_lines.append(f"<h3>{stripped}</h3>")
        elif stripped.startswith("Recommendation "):
            body_lines.append(f"<h3>{stripped}</h3>")
        elif stripped.endswith(":"):
            body_lines.append(f"<h4>{stripped}</h4>")
        elif stripped.startswith("- "):
            body_lines.append(f"<li>{stripped[2:]}</li>")
        else:
            body_lines.append(f"<p>{stripped}</p>")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{safe_title}</title>
<style>
body {{
    font-family: Arial, Helvetica, sans-serif;
    margin: 32px;
    line-height: 1.45;
    background: #f5f5f5;
    color: #111;
}}
.report-container {{
    max-width: 1100px;
    margin: auto;
    background: white;
    padding: 32px;
    border: 1px solid #ccc;
}}
h1 {{
    border-bottom: 3px solid #111;
    padding-bottom: 8px;
}}
h2 {{
    margin-top: 32px;
    border-bottom: 1px solid #999;
    padding-bottom: 4px;
}}
h3 {{
    margin-top: 24px;
}}
h4 {{
    margin-bottom: 4px;
}}
p {{
    margin: 4px 0;
}}
li {{
    margin: 3px 0 3px 24px;
}}
pre {{
    white-space: pre-wrap;
}}
</style>
</head>
<body>
<div class="report-container">
<h1>{safe_title}</h1>
{chr(10).join(body_lines)}
</div>
</body>
</html>
"""


def build_html_report_bundle(reports):
    reports = reports if isinstance(reports, dict) else {}

    sections = []

    for name, text in reports.items():
        section_html = report_text_to_html(name, text)
        body_start = section_html.find('<div class="report-container">')
        body_end = section_html.rfind("</div>")

        if body_start != -1 and body_end != -1:
            inner = section_html[body_start + len('<div class="report-container">'):body_end]
            sections.append(inner)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>LEAF Report Bundle</title>
<style>
body {{
    font-family: Arial, Helvetica, sans-serif;
    margin: 32px;
    line-height: 1.45;
    background: #f5f5f5;
    color: #111;
}}
.report-container {{
    max-width: 1200px;
    margin: auto;
    background: white;
    padding: 32px;
    border: 1px solid #ccc;
}}
h1 {{
    border-bottom: 3px solid #111;
    padding-bottom: 8px;
}}
h2 {{
    margin-top: 32px;
    border-bottom: 1px solid #999;
    padding-bottom: 4px;
}}
h3 {{
    margin-top: 24px;
}}
h4 {{
    margin-bottom: 4px;
}}
p {{
    margin: 4px 0;
}}
li {{
    margin: 3px 0 3px 24px;
}}
</style>
</head>
<body>
<div class="report-container">
<h1>LEAF Report Bundle</h1>
{chr(10).join(sections)}
</div>
</body>
</html>
"""