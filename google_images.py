import requests
import base64



def get_images(search_query: str, starting_image_id: int, ending_image_id: int) -> (bytes, str):
	'''
	Gets images from Google Images with a specified search queary
	
	:param search_query: The Google search query

	:param starting_image_id: The number corrisponding to the order in which the image appears after the search;
		that is, 0 corrisponds to the first image result, 1 to the second, 2 to the third...
		This is the id of the first image, inclusive
	
	:param ending_image_id: This is the id of the last image, exclusive. 


	:returns: A tuple containing two lists (images, file_types). Images contains the byte data of each image
	and file_types contains the coorisponding filetypes. For each id that is not present after the queary,
	the function saves None to both the image and the file_type

	:raises ConnectionError: If no valid web-response is recieved from Google
	'''
	response = response = requests.get("https://www.google.com/search?q=" + search_query.replace(" ", "+") 
		+ "&tbm=isch",
	 headers = __get_headers())

	if response == False:
		raise ConnectionError("Could not recieve data from Google")

	images, file_types = [], []

	for i in range(starting_image_id, ending_image_id):


		b64_str, file_type = __get_base64_image_string(response.text, i)

		# Check for invalid id
		if b64_str == None:
			images.append(None)
			file_types.append(None)
			continue

		byte_data = base64.b64decode(b64_str)

		images.append(byte_data)
		file_types.append(file_type)

	return images, file_types




# --------------- HELPER FUNCTIONS --------------- #

def __get_headers() -> dict:
	'''
	Gets the minimum headers required for Google to handle requests
	
	:returns: The headers
	'''
	return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}



def __get_base64_image_string(text: str, image_id: int) -> (str, str):
	'''
	Gets the base64 encoded string representing an image within "text"

	:param text: The body of text containing the image's string representation

	:param image_id: The id of the image within "text"

	:returns: A touple, (base64_string, type), which contains the base64 encoded string and the image data type.
	If no image with the id specified ecists on the webpage, the function returns (None, None)
	'''

	first_marker = "_setImgSrc('" + str(image_id)
	second_marker = "image\\/"
	third_marker = "base64,"

	temp_index = text.find("_setImgSrc('" + str(image_id))

	if temp_index == -1:
		return None, None

	image_type = __get_substring(text[temp_index:], text[temp_index:].find(second_marker) + len(second_marker), [";"])

	starting_index = temp_index + text[temp_index:].find(third_marker) + len(third_marker)

	base64_string = __get_substring(text, starting_index, ["\'"], ["\\"])

	# pad string to be proper length
	pad = len(base64_string) % 4
	base64_string += "="*pad

	return base64_string, image_type


def __get_substring(string: str, starting_character_index: int, terminating_characters: list, ignore_characters: list = []) -> str:
	'''
	Gets the substring within "string" which begins at the "starting_character_index" and
	ends at the "terminating_character".

	:param string: The string in which the desired substring resides

	:param starting_character_index: The index of the first character in the substring

	:param terminating_characters: The characters which proceeds the final character in the substring. If any character is reached, the substring ends.

	:param ignore_characters: The characters to be ignored

	:returns: The substring
	'''

	s = ""

	i = starting_character_index

	curr_char = string[i]

	while curr_char not in terminating_characters:

		# Skip ignored characters
		if curr_char in ignore_characters:

			i += 1
			curr_char = string[i]

			continue

		s += curr_char

		i += 1

		curr_char = string[i]

	return s