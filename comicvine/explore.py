from client import ComicVineClient


client = ComicVineClient()

volumes = client.search_volumes("Batman")

for volume in volumes:
    print(volume)