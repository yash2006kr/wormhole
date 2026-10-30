import pptx
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from lxml import etree
import copy
import os

# Read the uploaded reference PPT
ref_path = r'C:\Users\Yashwanth KR\.gemini\antigravity\brain\58c06b0e-74fa-452a-a6a9-130c71f087d4\.user_uploaded\media_1792857960745_b53dd461.pptx'
prs = Presentation(ref_path)

# Dump the XML of each slide to understand the background/theme
for idx, slide in enumerate(prs.slides):
    xml_str = etree.tostring(slide._element, pretty_print=True).decode('utf-8')
    with open(f'slide_{idx+1}_xml.txt', 'w', encoding='utf-8') as f:
        f.write(xml_str)
    print(f"Dumped slide {idx+1} XML ({len(xml_str)} chars)")
    
# Also dump slide layout and master for style reference
for idx, layout in enumerate(prs.slide_layouts):
    xml_str = etree.tostring(layout._element, pretty_print=True).decode('utf-8')
    with open(f'layout_{idx+1}_xml.txt', 'w', encoding='utf-8') as f:
        f.write(xml_str)
print(f"Dumped {len(prs.slide_layouts)} layouts")
print("Done")
