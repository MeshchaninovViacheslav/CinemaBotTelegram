import json
import typing as tp
import aiohttp

with open("package.json") as f:
    config = json.load(f)


async def process_response(response: tp.List[tp.Dict[str, tp.Union[str, float]]], ):
    if not response:
        return []

    top_count_response = 5

    results = []
    for film in response:
        film_info = dict()

        # title
        film_info["title"] = film["title"]
        if film["original_language"] == config["ru_language"]:
            film_info["title"] = film["original_title"]

        # rate
        film_info["rate"] = int(film["vote_average"]) * int(film["vote_count"])
        film_info["rating"] = film["vote_average"]

        # id
        film_info["id"] = film["id"]

        # year
        film_info["year"] = film["release_date"][:4] if "release_date" in film else "no release year"  # type: ignore

        # overview
        film_info["overview"] = film["overview"]

        # provider
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{config['api_search_url']}/movie/{film_info['id']}"  # type: ignore
                                   f"/watch/providers",
                                   params={'api_key': config["api_key"]}) as response:  # type: ignore
                response = (await response.json())['results']  # type: ignore
                if config["ru_region"] in response and "link" in response[config["ru_region"]]:
                    film_info["link"] = response[config["ru_region"]]["link"]
                else:
                    film_info["link"] = ""

        # poster
        if "poster_path" not in film or not film["poster_path"]:
            continue
        film_info["poster"] = f"https://image.tmdb.org/t/p/w600_and_h900_bestv2/{film['poster_path']}"

        results.append(film_info)

    # sort result by rate
    results.sort(key=lambda film_: film_["rate"], reverse=True)

    return results[:top_count_response]
