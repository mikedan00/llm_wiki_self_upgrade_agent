"""
LoRA/SFT 학습용 골격 코드입니다.

주의:
- 이 스크립트는 Streamlit Cloud용이 아닙니다.
- 26B MoE급 모델 학습은 로컬 노트북 8GB VRAM에서 매우 제한적입니다.
- 실제 학습은 Colab Pro, RunPod, Lambda, Vast.ai, A100/H100급 GPU, 또는 더 작은 모델로 시작하세요.
- 원격 Hugging Face Inference Provider 모델을 직접 덮어쓰는 방식이 아닙니다.
"""

print("LoRA fine-tuning skeleton")
print("1. data/training/sft_dataset.jsonl 확인")
print("2. TRL/SFTTrainer + PEFT/LoRA 구성")
print("3. 작은 모델 또는 quantized model부터 실험")
print("4. 평가 통과 후 별도 model repo로 push")
