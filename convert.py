import torch
import io
import pickle

class CPU_Unpickler(pickle.Unpickler):
    def persistent_load(self, pid):
        return pid.decode('ascii')

    def find_class(self, module, name):
        if module == 'torch.storage' and name == '_load_from_bytes':
            return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
        else:
            return super().find_class(module, name)

def load_model(path):
    with open(path, 'rb') as f:
        return CPU_Unpickler(f).load()

try:
    model = load_model('best.pt')
    torch.save(model, 'best_windows.pt', _use_new_zipfile_serialization=False)
    print("모델이 성공적으로 변환되었습니다.")
except Exception as e:
    print(f"오류 발생: {e}")