import base64
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import textwrap

TRAIN_CARD_TEMPLATE: str = Path(__file__).parent.parent / 'train_card.png'


def get_card_name(departure_location: str, arrival_location: str, departure_time: str, arrival_time: str):
    return (base64.b64encode(f"{departure_location}_{arrival_location}_{departure_time}_{arrival_time}".encode("utf-8")) + b".png").decode("utf-8")


def generate_train_card(departure_location: str, arrival_location: str, departure_time: str, arrival_time: str):
    # write text on image
    # create image object with the input image
    image = Image.open(TRAIN_CARD_TEMPLATE)
    draw = ImageDraw.Draw(image)
    # set font
    font = ImageFont.truetype(str(Path(__file__).parent.parent / 'RobotoMono-Regular.ttf'), size=20)
    font_bold = ImageFont.truetype(str(Path(__file__).parent.parent / 'RobotoMono-Bold.ttf'), size=20)

    # wrap text
    departure_location_w = textwrap.fill(departure_location, width=12)
    arrival_location_w = textwrap.fill(arrival_location, width=12)
    departure_time_w = textwrap.fill(departure_time, width=12)
    arrival_time_w = textwrap.fill(arrival_time, width=12)

    # draw text
    draw.text((20, 5), "Departure", font=font_bold, fill='white')
    draw.text((270, 5), "Arrival", font=font_bold, fill='white')
    draw.text((20, 50), "From: ", font=font, fill='white')
    draw.text((90, 50), departure_location_w, font=font, fill='white')
    draw.text((270, 50), "To: ", font=font, fill='white')
    draw.text((320, 50), arrival_location_w, font=font, fill='white')
    draw.text((45, 120), "At: ", font=font, fill='white')
    draw.text((90, 120), departure_time_w, font=font, fill='white')
    draw.text((270, 120), "At: ", font=font, fill='white')
    draw.text((320, 120), arrival_time_w, font=font, fill='white')

    # save image
    card_name = get_card_name(departure_location, arrival_location, departure_time, arrival_time)
    image.save(card_name)
    image.close()
    return card_name
