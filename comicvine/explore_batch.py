from pathlib import Path
from comicvine.client import ComicVineClient
from comicvine.service import ComicVineService
from pipeline.cbz_metadata import CBZMetadataPipeline
from pipeline.batch import BatchPipeline

CBZ_DIRECTORY = Path(
    r"F:\Comics\DC Comics"
)

sources = sorted(
    CBZ_DIRECTORY.glob("*.cbz")
)

client = ComicVineClient()
service = ComicVineService(client)
metadata = CBZMetadataPipeline(service)
batch = BatchPipeline(metadata)

items = batch.identify(
    sources
)

for item in items:
    print(
        f"\n{item.source.name}"
    )

    print(
        f"  Series: "
        f"{item.identification.parsed.series}"
    )

    print(
        f"  Issue: "
        f"{item.identification.parsed.issue}"
    )

    print(
        f"  Year: "
        f"{item.identification.parsed.year}"
    )

    if not item.has_candidates():
        print(
            "  No candidates found."
        )
        continue

    print("  Candidates:")

    for index, candidate in enumerate(
        item.identification.candidates,
        start=1
    ):
        volume = candidate.volume

        print(
            f"    {index}. "
            f"{volume.get('name')} "
            f"({volume.get('start_year')}) "
            f"[{volume.get('id')}]"
        )