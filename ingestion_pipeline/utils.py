import os
import re
import json
import echo_bot.ingestion_pipeline.halo_api as halo_api


def json_to_dict(json_str: str) -> dict:
    """Convert a JSON string to a Python dictionary."""
    return json.loads(json_str)


def slugify(name: str) -> str:
    """Turn an article name into a safe filename."""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)  # replace non-alphanumerics with -
    name = re.sub(r"-+", "-", name).strip("-")  # collapse multiple dashes
    return name or "article"


def export_article_to_txt(article: dict, output_dir: str = "kb_txt"):
    """
    Given the JSON/dict you printed above, create one .txt file per article.

    - output_dir: folder to write the files into (created if it doesn't exist)
    """
    os.makedirs(output_dir, exist_ok=True)

    art_id = article.get("id")
    title = article.get("name", "Untitled")
    desc = article.get("description", "") or ""
    tags = article.get("tag_string", "") or ""
    resolution = article.get("resolution", "") or ""
    # Build filename like "005_peplink-port-forwarding-fule.txt"
    if art_id is not None:
        filename = f"{int(art_id):03d}_{slugify(title)}.txt"
    else:
        filename = f"{slugify(title)}.txt"

    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        # Header
        f.write(f"{title}\n")
        f.write("=" * len(title) + "\n\n")

        # Metadata
        if art_id is not None:
            f.write(f"ID: {art_id}\n")
        if tags:
            f.write(f"Tags: {tags}\n")
            f.write("\n")

        # Body
        if desc:
            f.write("Problem / Description:\n")
            f.write(desc.strip())
        else:
            f.write("[No description/problem in API response]")

        if resolution:
            f.write("\n\n")
            f.write("Resolution / Steps:\n")
            f.write(resolution)
        else:
            f.write("[No resolution in API response]")

    print(f"Wrote {path}")
