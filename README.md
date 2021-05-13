# ransome_note_generator
A small program which creates a collage of images scrapped from Google to create user inputted bodies of text.

To run the program, you can either call it from the command line or just run the script.

To call it from the command line, navigate to the directory containing the python file and then type 'py create_ransome_note_script.py "YOUR TEXT" output/file/destination/file_name.png'. If "py" does not work, "python", "python3", or "py3" might work.

The image collection portion can take a few minutes, especially if there are some wierd words in your message. If the program cannot find an image online to acompany your word, it will create an image itself.


DEPENDENCIES: 

Scipy, Pillow, progress (found https://pypi.org/project/progress/), NumPy, EasyOCR, OpenCV
