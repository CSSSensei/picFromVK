from typing import Dict, Union, Any, List, Tuple
import requests
import re
from DB.vk_photo import WallPost, PhotoPost, Photo
from config_data.config import Config, load_config
from DB import vk_photo

config: Config = load_config()


def vk_get_photo(text) -> Union[PhotoPost, None]:
    data = _get_photo_json(text)
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
    return PhotoPost(photo=big_photo, thumbnail=small_photo, photo_info=photo_info)


def _extract_wall_id(text: str) -> Union[str, None]:
    pattern = r'-\d+_\d+'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def _fetch_wall_post(wall_id: str) -> Dict[str, Any]:
    response = requests.get('https://api.vk.ru/method/wall.getById',
                            params={'access_token': config.vk_parse.token,
                                    'v': config.vk_parse.version,
                                    'posts': wall_id})
    return response.json()


def _extract_caption_and_photos(data: Dict[str, Any]) -> Tuple[Union[str, None], List[str], int]:
    caption, photos, photo_id = None, [], 0

    if data.get('text'):
        caption = data['text']

    if data.get('attachments'):
        for attachment in data['attachments']:
            if isinstance(attachment, dict) and attachment.get('type') == 'photo':
                if photo_id != 0:
                    photo_id = attachment.get('id', 0)
                photo = attachment.get('photo')
                if photo and photo.get('sizes'):
                    url = photo['sizes'][-1].get('url')
                    if url:
                        photos.append(url)

    return caption, photos, photo_id


def vk_get_wall_post(text: Any) -> Union[WallPost, None]:
    if not isinstance(text, str):
        return None

    wall_id = _extract_wall_id(text)
    if not wall_id:
        return None

    data = _fetch_wall_post(wall_id)

    if data.get('error') or len(data.get('response', [{}])[0]) <= 0:
        return None

    data = data['response'][0]
    owner_id = abs(data.get('owner_id', 198071571))
    caption, photos, photo_id = _extract_caption_and_photos(data)
    public_name, public_photo = _api_group_name(owner_id)

    return WallPost(photos, caption, public_name, public_photo, Photo(owner_id=owner_id, photo_id=photo_id), wall_id)


def _get_photo_json(url):
    if type(url) is not str:
        return None
    pattern = r'-\d+_\d+'
    match = re.search(pattern, url)

    if not match:
        return None
    photo_id = match.group(0)

    response = requests.get('https://api.vk.ru/method/photos.getById',
                            params={'access_token': config.vk_parse.token,
                                    'v': config.vk_parse.version,
                                    'photos': photo_id}
                            )
    data = response.json()
    if data.get('error') is None:
        return data
    return None


# def vk_get_wall(url):
#     if not re.match(r'^vk\.com\/.*$', url):
#         if not re.match(r'^https:\/\/vk\.com\/.*$', url):
#             if not re.match(r'^http:\/\/vk\.com\/.*$', url):
#                 return False,
#     match = re.search(r'(?<=vk\.com\/).*$', url)
#     if not match:
#         return False,
#     domain = match.group(0)
#
#     response = requests.get('https://api.vk.ru/method/wall.get',
#                             params={'access_token': config.vk_parse.token,
#                                     'v': config.vk_parse.version,
#                                     'domain': domain,
#                                     'count': 10}
#                             )
#     data = response.json()
#     if data.get('error') is None:
#         return True, domain
#     return False,


def _api_group_name(domain: int) -> Tuple[str, str]:
    response = requests.get('https://api.vk.ru/method/groups.getById',
                            params={'access_token': config.vk_parse.token,
                                    'v': config.vk_parse.version,
                                    'group_id': domain}
                            )
    data = response.json()
    name = data['response'][0]['name']
    photo = data['response'][0]['photo_200']
    return name.replace('<', '').replace('>', ''), photo


if __name__ == "__main__":
    vk_get_photo('https://vk.com/aacontent?z=photo-198071571_457368483%2Fwall-198071571_82227')
    print(vk_get_wall_post('https://vk.com/webm?w=wall-30316056_7893265'))
    print(_api_group_name(198071571))
