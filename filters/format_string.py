import re
from typing import Union
from config_data.config import config


def transform_string(input_string: Union[str, None], input_public_name=False, public_name='', owner_id=0,
                     wall_post_link: Union[str, None] = None) -> Union[str, None]:
    if input_string is None:
        if input_public_name and public_name and owner_id != 0:
            link = f'https://vk.com/club{abs(owner_id)}' + (f'?w=wall{wall_post_link}' if wall_post_link else '')
            return f'<b><a href="{link}">{public_name}</a></b>'
        return None

    pattern = r'\[([^\|]+)\|([^\]]+)\]'

    def replace_pattern(match):
        str1, str2 = match.groups()
        return f'<a href="https://vk.com/{str1}">{str2}</a>'

    transformed_string = re.sub(pattern, replace_pattern, input_string)

    if input_public_name and public_name and owner_id != 0:
        link = f'https://vk.com/club{abs(owner_id)}' + (f'?w=wall{wall_post_link}' if wall_post_link else '')
        transformed_string = f'<b><a href="{link}">{public_name}</a></b>\n{transformed_string}'
    if len(transformed_string) > config.tg_bot.MAX_SYMBOLS:
        transformed_string = transformed_string[:config.tg_bot.MAX_SYMBOLS - 4] + '...'
    return transformed_string


def format_string(text: str):
    if not text:
        return '⬛️'
    return text.replace('<', '«').replace('>', '»')


def find_first_number(input_string):
    match = re.search(r'\d+', input_string)

    if match:
        return match.group()
    else:
        return None


def split_text(text, n):
    result = []
    lines = text.split('\n')
    current_chunk = ''
    current_length = 0

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= n:  # Check if adding the line and '\n' fits in the chunk
            if current_chunk:  # Add '\n' if it's not the first line in the chunk
                current_chunk += '\n'
            current_chunk += line
            current_length += len(line) + 1
        else:
            result.append(current_chunk)
            current_chunk = line
            current_length = len(line)

    if current_chunk:
        result.append(current_chunk)

    return result
