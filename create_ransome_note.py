import image_handling
import cv2
from sys import argv



if len(argv) == 1:
	words = input("Type your message: ").split()

	file_path = input("Type the output destination in form \"output/file/destination/file_name.png\": ")

elif len(argv) == 3:

	try:

		words = argv[1].split()

		file_path = argv[2]




	except:
		print("Improper use of arguments. To call this script from the command line type the following:")
		print("create_ransome_note.py \"YOUR TEXT\" output/file/destination/file_name.png")

		exit()



else:
	print("Improper use of arguments. To call this script from the command line type the following:")
	print("create_ransome_note.py \"YOUR TEXT\" output/file/destination/file_name.png")

	exit()






images = image_handling.get_word_images(words, minimum_similarity = 0.8, progress_bar = True)

print("Building image...")

image = image_handling.get_ransome_note(words, images, font_size = 190, line_length = 1920)

cv2.imwrite(file_path, image)

print("Done")