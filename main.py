import os
import shutil
import requests
import json
import math
from PIL import Image, ImageDraw, ImageFont

class WordApiService:
    def __init__(self):
        self.api_url = "https://finesentence.com/api/un-imaged-words"

    def get_data_from_service(self):
        """Fetch data from the API service."""
        data, err = self.get_data_from_api()
        if err is not None:
            print(f"Error: {err}")
            return None
        return data

    def get_data_from_api(self):
        """Make a request to the API and handle response."""
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
        except requests.RequestException as e:
            return None, f"Error fetching data from FineSentence API: {e}"

        try:
            words_data = response.json()
        except json.JSONDecodeError as e:
            return None, f"Error parsing JSON response: {e}"

        if "words" not in words_data:
            return None, "Unexpected data format: 'words' key not found"

        return words_data["words"], None

    def extract_word_definitions(self, data):
        """Extract word definitions from the API data."""
        word_definitions = []
        for item in data:
            if not isinstance(item, dict):
                print("Expected a dictionary but got:", type(item))
                continue
            word = item.get('word')
            definition = item.get('definition')
            if word and definition:
                word_definitions.append({'word': word, 'definition': definition})
        return word_definitions

def create_image_with_diagonal_border(width, height, frame_thickness, border_size, colors, angle):
    """Create an image with diagonal borders directly using high resolution for smoother stripes."""
    
    # Set high resolution
    scale_factor = 3
    high_res_width = width * scale_factor
    high_res_height = height * scale_factor
    high_res_frame_thickness = frame_thickness * scale_factor
    high_res_border_size = border_size * scale_factor

    angle_radians = math.radians(angle)
    image = Image.new("RGB", (high_res_width, high_res_height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    tan_angle = math.tan(angle_radians)
    extended_range = max(high_res_width, high_res_height) * 4

    for idx, i in enumerate(range(-extended_range, extended_range, high_res_frame_thickness)):
        color = colors[idx % len(colors)]
        start_x = i
        start_y = -extended_range
        end_x = i + extended_range / tan_angle
        end_y = extended_range
        draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=high_res_frame_thickness)

    draw.rectangle([high_res_border_size, high_res_border_size, high_res_width - high_res_border_size, high_res_height - high_res_border_size], fill=(255, 255, 255))

    # Resize the image to the desired resolution with anti-aliasing
    image = image.resize((width, height), Image.LANCZOS)
    return image

def wrap_text_to_fit_width(draw, text, font, max_width):
    """Wrap text to fit within a specified width."""
    lines = []
    words = text.split(' ')
    line = []
    for word in words:
        line.append(word)
        if draw.textbbox((0, 0), ' '.join(line), font=font)[2] > max_width:
            line.pop()
            lines.append(' '.join(line))
            line = [word]
    lines.append(' '.join(line))
    return lines

def calculate_aligned_position(draw, line, font, max_text_width, x, y, align):
    """Calculate the position of text based on alignment."""
    text_width, text_height = draw.textbbox((0, 0), line, font=font)[2:]
    if align == "center":
        return x + (max_text_width - text_width) // 2, y
    elif align == "right":
        return x + max_text_width - text_width, y
    else:  # Default is left alignment
        return x, y

def draw_wrapped_text(image, word, definition, border_size, word_font_size=60, def_font_size=40, font_path=None, text_color="black", align="left", word_padding=20, def_padding=10, footer_text="finesentence.com", footer_font_size=20):
    """
    Draw wrapped text on the given image at the specified position with customizable options.

    Parameters:
    - image: PIL.Image object where the text will be drawn.
    - word: The word to draw on the image.
    - definition: The definition to draw on the image.
    - border_size: The size of the border to ensure text stays within the border.
    - word_font_size: The size of the font for the word. Default is 60 (1.5 times original).
    - def_font_size: The size of the font for the definition. Default is 40 (2 times original).
    - font_path: The path to the .ttf font file. Default is None, which uses the default PIL font.
    - text_color: The color of the text. Default is "black".
    - align: The alignment of the text. Options are "left", "center", "right". Default is "left".
    - word_padding: The padding between the word and the top border. Default is 20.
    - def_padding: The padding between the word and the definition. Default is 10.
    - footer_text: The footer text to display in the bottom right corner. Default is "finesentence.com".
    - footer_font_size: The size of the font for the footer text. Default is 20.
    """
    draw = ImageDraw.Draw(image)
    if font_path:
        word_font = ImageFont.truetype("Lato-Regular.ttf", word_font_size)
        def_font = ImageFont.truetype("Lato-Regular.ttf", def_font_size)
        footer_font = ImageFont.truetype("Lato-Regular.ttf", footer_font_size)
    else:
        word_font = ImageFont.load_default()
        def_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Calculate the maximum width for the text
    image_width, image_height = image.size
    max_text_width = image_width - 2 * border_size - 20  # Extra padding to avoid touching the border

    # Reserve space for the footer text
    footer_text_height = draw.textbbox((0, 0), footer_text, font=footer_font)[3]
    reserved_space = footer_text_height + border_size + 10

    # Wrap the definition text to fit within the max_text_width
    def_lines = wrap_text_to_fit_width(draw, definition, def_font, max_text_width)

    # Draw the word with a larger font size and padding
    x, y = border_size + 10, border_size + word_padding
    word_position = calculate_aligned_position(draw, word, word_font, max_text_width, x, y, align)
    draw.text(word_position, word, fill=text_color, font=word_font)
    y += draw.textbbox((0, 0), word, font=word_font)[3] + def_padding

    # Draw each line of the definition with proper alignment, ensuring not to overlap the reserved space
    for line in def_lines:
        if y + draw.textbbox((0, 0), line, font=def_font)[3] + reserved_space <= image_height:
            position = calculate_aligned_position(draw, line, def_font, max_text_width, x, y, align)
            draw.text(position, line, fill=text_color, font=def_font)
            y += draw.textbbox((0, 0), line, font=def_font)[3]
        else:
            break  # Stop drawing if there's no space left without overlapping the footer text

    # Draw the footer text in the bottom right corner within the white area
    text_width, text_height = draw.textbbox((0, 0), footer_text, font=footer_font)[2:]
    corner_x = image_width - text_width - border_size - 10
    corner_y = image_height - text_height - border_size - 10
    draw.text((corner_x, corner_y), footer_text, fill=text_color, font=footer_font)

    return image

def main():
    """Main function to fetch data, generate image, and save it."""
    # Directory setup
    output_dir = "generated_images"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Fetch word definitions from the API
    service = WordApiService()
    data = service.get_data_from_service()
    if data:
        word_definitions = service.extract_word_definitions(data)

        # Iterate over each word definition and create an image
        for index, word_def in enumerate(word_definitions):
            word = word_def['word']
            definition = word_def['definition']

            # Create the image with the extracted text
            angle = 30
            frame_thickness = 20
            border_size = 20
            colors = [(0, 0, 0), (51, 129, 138), (160, 236, 246), (249, 147, 78), (236, 249, 247)]
            image = create_image_with_diagonal_border(800, 400, frame_thickness, border_size, colors, angle)

            # Draw the text on the image with enhancements
            font_path = "Lato-Regular.ttf"  # Ensure this path is correct
            text_color = "#1F2937"  # Dark blue color similar to the image
            image = draw_wrapped_text(image, word, definition, border_size, word_font_size=40, def_font_size=20, font_path=font_path, text_color=text_color, align="left", word_padding=30, def_padding=15)

            # Save the image to a file
            output_path = os.path.join(output_dir, f"word_image_{index + 1}.png")
            image.save(output_path)
            print(f"Image saved to {output_path}")

if __name__ == "__main__":
    main()
