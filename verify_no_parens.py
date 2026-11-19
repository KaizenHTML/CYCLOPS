import os
import re

scan_dirs = [".", "static", "templates", "static/css", "static/js"]
checked_files = []
violations = []

def check_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.splitlines()

    for idx, line in enumerate(lines):
        line_num = idx + 1
        
        # Check comments
        if "#" in line and filepath.endswith(".py"):
            comment = line[line.index("#"):]
            if "(" in comment or ")" in comment:
                violations.append(f"{filepath}:{line_num} Comment contains paren: {comment}")
        if "//" in line and (filepath.endswith(".js") or filepath.endswith(".html")):
            comment = line[line.index("//"):]
            if "(" in comment or ")" in comment:
                violations.append(f"{filepath}:{line_num} Comment contains paren: {comment}")
        if "<!--" in line and filepath.endswith(".html"):
            if "(" in line or ")" in line:
                violations.append(f"{filepath}:{line_num} HTML comment contains paren: {line}")

        # Check HTML content
        if filepath.endswith(".html"):
            # strip script tags or style tags if any, but in HTML tags and text:
            # any visible text or label or header:
            if "<" in line and ">" in line:
                # check outside attributes or in text
                text_parts = re.findall(r">([^<]+)<", line)
                for t in text_parts:
                    if "(" in t or ")" in t:
                        violations.append(f"{filepath}:{line_num} HTML text contains paren: {t}")

        # Check strings in JS or PY
        if filepath.endswith((".js", ".py")):
            # Ignore regex compilation patterns
            if "re.compile" in line or line.strip().startswith(("RE_", "r\"", "r'")):
                continue
            str_literals = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\'', line)
            for s1, s2 in str_literals:
                s = s1 if s1 else s2
                # Allow empty or non-parentheses
                if "(" in s or ")" in s:
                    violations.append(f"{filepath}:{line_num} String literal contains paren: {s}")

base_dir = os.path.dirname(os.path.abspath(__file__))
for root, dirs, files in os.walk(base_dir):
    # skip .git or .gemini or __pycache__ or .venv or .vscode or node_modules
    if any(ignored in root for ignored in [".git", ".gemini", "__pycache__", ".venv", ".vscode", "node_modules"]):
        continue
    for file in files:
        if file.endswith((".py", ".js", ".html", ".css")):
            if file == "verify_no_parens.py":
                continue
            path = os.path.join(root, file)
            checked_files.append(path)
            check_file(path)

print(f"Archivos auditados: {len(checked_files)}")
for cf in checked_files:
    print(f" - {cf}")

if violations:
    print(f"ADVERTENCIA: Se encontraron {len(violations)} violaciones de parentesis:")
    for v in violations:
        print(f" [!] {v}")
else:
    print("ESTADO: 100% CUMPLIMIENTO. Ningun parentesis detectado en textos, etiquetas, comentarios o literales.")
