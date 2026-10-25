"""Time how fast this laptop runs a pre-trained image network on CPU."""
import time
import torch
import torchvision

print("torch", torch.__version__, "| threads:", torch.get_num_threads())
model = torchvision.models.resnet18(weights="DEFAULT").eval()
batch = torch.rand(16, 3, 224, 224)  # 16 fake images

with torch.no_grad():
    model(batch)  # warm-up
    start = time.time()
    for _ in range(5):
        model(batch)
    elapsed = time.time() - start

per_image_ms = elapsed / (5 * 16) * 1000
print(f"Time per image: {per_image_ms:.1f} ms")
print(f"Images per second: {1000 / per_image_ms:.1f}")
