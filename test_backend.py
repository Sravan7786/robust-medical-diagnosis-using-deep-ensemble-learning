import io
from ensemble_model import predict_image
from PIL import Image
import numpy as np

def test_single_prediction():
    print("Creating a dummy X-ray image...")
    # Create a dummy grayscale image (simulating an X-ray)
    img = Image.fromarray(np.random.randint(0, 255, (224, 224), dtype=np.uint8))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    print("Testing predict_image function...")
    try:
        result = predict_image(img_byte_arr)
        print("Success! Result:")
        print(f"Modality: {result.get('modality')}")
        print(f"Condition: {result.get('condition')}")
        print(f"Confidence: {result.get('confidence')}")
        print(f"Report: {result.get('report')}")
        print(f"Ensemble Breakdown: {len(result.get('ensemble_breakdown', []))} models reported.")
    except Exception as e:
        print(f"FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_prediction()
