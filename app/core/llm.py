from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "TheBloke/Vicuna-13B-1.1-GPTQ-4bit-128g"

print("Loading Vicuna 13B GPTQ model...")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    trust_remote_code=True,
)
model.eval()
print("Vicuna 13B GPTQ loaded successfully.")

def generate_llm_response(prompt: str, max_tokens: int = 800, temperature: float = 0.7) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=temperature,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)