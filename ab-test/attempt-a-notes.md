# Attempt A: Notes (No Diagram)

## Uncertainties While Implementing

1. **Proportions were fuzzy**: Spec said 65%/35% and 70%/30%, but Tailwind doesn't have those fractions. I defaulted to 2/3 and 1/3 (66%/33%) because I couldn't visualize if the difference mattered.

2. **Metric card internal layout**: "Icon left, label above value, trend below" — I *think* I got this right, but I'd need to render it to verify. The vertical alignment of icon vs text block is particularly uncertain.

3. **Skipped responsive entirely**: Too much mental simulation required. What does "sidebar collapses to icons only" look like proportionally? What breakpoints? I punted.

4. **Sidebar height**: Is it supposed to stretch full height? Have its own scroll? Unclear.

5. **Spacing consistency**: I picked `gap-4`, `mb-6`, `p-4` somewhat arbitrarily. No way to verify visual rhythm without rendering.

## What I'd Want to Verify

- Does the chart actually take 65% width or did I approximate wrong?
- Is the metric card icon vertically centered relative to the label+value+trend block?
- Does the activity feed align nicely with the chart header?
- On mobile, does the stacked layout look intentional or broken?
