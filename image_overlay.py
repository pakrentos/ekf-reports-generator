from PIL import Image, ImageDraw, ImageFont
import io

def overlay_number(image_path, number):
    # Open the image
    with Image.open(image_path) as img:
        # Create a drawing object
        draw = ImageDraw.Draw(img)
        
        # Get image dimensions
        width, height = img.size
        
        # Choose a font (you may need to specify a font file path)
        font_size = int(min(width, height) / 7)  # Adjust size as needed
        font = ImageFont.truetype("Arial.ttf", font_size)
        
        # Convert number to string
        number_str = str(number)
        
        # Get size of the text
        left, top, right, bottom = font.getbbox(number_str)
        text_width = right - left
        text_height = bottom - top
        
        # Calculate circle size and position
        circle_diameter = max(text_width, text_height) * 1.8  # Increased for larger circle
        circle_radius = circle_diameter / 2
        circle_x = width / 2
        circle_y = height / 3
        
        # Increase border width
        border_width = 5  # Adjust this value to increase or decrease border width
        
        # Draw the white circle with thicker black border
        draw.ellipse([circle_x - circle_radius, circle_y - circle_radius,
                      circle_x + circle_radius, circle_y + circle_radius],
                     fill='white', outline='black', width=border_width)
        
        # Calculate position to center the text within the circle
        text_x = circle_x - text_width / 2
        text_y = circle_y - text_height / 1.3
        
        # Draw the number
        draw.text((text_x, text_y), number_str, fill='black', font=font)
        
        # Save to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return buffer

# Usage example:

def create_iq_image(subject_number, iq_value):
    result = overlay_number("assets/brain.jpg", int(iq_value))
    with open(f"subjects/{subject_number}/output_image.png", "wb") as f:
        f.write(result.getvalue())
