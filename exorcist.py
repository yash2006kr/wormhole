"""
ApplyCopilot Protocol 04: Document Exorcist
In-Flight Image Surgery & Constraint Healing Engine for Strict Portal Uploads.

Bypasses the "20KB - 50KB, 3.5cm x 4.5cm, 200 DPI" rejection loop in RAM.
"""

import os
import io
import time
from PIL import Image

def _pad_jpeg_bytes(jpeg_bytes, target_bytes):
    """
    Safely injects a standard non-rendering JPEG comment marker (COM 0xFFFE)
    to elevate a file to meet strict minimum file-size requirements (e.g. min 20KB).
    """
    curr_len = len(jpeg_bytes)
    if curr_len >= target_bytes:
        return jpeg_bytes
    
    needed = target_bytes - curr_len
    # COM segment: 0xFF 0xFE, 2 bytes length, payload
    # Max length of single segment is 65535
    pad_len = max(needed - 4, 1)
    # Ensure pad doesn't overflow single marker
    pad_len = min(pad_len, 65530)
    
    com_header = b"\xFF\xFE" + (pad_len + 2).to_bytes(2, "big")
    com_body = b"\x00" * pad_len
    com_segment = com_header + com_body
    
    # Inject after SOI (0xFFD8)
    if jpeg_bytes.startswith(b"\xFF\xD8"):
        return jpeg_bytes[:2] + com_segment + jpeg_bytes[2:]
    return jpeg_bytes

def heal_image(
    input_source,
    output_path=None,
    min_kb=20,
    max_kb=48,
    target_aspect=(7, 9),  # 3.5cm x 4.5cm
    target_dpi=200
):
    start_time = time.time()
    
    # 1. Load image
    if isinstance(input_source, str):
        orig_size = os.path.getsize(input_source)
        img = Image.open(input_source)
    elif isinstance(input_source, (bytes, bytearray)):
        orig_size = len(input_source)
        img = Image.open(io.BytesIO(input_source))
    else:
        orig_size = len(input_source.getvalue())
        img = Image.open(input_source)

    if img.mode != 'RGB':
        img = img.convert('RGB')

    orig_w, orig_h = img.size
    target_w_ratio, target_h_ratio = target_aspect

    # 2. Crop to 3.5cm x 4.5cm Aspect Ratio
    curr_aspect = orig_w / orig_h
    desired_aspect = target_w_ratio / target_h_ratio

    if curr_aspect > desired_aspect:
        new_w = int(orig_h * desired_aspect)
        offset = (orig_w - new_w) // 2
        crop_box = (offset, 0, offset + new_w, orig_h)
    else:
        new_h = int(orig_w / desired_aspect)
        offset = (orig_h - new_h) // 2
        crop_box = (0, offset, orig_w, offset + new_h)

    cropped_img = img.crop(crop_box)

    # 3. High-Fidelity Dimensions (e.g. 700x900 px)
    target_w = 700
    target_h = int(target_w / desired_aspect)
    working_img = cropped_img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # 4. Search optimal JPEG quality
    best_bytes = None
    best_kb = 0
    
    # Quality binary search
    low_q, high_q = 30, 95
    for _ in range(6):
        mid_q = (low_q + high_q) // 2
        buf = io.BytesIO()
        working_img.save(
            buf,
            format="JPEG",
            quality=mid_q,
            dpi=(target_dpi, target_dpi),
            optimize=True
        )
        data = buf.getvalue()
        kb = len(data) / 1024.0

        if min_kb <= kb <= max_kb:
            best_bytes = data
            best_kb = kb
            break
        elif kb < min_kb:
            best_bytes = data
            best_kb = kb
            low_q = mid_q + 1
        else:
            high_q = mid_q - 1

    # If still below min_kb (e.g. flat synthetic image), safely pad to exactly 32KB
    if best_kb < min_kb or best_bytes is None:
        target_bytes = int(32 * 1024)
        if best_bytes is None:
            buf = io.BytesIO()
            working_img.save(buf, format="JPEG", quality=85, dpi=(target_dpi, target_dpi))
            best_bytes = buf.getvalue()
        best_bytes = _pad_jpeg_bytes(best_bytes, target_bytes)
        best_kb = len(best_bytes) / 1024.0

    # If above max_kb, resize down
    if best_kb > max_kb:
        downscaled = cropped_img.resize((420, int(420 / desired_aspect)), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        downscaled.save(buf, format="JPEG", quality=65, dpi=(target_dpi, target_dpi), optimize=True)
        best_bytes = buf.getvalue()
        best_kb = len(best_bytes) / 1024.0

    # 5. Save if path specified
    if output_path:
        with open(output_path, "wb") as f:
            f.write(best_bytes)

    duration_ms = (time.time() - start_time) * 1000

    return {
        "status": "HEALED",
        "original_size_kb": round(orig_size / 1024.0, 1),
        "healed_size_kb": round(best_kb, 1),
        "target_range_kb": f"{min_kb}KB - {max_kb}KB",
        "compliant": min_kb <= best_kb <= max_kb,
        "aspect_ratio": "3.5cm x 4.5cm (7:9)",
        "dpi": target_dpi,
        "processing_time_ms": round(duration_ms, 1),
        "output_path": output_path
    }


if __name__ == "__main__":
    print("=== TESTING PROTOCOL 04: DOCUMENT EXORCIST ===")
    
    test_file = "test_oversized_photo.jpg"
    healed_file = "test_healed_passport_photo.jpg"
    
    print("1. Generating synthetic 2000x2600 candidate portrait...")
    dummy = Image.new("RGB", (2000, 2600), color=(140, 180, 220))
    dummy.save(test_file, format="JPEG", quality=95)
    print(f"   Created '{test_file}' -> Size: {round(os.path.getsize(test_file)/1024.0, 1)} KB")
    
    print("\n2. Executing In-Flight Document Exorcist surgery...")
    res = heal_image(test_file, output_path=healed_file, min_kb=20, max_kb=48)
    
    print("\n--- SURGERY TELEMETRY REPORT ---")
    for k, v in res.items():
        print(f"  * {k}: {v}")
    
    print("\n3. Result Verification:")
    print(f"   [OK] Input File:  {test_file} ({res['original_size_kb']} KB)")
    print(f"   [OK] Output File: {healed_file} ({res['healed_size_kb']} KB) -> Compliant: {res['compliant']}")
