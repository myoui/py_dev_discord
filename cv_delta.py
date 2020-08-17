import os, sys, cv2 as cv, numpy as np, pickle


cam = cv.VideoCapture('video2.mkv')
counter = 1
last_frame = np.ndarray(0)
while cam.isOpened():
    ret, frame = cam.read()
    if not ret:
        break

    # frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    if not last_frame.any():
        last_frame = frame
    
    difference = cv.subtract(frame, last_frame)

    delta = cv.imencode('.jpg', difference)
    full = cv.imencode('.jpg', frame)
    
    print(len(pickle.dumps(delta)), len(pickle.dumps(full)))
    if counter == 1:
        cur_frame = frame
        counter = 0
    else:
        cur_frame = cv.add(last_frame, difference)
        counter += 1
    cv.imshow('image', difference)

    cv.imshow('composite', cur_frame)
    cv.waitKey(25)
    last_frame = cur_frame