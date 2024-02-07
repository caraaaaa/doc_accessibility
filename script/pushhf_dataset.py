from datasets import Dataset, DatasetDict, Image
import os
import json

img_dir = '/Users/cara.t/Desktop/assebility/image_of_text/image/train'
image_paths_train = [os.path.join(img_dir, filename) for filename in os.listdir(img_dir)]
label_dir = '/Users/cara.t/Desktop/assebility/image_of_text/annotation/train'
label_paths_train = [os.path.join(label_dir, filename) for filename in os.listdir(label_dir)]

img_dir = '/Users/cara.t/Desktop/assebility/image_of_text/image/valid'
image_paths_validation = [os.path.join(img_dir, filename) for filename in os.listdir(img_dir)]
label_dir = '/Users/cara.t/Desktop/assebility/image_of_text/annotation/valid'
label_paths_validation = [os.path.join(label_dir, filename) for filename in os.listdir(label_dir)]

def create_dataset(image_paths, label_paths):
    dataset = Dataset.from_dict({"image": sorted(image_paths),
                                "label": sorted(label_paths)})
    dataset = dataset.cast_column("image", Image())
    dataset = dataset.cast_column("label", Image())

    return dataset

# step 1: create Dataset objects
train_dataset = create_dataset(image_paths_train, label_paths_train)
validation_dataset = create_dataset(image_paths_validation, label_paths_validation)

# step 2: create DatasetDict
dataset = DatasetDict({
     "train": train_dataset,
     "validation": validation_dataset,
     }
)

# step 3: push to Hub (assumes you have ran the huggingface-cli login command in a terminal/notebook)
dataset.push_to_hub("Caraaaaa/synthetic_image_text_2")

# optionally, you can push to a private repo on the Hub
# dataset.push_to_hub("name of repo on the hub", private=True)

id2label = {0: 'text'}
with open('id2label.json', 'w') as fp:
    json.dump(id2label, fp)