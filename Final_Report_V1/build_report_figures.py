"""Create presentation images from the existing, checksum-verified screenshots.

Run with --check to verify the derived images without writing files.
Requires Pillow. No simulator runs or original evidence files are changed.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "Figures"
PREFIXES = {"best": "BC", "worst": "WC", "real1": "RC1", "real2": "RC2"}
PROGRAMS = ["baseline", "branchfree", "unrolled", "looptest", "combined"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def panel_spans(image):
    """Locate the four green-bordered sections in a 1280-pixel trace capture."""
    require(image.width == 1280, "Unexpected trace screenshot width")
    spans, start = [], None
    for y in range(image.height + 1):
        green = y < image.height and image.getpixel((15, y)) == (0, 255, 0)
        if green and start is None:
            start = y
        elif not green and start is not None:
            if y - start > 50:
                spans.append((start, y))
            start = None
    require(len(spans) == 4, f"Expected status, instructions, pixels and metrics borders; got {spans}")
    # The long left borders exclude a few corner pixels; restore panel edges.
    return [(start - 2, end + 2) for start, end in spans]


def extract(image, kind):
    spans = panel_spans(image)
    if kind == "state":
        y, bottom = spans[0]
        require(90 <= bottom - y <= 100, "Unexpected status-strip height")
        # Four intact status boxes, rearranged as a 2x2 block above the registers.
        parts = [
            {"box": [32, y + 16, 329, y + 79], "at": [0, 0]},
            {"box": [339, y + 16, 635, y + 79], "at": [322, 0]},
            {"box": [645, y + 16, 943, y + 79], "at": [0, 75]},
            {"box": [953, y + 16, 1248, y + 79], "at": [322, 75]},
            {"box": [648, spans[1][0], 1265, spans[1][1]], "at": [0, 150]},
        ]
        result = Image.new("RGB", (620, 150 + spans[1][1] - spans[1][0]), (10, 10, 10))
    else:
        top, bottom = spans[2 if kind == "pixels" else 3]
        # Keep the whole pixel grid; trim only the metrics panel's empty right side.
        box = [15, top, 633 if kind == "pixels" else 515, bottom]
        parts = [{"box": box, "at": [0, 0]}]
        result = Image.new("RGB", (box[2] - box[0], box[3] - box[1]))
    for part in parts:
        left, top, right, bottom = part["box"]
        require(0 <= left < right <= image.width and 0 <= top < bottom <= image.height,
                f"Crop outside source image: {part}")
        result.paste(image.crop(part["box"]), part["at"])
    return result, parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without writing files")
    args = parser.parse_args()
    originals = {}
    for name in ("source_manifest.json", "evidence_manifest.json"):
        originals.update({item["path"]: item["sha256"] for item in json.loads((ROOT / name).read_text())["files"]})
    runs = json.loads((ROOT / "data.json").read_text())["runs"]
    jobs = []
    for run in runs[8:]:
        prefix = f"Run{run['run']}_{PREFIXES[run['case']]}"
        for index, checkpoint in [(1, "setup"), (4, "pixel1_done"), (6, "final")]:
            source = f"Traces/{prefix}_{index:02d}_{checkpoint}.png"
            jobs.append((source, f"{prefix}_{checkpoint}_state.png", "state"))
        for kind in ("pixels", "metrics"):
            jobs.append((f"Traces/{prefix}_06_final.png", f"{prefix}_final_{kind}.png", kind))
    screenshots = [source for run in runs for source in run["screenshots"]]
    require(len(screenshots) == len(set(screenshots)) == 44, "Expected 44 distinct run screenshots")
    screenshots += [f"Optimizations/{program}_final_state.png" for program in PROGRAMS]
    for source in screenshots:
        jobs.append((source, f"thumb_{Path(source).stem}.png", "thumbnail"))
    require(len({name for _, name, _ in jobs}) == len(jobs), "Duplicate figure filenames")
    if not args.check:
        FIGURES.mkdir(exist_ok=True)
    records = []
    for source, name, kind in jobs:
        source_path = ROOT / source
        require(source in originals and sha(source_path) == originals[source], f"Original checksum mismatch: {source}")
        with Image.open(source_path) as original:
            image = Image.alpha_composite(Image.new("RGBA", original.size, "white"),
                                          original.convert("RGBA")).convert("RGB")
        if kind == "thumbnail":
            result = image.copy()
            result.thumbnail((360, 520), Image.Resampling.LANCZOS)
            parts = [{"box": [0, 0, image.width, image.height], "at": [0, 0]}]
        else:
            result, parts = extract(image, kind)
        output = FIGURES / name
        if args.check:
            require(output.is_file(), f"Missing figure: {name}")
            with Image.open(output) as saved:
                saved = saved.convert("RGB")
                require(saved.size == result.size and saved.tobytes() == result.tobytes(),
                        f"Figure differs from source extraction: {name}")
        else:
            result.save(output, optimize=True)
        records.append({"path": f"Figures/{name}", "kind": kind, "source": source,
                        "source_sha256": originals[source], "source_size": list(image.size),
                        "parts": parts, "size": list(result.size), "sha256": sha(output)})
    manifest = {"description": "Derived presentation images only. State figures rearrange panels from one screenshot; "
                 "pixel and metric figures are unscaled crops; thumbnails resize the entire screenshot. "
                 "No displayed values are replaced or retouched.", "files": records}
    manifest_path = FIGURES / "manifest.json"
    if args.check:
        require(json.loads(manifest_path.read_text()) == manifest, "Figure manifest differs from derived images")
        require({p.name for p in FIGURES.glob("*.png")} == {name for _, name, _ in jobs}, "Unexpected PNG files")
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{'Verified' if args.check else 'Created'} 20 report figures and 49 gallery thumbnails; "
          "all original screenshot checksums match.")


if __name__ == "__main__":
    main()
