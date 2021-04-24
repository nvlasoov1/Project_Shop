from PIL import Image


def resize_image(input_image_path,
                 output_image_path):
    original_image = Image.open(input_image_path)
    resized_image = original_image.resize((180, 180))
    resized_image.save(output_image_path)