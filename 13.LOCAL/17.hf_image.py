# pip install Pillow
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(
    model="black-forest-labs/FLUX.1-dev",
    token=os.getenv('HUGGINGFACEHUB_API_TOKEN')
)

def generate_image(prompt, output_path="output.png"):
    image_bytes = client.text_to_image(
        prompt=prompt,
        guidance_scale=7.5,
        negative_prompt="low quality, blurry"
    )

    if isinstance(image_bytes, Image.Image):
        image = image_bytes
    else:
        image = Image.open(BytesIO(image_bytes))
    image.save(output_path)
    print("이미지가 저장되었습니다:", output_path)

# generate_image("A robot reading a book under a cherry blossom tree")
generate_image("A dolphine reading a book under a cherry blossom tree")
