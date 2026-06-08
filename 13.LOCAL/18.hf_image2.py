# pip install -U diffusers transformers accelerate sentencepiece torch safetensors

from diffusers import FluxPipeline
import torch
import time

MODEL_ID = "black-forest-labs/FLUX.1-schnell"

print("Loading model...")
pipe = FluxPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32
)

pipe = pipe.to("cpu")

prompt = """
ultra realistic photo of a korean girl,
cinematic lighting,
highly detailed,
8k,
professional photography
"""

start = time.time()

image = pipe(
    prompt,
    guidance_scale=0.0,
    num_inference_steps=4,
    height=768,
    width=768,
).images[0]

image.save("flux_output.png")

print(f"done : {time.time()-start:.1f} sec")
