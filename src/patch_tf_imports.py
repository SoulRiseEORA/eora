import os
import re

def patch_imports(site_packages):
    patched = 0
    for root, dirs, files in os.walk(site_packages):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, encoding='utf-8', errors='ignore') as f:
                        code = f.read()
                    # 이미 패치된 경우는 건너뜀
                    if 'try:\n    import tensorflow' in code or 'try:\n    import keras' in code:
                        continue
                    new_code = re.sub(
                        r'^(import tensorflow[^\n]*)',
                        r'try:\n    \1\nexcept ImportError:\n    pass',
                        code,
                        flags=re.MULTILINE
                    )
                    new_code = re.sub(
                        r'^(import keras[^\n]*)',
                        r'try:\n    \1\nexcept ImportError:\n    pass',
                        new_code,
                        flags=re.MULTILINE
                    )
                    if new_code != code:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_code)
                        patched += 1
                except Exception as e:
                    print(f"Error patching {path}: {e}")
    print(f"✅ Patched {patched} files for tensorflow/keras import errors.")

if __name__ == "__main__":
    import site
    # site-packages 경로 자동 탐지
    for sp in site.getsitepackages():
        if os.path.exists(sp):
            print(f"패치 중: {sp}")
            patch_imports(sp) 