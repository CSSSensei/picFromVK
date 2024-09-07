import requests
import re
from config_data.config import Config, load_config
from DB import vk_photo
config: Config = load_config()


def vk_get_photo(text):
    data = _check_valid_url(text)
    if not data:
        return None
    if len(data.get('response', [{}])[0].get('sizes', [])) <= 0:
        return None

    data = data['response'][0]
    photo_info = vk_photo.Photo(data['owner_id'], data['id'])

    max_size = 0
    min_size = float('inf')
    url_min, url_max = None, None
    for photo in data['sizes']:
        if photo['width'] >= max_size:
            url_max = photo['url']
            max_size = photo['width']
        if photo['width'] <= min_size:
            url_min = photo['url']
            min_size = photo['width']
    small_photo = url_min
    big_photo = url_max
    return small_photo, big_photo, photo_info


def _check_valid_url(url):
    if type(url) != str:
        return None
    pattern = r'-\d+_\d+'
    match = re.search(pattern, url)

    if not match:
        return None
    photo_id = match.group(0)

    response = requests.get('https://api.vk.com/method/photos.getById',
                            params={'access_token': config.vk_parse.token,
                                    'v': config.vk_parse.version,
                                    'photos': photo_id}
                            )
    data = response.json()
    if data.get('error') is None:
        return data
    return None


def vk_get_wall(url):
    if not re.match(r'^vk\.com\/.*$', url):
        if not re.match(r'^https:\/\/vk\.com\/.*$', url):
            if not re.match(r'^http:\/\/vk\.com\/.*$', url):
                return False,
    match = re.search(r'(?<=vk\.com\/).*$', url)
    if not match:
        return False,
    domain = match.group(0)

    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': config.vk_parse.token,
                                    'v': config.vk_parse.version,
                                    'domain': domain,
                                    'count': 10}
                            )
    data = response.json()
    print(data)
    if data.get('error') is None:
        return True, domain
    return False,


if __name__ == "__main__":
    print(vk_get_photo('https://vk.com/kfprod?z=photo-174060696_457239398%2Falbum-174060696_00%2Frev'))
    print(_check_valid_url(None))
    vk_get_wall('https://vk.com/pi_memes')