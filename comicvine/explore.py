from pathlib import Path

from comicvine.client import ComicVineClient
from comicvine.service import ComicVineService
from pipeline.cbz_metadata import CBZMetadataPipeline

CBZ_PATH = Path(
    r"F:\Comics\DC Comics\Green Lantern (2023)\Green Lantern #034 (2026).cbz"
)

client = ComicVineClient()

service = ComicVineService(client)

pipeline = CBZMetadataPipeline(service)

identification = pipeline.identify(CBZ_PATH)

print(f"Series: {identification.parsed.series}")
print(f"Issue: {identification.parsed.issue}")
print(f"Year: {identification.parsed.year}")

print("\nPossible volumes:")

for i, candidate in enumerate(
    identification.candidates,
    start=1
):
    volume = candidate.volume
    
    print(
        f"{i}. "
        f"{volume.get("name")} "
        f"({volume.get("start_year")}) "
        f"[ID: {volume.get("id")}] "
        f"score = {candidate.score:.3f} - "
        f"#{volume.get("count_of_issues")}"
    )
    
selection = int(
    input("\nSelect a volume: ")
)

candidate = identification.candidates[
    selection - 1
]

volume_id = candidate.volume["id"]

print(
    f"\nSelected: "
    f"{candidate.volume.get("name")} "
    f"({candidate.volume.get("start_year")})"
)

print(
    f"Volume ID: {volume_id}, "
)

confirmation = input(
    "\nProcess this CBZ? [y/N]: "
)

if confirmation.lower() != "y":
    print("Cancelled.")
    raise SystemExit

pipeline.process(
    source=CBZ_PATH,
    identification=identification,
    volume_id=volume_id
)

print(
    "\nComicInfo.xml successfully written."
)

