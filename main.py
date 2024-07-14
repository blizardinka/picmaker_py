from PIL import Image, ImageDraw, ImageFont

def create_diagonal_stripes_frame(image, frame_thickness, colors):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    num_colors = len(colors)

    for i in range(0, width + height, frame_thickness):
        color = colors[(i // frame_thickness) % num_colors]
        draw.line([(i, 0), (0, i)], fill=color, width=frame_thickness)
        draw.line([(width - i, height), (width, height - i)], fill=color, width=frame_thickness)
        draw.line([(0, i), (i, height)], fill=color, width=frame_thickness)
        draw.line([(width, i), (width - i, 0)], fill=color, width=frame_thickness)

def create_colorful_frame_image(output_path, text="keyesc.xyz"):
    # Define the image size and colors
    image_width, image_height = 1024, 512
    original_frame_thickness = 50
    frame_thickness = int(original_frame_thickness * 0.7)  # Reduce thickness by 30%
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # Create a new image with a white background
    image = Image.new('RGB', (image_width, image_height), 'white')
    
    # Draw the colorful frame with diagonal stripes
    create_diagonal_stripes_frame(image, frame_thickness, colors)
    
    # Draw the inner white rectangle
    draw = ImageDraw.Draw(image)
    draw.rectangle([frame_thickness, frame_thickness, image_width - frame_thickness, image_height - frame_thickness], fill='white')
    
    # Load a font
    font = ImageFont.load_default()
    
    # Calculate text size and position using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (image_width - text_width) // 2
    text_y = (image_height - text_height) // 2
    
    # Draw the text in the center of the image
    draw.text((text_x, text_y), text, fill='grey', font=font)
    
    # Save the image to a file
    image.save(output_path)

# Create the image with a colorful frame and centered text
desired_output_path = 'output_image.png'  # Change this to your desired path
create_colorful_frame_image(desired_output_path)
