from client import ComicVineClient


client = ComicVineClient()

volume = client.get_volume(109498)

print(volume)