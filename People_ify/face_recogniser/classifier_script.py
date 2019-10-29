'''
code to upload images to azure-cognitiveservices-api and group them
'''

import asyncio, io, glob, os, sys, time, uuid, requests, shutil
from os import listdir
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw  # Pillow
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType

# Set the FACE_SUBSCRIPTION_KEY environment variable with your key as the value.
KEY = os.environ['FACE_SUBSCRIPTION_KEY']
# Set the FACE_ENDPOINT environment variable with the endpoint from your Face service in Azure.(in our case Central India)
ENDPOINT = os.environ['FACE_ENDPOINT']
# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))


def identify_face(image, face_ids, image_n_faces,PERSON_GROUP_ID):
    # Identify faces
    for image in list(image_n_faces.keys()):
        for face in image_n_faces[image]:
            result = face_client.face.identify(face.id, PERSON_GROUP_ID)  # have to write code for if there are no Person/ or no images in all Persons, in Person group.
            if not result:
                person = face_client.person_group_person.create(PERSON_GROUP_ID, face.id)  # define a new person 
                w = open(image, 'r+b')  # correct 
                face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, person.person_id, w)  # add face to person
                try:
                    os.mkdir("/home/akshay/Code_/code/username/" + str(face.id))  # creates a directory for new face_id
                    n = "/home/akshay/Code_/code/username/" + str(face.id)  # moves image from uploads directory to new directory
                    shutil.move(image, n)
                except FileExistsError:  # if directory exists 
                    n = "/home/akshay/Code_/code/username/" + str(face.id)  # moves image from uploads directory to new directory
                    shutil.move(image, n)
                    
            else:
                """
                may have to remove for-loop if result is not iterable
                """ 
                for person in result:  # in case face matches more than 1 image 
                    w = open(image, 'r+b')
                    face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, person.person_id, w)
                    try:
                        os.mkdir("/home/akshay/Code_/code/username/" + str(face.id))  # creates a directory for new face_id
                        n = "/home/akshay/Code_/code/username/" + str(face.id)  # moves image from uploads directory to new directory
                        shutil.move(image, n)

                    except FileExistsError:  # if directory exists 
                        n = "/home/akshay/Code_/code/username/" + str(face.id)  # moves image from uploads directory to new directory
                        shutil.move(image, n)
                    
    # results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
    # print('Identifying faces in {}')
    # if not results:
    #     # Define new persons
    #     for x in face_ids:
    #         person = face_client.person_group_person.create(PERSON_GROUP_ID, x)
    #         # create a seperate folder for this person
    #         # print('No person identified in the person group for faces from the{}.'.format(os.path.basename(image.name)))
    # else:
    #     for person in results:
    #         # move image from upload directory to directory for matched face_id
    #         print('Person for face ID {} is identified in {} with a confidence of {}.'.format(person.face_id, os.path.basename(image.name), person.candidates[0].confidence)) # Get topmost confidence score


def main(username):
    '''
        Detect faces in images that are just uploaded, basically code to check if there is a face, if not  
        and then create a dictionary with {"image_path": [face0, face2, face3, ...]} structure
    '''
    # get all 'files' inside upload/username directory
    folder_path = "/home/akshay/Code_/code/People_ify/People_ify/uploads/" + str(username)  # will have to change while hosting!!!
    onlyfiles = [f for f in listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))] 

    path_list = []
    for f in onlyfiles:    # create pathname for all images
        img_path = glob.glob(os.path.join(folder_path, f))
        path_list.append(img_path)

    img_with_faces = {} # key is path to image, value is 'list' of detected faces  
    for f in path_list:
        image = open(f, 'r+b')
        detected_faces = face_client.face.detect_with_stream(image)

        if not detected_faces:
            pass  # "move" image to username/miscellaneous/ directory
        else:
            img_with_faces[f] = []
            for face in detected_faces:
                img_with_faces[f].append(face)

    identify_face(img_with_faces)

    
if "__name__" == "__main__":
    main()


# for a new user
# PERSON_GROUP_ID = 'my-unique-person-group'
# face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)


# detected_faces = face_client.face.detect_with_url(url=single_face_image_url)  #  extracting name of file from url
    # if not detected_faces:
    #     raise Exception('No face detected from image {}'.format(single_image_name))
    #     #  add code to sort in 'objects/ no human' folder

    # # Display the detected 'face ID' in the first single-face image.
    # # Face IDs are used for comparison to faces (their IDs) detected in other images.
    # print('Detected face ID from', single_image_name, ':')
    # for face in detected_faces: 
    #     print (face.face_id)
    # print()
    # # Save this ID for use in Find Similar
    # first_image_face_ID = detected_faces[0].face_id


# def extract_uploaded_image(paths):
#     '''
#     Identify a face against a defined PersonGroup
#     '''
#     # Reference image for testing against
#     group_photo = 'test-image-person-group.jpg'
#     IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)))  #  change path for directory where just-uploaded pictures will be stored 
#     # Get test image
#     test_image_array = glob.glob(os.path.join(IMAGES_FOLDER, group_photo)) #  change as per above
#     image = open(test_image_array[0], 'r+b')
#     # Detect faces
#     face_ids = []
#     faces = face_client.face.detect_with_stream(image)
#     for face in faces:
#         face_ids.append(face.face_id)
#     identify_face(image, face_ids) # PERSON_GROUP_ID