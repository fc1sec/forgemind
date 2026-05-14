# ForgeMind: First-Time User Guide

**For**: Anyone installing ForgeMind for the first time  
**Time**: 15 minutes (including understanding what ForgeMind does)  
**Goal**: Complete your first project analysis and understand ForgeMind's capabilities + limitations

---

## Before You Start: Honest Truth

**What ForgeMind Will Do**
- ✅ Analyze your project description and create 17 structured documents
- ✅ Help you surface risks, assumptions, and unclear success criteria *before* you build
- ✅ Create governance templates and decision logs
- ✅ Prepare handoff documents for your agent or team

**What ForgeMind Will NOT Do**
- ❌ Make decisions for you (that's your job)
- ❌ Know your domain better than you do (you're the expert)
- ❌ Guarantee your project succeeds (ForgeMind structures; you execute)
- ❌ Write code, create code review PRs, or deploy systems
- ❌ Certify compliance or guarantee safety
- ❌ Replace human judgment or domain expertise

**Best Use Case**: You have a project idea or issue, you're *before* execution starts, and you want rigor.

---

## Step 1: Install ForgeMind (1 minute)

```bash
pip install forgemind
```

Verify installation:
```bash
forgemind version
# Output: ForgeMind v1.2.1
```

---

## Step 2: Initialize Your Workspace (1 minute)

```bash
# Go to a project directory (or create one)
mkdir my_forgemind_work
cd my_forgemind_work

# Initialize ForgeMind
forgemind init
```

What this creates:
```
forgemind_projects/          ← Your project input files go here
├── sample_ai_project.md     ← Example (you can run this as-is)
forgemind_outputs/           ← Generated analyses appear here (empty until you run intake)
.forgemind/                  ← ForgeMind internal files (ignore this)
```

---

## Step 3: Understand What ForgeMind Creates (2 minutes)

Before analyzing your project, let's see what ForgeMind produces using the pre-filled example.

```bash
forgemind intake forgemind_projects/sample_ai_project.md
```

This generates 17 analysis documents. Here's what matters:

### If You're Pressed for Time (read these 3):
1. **PROJECT_CHARTER.md** ← Your project objective, scope, success criteria in one place
2. **RISK_REGISTER.md** ← What could go wrong, how bad, what to do about it
3. **ACCEPTANCE_CRITERIA.md** ← How you'll know you succeeded

### If You Want the Full Picture (read these):
- RDMAICSI_MATRIX.md ← Eight-phase improvement cycle (Recognize → Integrate)
- SENGE_LENS.md ← Five disciplines for learning organizations
- LEAN_WASTE_SCAN.md ← Where are you wasting time/money?
- ASSUMPTION_LOG.md ← What bets are you making?
- CONTROL_PLAN.md ← How will you prevent scope creep?
- DECISION_LOG.md ← What did we decide and why?
- BACKLOG.md ← Prioritized work items
- AGENT_HANDOFF.md ← If you're using an AI agent, what it needs to know

Check the output:
```bash
cat forgemind_outputs/sample-ai-project/PROJECT_CHARTER.md
```

You'll see a structured document with:
- Clear objective statement
- Defined scope and constraints
- Stakeholders
- Success metrics
- Risks and assumptions

**Aha moment**: ForgeMind just structured your vague project idea into something testable.

---

## Step 4: Create Your Own Project (5 minutes)

Now let's analyze *your* project. Create a new file:

```bash
nano forgemind_projects/my_project.md
```

Fill in these sections (even if rough):

```markdown
# My Project Title

## Objective
What are we trying to accomplish? (2-3 sentences)

## Context
Why is this important? What's the background?

## Scope
What's IN scope? What's OUT of scope?

## Constraints
Timeline, budget, team size, technical limits?

## Risks
What could go wrong? (List 3-5)

## Success Criteria
How will we know we succeeded?
```

**Real Example** (you can copy this structure):

```markdown
# AI Backend Automation Agent

## Objective
Build an AI agent that generates backend microservice boilerplate 
in 30 minutes instead of 4 hours, while maintaining security standards.

## Context
Our backend team spends 4 hours per new service on boilerplate setup 
(models, routes, tests, migrations). An agent could reduce this to 
30 minutes of AI work + 1 hour of human review.

## Scope
- Agent reads service spec (JSON)
- Generates Django models, REST routes, unit tests
- Validates against our patterns
- Submits PR for human review

## Out of Scope
- Database schema design (human does this)
- Production deployment (use our deployment pipeline)
- Security fixes (human security team reviews)

## Constraints
- Agent cannot modify production code directly
- All outputs go to PR for approval first
- Must integrate with our CI/CD in 2 weeks
- Cannot call external APIs (must be local)

## Risks
- Agent generates insecure code patterns
- Agent hallucinates non-existent APIs
- Scope creeps to dangerous operations (deleting data, etc.)
- Team doesn't trust agent outputs

## Success Criteria
- First 5 agent-generated services deployed to production
- Security team approves all agents without finding vulnerabilities
- Backend team reports 50% time savings on setup
- Agent code passes linter without edits
```

Save and exit (`Ctrl+O`, Enter, `Ctrl+X` in nano).

---

## Step 5: Run Analysis on Your Project (2 minutes)

```bash
forgemind intake forgemind_projects/my_project.md
```

ForgeMind will:
1. Read your project description
2. Analyze it against 17 templates
3. Generate 17 documents
4. Store them in `forgemind_outputs/my-project/`

Output looks like:
```
✓ Analysis complete: my_project

Generated 17 documents in forgemind_outputs/my-project/:

Core Documents:
✓ PROJECT_CHARTER.md
✓ RISK_REGISTER.md
✓ ASSUMPTION_LOG.md
✓ ACCEPTANCE_CRITERIA.md
...and 13 more

Time taken: 2.3s
```

---

## Step 6: Review Your Results (3 minutes)

```bash
# Open the main analysis files
cat forgemind_outputs/my-project/PROJECT_CHARTER.md
cat forgemind_outputs/my-project/RISK_REGISTER.md
cat forgemind_outputs/my-project/ACCEPTANCE_CRITERIA.md
```

**Ask yourself**:
- Did ForgeMind catch important risks I hadn't written down?
- Are my success criteria actually testable?
- Is my scope realistic, or did ForgeMind spot scope creep?
- Did ForgeMind find assumptions I was making without realizing?

**Good sign**: ForgeMind surfaces things you knew but hadn't explicitly documented.

**Red flag**: ForgeMind outputs seem generic or irrelevant. (If this happens, your project description was too vague—add more detail and re-run.)

---

## Step 7: Understand ForgeMind's Limitations (2 minutes)

Read this before you decide whether to use ForgeMind for a real project:

### ForgeMind Knows About Tools, Not Your Domain

```
✅ ForgeMind can help you structure a software project's risks
❌ ForgeMind cannot tell you which software architectures are secure

✅ ForgeMind can help you create an AI agent handoff document
❌ ForgeMind cannot verify your agent is safe

You provide domain expertise. ForgeMind provides structure.
```

### ForgeMind Uses Rules, Not AI Magic

- ForgeMind matches keywords and applies templates.
- If you don't mention a risk, ForgeMind can't invent it.
- If you're vague about scope, ForgeMind's output will be vague.

**Good input → Good output. Vague input → Vague output.**

### ForgeMind Requires Human Review

Every ForgeMind output must be reviewed by someone who understands your domain before you act on it. ForgeMind is a thinking tool, not a decision-maker.

### ForgeMind Doesn't Guarantee Reversibility

For some domains (government tenders, biomedical devices, nuclear systems), reversing decisions is constrained by regulation. ForgeMind documents what it knows, but escalates when domain expertise is required.

See `docs/AI_SYSTEM_TRANSPARENCY.md` for the full transparency statement.

---

## Step 8: Decide: Keep Going or Stop?

**Keep ForgeMind if**:
- You're starting a new project and want upfront rigor
- Your team tends to discover missing requirements mid-project
- You're handing work to an AI agent and need structured context
- You want documented decision logs for compliance

**Don't use ForgeMind if**:
- Your project is fully defined and you're just building it now
- You need code generation (ForgeMind doesn't write code)
- You're in pure firefighting/tactical mode (this is strategic)

---

## Next Steps After This Guide

### Option A: Create a Real Project Analysis
1. Create a new project file in `forgemind_projects/`
2. Describe your actual project
3. Run `forgemind intake your_project.md`
4. Review the 17 documents with your team
5. Use them to structure your approach before you build

### Option B: Learn More About Specific Features
```bash
# Get help on any command
forgemind --help
forgemind intake --help

# Check for updates (non-blocking, daily)
# Notifications show automatically if a new version is available

# Detailed docs
cat docs/UPDATES_AND_SAFETY.md    ← How to safely update ForgeMind
cat docs/COMPATIBILITY_MATRIX.md  ← What versions work together
cat docs/AI_SYSTEM_TRANSPARENCY.md ← What ForgeMind is/isn't
```

### Option C: Contribute a Domain Pattern
If you're an expert in a domain (ISO 9001, biomedical, AI safety, etc.) and you want to contribute reverse patterns:
```bash
cat CONTRIBUTING_REVERSE_PATTERNS.md
# See how to add domain-specific expertise to ForgeMind
```

---

## FAQ: Common Questions

### Q: Why does ForgeMind need my project description in Markdown?

**A**: ForgeMind analyzes what you write. Markdown is human-readable and machine-parseable. You can edit it easily in any text editor.

### Q: Can ForgeMind update my project automatically?

**A**: No. ForgeMind generates *analysis documents*, not code. You read them, decide what to do, and update your project.

### Q: Is my project data safe?

**A**: Yes. ForgeMind runs locally on your computer. Your project files never go to the cloud. You own all generated documents.

### Q: What if ForgeMind's output is wrong?

**A**: Report it on GitHub. Include your project file (redact sensitive info) and what you expected vs. what you got.

### Q: How often should I re-run `forgemind intake`?

**A**: Every time your project changes significantly. Re-running takes ~2 seconds and updates all 17 documents.

### Q: Can I use ForgeMind for compliance/audit purposes?

**A**: ForgeMind *helps* document decisions, but it's not a compliance certifier. For regulated work (medical, aviation, government), validate ForgeMind's outputs with regulatory bodies.

### Q: What's the difference between ForgeMind and a project management tool?

**A**: ForgeMind structures the *planning* phase (before execution). Project management tools track the *execution* phase (during building). You need both.

---

## Support

- **Questions?** Read `docs/` directory first
- **Found a bug?** Open an issue on GitHub with: project file (redacted), error message, what you expected
- **Security issue?** Email fc1sec@hotmail.com (48-hour response)

---

**You're ready. Good luck with your project. Bring structure, rigor, and your expertise. ForgeMind handles the rest.**

---

*ForgeMind v1.2.1 | Philosophy: Structure work rigorously. Update safely. Maintain trust.*
