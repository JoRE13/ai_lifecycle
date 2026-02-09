"""
Review the output of the three different prompting strategies
"""
import pandas as pd

for v in ['v1','v2','v3']:
    verdict_acc = 0
    non_feas = 0
    df = pd.read_csv(f"results_{v}.csv")
    for row in df.itertuples():
        # test wether the verdict is the same as the expected (true) verdict
        if row.verdict == row.expected_verdict:
            verdict_acc += 1
        # count how many non feasible results. If fix_first the solution must be incorrect, if hint the solution must be correct_so_far, if full_solution it must be fully_solved and if ask_clarification it must be unclear
        if (row.response_type == "fix_first" and row.verdict != "incorrect") or (row.response_type == "hint" and row.verdict != "correct_so_far") or (row.response_type == "full_solution" and row.verdict != "fully_solved") or (row.response_type == "ask_clarification" and row.verdict != "unclear"):
            non_feas += 1
        
    n = len(df)
    print("Results for prompting strategy {0}".format(v))
    print("Accuracy of verdicts: {0}".format(verdict_acc/n))
    print("Ratio of non feasible results: {0}\n".format(non_feas/n))