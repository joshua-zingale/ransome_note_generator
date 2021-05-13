import cv2
import easyocr
import numpy as np
import google_images
import scipy
import random
from difflib import SequenceMatcher
from PIL import Image, ImageDraw
from progress.bar import Bar

# Create reader for functions
reader = easyocr.Reader(['en'])

def get_ransome_note(words: list, images: list, line_length: int = 1920,
	font_size: int = 150, allow_dimension_increase: bool = True) -> np.ndarray:
	'''
	Combines images of words into a collage. The height of the image grows as needed.

	:param words: A list of words inside the collage

	:param images: A list of images (3D numpy arrays)

	:param line_length: The number of pixels in each line; the width of the image

	:param font_size: The pixel height of each image


	:returns: An image in a format readable to cv2 (3D numpy array)
	'''
	
	# resize everything
	# minorly rotate everything
	for i, image in enumerate(images):

		factor = font_size / image.shape[0]

		images[i] = cv2.resize(image, dsize = (int(factor *image.shape[1]), font_size), interpolation = cv2.INTER_AREA)

		deg = random.randrange(-5,5)

		images[i] = scipy.ndimage.rotate(images[i], deg, mode = 'nearest')


	canvas = np.ones(shape = (font_size, line_length, 3))*255

	x = 0
	y = 0


	for word, image in zip(words, images):
		h, w, _= image.shape


		if w > line_length:

			image = cv2.resize(image, dsize = (line_length, font_size), interpolation = cv2.INTER_AREA)

			h, w, _= image.shape

		if x + w > line_length:

			y += font_size

			x = 0

		if y + h > canvas.shape[0]:

			canvas = np.append(canvas, np.ones(shape = (y + h - canvas.shape[0], line_length, 3))*255, axis = 0)


		canvas[y : y + h, x : x + w, :] = image

		x += int(w - font_size*.2)



	return canvas.astype(np.uint8)


def get_word_images(words: list, search_queries: list = ["{word} title", "{word} presentation",
 "definition {word}", "The word {word}"], minimum_similarity: float = 1.0,  progress_bar = False) -> list:
	'''
	Searches Google Images and extracts an image for each word input

	:param words: The words for which the function will search
	
	:param search_queries: A list of all the queries posed to Google in attempts to find
		an image of the word. Within each query, "{word}" is replaced by an input word.

	:param minimum_similarity: Between 0.0 and 1.0. The minimum level of similarity the function can determine
		an image has to an input word for it to consider it a match. 1.0 is a perfect match.
		Technically, the number is the ratio of like-letters to all characters between the the input word
		and detected words
	:param progress_bar: If True, prints a progress bar

	:returns: A list of isolated word images in a format readable to cv2 (numpy arrays)
	'''

	if progress_bar:
		bar = Bar('Getting images...', max=len(words))

	images = []

	for word in words:
		images.append(get_word_image(word, search_queries, minimum_similarity))

		if progress_bar:
			bar.next()

	if progress_bar:
		bar.finish()

	return images



def get_word_image(word: str, search_queries: list = ["{word} title", "{word} presentation", "definition {word}",
	"The word {word}"], minimum_similarity: float = 1.0) -> np.ndarray:
	'''
	Searches Google Images and extracts an image of the word isolated

	:param word: The words for which the function will search
	
	:param search_queries: A list of all the queries posed to Google in attempts to find
		an image of the word. Within each query, "{word}" is replaced by your word.

	:param minimum_similarity: Between 0.0 and 1.0. The minimum level of similarity the function can determine
		an image has to the input word for it to consider it a match. 1.0 is a perfect match.
		Technically, the number is the ratio of like-letters to all characters between the the input word
		and detected words

	:returns: The isolated word image in a format readable to cv2 (numpy array)
	'''
	
	# Really, the letter width should be about .5 times the height; but to facilitate
	# some variety, I chose to keep this number higher.
	MAX_LETTER_WIDTH_HEIGHT = 1.5
	
	# After this many images containing the word have been found, the function randomly returns one of them.
	# The benefit to having this number be higher is there will be more variety in image selections.
	# The down side is as this number gets higher, the function starts taking a LONG time.
	WORDS_BEFORE_QUIT = 2

	# Attempt searching using differnet methods
	# Add all of the images which contain the word to an array in the image's cropped form
	images = []

	for query in search_queries:

		query = query.replace("{word}", word)

		images_temp, _ = google_images.get_images(query, 5, 25)

		# Find all the images that contain the word
		# Loop stops if b_img is ever None, ie there are no more images
		for b_im in images_temp:

			if b_im == None:
				break

			im = __bytes_to_cv2_img(b_im)

			outputs = reader.readtext(im)

			# if the image contains the word, add the cropped version to the list
			for info in outputs:

				if __string_similarity(info[1].lower(), word.lower()) >= minimum_similarity:

					box = info[0]
					im_cropped = im[int(box[0][1]) : int(box[2][1]), int(box[0][0]) : int(box[2][0])]

					h, w, _ = im_cropped.shape

					letter_width = float(w) / len(word)

					# Librally check if the image is wide to realistically be the correct word
					if letter_width/h < MAX_LETTER_WIDTH_HEIGHT:
						images.append(im_cropped)

			
			if len(images) >= WORDS_BEFORE_QUIT:
				break

		if len(images) >= WORDS_BEFORE_QUIT:
				break

	# Generate image if none are found
	if len(images) == 0:

		# Randomly choose either red blue or green
		color_id = random.randrange(0,3)

		color = [0,0,0]

		color[color_id] = 255

		temp_img = Image.new('RGB', (6 * len(word), 10))

		ImageDraw.Draw(temp_img).text((0,0), word, tuple(color))

		im = np.array(temp_img)

		images.append(im)




	return images[random.randrange(0, len(images))]



# -------------- HELPER FUNCTIONS -------------- #

def __string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def __bytes_to_cv2_img(byte_image: bytes) -> np.ndarray:
	'''
	Converts an image from byte format to a cv2 readable format (numpy array)

	:param byte_image: The image in bytes format

	:returns: The converted image
	'''

	nparr = np.frombuffer(byte_image, np.uint8)

	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

	return img
