# SUS Scoring Guide

## Formula
For each participant:

1. For odd-numbered items (1,3,5,7,9):  
   adjusted score = response - 1

2. For even-numbered items (2,4,6,8,10):  
   adjusted score = 5 - response

3. Sum all 10 adjusted scores.

4. Multiply by 2.5.  
   Final SUS score is from 0 to 100.

## Example
Raw responses:  
Q1=4, Q2=2, Q3=4, Q4=2, Q5=4, Q6=2, Q7=4, Q8=2, Q9=4, Q10=2

Adjusted:  
Q1=3, Q2=3, Q3=3, Q4=3, Q5=3, Q6=3, Q7=3, Q8=3, Q9=3, Q10=3

Sum = 30  
SUS = 30 * 2.5 = 75

## Suggested Report Output
- Individual SUS per user (U1 to U5)
- Mean SUS
- Median SUS
- Min and max SUS
- 1 to 2 sentence interpretation

## Spreadsheet Formulas
If B:K contains Q1:Q10:

- Adjusted total formula:
`=(B2-1)+(5-C2)+(D2-1)+(5-E2)+(F2-1)+(5-G2)+(H2-1)+(5-I2)+(J2-1)+(5-K2)`

- SUS score formula:
`=((B2-1)+(5-C2)+(D2-1)+(5-E2)+(F2-1)+(5-G2)+(H2-1)+(5-I2)+(J2-1)+(5-K2))*2.5`
