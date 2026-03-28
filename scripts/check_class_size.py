#!/usr/bin/env python3
"""
Kod Boyutu Kontrolü
AGENT_RULES.md:
  - 5.1 Sınıf max 200 satır
  - 5.2 Fonksiyon max 30 satır
  - 5.3 Fonksiyon max 4 parametre
"""

import ast
import argparse
import sys
from pathlib import Path


def check_file(
    file_path: Path, max_class_lines: int, max_func_lines: int, max_params: int
) -> list[str]:
    """Tek dosyayı kontrol et."""
    errors = []

    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError) as e:
        return [f"{file_path}: Parse hatası: {e}"]

    for node in ast.walk(tree):
        # Sınıf boyutu kontrolü (Kural 5.1)
        if isinstance(node, ast.ClassDef):
            if hasattr(node, "end_lineno") and node.end_lineno:
                class_lines = node.end_lineno - node.lineno + 1
                if class_lines > max_class_lines:
                    errors.append(
                        f"{file_path}:{node.lineno}: "
                        f"Sınıf çok büyük (Kural 5.1): "
                        f"{class_lines} > {max_class_lines} satır - "
                        f"'{node.name}' sınıfını böl"
                    )

        # Fonksiyon/metod kontrolü (Kural 5.2, 5.3)
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            if hasattr(node, "end_lineno") and node.end_lineno:
                func_lines = node.end_lineno - node.lineno + 1
                if func_lines > max_func_lines:
                    errors.append(
                        f"{file_path}:{node.lineno}: "
                        f"Fonksiyon çok büyük (Kural 5.2): "
                        f"{func_lines} > {max_func_lines} satır - "
                        f"'{node.name}' fonksiyonunu böl"
                    )

            # Parametre sayısı kontrolü
            params = len(node.args.args)
            if node.args.vararg:
                params += 1
            if node.args.kwarg:
                params += 1

            if params > max_params:
                errors.append(
                    f"{file_path}:{node.lineno}: "
                    f"Çok fazla parametre (Kural 5.3): "
                    f"{params} > {max_params} - "
                    f"'{node.name}' için config object kullan"
                )

    return errors


def main():
    """Ana kontrol fonksiyonu."""
    parser = argparse.ArgumentParser(description="Kod boyutu kontrolü")
    parser.add_argument("--max-class-lines", type=int, default=200)
    parser.add_argument("--max-func-lines", type=int, default=30)
    parser.add_argument("--max-params", type=int, default=4)
    args = parser.parse_args()

    errors = []

    # engine klasörünü kontrol et
    engine_path = Path("engine")
    if not engine_path.exists():
        print("⚠️ engine/ klasörü bulunamadı")
        sys.exit(0)

    for py_file in engine_path.rglob("*.py"):
        file_errors = check_file(
            py_file,
            args.max_class_lines,
            args.max_func_lines,
            args.max_params,
        )
        errors.extend(file_errors)

    if errors:
        print("\n❌ KOD BOYUTU İHLALLERİ:\n")
        for err in errors:
            print(f"  {err}")
        print(f"\nToplam {len(errors)} ihlal bulundu.")
        print("AGENT_RULES.md'e uygun düzeltme yapın.\n")
        sys.exit(1)

    print("✅ Tüm kod boyutu kuralları geçti")
    sys.exit(0)


if __name__ == "__main__":
    main()
