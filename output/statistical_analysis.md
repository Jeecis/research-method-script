# Statistical Analysis Report

## 1. Chi-Square Test: Fact Depth vs Accuracy

Tests whether accuracy is independent of depth position.

- χ² = 26.8416
- Degrees of freedom = 10
- p-value = 0.002759
- **Significant** at α=0.05
- Interpretation: Depth position does significantly affect accuracy

## 2. Chi-Square Test: Context Length vs Accuracy

Tests whether accuracy is independent of context length category.

- χ² = 35.5745
- Degrees of freedom = 5
- p-value = 0.000001
- **Significant** at α=0.05
- Interpretation: Context length does significantly affect accuracy

## 3. Spearman Rank Correlation: Depth vs Accuracy

Tests the monotonic relationship between depth position and accuracy.

- Spearman's ρ = -0.1794
- p-value = 0.001064
- **Significant** at α=0.05
- Interpretation: Negative correlation — deeper positions tend to have lower accuracy

## 4. Spearman Rank Correlation: Context Length (words) vs Accuracy

- Spearman's ρ = -0.3407
- p-value = 0.000000
- **Significant** at α=0.05
- Interpretation: Negative correlation — longer contexts tend to have lower accuracy

## 5. Fisher's Exact Test: Edge Positions vs Middle Positions

Compares accuracy at edge positions (0%, 10%, 100%) vs middle positions (40%, 50%, 60%).

- Edge accuracy: 89/90 (99%)
- Middle accuracy: 78/90 (87%)
- Odds ratio = 13.6923
- p-value = 0.002451
- **Significant** at α=0.05
- Interpretation: Edge positions significantly outperform middle positions

## 6. Descriptive Summary

- Total observations: 330
- Overall accuracy: 301/330 (91.2%)
- Best depth: 0% and 10% (100%)
- Worst depth: 50% (80%)
- Best category: 0 - 32k (100%)
- Worst category: 160k - 192k (76%)
