
import numpy as np
import utils
from collections import Counter
import os
from sklearn.model_selection import train_test_split

class DataGenerator:
    def __init__(self, base_dir, batch_size, prune=None, augment=2):
        self.base_dir = base_dir
        self.batch_size = batch_size
        self.augment = augment

        self.x = utils.pickle_load(os.path.join(self.base_dir, 'dataset/imgs.pkl'))
        self.y = utils.pickle_load(os.path.join(self.base_dir, 'dataset/labels.pkl'))
        self.labels = np.array([1 if np.sum(mask) > 0 else 0 for mask in self.y])

        if prune is not None:
            self.x, self.y, self.labels = utils.prune(self.x, self.y, self.labels, prune)

        self.x = utils.norm(self.x)
        self.y = utils.norm(self.y)
        self.classes = np.unique(self.labels)
        self.per_class_ids = {}
        ids = np.array(range(len(self.x)))
        for c in self.classes:
            self.per_class_ids[c] = ids[self.labels == c]

        print(Counter(self.labels))


    def get_samples_for_class(self, c, samples=None):
        if samples is None:
            samples = self.batch_size
        try:
            np.random.shuffle(self.per_class_ids[c])
            to_return = self.per_class_ids[c][0:samples]
            return self.dataset_x[to_return]
        except:
            random = np.arange(self.dataset_x.shape[0])
            np.random.shuffle(random)
            to_return = random[:samples]
            return self.dataset_x[to_return]


    def augment(self, x, y, for_seg=True):
        seed = np.random.randint(0, 100)
        new_x = utils.transform(x, seed))
        if for_seg:
            new_y = utils.transform(x, seed)
        else:
            new_y = y

        return new_x, new_y

    def augment_array(self, x, y, for_seg=True):
        imgs = []
        labels = []
        for i in range(len(x)):
            imgs.append(x[i])
            labels.append(y[i])
            for _ in range(self.augment):
                _x, _y = self.augment(x[i], y[i], for_seg)
                imgs.append(_x)
                labels.append(_y)


        return np.array(imgs), np.array(labels)


    def next_seg_batch(self):
        x = self.x
        y = self.y

        indices = np.arange(x.shape[0])
        np.random.shuffle(indices)

        for start_idx in range(0, x.shape[0] - self.batch_size + 1, self.batch_size):
            access_pattern = indices[start_idx:start_idx + self.batch_size]

            yield self.augment_array(x[access_pattern, :, :, :], y[access_pattern])

    def next_cls_batch(self):
        x = self.x
        y = self.labels

        indices = np.arange(x.shape[0])
        np.random.shuffle(indices)

        for start_idx in range(0, x.shape[0] - self.batch_size + 1, self.batch_size):
            access_pattern = indices[start_idx:start_idx + self.batch_size]

            # yield self.augment_array(x[access_pattern, :, :, :], y[access_pattern], for_seg=False)
            yield x[access_pattern, :, :, :], y[access_pattern]
