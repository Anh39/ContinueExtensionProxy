DEBUG = True
if DEBUG:
    from transformers import Qwen2TokenizerFast, AutoTokenizer
    import threading
    import os
    os.makedirs("log", exist_ok=True)
    TOKENIZER: Qwen2TokenizerFast = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-0.5B", use_fast=True)
    previous_prompt = ""
    def compare_simmilar(prompt_1: str, prompt_2: str):
        ids_1 = TOKENIZER.encode(prompt_1)
        ids_2 = TOKENIZER.encode(prompt_2)
        same = sum(1 for x, y in zip(ids_1, ids_2) if x == y)
        print(f"Simmilar: {same}, Old diff: {len(ids_1)-same}, New diff: {len(ids_2)-same}")
    def compare_simmilar_async(prompt_1: str, prompt_2: str):
        threading.Thread(
            target=compare_simmilar,
            args=(prompt_1, prompt_2),
            daemon=True
        ).start()
    def compare_diff(prompt: str):
        global previous_prompt
        compare_simmilar_async(previous_prompt, prompt)
        previous_prompt = prompt