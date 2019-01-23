from PIL import Image, ImageDraw
from collections import defaultdict


def load_image(filename):
    "Load image file, using RGB values."
    im = Image.open(filename)
    rgb_im = im.convert('RGB')
    return rgb_im


def count_pixels(image, r_range, g_range, b_range):
    "Count pixels with RGB values in a particular range."
    yellow_count = defaultdict(int)
    for width in range(image.width):
        for height in range(image.height):
            pixel = image.getpixel((width,height))
            r,g,b = pixel
            if all([r in range(*r_range),
                    g in range(*g_range),
                    b in range(*b_range)]):
                yellow_count[height] += 1
    return yellow_count


def get_box_data(counts, threshold=200):
    "Extract the top and the bottom of the box."
    selection = [(height, count) for height, count in counts.items() if count >= threshold]
    if len(selection) > 0:
        top = min(height for height,count in selection)
        bottom = max(height for height,count in selection)
        amount_yellow = sum(count for height,count in selection)
    else:
        top = bottom = None
        amount_yellow = 0
    return top, bottom, amount_yellow

# Manually estimated RGB values:
# r: 225 - 260
# g: 170 - 215
# b: 0 - 80

def get_metadata(image_paths, threshold=200):
    """
    Get box metadata for a list of image paths.
    Input: ['frames/frame0001.jpg', 'frames/frame0002.jpg', ...]
    Output: list of dictionaries with metadata for each frame.
    """
    all_metadata = []
    box_count = 0
    box_present = False
    for path in sorted(image_paths):
        image = load_image(path)
        counts = count_pixels(image, r_range=(225,260), g_range=(170,215), b_range=(0,80))
        top, bottom, amount_yellow = get_box_data(counts, threshold=threshold)
        if box_present:
            if amount_yellow == 0:
                box_present = False
        elif amount_yellow != 0:
                box_present = True
                box_count += 1
        
        meta = dict(path=path,
                    bbox=(0, top, image.width, bottom),
                    amount_yellow=amount_yellow,
                    box=box_present,
                    box_id= box_count if box_present else 0)
        all_metadata.append(meta)
    return all_metadata
