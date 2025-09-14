import os
import sys
import django
import requests

# ✅ Set the correct settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pin_to_beans.settings")

# ✅ Add root directory (the one containing manage.py) to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(BASE_DIR)

# ✅ Initialize Django
django.setup()

from core.models import Image

def update_image_blobs():
    images = Image.objects.all()
    for img in images:
        try:
            print(f"Fetching image for ID {img.image_id} from {img.url}...")
            response = requests.get(img.url)
            if response.status_code == 200:
                img.stored_blob = response.content
                img.save()
                print(f"✅ Updated blob for image_id={img.image_id}")
            else:
                print(f"❌ Failed (HTTP {response.status_code}) for image_id={img.image_id}")
        except Exception as e:
            print(f"❌ Error for image_id={img.image_id}: {e}")

if __name__ == "__main__":
    update_image_blobs()
