import sys
from pathlib import Path
import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.experimental_voice.bengali_script.tts import ExperimentalManipuriTTS

print("=" * 70)
print("MANIPURI TTS CPU OPTIMIZATION INSPECTION")
print("=" * 70)

print(f"PyTorch version: {torch.__version__}")
print(f"CPU threads: {torch.get_num_threads()}")
print(f"CUDA available: {torch.cuda.is_available()}")

print("\nLoading existing TTS model...")
tts = ExperimentalManipuriTTS()

print("\nModel object:")
print(type(tts.model))

linear_layers = 0
embedding_layers = 0
conv_layers = 0
attention_layers = 0
total_parameters = 0
trainable_parameters = 0

for name, module in tts.model.named_modules():
    if isinstance(module, nn.Linear):
        linear_layers += 1
    elif isinstance(module, nn.Embedding):
        embedding_layers += 1
    elif isinstance(module, (nn.Conv1d, nn.Conv2d, nn.ConvTranspose1d, nn.ConvTranspose2d)):
        conv_layers += 1
    elif "attention" in module.__class__.__name__.lower():
        attention_layers += 1

for parameter in tts.model.parameters():
    count = parameter.numel()
    total_parameters += count
    if parameter.requires_grad:
        trainable_parameters += count

print("\n========== MODEL STRUCTURE ==========")
print(f"Total parameters:       {total_parameters:,}")
print(f"Trainable parameters:   {trainable_parameters:,}")
print(f"Linear layers:          {linear_layers}")
print(f"Embedding layers:       {embedding_layers}")
print(f"Convolution layers:     {conv_layers}")
print(f"Attention-related:      {attention_layers}")

print("\n========== MODEL COMPONENTS ==========")

for attribute in [
    "model",
    "text_encoder",
    "audio_encoder",
    "decoder",
    "processor"
]:
    if hasattr(tts, attribute):
        value = getattr(tts, attribute)
        if value is not None:
            print(f"{attribute}: {type(value)}")

print("\n========== MEMORY ==========")

parameter_bytes = sum(
    p.numel() * p.element_size()
    for p in tts.model.parameters()
)

buffer_bytes = sum(
    b.numel() * b.element_size()
    for b in tts.model.buffers()
)

print(f"Parameter memory: {parameter_bytes / (1024 ** 3):.2f} GB")
print(f"Buffer memory:    {buffer_bytes / (1024 ** 3):.2f} GB")
print(f"Total model data: {(parameter_bytes + buffer_bytes) / (1024 ** 3):.2f} GB")

print("\n========== NEXT OPTIMIZATION ==========")

if linear_layers > 0:
    print("Dynamic INT8 quantization may be worth testing.")
else:
    print("Dynamic INT8 quantization is unlikely to be useful for this model.")

print("\nInspection complete.")
print("No production files were modified.")