# AI Infra | 技术简历

## 教育背景
### 工科硕士在读 | 2025.09 - 2027.06（预计）
集成电路与系统。

### 工学本科 | 2021.09 - 2025.06
电子科学与技术；计算机科学与技术辅修。获学业及竞赛创新奖学金。

## 实习经历
### 基础模型研发团队 | 大模型与高性能计算 | 2026.04 - 至今
参与 MoE 模型训练、推理与 RL rollout 基础设施开发，负责算子优化、确定性验证与稳定性排障。

### 确定性 Attention 反向优化
定位长序列滑窗反向传播的同步依赖并调整调度。代表工作负载完整 backward 加速 3.98 倍；通过 3,601 项回归及 1,000 次逐位确定性测试，完成 wheel 交付。

### 计算与通信协同
搭建多 GPU 双 stream 代理，联合调整通信并行度与计算资源预算。AllGatherV 代理联合耗时降低 12.80%；固定通信设置下，控核独立贡献 7.58%。

### 确定性 MoE Router GEMM
接入 DeepGEMM / Triton Full-K / persistent 三级后端与 Graph preflight、cache、fallback。代表工作负载 Router 耗时降低 73.39%；135/135 kernel、20/20 模型场景逐位一致。async OE + prefix-cache hit 下，TP1/TP2 整请求吞吐提升 3.81%/4.36%。

### 异步 GPU 状态管理
历史 token 状态保留在 GPU，优化计算并修复请求恢复、slot 复用等跨 step 状态。TP1 通过 28/28 case，吞吐提升 4.99%；TP2/TP4 安全路径各通过 84/84 case，0 mismatch。

### MoE 训推路由一致性
打通 rollout 路由采集、传输与训练侧回放，建立 mask 对齐及概率漂移监控。短程对照中执行路由不一致率由 17%-19% 降至 0；完成更大规模多卡 rollout 验证。

### CUDA Graph 稳定性
构建两卡最小复现，定位浮点 FTZ 对同步标记的误判；回移上游位级判断修复，完成模型级回归。

## 实习经历（续）
### 国产 GPU 企业 | 算子与编译器优化 | 2026.01 - 2026.04
参与深度学习框架后端的算子、优化器适配、图融合、性能分析与长跑稳定性修复。

### 图融合与热点算子
完成整网 GELU 融合；真实 shape 测试耗时降低 36.6%。Logical_Or 从 21.2 us 降至 10.7 us，补齐优化器实现及测试。

### 长跑稳定性
定位 shape tensor 的 host/device 路径错误，修复资源变量与 session 关闭问题。测试由 500 轮约 30% 成功率提升至 1,000 轮 100%，通过最高 80 万轮长跑。

## 项目与研究
### 量化推理 Runtime | 2025.12 - 至今
基于 PyTorch Extension 完成 W4A16 / W8A8 / FP8 后端、Attention 与 TP=2 集成。使用 Compute Sanitizer 修复尾组越界，代表 shape 四类检查均为 0 error / 0 hazard。

### 双卡量化部署
在公开 32B 模型的对照部署中，checkpoint / 峰值显存降低 70.5% / 66.8%，端到端输出吞吐提升 76.8%；通过数值及跨 rank token 一致性验收。

### 关键 Token 加权思维链蒸馏 | 已投稿
参与结构恢复、关键 token 加权监督与偏好优化框架；负责模型训练、超参调优、LoRA / DPO 及多卡评测。

## 开源与技能
### 上游贡献
22 个已合入 PR，其中 12 个社区贡献、10 个实习产出；覆盖训练、推理、分布式存储及框架后端。

### 开发与性能工程
C/C++、Python、CUDA、Triton、PyTorch Extension；Nsight Systems、Nsight Compute、Compute Sanitizer。

### 语言与证书
IELTS 6.5、CET-6、HCIA-AI。
