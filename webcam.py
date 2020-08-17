from cv2 import VideoCapture, imshow as show, waitKey as wait, destroyAllWindows


cam = VideoCapture(0)

while cam.isOpened():
    ret, frame = cam.read()

    if not ret:
        print('Stopped')
        break      

    show('sending', frame)
    wait(50)

cam.release()
destroyAllWindows()