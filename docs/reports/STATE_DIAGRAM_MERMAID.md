# AI THERAPIST STAGE 1 - STATE ACTION DIAGRAMS (MERMAID)

**Interactive Flow Diagrams for System Visualization**

---

## 📊 MAIN PROGRESSION FLOW

### Complete Stage 1 Flow (Happy Path)

```mermaid
graph TD
    Start([Client Enters]) --> 1.1[1.1 Goal Inquiry]

    1.1 -->|Goal Stated| 1.2[1.2 Build Vision]
    1.1 -->|Vague Problem| 1.1_r[1.1_redirect<br/>Redirect to Goal]
    1.1_r -->|Goal Clarified| 1.2

    1.2 -->|Accepts Vision| 1.3[1.3 Get Permission]
    1.2 -->|Needs Clarification| 1.2

    1.3 -->|Permission Granted| 2.1[2.1 Problem Inquiry]

    2.1 -->|Has Body Words| 2.2[2.2 Body Location]
    2.1 -->|No Body Words| 2.1_s[2.1_seek<br/>Guide to Body<br/>MAX 3 attempts]

    2.1_s -->|Body Mentioned| 2.2
    2.1_s -->|3 Attempts Failed| ESCAPE1{Escape Route}
    ESCAPE1 -->|Option A| CARD[Card Game<br/>Framework]
    ESCAPE1 -->|Option B| 3.1
    CARD --> 2.2

    2.2 -->|Location Given| 2.3[2.3 Sensation Quality]

    2.3 -->|Sensation Described| 2.4[2.4 Present Check]

    2.4 -->|Present Aware| 2.5[2.5 Pattern Inquiry]
    2.4 -->|Not Present| 2.4

    2.5 -->|Pattern Identified| 3.1[3.1 Assess Readiness]

    3.1 -->|Ready| 3.2[3.2 Introduce Alpha]
    3.1 -->|More to Discuss| 2.5

    3.2 -->|Willing| 3.3[3.3 Execute Alpha<br/>⚡FRAMEWORK: alpha_sequence]
    3.2 -->|Hesitant| 3.2

    3.3 --> 3.4[3.4 Post-Alpha]

    3.4 -->|Positive Response| 3.5[3.5 Link to Vision]
    3.4 -->|Neutral| 3.6

    3.5 --> 3.6[3.6 Compare Progress]

    3.6 -->|Improved| 4.1[4.1 Ready Stage 2]
    3.6 -->|Same/Worse| 3.1

    4.1 --> STAGE2([Begin Stage 2])

    style 1.1 fill:#e1f5ff
    style 2.1 fill:#fff4e6
    style 3.3 fill:#ffe6e6
    style 4.1 fill:#e6ffe6
    style CARD fill:#ffccff
```

---

## 🚨 PRIORITY REDIRECTS

### Priority Routing System (Can Interrupt Any State)

```mermaid
graph TD
    ANY[ANY STATE] --> PRIORITY{Priority<br/>Detection}

    PRIORITY -->|1. Self-Harm<br/>HIGHEST| SELFHARM[SELFHARM State<br/>⚡no_harm framework]
    PRIORITY -->|2. Thinking Mode| THINK[THINK State<br/>MAX 3 attempts]
    PRIORITY -->|3. Past Tense| PAST[PAST State<br/>MAX 3 attempts]
    PRIORITY -->|4. Body + Present| AFFIRM[AFFIRM State<br/>Just affirm]
    PRIORITY -->|5. Normal| NORMAL[Continue<br/>Normal Flow]

    SELFHARM -->|Engaged| ASSESS_SAFE{Safety<br/>Assessment}
    SELFHARM -->|Crisis| CRISIS[CRISIS State<br/>⚡no_harm framework]

    ASSESS_SAFE -->|Safe| RETURN1[Return to Flow]
    ASSESS_SAFE -->|Unsafe| CRISIS

    THINK -->|Feeling Response| RETURN2[Return to Flow]
    THINK -->|3 Attempts| ESCAPE_THINK[Escape to 3.2<br/>Alpha Grounding]

    PAST -->|Present Response| RETURN3[Return to Flow]
    PAST -->|3 Attempts| ESCAPE_PAST[Escape to 3.2<br/>Alpha Anchoring]

    AFFIRM --> RETURN4[Continue Flow]
    NORMAL --> RETURN5[Continue Flow]

    ESCAPE_THINK --> 3.2[3.2 Introduce Alpha]
    ESCAPE_PAST --> 3.2

    3.2 --> 3.3[3.3 Execute Alpha<br/>⚡alpha_sequence]

    style SELFHARM fill:#ff6b6b
    style CRISIS fill:#c92a2a
    style THINK fill:#ffd43b
    style PAST fill:#ffd43b
    style AFFIRM fill:#51cf66
    style 3.3 fill:#ffe6e6
```

---

## 🔄 LOOP PREVENTION SYSTEM

### Loop Detection and Escape Routes

```mermaid
graph TD
    subgraph "LOOP 1: Body Awareness"
        S1[2.1_seek State] -->|Attempt 1| C1{Body<br/>Mentioned?}
        C1 -->|Yes| EXIT1[→ 2.2 Location]
        C1 -->|No| COUNT1[Counter: 1]
        COUNT1 --> S1

        S1 -->|Attempt 2| C2{Body<br/>Mentioned?}
        C2 -->|Yes| EXIT1
        C2 -->|No| COUNT2[Counter: 2]
        COUNT2 --> S1

        S1 -->|Attempt 3| C3{Body<br/>Mentioned?}
        C3 -->|Yes| EXIT1
        C3 -->|No| ESC1{Escape<br/>Route}
        ESC1 -->|Option A| CARD1[Trigger<br/>card_game]
        ESC1 -->|Option B| SKIP1[Skip to 3.1]
        CARD1 --> EXIT1
    end

    subgraph "LOOP 2: Thinking Mode"
        T1[THINK State] -->|Attempt 1| TC1{Feeling<br/>Response?}
        TC1 -->|Yes| TEXIT[Return to Flow]
        TC1 -->|No| TCOUNT1[Counter: 1]
        TCOUNT1 --> T1

        T1 -->|Attempt 2| TC2{Feeling<br/>Response?}
        TC2 -->|Yes| TEXIT
        TC2 -->|No| TCOUNT2[Counter: 2]
        TCOUNT2 --> T1

        T1 -->|Attempt 3| TESC[Escape to 3.2<br/>Alpha Grounding]
    end

    subgraph "LOOP 3: Past Tense"
        P1[PAST State] -->|Attempt 1| PC1{Present<br/>Response?}
        PC1 -->|Yes| PEXIT[Return to Flow]
        PC1 -->|No| PCOUNT1[Counter: 1]
        PCOUNT1 --> P1

        P1 -->|Attempt 2| PC2{Present<br/>Response?}
        PC2 -->|Yes| PEXIT
        PC2 -->|No| PCOUNT2[Counter: 2]
        PCOUNT2 --> P1

        P1 -->|Attempt 3| PESC[Escape to 3.2<br/>Alpha Anchoring]
    end

    TESC --> ALPHA[3.2 → 3.3<br/>Alpha Sequence]
    PESC --> ALPHA

    style ESC1 fill:#ffd43b
    style TESC fill:#ffd43b
    style PESC fill:#ffd43b
    style ALPHA fill:#ffe6e6
    style CARD1 fill:#ffccff
```

---

## 🎯 SPECIAL STATES HANDLING

### Edge Cases and Special Situations

```mermaid
graph TD
    ANY[Client Input] --> DETECT{Detection}

    DETECT -->|High Intensity<br/>CAPS, !!!| EMOTION[EMOTION State<br/>Validate + Ground]
    DETECT -->|Crying| CRY[CRY State<br/>Normalize Tears]
    DETECT -->|Silent/Pause| SILENT[SILENT State<br/>Gentle Prompt]
    DETECT -->|Off-Topic| OFF[OFF State<br/>Gentle Redirect]
    DETECT -->|"Is this normal?"| VALID[VALID State<br/>Normalize]
    DETECT -->|People-Pleasing| RELATION[RELATION State<br/>Redirect to Body]
    DETECT -->|"Not helping"| RESIST[RESISTANCE State<br/>Explain Process]
    DETECT -->|Excessive Detail| RAMBLE[RAMBLING State<br/>Gentle Interrupt]
    DETECT -->|Incoherent/Panic| CRISIS2[CRISIS State<br/>⚡Safety Check]

    EMOTION -->|Calm| CONT1[Continue Flow]
    EMOTION -->|Escalates| CRISIS2

    CRY -->|Calm| CONT2[Continue Previous]
    CRY -->|Upset| MORE[More Support]

    SILENT -->|Speaks| CONT3[Continue]
    SILENT -->|Still Silent| CARD2[⚡card_game<br/>Framework]

    OFF -->|Back on Track| CONT4[Continue]
    OFF -->|Still Off| FIRMER[Firmer Redirect]

    VALID -->|Reassured| CONT5[Continue]

    RELATION -->|Body Mentioned| CONT6[Continue]

    RESIST -->|Willing| CONT7[Continue]
    RESIST -->|Still Resistant| EXPLAIN[Explain Method]

    RAMBLE -->|Body Mentioned| BODY[→ 2.2 Location]
    RAMBLE -->|Still Rambling| FIRM[Firmer Interrupt]

    CRISIS2 -->|Safe + Calm| CONT8[Continue]
    CRISIS2 -->|Unsafe| EMERGENCY[Emergency<br/>Resources]

    CARD2 --> BODY

    style EMOTION fill:#ffd8a8
    style CRY fill:#d0bfff
    style CRISIS2 fill:#ff6b6b
    style RESIST fill:#ffd43b
    style CARD2 fill:#ffccff
```

---

## 🔧 FRAMEWORK TRIGGERS

### When Frameworks Are Triggered

```mermaid
graph LR
    subgraph "Framework Triggers"
        A[3.3 Execute Alpha] -->|Always| AF1[⚡alpha_sequence<br/>6 steps + body checks]

        B[SELFHARM State] -->|Always| AF2[⚡no_harm<br/>Safety protocol]

        C[CRISIS State] -->|If unsafe| AF3[⚡no_harm<br/>Emergency]

        D[SILENT State] -->|After 2 attempts| AF4[⚡card_game<br/>Non-verbal]

        E[2.1_seek Loop] -->|After 3 attempts| AF5[⚡card_game<br/>OR skip to 3.1]

        F[Client Confused] -->|On-demand| AF6[⚡metaphors Type A<br/>Vector DB query]

        G[Stage 2 Strategic] -->|Per TRT PDF| AF7[⚡metaphors Type B<br/>Trauma explanation]
    end

    style AF1 fill:#ffe6e6
    style AF2 fill:#ff6b6b
    style AF3 fill:#c92a2a
    style AF4 fill:#ffccff
    style AF5 fill:#ffccff
    style AF6 fill:#e6f7ff
    style AF7 fill:#e6f7ff
```

---

## 🎭 COMPLETE SYSTEM OVERVIEW

### All Components Together

```mermaid
graph TB
    CLIENT[Client Message] --> MASTER[Master Agent LLaMA]

    MASTER --> DET1{Self-Harm?}
    DET1 -->|Yes| SELF[SELFHARM + no_harm]
    DET1 -->|No| DET2{Thinking?}

    DET2 -->|Yes| TH[THINK State]
    DET2 -->|No| DET3{Past?}

    DET3 -->|Yes| PA[PAST State]
    DET3 -->|No| DET4{Body+Present?}

    DET4 -->|Yes| AFF[AFFIRM State]
    DET4 -->|No| CSV[CSV State Lookup]

    CSV --> STATE[Current State Info]
    STATE --> CHECK{Framework<br/>Trigger?}

    CHECK -->|alpha_sequence| ALPHA_F[Execute Alpha<br/>Framework]
    CHECK -->|no_harm| HARM_F[Execute no_harm<br/>Framework]
    CHECK -->|card_game| CARD_F[Execute card_game<br/>Framework]
    CHECK -->|None| RAG[RAG Query]

    ALPHA_F --> RAG
    HARM_F --> RAG
    CARD_F --> RAG

    RAG --> VDB[Vector Database]
    VDB --> DIALOG[Dialogue Agent LLaMA]

    DIALOG --> RESPONSE[Therapist Response]
    RESPONSE --> NEXT[Determine Next State]
    NEXT --> LOOP{Loop<br/>Counter?}

    LOOP -->|< 3| UPDATE[Update State]
    LOOP -->|>= 3| ESCAPE[Trigger Escape]

    ESCAPE --> UPDATE
    UPDATE --> CLIENT

    style MASTER fill:#e1f5ff
    style CSV fill:#fff4e6
    style VDB fill:#e6ffe6
    style DIALOG fill:#ffe6f7
    style SELF fill:#ff6b6b
    style ALPHA_F fill:#ffe6e6
    style CARD_F fill:#ffccff
```

---

## 📈 STATE STATISTICS

### System Composition

```mermaid
pie title State Distribution (31 Total States)
    "Goal & Vision (3)" : 3
    "Body Awareness (5)" : 5
    "Alpha Sequence (6)" : 6
    "Priority Redirects (3)" : 3
    "Special Handling (8)" : 8
    "Safety & Crisis (2)" : 2
    "Transition (1)" : 1
    "Redirect States (3)" : 3
```

---

## 🔍 DECISION TREE

### Master Agent Decision Logic

```mermaid
graph TD
    START([Client Message]) --> P1{Self-Harm<br/>Detected?}

    P1 -->|YES| ACT1[Route to SELFHARM<br/>PRIORITY 1<br/>⚡no_harm]
    P1 -->|NO| P2{Thinking<br/>Mode?}

    P2 -->|YES| ACT2[Route to THINK<br/>PRIORITY 2<br/>Max 3→Alpha]
    P2 -->|NO| P3{Past<br/>Tense?}

    P3 -->|YES| ACT3[Route to PAST<br/>PRIORITY 2<br/>Max 3→Alpha]
    P3 -->|NO| P4{Body Words<br/>+ Present?}

    P4 -->|YES| ACT4[Route to AFFIRM<br/>PRIORITY 3<br/>60%+ usage]
    P4 -->|NO| P5{Current<br/>State?}

    P5 --> STATE_LOGIC{State-Specific<br/>Logic}

    STATE_LOGIC -->|State 1.x| GOAL[Goal/Vision<br/>States]
    STATE_LOGIC -->|State 2.x| BODY[Body Awareness<br/>States]
    STATE_LOGIC -->|State 3.x| ALPHA_S[Alpha Sequence<br/>States]
    STATE_LOGIC -->|State 4.x| TRANS[Transition<br/>State]
    STATE_LOGIC -->|Special| SPECIAL[Special<br/>States]

    GOAL --> ROUTE[Determine Route]
    BODY --> ROUTE
    ALPHA_S --> ROUTE
    TRANS --> ROUTE
    SPECIAL --> ROUTE

    ROUTE --> LOOP_CHK{Loop<br/>Counter<br/>>= 3?}

    LOOP_CHK -->|YES| ESCAPE_R[Trigger<br/>Escape Route]
    LOOP_CHK -->|NO| NORMAL[Normal<br/>Routing]

    ESCAPE_R --> NEXT
    NORMAL --> NEXT[Next State]

    style ACT1 fill:#ff6b6b
    style ACT2 fill:#ffd43b
    style ACT3 fill:#ffd43b
    style ACT4 fill:#51cf66
    style ESCAPE_R fill:#ffa94d
```

---

## 💡 USAGE INSTRUCTIONS

### How to Use These Diagrams

1. **Copy** any diagram code block above
2. **Paste** into:
   - [Mermaid Live Editor](https://mermaid.live)
   - GitHub markdown (supports mermaid natively)
   - Any mermaid-compatible tool
3. **View** the interactive diagram
4. **Export** as SVG or PNG if needed

### Diagram Types Included

- **Main Progression Flow** - Complete happy path from start to Stage 2
- **Priority Redirects** - How priority routing interrupts flow
- **Loop Prevention** - How loops are detected and escaped
- **Special States** - Edge case handling
- **Framework Triggers** - When frameworks activate
- **System Overview** - Complete architecture
- **Decision Tree** - Master Agent logic flow

---

**Created:** 2025-10-08
**System:** AI Therapist Stage 1
**Total States:** 31
**Total Diagrams:** 8

---

*State Diagrams - AI Therapist Stage 1*
*Interactive Mermaid Visualizations*
