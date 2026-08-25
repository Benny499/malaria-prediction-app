import torch
import pandas
import sklearn
import transformers

print("Torch:", torch.__version__)
print("Pandas:", pandas.__version__)
print("Sklearn:", sklearn.__version__)
print("Transformers:", transformers.__version__)
print("CUDA available:", torch.cuda.is_available())