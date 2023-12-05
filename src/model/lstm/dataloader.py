import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader

class DataLoader():
    
    def __init__(self, data, target: str):
        self.time_series = data[::-1]
        self.length_series = len(data)
        self.target = target
        pass
    
    def _build_dataset(self, time_series, seq_length: int) -> tuple[np.ndarray, np.ndarray]:
        data_x, data_y = [], []
        for i in range(len(time_series)-seq_length):
            _x = time_series.iloc[i:i+seq_length, :]
            _y = time_series.loc[i+seq_length, [self.target]]
            data_x.append(_x)
            data_y.append(_y)
        return np.array(data_x), np.array(data_y)
    
    def make_dataset(self, train_size: float, train_batch_size: int, valid_batch_size: int, seq_length: int) -> tuple[DataLoader, torch.FloatTensor, torch.FloatTensor]:
        train_size = int(self.length_series * train_size)
        train_set = self.time_series[0:train_size]
        print(f"train_set\n{train_set.head()}")
        print(f"train_set\n{train_set.loc[100, ['Close']]}")
        test_set = self.time_series[train_size-seq_length:]
        train_x, train_y = self._build_dataset(time_series=train_set, seq_length=seq_length)
        test_x, test_y = self._build_dataset(time_series=test_set, seq_length=seq_length)
        train_dataset = TensorDataset(torch.FloatTensor(train_x), torch.FloatTensor(train_y))
        valid_dataset = TensorDataset(torch.FloatTensor(test_x), torch.FloatTensor(test_y))
        train_data_loader = DataLoader(data=train_dataset, batch_size=train_batch_size, shuffle=True, drop_last=True)
        valid_data_loader = DataLoader(data=valid_dataset, batch_size=valid_batch_size, shuffle=True, drop_last=True)
        return (train_data_loader, valid_data_loader), (train_dataset, valid_dataset)
    
if __name__ == '__main__':
    pass