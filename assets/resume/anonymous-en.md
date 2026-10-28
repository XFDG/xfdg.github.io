# AI Infrastructure | Resume

## Education
### M.Sc. candidate | Sep 2025 - Jun 2027 (expected)
Integrated Circuits and Systems.

### B.Eng. | Sep 2021 - Jun 2025
Electronic Science and Technology; minor in Computer Science. Academic and competition/innovation scholarships.

## Experience
### Foundation-model team | LLM and HPC intern | Apr 2026 - Present
Training, inference and RL rollout infrastructure for MoE models: kernel optimization, determinism validation and stability debugging.

### Deterministic attention backward
Diagnosed synchronization dependencies in long-context sliding-window backward and revised scheduling. Representative full-backward speedup: 3.98x; 3,601 regressions and 1,000 repeated bitwise checks; delivered a wheel.

### Compute-communication coordination
Built a multi-GPU dual-stream proxy and co-tuned communication and compute budgets. AllGatherV proxy joint latency fell 12.80%; isolated compute-budget gain at fixed communication settings: 7.58%.

### Deterministic MoE router GEMM
Integrated DeepGEMM / Triton Full-K / persistent backends, Graph preflight and fallback. Router latency fell 73.39% on the tested workload; 135/135 kernel and 20/20 model cases matched bitwise. Full-request throughput with async OE and prefix-cache hits: TP1 +3.81%, TP2 +4.36%.

### Asynchronous GPU state
Kept token history on the GPU and fixed cross-step recovery and slot reuse. TP1: 28/28 cases, +4.99% throughput. TP2/TP4 safe paths: 84/84 each, zero mismatches.

### Training-rollout consistency
Connected route capture, transport and replay, response masks and drift metrics. Executed-route mismatch fell from 17%-19% to zero in a short controlled run; completed larger multi-GPU rollout validation.

### CUDA Graph stability
Isolated FTZ-sensitive synchronization sentinel handling with a two-GPU reproducer; backported an upstream bitwise fix and completed model-level regression.

## Experience (continued)
### GPU company | Operator/compiler optimization intern | Jan - Apr 2026
Deep-learning framework backend: operators, optimizers, graph fusion, profiling and long-run stability.

### Fusion and hot operators
Completed GELU fusion across the tested graph; workload-shaped latency fell 36.6%. Logical_Or improved from 21.2 us to 10.7 us; added optimizer implementations and tests.

### Long-run reliability
Fixed host/device shape-tensor semantics, resource-variable updates and session shutdown. Success improved from about 30% over 500 iterations to 100% over 1,000; validated runs up to 800,000 iterations.

## Projects and research
### Quantized inference runtime | Dec 2025 - Present
Integrated W4A16 / W8A8 / FP8 backends, attention and TP=2 through PyTorch Extension. Fixed tail-group memory errors; four Compute Sanitizer checks showed zero errors/hazards on representative shapes.

### Two-GPU quantized deployment
In a paired deployment of a public 32B model, checkpoint / peak memory fell 70.5% / 66.8% and output throughput rose 76.8%; numerical and cross-rank token checks passed.

### Token-weighted CoT distillation | Submitted
Contributed to structure recovery, token-weighted supervision and preference optimization. Owned training, hyperparameter tuning, LoRA / DPO and multi-GPU evaluation.

## Open source and skills
### Upstream contributions
22 merged PRs: 12 community contributions and 10 internship outputs, spanning training, inference, distributed storage and framework backends.

### Engineering
C/C++, Python, CUDA, Triton, PyTorch Extension; Nsight Systems, Nsight Compute and Compute Sanitizer.

### Language and certification
IELTS 6.5; CET-6; HCIA-AI.
