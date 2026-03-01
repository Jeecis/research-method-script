# Lost in the Middle — Results Analysis

**Total results:** 330 | **Models:** 1 | **Context files:** 30

## 1. Accuracy by Model × Depth

| Model | Size | Type | 0% | 10% | 20% | 30% | 40% | 50% | 60% | 70% | 80% | 90% | 100% | Overall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen/qwen3-vl-8b-instruct | 8B | Instruct | 100% (30/30) | 100% (30/30) | 100% (30/30) | 97% (29/30) | 97% (29/30) | 80% (24/30) | 83% (25/30) | 83% (25/30) | 87% (26/30) | 80% (24/30) | 97% (29/30) | 91% |

## 2. Accuracy by Model Size × Depth

| Size | 0% | 10% | 20% | 30% | 40% | 50% | 60% | 70% | 80% | 90% | 100% | Overall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8B | 100% (30/30) | 100% (30/30) | 100% (30/30) | 97% (29/30) | 97% (29/30) | 80% (24/30) | 83% (25/30) | 83% (25/30) | 87% (26/30) | 80% (24/30) | 97% (29/30) | 91% |
| 30B | — | — | — | — | — | — | — | — | — | — | — | — |
| 235B | — | — | — | — | — | — | — | — | — | — | — | — |

## 3. Accuracy by Architecture × Depth

| Architecture | 0% | 10% | 20% | 30% | 40% | 50% | 60% | 70% | 80% | 90% | 100% | Overall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Instruct | 100% (30/30) | 100% (30/30) | 100% (30/30) | 97% (29/30) | 97% (29/30) | 80% (24/30) | 83% (25/30) | 83% (25/30) | 87% (26/30) | 80% (24/30) | 97% (29/30) | 91% |
| Thinking | — | — | — | — | — | — | — | — | — | — | — | — |

## 4. Accuracy by Context Length Category × Depth

| Category | 0% | 10% | 20% | 30% | 40% | 50% | 60% | 70% | 80% | 90% | 100% | Overall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 - 32k | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% |
| 32k - 64k | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% |
| 64k - 96k | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% |
| 96k - 128k | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 80% (4/5) | 80% (4/5) | 80% (4/5) | 60% (3/5) | 60% (3/5) | 80% (4/5) | 85% |
| 128k - 160k | 100% (5/5) | 100% (5/5) | 100% (5/5) | 80% (4/5) | 80% (4/5) | 80% (4/5) | 60% (3/5) | 80% (4/5) | 100% (5/5) | 60% (3/5) | 100% (5/5) | 85% |
| 160k - 192k | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 100% (5/5) | 20% (1/5) | 60% (3/5) | 40% (2/5) | 60% (3/5) | 60% (3/5) | 100% (5/5) | 76% |

## Hypothesis Evaluation

- ✅ **H1** (50% depth = worst accuracy): Supported. 0%=100%, 10%=100%, 20%=100%, 30%=97%, 40%=97%, 50%=80%, 60%=83%, 70%=83%, 80%=87%, 90%=80%, 100%=97%
- ❌ **H2** (Larger = better): Not supported. 8B=91%, 30B=0%, 235B=0%
- ❌ **H3** (Thinking > Instruct): Not supported. Instruct=91%, Thinking=0%
- ✅ **H4** (Longer context = lower accuracy): Supported. 0 - 32k=100%, 32k - 64k=100%, 64k - 96k=100%, 96k - 128k=85%, 128k - 160k=85%, 160k - 192k=76%, 192k - 224k=0%

## Failed Responses (Accuracy = 0)

| Context File | Failed On |
|---|---|
| 128k-160k_1939.txt | qwen/qwen3-vl-8b-instruct (90%) |
| 128k-160k_55510.txt | qwen/qwen3-vl-8b-instruct (70%) |
| 128k-160k_6412.txt | qwen/qwen3-vl-8b-instruct (30%), qwen/qwen3-vl-8b-instruct (90%), qwen/qwen3-vl-8b-instruct (50%), qwen/qwen3-vl-8b-instruct (40%), qwen/qwen3-vl-8b-instruct (60%) |
| 128k-160k_6933.txt | qwen/qwen3-vl-8b-instruct (60%) |
| 160k-192k_25700.txt | qwen/qwen3-vl-8b-instruct (80%) |
| 160k-192k_49468.txt | qwen/qwen3-vl-8b-instruct (70%), qwen/qwen3-vl-8b-instruct (50%) |
| 160k-192k_49987.txt | qwen/qwen3-vl-8b-instruct (50%), qwen/qwen3-vl-8b-instruct (70%), qwen/qwen3-vl-8b-instruct (60%) |
| 160k-192k_55824.txt | qwen/qwen3-vl-8b-instruct (50%), qwen/qwen3-vl-8b-instruct (90%) |
| 160k-192k_6941.txt | qwen/qwen3-vl-8b-instruct (60%), qwen/qwen3-vl-8b-instruct (50%), qwen/qwen3-vl-8b-instruct (90%), qwen/qwen3-vl-8b-instruct (70%), qwen/qwen3-vl-8b-instruct (80%) |
| 96k-128k_42081.txt | qwen/qwen3-vl-8b-instruct (80%), qwen/qwen3-vl-8b-instruct (60%), qwen/qwen3-vl-8b-instruct (70%), qwen/qwen3-vl-8b-instruct (90%), qwen/qwen3-vl-8b-instruct (50%), qwen/qwen3-vl-8b-instruct (100%) |
| 96k-128k_55339.txt | qwen/qwen3-vl-8b-instruct (80%), qwen/qwen3-vl-8b-instruct (90%) |
