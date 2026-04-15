#import "@preview/typslides:1.3.2": *

#show: typslides.with(
  ratio: "16-9",
  theme: rgb("#6C3F22"),
  back-color: rgb("#e8d8c2"),
  font: "Fira Sans",
  font-size: 20pt,
  link-style: "color",
  show-progress: true,
)

#let frame(stroke) = (x, y) => (
  left: if x > 0 { 0pt } else { stroke },
  right: stroke,
  top: if y < 2 { stroke } else { 0pt },
  bottom: stroke,
)

#set table(
  fill: (_, y) => (
    rgb(244, 235, 221),   // same as your boxes
    rgb(236, 225, 205),   // slightly darker stripe
    rgb(228, 215, 190)    // even slightly darker
  ).at(calc.rem(y, 3)),
  stroke: 1pt + black,
)


#front-slide(
  title: [],
  subtitle: [],
  authors: [],
  info: [
    #align(center + horizon)[
      #v(0.2cm)
      #text(weight: "bold", size: 30pt)[Ratatoskur]
      #v(-1.2cm)
      #image("logo.svg", width: 5cm)
      #v(-0.5cm)
      #text(size: 20pt)[Persónulegi kennarinn þinn]

      #v(0.8cm)
      //#line(length: 10cm)

      #v(0.6cm)
      #text(size: 16pt)[
        Jóhannes Reykdal Einarsson, Sævar Breki Snorrason, Sölvi Santos
      ]

      #v(0.3cm)
      #text(size: 16pt)[Final assignment: REI603M]
      #v(-0.1cm)
      #line(length: 26cm, stroke: 2pt + rgb("#6C3F22"))
      #v(-1cm)
    ]
  ],
)

#slide(title: "Problem & Users", outlined: true)[
  #columns(2)[
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
    )[
      *Problem*\
      - Students solving mathematics problems make errors or get stuck
      - Current LLM solutions are rigid and break chain of reasoning
        - Generative AI Without Guardrails Can Harm Learning (Bastani et al., 2024, PNAS)
     
      
      
    ]

    #colbreak()

    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
    )[
      *Users*\
      - High school and early undergradute students learning mathematics
    ]
    #columns(4)[
      #image("avatar_loki.png")
      #colbreak()
      #image("avatar_freya.png")
      #colbreak()
      #image("avatar_garmur.png")
      #colbreak()
      #image("avatar_idun.png")
    ]
    
  ]
]

#slide(title: "Solution", outlined: true)[
  #columns(2)[
    *An LLM powered Notebook for iPad where students*
    - can work on mathematical problems
    - can get Socratic hints when stuck
    - can check their solutions
    - can get a full "perfect" solution after they solve a problem

    
    #colbreak()
    #align(center)[
      #image("Screenshot 2026-04-15 at 13.30.07.png")
    ]
    
  ]
  *While* 
    - maintaining the chain of reasoning and entire solving process
    - making LLM use easier, safer and better for educational purposes


]

#slide(title: "Technical Architecture", outlined: true)[
  #image("background.png")
]


#slide(title: "LLM Integration", outlined: true)[
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Model:*
        - _Gemini 3 flash_ 
          - Speed, output quality, performance in Icelandic
          - Different thinking levels for different tasks
        - Future: Model rerouting based on traffic and/or complexity of problems
    ]
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Prompting Strategy*
      - Zero shot, structured output, chain of thought, refined meta-prompting
    ]

    
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Evolution*
     - One prompt for all modes -> One focused prompt for each mode
     - One prompt for every phase of analysis ->
      - An optional legibility checker prompt
      - Mathematical reasoning prompt
      - Error categorization prompt
    - Zero shot -> One shot -> Few shot -> One shot -> Zero shot
    ]

    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Advanced patterns*
     - Agentic Vision for error detection
    ]
]

#slide(title:"Evaluation & Quality", outlined: true)[
  #v(-0.3cm)
  The *evaluation dataset* contains 50 handwritten mathematics problems
  - Used to test prompting. Newest iteration, *v6*, vs. assignment 3 iteration, *a3*
  - Prompt results evaluated against true labels and with gpt-5.4-Nano as a judge
  #columns(2)[
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *LLM as judge*
     - Mathematical correctness (MC)
     - Pedagocical helpfulness (PH)
     - Policy compliance (PC)
     - Clarity (C)
     - Specificity (S)
     
     *Score 1-5*
     - *v6* avg: 3.7 & *a3* avg: 3.76 
    ]
    #colbreak()
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Comparison to true labels*
     - Accuracy of verdicts:
      - *v6*: 0.96* & *a3*: 0.96
    - Non feasability ratio
      - *v6*: 0 & *a3*: 0
    - Average latency
      - $approx 17$ seconds for *v6*
    ]
  ]
  #v(-0.5cm)
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb("#FFF"),
      width: 100%
    )[
      * Specific legibility prompt caught one of two errors for *v6*
    ]

    
#align(center + horizon)[
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *LLM as judge results*
#table(
  columns: 9,

  table.header(
    [*prompt*], [*mode*], [*cases*], [*avg*], [*avg MC*],
    [*avg PH*], [*avg PC*], [*avg C*], [*avg S*],
  ),

  // --- old ---
  [*a3*], [check], [22], [*3.23*], [3.73], [2.95], [4.5], [4.55], [2.64],
  [*a3*], [hint],  [23], [*4.3*],  [4.43], [4.26], [4.91], [4.52], [3.65],
  [*a3*], [reveal],[5],  [*3.6*],  [3.6],  [3.8],  [4.6],  [4.6],  [3.8],

  // thick separator row
  table.hline(stroke: 1.5pt),

  // --- new ---
  [*v6*], [check], [22], [*3.09*], [3.45], [2.95], [4.59], [4.41], [2.59],
  [*v6*], [hint],  [23], [*4.09*], [4.17], [4.09], [4.83], [4.57], [3.48],
  [*v6*], [reveal],[5],  [*4.6*],  [4.8],  [4.6],  [5.0],  [4.6],  [4.6],
)]
]
*Failures*: Unclear writing -> Legibility check\
*Safety*: Output validation, legibility, prompt level behavioral guidelines
]

#slide(title: "Deployment and Monitoring", outlined: true)[
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
  *Deployment*
  - Backend hosted on Render
  - Frontend hosted locally
  *Observability*
  - Admin dashboard containg user behaviour data
  - Langfuse dashboard containg tracing data
  *Metrics*
  - API call metadata, cost spikes, weekly changes in user behaviour]
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb("FFF"),
      width: 100%
    )[
#image("Screenshot 2026-04-14 at 23.26.04.png")]
]

#slide(title: "Feature Plan Retrospective", outlined: true)[
  #columns(2)[
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
    *Assignment 5 planned features*
    1. Add user-based statistics to the homepage #text(fill: green)[✓]
    2. Add an error bank for users #text(fill: green)[✓]
    3. Try to lower latency further #text(fill: green)[✓]
    4. Generate problems based on user errors #text(fill: red)[✗]
    5. Implement anonymous data collection #text(fill: red)[✗]
    ]

    #colbreak()
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
    *Additional features*
    1. Explicit legibility phase
    2. Explicit error categorization
    3. Agentic vision for error detection
    4. Greatly improved user experience
      - folder structure, writing, notebook, latex, toolbar, etc.
    5. Share problems
    6. Expert mode
    ]
  ]
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
    *Anonymous data collection*: Exists in the backend but not activated\
    *Problem generation*: Increased scope and therefore backlogged
    ]
]

#slide(title:"LIVE DEMO", outlined:true)[

  #align(center)[

      #image("avatar_loki.png", width: 8cm)
      
  ]
]

#slide(title: "User testing", outlined: true)[
  #columns(2, gutter: 14pt)[
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Methodology*
      - 5 moderated sessions with external users, 20 to 30 minutes each.
      - Standardized 6-task script: login + folders, solve/review, hint flow, seeded-error recovery, error bank, PDF export
      - Think-aloud protocol, no help unless user was blocked for over 60 seconds.
      - Data captured per session: task completion, time-on-task, interventions, unexpected actions, latency perception, SUS
    ]

    #colbreak()

    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Interaction Data*
      - Task completion: *30/30 tasks completed* across all sessions.
      - SUS scores: *72.5, 67.5, 95.0, 72.5, 92.5*
      - Overall usability: *mean 80.0*, *median 72.5*
      - Repeated behavior patterns:
        - users opened wrong folder levels first
        - misread add-page/media controls
        - hesitated during AI wait states
    ]
  ]

  #v(0.4cm)

  #columns(2, gutter: 14pt)[
    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Main Findings*
      - Folder and subfolder hierarchy was not immediately discoverable.
      - Latency and timeout behavior reduced confidence, even when tasks were eventually completed.
      - Canvas/media actions needed clearer affordances and placement.
      - Missing name capture at registration created downstream friction in PDF/export flows.
    ]

    #colbreak()

    #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *How Feedback Shaped the Product*
      - Reworked folder IA and safer folder actions after repeated navigation errors.
      - Improved onboarding/profile flow to capture user name earlier for submission exports.
      - Refined media, canvas, and fullscreen controls to match how users actually searched for actions.
      - Treated response-time friction as a product priority.
    ]
  ]
]

#slide(title:"Lessons learned", outlined: true)[
  #box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
  *What would we change if starting over?*
  - Start focusing on latency earlier to prevent bottleneck
]#box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
  *Next Iteration*
  - Collect handwritten mathematics data from various users
  - Model rerouting based on traffic and/or complexity of problems
  - Generate a question bank based on solved problems and errors by a user
  - Structured follow ups to LLM responses, e.g. use RAG to retrieve theorem
  - CI/CD, especially for prompts
  - Generate a user profile based on methods used and errors made
  - Open notes where student can ask clarifying questions on theorems, definitions, etc.
  - Actual research in the field of math and education
]
#box(
      stroke: black,
      inset: 12pt,
      radius: 6pt,
      fill: rgb(244, 235, 221),
      width: 100%
    )[
      *Final Takeaways:*
      - Technical:
        - LLM were more capable than we initially thought
        - Prompting plays a huge role in the quality of LLM based projects
      - Non-technical:
        - Good preperation, planning and project definition always kept us on the correct path
    ]

]

#slide(title: "", outlined: true)[
  #align(center)[
    #text(size: 30pt)[Questions?]
    #image("logo.svg", width: 5cm)
  ]
]
