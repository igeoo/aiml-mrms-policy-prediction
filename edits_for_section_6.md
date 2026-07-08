# Outstanding Manuscript Edits (Section 6.6.2 LP Outputs)

**Note to Author:** 
While the `AIML_MRMS_manuscript_edit.docx` successfully addresses many missed edits (such as ROC-AUC values and the Cycle 3 narrative), **it still entirely misses the Section 6.6.2 LP updates that the reviewer pointed out.** 

Because the new verified dataset substantially increases Project B's return ($r_j$), the Linear Programming (LP) optimisation now yields a **corner solution (100% allocation to Project B)**. The previously reported fractional allocations are now obsolete.

Please manually update the following paragraphs in your manuscript to reflect the accurate pipeline outputs:

---

### 1. Paragraph 142 (Section 6.6.1 / 6.6.2 transition)
* **Current text:** "...the relaxed LP (∈ [0,1]) yields $x^*$ = (0.14, 0.72, 0.14) with NG-B (FDI-compliant open-pit) absorbing the dominant share..." and "...the share allocated to NG-B rises from 0.62 at $\lambda$ = 0.05 to 0.88 at $\lambda$ = 0.25..."
* **Required Correction:** The re-computed value is a corner solution of 1.00 for NG-B. The allocation doesn't rise from 0.62 to 0.88; it is pegged at 1.00 across the entire sweep. Update the narrative to state that the LP yields a corner solution of $x^*$ = (0.0, 1.0, 0.0) where NG-B absorbs 100% of the allocation, and this remains saturated at 1.00 across the $\lambda$-sweep.

### 2. Paragraph 145 (Section 6.6.2 $\lambda$-sweep breakdown)
* **Current text:** "At $\lambda$ = 0.05 the allocation is (0.21, 0.62, 0.17); at $\lambda$ = 0.15 (the manuscript’s central value) it is (0.14, 0.72, 0.14); at $\lambda$ = 0.25 it is (0.06, 0.88, 0.06)."
* **Required Correction:** None of these vectors are correct under the verified data. NG-B's return is so dominant that the vector is (0.0, 1.0, 0.0) for *all* these $\lambda$ values. Replace this sentence entirely. State that the allocation remains strictly $x^*$ = (0.0, 1.0, 0.0) for $\lambda$ = 0.05, 0.15, and 0.25 due to NG-B's overwhelming economic return overriding the governance penalty across this range.

### 3. Paragraph 145 (PCI monotonic increase claim)
* **Current text:** "Nigeria PCI at Cycle 3 increases monotonically with $\lambda$ from 0.108 ($\lambda$ = 0.05) to 0.118 ($\lambda$ = 0.25)..."
* **Required Action:** Since the allocation vector $x^*$ is now static at (0.0, 1.0, 0.0) across this sweep rather than varying smoothly, verify if the resulting PCI calculation at Cycle 3 changes. Either recalculate these PCI values if they depend directly on the varying $x^*$, or adjust the sentence to reflect the static allocation reality.
