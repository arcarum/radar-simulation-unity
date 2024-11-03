import os
import json
import numpy as np
from PIL import Image, ImageDraw
import random
from torch.utils.data import Dataset
from ultralytics import YOLO

class PPIDataset(Dataset):
    def __init__(self, json_dir, save_dir, val_split=0.2):
        self.json_dir = json_dir
        self.save_dir = save_dir
        self.json_files = [file for file in os.listdir(json_dir) if file.endswith('.json')]
        self.val_split = val_split

        # Create directories for train and val under images and labels
        os.makedirs(os.path.join(save_dir, 'images', 'train'), exist_ok=True)
        os.makedirs(os.path.join(save_dir, 'images', 'val'), exist_ok=True)
        os.makedirs(os.path.join(save_dir, 'labels', 'train'), exist_ok=True)
        os.makedirs(os.path.join(save_dir, 'labels', 'val'), exist_ok=True)

        # Shuffle files and split into train and validation
        random.shuffle(self.json_files)
        split_index = int(len(self.json_files) * (1 - val_split))
        self.train_files = self.json_files[:split_index]
        self.val_files = self.json_files[split_index:]

    def __len__(self):
        return len(self.json_files)

    def __getitem__(self, idx):
        json_path = os.path.join(self.json_dir, self.json_files[idx])

        with open(json_path, 'r') as file:
            data = json.load(file)

        ppi_array = np.array(data['PPI'], dtype=np.float32)

        # Convert to PIL Image
        image = Image.fromarray(ppi_array)
        image = image.convert('L')

        ships = data['ships']
        output_size = ppi_array.shape

        yolo_bboxes = []

        # Draw bounding boxes for each ship
        for ship in ships:
            model_class, x_center, y_center, width, height = ship["Bounds"].split()
            x_center, y_center, width, height = map(float, (x_center, y_center, width, height))

            # Convert normalized coordinates to pixel values
            x_scaled = int(x_center / data['range'] * output_size[1])
            y_scaled = int(y_center / 360 * output_size[0])

            # Ensure coordinates are within bounds
            x_scaled = min(max(0, x_scaled), output_size[1] - 1)
            y_scaled = min(max(0, y_scaled), output_size[0] - 1)

            # Scale width and height to pixel values
            width_scaled = int(width / data['range'] * output_size[1])
            height_scaled = int(height / data['range'] * output_size[1])

            # Clamp width and height (Needed for very small boats)
            min_width = 20
            min_height = 20
            width_scaled = max(width_scaled, min_width)
            height_scaled = max(height_scaled, min_height)

            # Normalize bounding box values for YOLO format
            img_width, img_height = output_size[1], output_size[0]
            x_normalized = x_scaled / img_width
            y_normalized = y_scaled / img_height
            width_normalized = width_scaled / img_width
            height_normalized = height_scaled / img_height

            model_class = 0 # Class 0 is ships
            yolo_bboxes.append(f"{model_class} {x_normalized} {y_normalized} {width_normalized} {height_normalized}")

        # Determine save directory based on training/validation split
        if self.json_files[idx] in self.train_files:
            save_subdir = 'train'
        else:
            save_subdir = 'val'

        # Save the image
        image_file_name = os.path.splitext(os.path.basename(json_path))[0] + '.png'
        image.save(os.path.join(self.save_dir, 'images', save_subdir, image_file_name))

        # Save the YOLO format bounding boxes to a text file
        yolo_file_path = os.path.splitext(image_file_name)[0] + '.txt'
        with open(os.path.join(self.save_dir, 'labels', save_subdir, yolo_file_path), 'w') as yolo_file:
            for bbox in yolo_bboxes:
                yolo_file.write(bbox + '\n')

        return image

if __name__ == '__main__':
    json_directory = os.path.expanduser('~/Downloads/output')
    
    save_directory = os.path.expanduser('~/Downloads/yolo_dataset')
    os.makedirs(save_directory, exist_ok=True)

    dataset = PPIDataset(json_directory, save_directory, val_split=0.2)

    # Create the image and labels in the directories (train and val) for YOLO
    for i in range(len(dataset)):
        image = dataset[i]
        print(f"Processed image {i + 1}/{len(dataset)}")

    model = YOLO("yolo11n.pt")  # Load a pretrained model

    # Assuming yaml is in the same directory as this script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_directory, 'ppi_dataset.yaml')
    results = model.train(data=data_path, epochs=500, patience=100, imgsz=[720,1000]) 
    #model.val()
    