"""Small real wheels for offline installation, inheritance and integrity cases."""

import base64
import csv
import hashlib
import io
from pathlib import Path
from zipfile import ZipFile


def wheel(
    directory: Path, name: str, version: str, source: str, requires: tuple[str, ...] = ()
) -> Path:
    module = name.replace("-", "_")
    info = f"{module}-{version}.dist-info"
    metadata = f"Metadata-Version: 2.3\nName: {name}\nVersion: {version}\n"
    metadata += "".join(f"Requires-Dist: {item}\n" for item in requires)
    files = {
        f"{module}/__init__.py": source.encode(),
        f"{info}/METADATA": metadata.encode(),
        f"{info}/WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
    }
    record = io.StringIO()
    writer = csv.writer(record, lineterminator="\n")
    for path, content in files.items():
        checksum = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode().rstrip("=")
        writer.writerow((path, f"sha256={checksum}", len(content)))
    writer.writerow((f"{info}/RECORD", "", ""))
    files[f"{info}/RECORD"] = record.getvalue().encode()
    target = directory / f"{module}-{version}-py3-none-any.whl"
    with ZipFile(target, "x") as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return target


def lockfile(directory: Path, wheels: tuple[Path, ...]) -> Path:
    lines: list[str] = []
    for path in wheels:
        name, version, *_ = path.name.split("-")
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{name}=={version} --hash=sha256:{checksum}\n")
    lock = directory / "requirements.txt"
    lock.write_text("".join(lines))
    return lock
