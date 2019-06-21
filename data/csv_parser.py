import pandas as pd
import os


class Master:

    def __init__(self, path):
        self.path = path
        self.load_csv()
        self.cnt = 0

    def load_csv(self):
        assert os.path.exists(self.path)
        self.csv = pd.read_csv(self.path)
        self.total_items = len(self.csv)
        heights = self.csv['H'][self.csv['H'].str.strip().str.len() >
                                1].astype(float)
        self.max_height = heights.max()
        self.min_height = heights.min()
        self.median_height = heights.median()

    def get_item(self):
        sku, height, item = self.csv['Sku'], self.csv[
            'H'][self.cnt], self.csv['s3 link'][self.cnt]
        if "tif" in item:
            item = item.replace("[", "").replace("'", "").replace("]", "")

        height = height.strip()
        try:
            height = float(height)
            self.prev_height = height
        except Exception as e:
            print (
                e, "Exception, Height of Chair not found Using height of previous chair", self.prev_height)
            height = self.prev_height
        self.cnt += 1

        yield sku, height, item
