from uuid import uuid4
from pathlib import Path
import pickle
from collections import defaultdict, Counter
import cv2
import face_recognition

IMAGE_PATH = Path(__file__).parent.parent / 'images'
ENCODED_PATH = Path(__file__).parent.parent / 'data' / 'encoding.pkl'
DEFAULT_USER_NAME = "DEFAULT"
THRESHOLD = 30

"""
dla nieznanych osob wykrywa jako ja
prawdopodobnie bledy wynikaja zza ciemnych obrazow
"""


def _get_face():
    frame = new_face()
    # frame = cv2.imread(str(Path(__file__).parent.parent / 'images_test' / 'tom cruise test.jpg'))
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    return face_encodings, frame


def new_face(threshold: int = THRESHOLD):
    cam = cv2.VideoCapture(0)

    ret, frame = cam.read()
    count = 0
    # mozliwe ze wszystkie problemy wynikaly z thresholdu
    while count > threshold:
        ret, frame = cam.read()
        count += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    return frame


def _recognize(face_encoding, loaded_item):
    matches = face_recognition.compare_faces(loaded_item["encodings"], face_encoding)
    votes = Counter(name for match, name in zip(matches, loaded_item["names"]) if matches)
    if votes:
        # tu cos nie dziala
        return votes.most_common(1)[0][0]
    else:
        return "NOT DETECTED"


def validate_face():
    face_encodings, image = _get_face()
    # moze trzeba dodac twarz
    if not face_encodings:
        return None

    with ENCODED_PATH.open('rb') as f:
        loaded = pickle.load(f)
    result = _recognize(face_encodings[0], loaded)
    return result, image


def encode_known():
    # musi sie odpalac co jakis czas i przy wylaczaniu
    images = IMAGE_PATH.rglob("*.jpg")
    data = defaultdict(list)
    for i in images:
        data['names'].append(i.with_suffix('').name)
        image = face_recognition.load_image_file(i)
        data['encodings'].append(face_recognition.face_encodings(image, face_recognition.face_locations(image)))
    with ENCODED_PATH.open('wb') as f:
        pickle.dump(data, f)


def recognize_gui(main_window):
    # maybe will return name of the user
    # DEFAULT if no face is detected
    validation_result = validate_face()
    if validation_result is None or validation_result[0] is None:
        index = main_window.db.get_user_id(DEFAULT_USER_NAME)
        main_window.current_index = index
        main_window.load_at_startup()
        return 'DEFAULT'

    result, frame = validation_result
    # teraz mozliwe ze tutaj sie robi blad bo obraz jest juz jasny
    print(result)
    if result != "NOT DETECTED":
        # blad tutaj
        # cos tu nie dziala z wykrywaniem twarzy
        index = main_window.db.get_user_id(result)
        # mozliwe ze na tym etapie zle dziala ustalanie uzytkownika
        if index is not None:
            main_window.current_index = index
        else:
            name = str(uuid4())
            index = main_window.db.add_user(name)
            main_window.index = index
            cv2.imwrite(str((IMAGE_PATH / name).with_suffix('.jpg')), frame)
        main_window.load_at_startup()
    # prawdopodobnie useless nie dziala jak powinno
    # blad na innym etapie
    # ta czesc z tworzeniem nowego konta gdy nie wykryto przechodzi do login dialog
    else:
        name = str(uuid4())
        index = main_window.db.add_user(name)
        main_window.index = index
        cv2.imwrite(str((IMAGE_PATH / name).with_suffix('.jpg')), frame)
    main_window.load_at_startup()
    return result


if __name__ == '__main__':
    cv2.imshow("", new_face(300))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # encode_known()
    # encoding, _ = _get_face()
    # print(validate_face())
    # new_face()
