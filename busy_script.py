# import torch

# for i in range(torch.cuda.device_count()):
#     torch.empty(1, device=f"cuda:{i}")  # init context

# xs = [torch.randn(4096, 4096, device=f"cuda:{i}") for i in range(torch.cuda.device_count())]
# ys = [torch.randn(4096, 4096, device=f"cuda:{i}") for i in range(torch.cuda.device_count())]

# while True:
#     for i in range(torch.cuda.device_count()):
#         xs[i] @ ys[i]
#!/usr/bin/env python3
import os, time
from vllm import LLM, SamplingParams
import argparse

def run_vllm_prompts(device):
    assert isinstance(device, int) 

    # Pick exactly one GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = f"{device}"

    model = "meta-llama/Llama-3.1-8B-Instruct"  # change as needed

    llm = LLM(
        model=model,
        gpu_memory_utilization=0.90,
        # enforce_eager=True,  # optional: can reduce graph/capture variance
    )

    sp = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        max_tokens=256,   # increase to make it heavier
    )

    prompts = [
        "Summarize the key idea of speculative decoding in 4 bullet points.",
        "Write a short paragraph explaining NUMA and tail latency.",
        "Explain why decode dominates prefill for long generations.",
        "Give a 6-step checklist to debug GPU frequency scaling.",
    ] * 8  # batching; increase for more load

    i = 0
    while True:
        t0 = time.perf_counter()
        out = llm.generate(prompts, sp)
        dt = time.perf_counter() - t0
        i += 1
        # lightweight status print
        print(f"iter={i} batch={len(prompts)} max_tokens={sp.max_tokens} dt={dt:.3f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run clock frequency change experiment with cooldown."
    )
    parser.add_argument(
        "--device",
        type=int,
        required=True,
        help="NVIDIA device number"
    )

    args = parser.parse_args()

    run_vllm_prompts(args.device)