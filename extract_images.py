import pptx
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from lxml import etree
import copy

# Read the uploaded reference PPT
ref_path = r'C:\Users\Yashwanth KR\.gemini\antigravity\brain\58c06b0e-74fa-452a-a6a9-130c71f087d4\.user_uploaded\media_1792857960745_b53dd461.pptx'
prs = Presentation(ref_path)

# The template uses background images stored in slide relationships
# Let's extract all images from slides 1-8
print("=== Slide Relationships ===")
for idx, slide in enumerate(prs.slides):
    rels = slide.part.rels
    print(f"\nSlide {idx+1} relationships:")
    for rId, rel in rels.items():
        print(f"  {rId}: target_ref={rel.target_ref}, reltype={rel.reltype.split('/')[-1]}")
        if 'image' in rel.reltype.lower():
            try:
                img_part = rel.target_part
                ext = img_part.content_type.split('/')[-1].replace('jpeg','jpg')
                img_path = f'slide_{idx+1}_bg.{ext}'
                with open(img_path, 'wb') as f:
                    f.write(img_part.blob)
                print(f"    -> Saved to {img_path} ({len(img_part.blob)} bytes)")
            except Exception as e:
                print(f"    -> Error: {e}")
