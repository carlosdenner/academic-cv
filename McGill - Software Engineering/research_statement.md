Research Statement
Secure Software Engineering for LLM-Intensive Systems

Over the next decade, software systems will increasingly be built “around” large language models (LLMs) and agents rather than simply “using” them as add-ons. Modern applications already combine proprietary and open-source LLMs with retrieval-augmented generation (RAG), tool-calling, code generation, and multi-agent workflows to automate complex business and public-sector processes. These systems break many assumptions of classical software engineering: they are non-deterministic, heavily data-driven, partially opaque, and deeply entangled with external providers and regulatory constraints. My research program aims to bring hard software engineering methods—automated analysis and testing, security architectures, and governance-aware development practices—to this new class of LLM-intensive systems, so that they can be deployed safely and responsibly in safety- and mission-critical domains.

This vision aligns closely with McGill’s strengths in software analysis and testing, software security, and cyber-physical and internet-scale systems in the Department of Electrical and Computer Engineering. My work extends these themes to a new frontier: secure and trustworthy LLM-centric architectures, where prompts, RAG pipelines, and agent workflows are treated as first-class software artifacts with explicit fault models, coverage criteria, and assurance cases. The end goal is to give developers and organizations concrete methods and tools to build LLM-intensive software that is testable, auditable, and governable—rather than relying on ad-hoc prompt engineering and disconnected “ethics guidelines.”

My research program is organized around three tightly coupled pillars:

1. Automated assurance for LLM-intensive software;
2. Security of agentic, tool-using, and multimodal systems;
3. Governance-aware software engineering for AI-intensive systems.

I. Automated Assurance for LLM-Intensive Software

The first pillar focuses on adapting and extending automated program analysis and testing to LLM-centric architectures. Rather than treating LLM calls as opaque API invocations, I view prompts, RAG pipelines, and agent workflows as software artifacts that should be subject to systematic analysis.

The core research questions are:

• How can we define meaningful fault models, coverage criteria, and test oracles for LLM-driven workflows, beyond simple unit tests around API calls?

• How do we integrate prompt- and workflow-level analysis into CI/CD pipelines without overwhelming developers or stalling delivery?

• How can we leverage the models themselves to amplify testing (e.g., for fuzzing, metamorphic testing, or automated oracle construction) while still maintaining clear trust boundaries?

One research direction is a “static analysis for prompts and orchestrations.” Here, I plan to develop a static analysis and linting framework for prompt templates, tool schemas, and orchestration graphs in common agent frameworks. The goal is to automatically flag patterns that are known to be risky—such as unscoped tool capabilities, missing human-in-the-loop checkpoints, unsafe data flows (e.g., PII being sent to external models), or structures that are systematically vulnerable to prompt injection and data exfiltration. This extends familiar ideas from static analysis and taint tracking into the LLM/RAG layer.

A complementary direction is “LLM-aware fuzzing and red-teaming.” Building on emerging work on prompt injection and jailbreak attacks, I want to design fuzzing frameworks that automatically generate adversarial prompts and tool-call sequences, measure coverage across tools, flows, and retrieval spaces, and integrate as regressions tests in CI. Here the emphasis is not only on discovering failures, but on defining operational robustness metrics (e.g., harmful-output rate under a threat model, stability of responses under paraphrases, or robustness to corpus perturbations) that teams can track over time.

A third line of work concerns reliability metrics for RAG pipelines. In many real deployments, hallucination is not a single scalar; what matters is the reliability of the entire question-to-answer pipeline under real workloads. I plan to develop metrics and evaluation harnesses that characterize RAG behavior under paraphrasing, partial or adversarial retrieval, and evolving corpora, and to connect these metrics to concrete design decisions: chunking strategies, retrieval filters, citation requirements, and multi-model voting. This work will naturally feed back into the static and dynamic analysis tools above.

These research threads will produce both foundational results (definitions of coverage, fault models, and oracles for LLM-intensive software) and practical artifacts (linters, CI plug-ins, testing frameworks) that are directly aligned with McGill’s focus on automated software analysis and testing.

II. Security of Agentic, Tool-Using, and Multimodal Systems

The second pillar addresses the security of LLM agents that call tools, execute code, interact with multimodal inputs, and make changes in digital or physical environments. Once LLMs are granted the ability to browse, run code, access internal APIs, or operate robotic systems, they effectively become a new class of software “principal” with a complex and often implicit security perimeter. My goal is to make that perimeter explicit, analyzable, and enforceable.

Here my research questions include:

• How do we construct realistic threat models and benchmarks for LLM agents—covering prompt injection (including multimodal forms), tool abuse, data exfiltration, and financial or safety harms?

• What kind of capability systems, sandboxing mechanisms, and runtime monitors are needed to constrain agents in practice, without making them unusable for developers?

• How can we embed security constraints into the design of tools and orchestrators, instead of bolting on filtering layers around an already over-powered agent?

A first project line is the development of standardized security benchmarks and red-team suites for LLM agents. I plan to synthesize and extend recent research on code-capable agents, harmful autonomous behaviors, and multimodal prompt injection into a set of open, reproducible benchmarks that evaluate agents not just on capabilities but on their behavior under attack. These benchmarks will be designed to integrate into CI/CD and to emit rich diagnostic information—what tools were misused, what data flowed where, which policies were violated—so that they can support both research and industrial adoption.

A second line focuses on “tool firewalls” and agent capability systems. Here I aim to design architectural patterns, formal models, and prototype implementations for capability-scoped tool access: instead of a monolithic agent being allowed to “do anything,” tools are annotated with permissions, security invariants, and preconditions that are checked by an independent enforcement layer. This includes designing token- and policy-based delegation schemes for agents that call other agents or services, and formalizing how these delegation chains can be analyzed and restricted. The practical deliverables would be libraries and middleware that developers can adopt when building LLM agents in common frameworks, plus formalizations that can be published in top SE and security venues.

A third project line studies multimodal prompt injection and “AI worms” as they appear in real systems—e.g., malicious text in documents or images that an agent is instructed to process. My goal is to derive concrete sanitization strategies, provenance constraints, and runtime checks that can be implemented as systematic patterns in software, rather than case-by-case fixes after incidents.

This pillar builds on my practical experience building agentic systems for home and office automation, where I have already confronted the risk of over-permissioned agents controlling browsers, applications, and devices. It also leverages my strategic work analyzing patent landscapes around LLM hallucination, prompt injection, agent security, and federated LLMs, which confirms both the industrial relevance and the relative immaturity of current solutions.

III. Governance-Aware Software Engineering for AI-Intensive Systems

The third pillar connects technical software engineering work to AI governance and regulation—not as abstract ethics, but as executable requirements engraved into development processes and system architectures.

In my earlier work on AI regulation and governance, particularly the highly cited article “Artificial Intelligence Regulation: a framework for governance” (Ethics and Information Technology, 2021), I co-developed an integrative framework that organizes the policy-making process for AI regulation across all stages of modern public policy, from agenda setting to implementation and oversight. More recently, in “Artificial intelligence governance: understanding how public organizations implement it” (Government Information Quarterly, 2025), I co-authored an empirical study of 28 public organizations on five continents, identifying how ethical principles and governance guidelines are actually internalized—or not—in real AI development processes. These works give me a deep, grounded understanding of the gap between high-level governance principles and what happens inside organizations.

In this pillar, I aim to close that gap by treating AI governance as a software engineering problem. Research directions include:

• Governance design patterns for AI-intensive systems: translating AI governance principles (accountability, transparency, human oversight, robustness, non-discrimination) into concrete architectural and process patterns. For example, risk controls that must be attached to specific pipeline stages, mandatory human-in-the-loop checkpoints for certain tools or decisions, or traceability links between training data, model versions, and deployed services.

• Governance-aware LLM security frameworks: mapping LLM-specific threats (prompt injection, RAG poisoning, agent misuse) to regulatory obligations (e.g., under the EU AI Act or sectoral rules in health and finance) and encoding these mappings as checkable constraints in CI pipelines. The goal is for a pull request that adds a new agent or tool to be automatically analyzed for missing controls, with actionable feedback for developers and auditable records for compliance teams.

• Empirical software engineering studies of AI governance in practice: building on my prior empirical work with public organizations, I plan to study how cross-functional teams (developers, legal, risk, operations) actually coordinate around AI systems, what tools they use to track models and risks, and where failure modes arise. These studies will inform the design of both governance patterns and developer-facing tools, and provide a rich source of qualitative and quantitative data for students.

The intended outcome is a body of work that positions governance not as “someone else’s problem,” but as an integrated dimension of software engineering for AI-intensive systems.

Prior Contributions and Readiness

I am not starting this program from scratch. My prior work spans conceptual foundations, empirical governance research, large-scale patent analytics, and industrial AI deployments.

• Governance foundations: As noted above, “Artificial Intelligence Regulation: a framework for governance” proposes an integrative framework for AI regulation based on a systematic review of the AI regulation literature and the synthesis of 21 prior policy models. This work has been widely cited and used as a conceptual reference by both academics and policymakers. The more recent Government Information Quarterly article on AI governance in public organizations extends this work into empirical territory, showing how governance principles are actually implemented and where they fail.

• Patent-landscape and white-space analysis: In a recent project, I led the design and implementation of a full patent-analytics pipeline over more than a quarter-million machine-learning-related patents (2010–2025). We clustered patents into 21 emerging technology domains (including LLM hallucination detection, prompt injection defenses, AI agent security, federated LLM training, and AI governance tooling), computed “white-space scores” that combine prior-art density and market potential, and delivered dashboards and reports identifying under-served but economically important areas. This work provides a strategic map of where rigorous research and tooling in LLM security and governance are most needed and likely to have high impact, and demonstrates my ability to build and operate large data pipelines around AI innovation.

• Industrial AI systems: Over the last decade, I have built and deployed data-intensive and AI-driven systems in telecommunications, energy, healthcare, and public-sector contexts. These include real-time analytics and recommendation engines, as well as early agentic systems for automating complex workflows. These experiences anchor my research questions in realistic constraints: legacy systems, compliance requirements, data quality problems, organizational politics, and the practical need to ship robust solutions, not just proofs of concept.

Together, these contributions show that I can move fluently between conceptual frameworks, empirical observation, and concrete system building—exactly what is needed to make secure, governance-aware software engineering for LLM-intensive systems a reality.

Environment, Collaboration, and Training Plan

McGill’s ECE department is an ideal environment for this program. The existing strengths in automated program analysis and testing, software security and vulnerability detection, and cyber-physical and internet-scale systems provide both methodological depth and diverse application domains. I see natural collaborations with colleagues working on static and dynamic analysis, model-driven engineering, and intelligent systems, as well as with researchers in computer science and law who focus on machine learning, security, and technology policy. Externally, Montreal’s AI ecosystem (including Mila and industrial partners) offers rich opportunities for joint projects on trustworthy AI and LLM-intensive applications.

On the training side, my research integrates naturally with courses such as “Automated Program Analysis and Testing” and advanced software engineering topics. I plan to engage undergraduate and graduate students in building open-source benchmarks, security and governance tools, and empirical datasets that can serve both the research community and industry. Students will have the opportunity to work on projects that combine theoretical rigor, hands-on system development, and exposure to real-world stakeholders in government and industry.

Five years out, my goal is for McGill to be recognized as a leading hub for secure software engineering of LLM-intensive systems—a place where new methods for analyzing, testing, securing, and governing LLM-centric architectures are developed, evaluated, and translated into practice. The three pillars outlined above provide a coherent path toward that goal, rooted in my prior work and aligned with the department’s strengths and strategic direction.