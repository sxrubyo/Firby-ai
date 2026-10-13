#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
firby_code_graph.py — Codebase Comprehension & Dependency Visualizer.
Parses AST, imports, class hierarchies, function calls, and module relationships
across the entire Firby repository for 10000% instant full-codebase comprehension.
"""
import ast
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Any

ROOT_DIR = Path("/home/ubuntu/firby")

class CodebaseAnalyzer(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.rel_path = str(filepath.relative_to(ROOT_DIR))
        self.classes: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.imports: List[str] = []
        self.calls: Set[str] = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}" if mod else alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        bases = [ast.unparse(b) for b in node.bases]
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef)]
        self.classes.append({
            "name": node.name,
            "bases": bases,
            "methods": methods,
            "line": node.lineno
        })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if not any(node.name == c["name"] for c in self.classes):
            self.functions.append({
                "name": node.name,
                "async": isinstance(node, ast.AsyncFunctionDef),
                "args": [arg.arg for arg in node.args.args],
                "line": node.lineno
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        try:
            func_str = ast.unparse(node.func)
            if len(func_str) <= 40:
                self.calls.add(func_str)
        except Exception:
            pass
        self.generic_visit(node)


def analyze_repository(root_dir: Path) -> Dict[str, Any]:
    summary = {
        "total_files": 0,
        "total_lines": 0,
        "modules": {},
        "all_classes": {},
        "all_functions": {},
    }

    exclude_dirs = {".venv", ".git", "__pycache__", "node_modules", "dist", "build"}

    for py_path in root_dir.glob("**/*.py"):
        if any(ex in py_path.parts for ex in exclude_dirs):
            continue

        try:
            content = py_path.read_text(encoding="utf-8", errors="ignore")
            lines = len(content.splitlines())
            tree = ast.parse(content, filename=str(py_path))
            visitor = CodebaseAnalyzer(py_path)
            visitor.visit(tree)

            summary["total_files"] += 1
            summary["total_lines"] += lines

            mod_key = visitor.rel_path
            summary["modules"][mod_key] = {
                "lines": lines,
                "classes": visitor.classes,
                "functions": visitor.functions,
                "imports": visitor.imports[:20],
                "calls_sample": list(visitor.calls)[:15],
            }

            for cls in visitor.classes:
                summary["all_classes"][cls["name"]] = mod_key

            for func in visitor.functions:
                summary["all_functions"][func["name"]] = mod_key

        except Exception as e:
            pass

    return summary


def main():
    print("🔍 Analizando arquitectura y árbol de dependencias del repositorio...")
    data = analyze_repository(ROOT_DIR)

    out_json = ROOT_DIR / "codebase_map.json"
    out_json.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Generar Sitemap Markdown estructurado
    sitemap_lines = [
        "# 🗺️ Mapa de Arquitectura y Funciones del Repositorio",
        f" Total Archivos Python: **{data['total_files']}**",
        f" Total Líneas de Código: **{data['total_lines']:,}**\n",
        "## 📦 Módulos Principales\n"
    ]

    for mod, meta in sorted(data["modules"].items(), key=lambda x: x[1]["lines"], reverse=True):
        classes_str = ", ".join(c["name"] for c in meta["classes"]) or "Ninguna"
        funcs_count = len(meta["functions"])
        sitemap_lines.append(f"### `{mod}` ({meta['lines']} líneas)")
        sitemap_lines.append(f"- **Clases ({len(meta['classes'])}):** {classes_str}")
        sitemap_lines.append(f"- **Funciones:** {funcs_count}")
        if meta["imports"]:
            sitemap_lines.append(f"- **Imports:** `{', '.join(meta['imports'][:8])}`")
        sitemap_lines.append("")

    out_md = ROOT_DIR / "codebase_sitemap.md"
    out_md.write_text("\n".join(sitemap_lines), encoding="utf-8")

    print(f"✓ Mapa generado exitosamente:\n  - {out_json}\n  - {out_md}")
    print(f"📊 Resumen: {data['total_files']} archivos, {data['total_lines']:,} líneas de código.")

if __name__ == "__main__":
    main()
