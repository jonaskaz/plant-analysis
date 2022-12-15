import os
import cv2


def generate_video():
    image_folder = "./top/plants"  # make sure to use your folder
    video_name = "top_plants.avi"

    images = [
        img
        for img in os.listdir(image_folder)
        if img.endswith(".jpg") or img.endswith(".jpeg") or img.endswith("png")
    ]

    frame = cv2.imread(os.path.join(image_folder, images[0]))

    # setting the frame width, height width
    # the width, height of first image
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 1, (width, height))

    # Appending the images to the video one by one
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    # Deallocating memories taken for window creation
    cv2.destroyAllWindows()
    video.release()  # releasing the video generated


if __name__ == "__main__":
    generate_video()
