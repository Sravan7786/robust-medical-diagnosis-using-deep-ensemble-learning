import torch
from ensemble_model import MedicalEnsemble

def test_ensemble():
    print("Initializing ensemble model (8 classes)...")
    classes = [
        'Normal', 'Pneumonia', 'Cardiomegaly', 'Effusion', 
        'Infiltration', 'Mass', 'Nodule', 'Pneumothorax'
    ]
    model = MedicalEnsemble(num_classes=len(classes))
    
    # Create a dummy image tensor (Batch size 1, 3 Channels, 224x224)
    dummy_input = torch.randn(1, 3, 224, 224)
    
    print("Running dummy inference...")
    final_prob, individual_probs = model(dummy_input)
    
    print(f"Final probability shape: {final_prob.shape}")
    print(f"Confidence for Normal: {final_prob[0][0].item():.4f}")
    print(f"Confidence for Pneumonia: {final_prob[0][1].item():.4f}")
    
    print("Ensemble test successful!")

if __name__ == "__main__":
    test_ensemble()
