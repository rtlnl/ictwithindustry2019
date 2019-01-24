# Info box detection script

This is a really basic script to extract metadata from a sequence of frames extracted from a video.
It detects the presence of on-screen information boxes.

## Rationale
We manually estimated the RGB values for RTL's on-screen information boxes, using Photoshop's color picker tool.
These information boxes are all yellow, and the color is roughly in the following range:

* R: 225 - 260
* G: 170 - 215
* B: 0 - 80

Our code checks for the amount of yellow pixels on each row of pixels, to get the height of the information boxes.

## Requirements
* Python 3.6.6
* Pillow 5.2.0

## Usage
Make sure that you've installed Pillow, and use the script as follows:

```python
import glob
from yellowbox import get_metadata

paths = glob.glob('./Frames/*.jpg')
metadata = get_metadata(paths)
```

You could run this script in parallel by using the `get_metadata()` function on
the paths for different videos. But do make sure that you run the function for
all paths for the same video at once. Else the box IDs won't make sense.

## Resources
The frames in the `./Frames` folder were extracted from [this RTL YouTube video](https://www.youtube.com/watch?v=9ICT6XIuTM8),
using FFMPEG. If you have a similar task, run the following command to get the frames:

* `ffmpeg -i video.mp4 frame%04d.jpg -hide_banner`
