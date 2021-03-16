# /usr/bin/python3
import re
import random

from xml.sax.saxutils import escape as xml_escape
from cairosvg import svg2png
from PIL import Image

COLORS = [
    ['#DF7FD7', '#DF7FD7', '#591854'],
    ['#E3CAC8', '#DF8A82', '#5E3A37'],
    ['#E6845E', '#E05118', '#61230B'],
    ['#E0B050', '#E6CB97', '#614C23'],
    ['#9878AD', '#492661', '#C59BE0'],
    ['#787BAD', '#141961', '#9B9FE0'],
    ['#78A2AD', '#104F61', '#9BD1E0'],
    ['#78AD8A', '#0A6129', '#9BE0B3'],
]

INITIALS_SVG_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" 
    pointer-events="none" 
    width="90" height="90">
  <defs>
    <linearGradient id="grad">
    <stop offset="0%" stop-color="{color1}" />
    <stop offset="100%" stop-color="{color2}" />
    </linearGradient>
  </defs>
  <rect width="90" height="90" rx="20" ry="20" fill="url(#grad)"></rect>
  <text text-anchor="middle" y="50%" x="50%" dy="0.35em"
        pointer-events="auto" fill="{text_color}" font-family="sans-serif"
        style="font-weight: 400; font-size: 50px">{text}</text>
</svg>
""".strip()
INITIALS_SVG_TEMPLATE = re.sub('(\s+|\n)', ' ', INITIALS_SVG_TEMPLATE)


def get_png_account(text, output_file):

    initials = ':)'

    text = text.strip()
    if text:
        split_text = text.split(' ')
        if len(split_text) > 1:
            initials = split_text[0][0] + split_text[-1][0]
        else:
            initials = split_text[0][0]

    random_color = random.choice(COLORS)
    svg_avatar = INITIALS_SVG_TEMPLATE.format(**{
        'color1': random_color[0],
        'color2': random_color[1],
        'text_color': random_color[2],
        'text': xml_escape(initials.upper()),
    }).replace('\n', '')

    svg2png(svg_avatar, write_to=output_file)
