from PIL import Image
import imagehash
import os
from global_functions.send_to_db import send_frames_to_db
from models.content_frame_model import ContentFrameIndex


def remove_duplicate_similar_frames(folder_path: str):
    """
    Delete the duplicate frames in the folder provided

    Keyword arguments:
    folder_path : Path of the folder contains frames
    """

    # Files list of the folder provided. It is sorted by frame number
    folder = sorted(os.listdir(folder_path),
                    key=lambda x: int(x.split("_")[3]))

    # Master frame that referance for comparison of two frames
    master_frame_number = 0

    # Similar locations dictionary that stores similar location of each master frames
    similar_locations = {}

    # all_frames list that stores all frames
    all_frames = []

    for frame_number in range(1, len(folder)):
        # Open the frame file by its location in the list
        current_frame = Image.open(os.path.join(
            folder_path, folder[frame_number]))

        # Open the master frame file. Initially first frame of the list.
        master_frame = Image.open(os.path.join(
            folder_path, folder[master_frame_number]))

        # Calculate treshold value using average_hash difference
        treshold = imagehash.average_hash(
            current_frame)-imagehash.average_hash(master_frame)

        if treshold < 20:

            # If there is no key with that name
            if not (f"{folder[master_frame_number]}" in similar_locations):

                # Create that key
                similar_locations[f"{folder[master_frame_number]}"] = ""

                # Append the frame as similar
                similar_locations[f"{folder[master_frame_number]}"] += (
                    f"{folder[frame_number]}")

            else:
                # If the key exists, append directly
                similar_locations[f"{folder[master_frame_number]}"] += (
                    f"|{folder[frame_number]}")

            print(
                f"Treshold value is {treshold}. {folder[frame_number]} deleted.")

            # Create new ContentFrameIndex object
            new_frame = ContentFrameIndex(
                folder[master_frame_number].split("_")[1],
                folder[frame_number],
                folder_path,
                folder[frame_number].split("_")[5].split(".")[0],
                ""
            )

            # Append to the list of frames
            all_frames.append(new_frame)

            # Remove the frame
            os.remove(os.path.join(folder_path, folder[frame_number]))
        else:
            # If there is no key with that name
            if not (f"{folder[master_frame_number]}" in similar_locations):
                # Create that key
                similar_locations[f"{folder[master_frame_number]}"] = ""

            # Create new ContentFrameIndex object
            new_frame = ContentFrameIndex(
                folder[master_frame_number].split("_")[1].split(".")[0],
                folder[master_frame_number],
                folder_path,
                folder[master_frame_number].split("_")[5].split(".")[0],
                similar_locations[folder[master_frame_number]]
            )

            # Append to the list of frames
            all_frames.append(new_frame)

            # If treshold value is greater than 20, then set the current frame as master frame
            master_frame_number = frame_number

            print(
                f"Treshold value is {treshold}. {folder[frame_number]} is the new master frame.")

        # If the lenght of the frames list reachs 1500, send it to database with the corresponding function
        if len(all_frames) % 1500 == 0:
            send_frames_to_db(all_frames)

            # Clear the list for the memory efficiency
            all_frames.clear()

    # Finally, if the lenght of the frames list never reachs to 1500, add them to db with the corresponding function
    if len(all_frames) != 0 and len(all_frames) < 1500:
        send_frames_to_db(all_frames)

        # Clear the list for the memory efficiency
        all_frames.clear()
