import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import smtplib
import ssl
import random
from random import randint

# Import pictures from folder and copy the name from the img to a list.
# for using if face is recognized.
path = "Pictures"
images = []
PicNames = []

# Picture list
myList = os.listdir(path)

# Read out the picture names and add them to the list above.
# And remove the extension name (Example .jpg)
for pic in myList:
	curImg = cv2.imread(f'{path}/{pic}')
	images.append(curImg)
	PicNames.append(os.path.splitext(pic)[0])
print(PicNames)


# looping trough images and find the encoding/measurements
# for each picture in folder.
# convert webcam input to RGB for measurements


def find_encodings(images):
	enc_images = []
	for im in images:
		im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
		encode = face_recognition.face_encodings(im)[0]
		enc_images.append(encode)
	return enc_images



# Load the findings in function above in a list

encodeListKnown = find_encodings(images)
print("Encoding complete")


cap = cv2.VideoCapture(0)


# A log function to log when someone entry (must be authenticated to log). Only log one's a minute IF not -
# a new authorized face is detected

def log(name):
	with open('logfile.csv', 'r+') as file:
		data = file.readlines()
		now = datetime.now()
		dtstring = now.strftime('%H:%M')
		entry = f'{name}, {dtstring}'
		if entry not in data:
			file.writelines(f'\n{name}, {dtstring}')
			TWOFA(name)


# Logs the findings in function above in a list

def TWOFA(name):
	randomcode = ''.join([str(randint(0,9)) for _ in range(4)])
	random_message = """\
	Subject: One time code.

	Use the code: """

	port = 465  # For SSL
	smtp_server = "smtp.example.com"
	sender_email = "mailadcdress"
	receiver_email = name
	password = "password"
	message = random_message + randomcode
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message)

	twofactorcheck(randomcode)

# This function (above) email the user with 2fa.

def twofactorcheck(randomcode):
	inputcode = input('Code received on Email: ')
	if inputcode == randomcode:
		print('Code accepted. Welcome')
	else:
		print('Incorrect code.')


# Resize video capture to half the size to save computing power


while True:
	success, img = cap.read()
	image_resize = cv2.resize(img, (0, 0), None, 0.50, 0.50)
	image_resize = cv2.cvtColor(image_resize, cv2.COLOR_BGR2RGB)

# find measurements/distance and encode the face in webcam

	faceInCurrentFrame = face_recognition.face_locations(image_resize)

	encodesCurrentFrame = face_recognition.face_encodings(image_resize, faceInCurrentFrame)

# check for matches in measurements/distances in face on the webcam against the encoded pictures in folder

	for encodeFace, faceLocation in zip(encodesCurrentFrame, faceInCurrentFrame):
		matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
		FaceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
		matchIndex = np.argmin(FaceDistance)

# show name, rectangle if face is matched
# rescale the reading of webcam to show rectangle on.
		if matches[matchIndex]:
			y1, x2, y2, x1 = faceLocation
			y1, x2, y2, x1 = y1*2, x2*2, y2*2, x1*2

			name = PicNames[matchIndex].upper()

			cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)
			cv2.rectangle(img, (x1, y2), (x2, y2), (0, 255, 0), cv2.FILLED)
			cv2.putText(img, name, (x1+10, y2-10), cv2.QT_FONT_NORMAL, 0.5, (0, 255, 0), 1)
			log(name)


# Show webcam window.

	cv2.imshow('Webcam', img)
	cv2.waitKey(1)
