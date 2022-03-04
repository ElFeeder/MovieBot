import face_recognition
import os
import cv2

from simple_image_download import simple_image_download as sid


# First fetch the images with user given query
response = sid.simple_image_download() 
searchQuery = 'Shrek'

response.download(keywords = searchQuery, limit = 10, extensions = {'.jpg', '.png', '.ico', '.gif', '.jpeg'})

DIR_KNOWN = "Characters"     # Directories where the faces are
DIR_UNKNOWN = "simple_images"



tolerance = 0.05         # Tolerance of a match

frameThickness = 2      # These two are to draw rectangles around the faces
fontThickness = 2

model = "cnn"           # What NN we'll be using

knownFaces = []                         # List of all the different faces that we know
knownNames = []                         # Give a name to each face
facesNumber = []                        # How many images of each face
diffFaces = len(os.listdir(DIR_KNOWN))  # How many different faces


print("Loading known faces...")

for name in os.listdir(DIR_KNOWN):                      # List of all the names in the Known directory
    print("")
    print("Checking " + name + " images")
    print("")
    total = 0

    for filename in os.listdir(f"{DIR_KNOWN}/{name}"):  # List all files there
        print("Checking " + filename)

        # Load an image
        image = face_recognition.load_image_file(f"{DIR_KNOWN}/{name}/{filename}")
        
        # If we found exactly one face, use it
        if(len(face_recognition.face_encodings(image)) == 1):
            encoding = face_recognition.face_encodings(image)

            # Add the face and the name to the lists
            knownFaces.append(encoding)
            knownNames.append(name)
            total += 1

        elif(len(face_recognition.face_encodings(image)) > 1):
            print(" File " + filename + " had more than one face")

        elif(len(face_recognition.face_encodings(image)) < 1):
            print(" File " + filename + " had no faces")

    facesNumber.append(total)


print("")
print("Processing unknown faces...")

for filename in os.listdir(DIR_UNKNOWN):
    print("Checking " + filename)
    image = face_recognition.load_image_file(f"{DIR_UNKNOWN}/{filename}")

    # Find every face in each given image and encode each one
    locations = face_recognition.face_locations(image, model = model)
    encodings = face_recognition.face_encodings(image, locations)

    # Make it workable by CV2
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # For each encoding that we have, compare against encodings of known faces
    for faceEncoding, faceLocation in zip(encodings, locations):
        results = face_recognition.compare_faces(knownFaces, faceEncoding, tolerance)
        finalResults = []

        # If we have a match, the associated name will be in the same position as the face
        # was in knownFaces. We'll have to handle the array "results" in a way that we can
        # work with (results is an array of arrays)
        
        # subdivision is the second layer array
        for subdivision in results:
            isMatch = 128               # Each subarray has 128 booleans

            # result is the third layer
            for result in subdivision:
                if result == False:     # Count how many falses
                    isMatch -= 1

            # Create an array which has all the percentages of the encoding vs the known ones
            finalResults.append((isMatch * 100) / 128)
             
        person = 0
        count = 0
        past = 0
        while person < diffFaces:           # For each person
            number = facesNumber[person]    # How many images of each
            
            good = 0
            while count < number + past:        # Only count the images relative to the person in question
                if (finalResults[count] >= 65): # If it's over 65%, it's good
                    good += 1
                count += 1
            past = count                        # How many images of other people have passed

            # If more than 80% are over 75%, it's a match 
            if (good > 0.8 * facesNumber[person]):
                match = knownNames[count - 1]

                print("")
                print("Match found: " + match)

                # Draw a rectangle around the face
                topLeft = (faceLocation[3], faceLocation[0])
                bottomRight = (faceLocation[1], faceLocation[2])

                # Have a specific color for each name
                color = [(ord(c.lower())-97)*8 for c in match[:3]]

                cv2.rectangle(image, topLeft, bottomRight, color, frameThickness)

                # Nameplate
                topLeft = (faceLocation[3], faceLocation[2])
                bottomRight = (faceLocation[1], faceLocation[2] + 22)

                cv2.rectangle(image, topLeft, bottomRight, color, cv2.FILLED)
                
                title = str(match) + "  " + str(int(good / facesNumber[person] * 100)) + "%"
                
                # Name the rectangle
                cv2.putText(image, title, (faceLocation[3] + 10, faceLocation[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), fontThickness)


            person += 1 # Next person

    # Show the image until I press something
    cv2.imshow(filename, image)
    cv2.waitKey(0)
    cv2.destroyWindow(filename)