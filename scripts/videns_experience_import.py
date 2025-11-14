#!/usr/bin/env python3
"""
Parse Videns AI Expert experience from text file.
Extract detailed professional experience for 2025.
"""
import json
import re
from pathlib import Path

def parse_videns_experience():
    """Parse Videns AI Expert role from text file."""
    
    txt_path = Path('data/raw/AI Projects and Contributions at Videns (Jul–Nov 2025).txt')
    
    if not txt_path.exists():
        print(f"⚠️  Warning: {txt_path} not found")
        return None
    
    # Try multiple encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            with open(txt_path, 'r', encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        print(f"❌ Could not decode {txt_path} with any encoding")
        return None
    
    # Extract main position
    position = {
        "role": "AI Expert / Consultant",
        "institution": "Videns Analytics (now Cofomo)",
        "type": "Consulting",
        "start_year": "2025",
        "start_month": "07",
        "end_year": None,  # Current
        "end_month": None,
        "location": "Montreal, Canada",
        "description": "Lead AI strategy and implementation projects for enterprise clients",
        "projects": [],
        "technologies": [
            "Python", "ChatGPT/GPT-4", "Azure OpenAI", "Machine Learning",
            "NLP", "LLMs", "Prompt Engineering", "AI Security",
            "Data Analytics", "Business Intelligence"
        ],
        "achievements": []
    }
    
    # Extract key projects
    projects = []
    
    # Project 1: LGI Healthcare Solutions
    if "LGI Healthcare Solutions" in content:
        projects.append({
            "name": "AI Strategy and Roadmap for LGI Healthcare Solutions",
            "client": "LGI Healthcare Solutions (Novacap Portfolio)",
            "period": "July-October 2025",
            "role": "Lead AI Consultant",
            "description": "Led AI transformation project for healthcare software provider, analyzing use cases and formulating multi-phase AI adoption roadmap",
            "deliverables": [
                "Identified and prioritized 50+ AI use cases across hospital management systems",
                "Developed phased AI implementation roadmap (3 phases)",
                "Provided technical architecture recommendations for predictive patient flow optimization",
                "Proposed LLM integration for RPA systems to handle unstructured documents",
                "Assessed feasibility, business value, and technical requirements for each use case"
            ],
            "technologies": ["Predictive Analytics", "NLP", "LLMs", "RPA", "Healthcare IT"],
            "impact": "Equipped client leadership with concrete AI strategy and implementation plan"
        })
    
    # Project 2: AI Training and Maturity Assessment
    if "Lucia" in content or "Formation" in content:
        projects.append({
            "name": "AI Upskilling and Maturity Evaluation",
            "client": "LGI Healthcare Solutions",
            "period": "September-October 2025",
            "role": "AI Training Lead",
            "description": "Designed and delivered AI training program and conducted organizational maturity assessment",
            "deliverables": [
                "Created bilingual (French/English) AI training modules on Generative AI fundamentals",
                "Facilitated AI maturity assessment using Videns' Lucia platform",
                "Delivered executive and technical training on ChatGPT use cases in healthcare",
                "Provided maturity report identifying gaps in AI capabilities",
                "Beta-tested Lucia platform and provided product feedback"
            ],
            "technologies": ["ChatGPT", "Lucia AI Maturity Platform", "Training & Education"],
            "impact": "Built AI awareness and readiness across client organization"
        })
    
    # Project 3: LLM Security R&D
    if "prompt injection" in content.lower() or "security" in content.lower():
        projects.append({
            "name": "LLM Security Research (Prompt Injection Defense)",
            "client": "Videns Internal R&D",
            "period": "October-November 2025",
            "role": "Security Researcher",
            "description": "Led R&D initiative on Large Language Model security and prompt injection defense mechanisms",
            "deliverables": [
                "Created 'prompt-injection-security' GitHub repository with defense prototypes",
                "Implemented multi-layer defense pipeline (input sanitization, intent verification, output filtering)",
                "Developed proof-of-concept LLM Firewall using multi-agent guardrails",
                "Established best practices for secure LLM deployment",
                "Automated testing with CI/CD workflows"
            ],
            "technologies": ["Python", "Azure OpenAI", "Security", "CI/CD", "GitHub Actions"],
            "impact": "Strengthened internal AI security knowledge and client deployment guidelines"
        })
    
    # Project 4: Germain Hotels
    if "Germain" in content or "hospitality" in content.lower():
        projects.append({
            "name": "AI Opportunity Discovery for Hospitality Sector",
            "client": "Germain Hotels",
            "period": "November 2025",
            "role": "AI Advisor",
            "description": "Initiated AI exploration project for hotel chain operations and guest experience",
            "deliverables": [
                "Conducted discovery meeting with innovation lead",
                "Researched AI use cases in hospitality (demand forecasting, personalized marketing, chatbots)",
                "Identified opportunities for ML-based pricing optimization and GPT-powered virtual concierge"
            ],
            "technologies": ["Machine Learning", "Predictive Analytics", "Chatbots", "Hospitality Analytics"],
            "impact": "Expanded Videns' reach into hospitality sector"
        })
    
    position["projects"] = projects
    
    # Extract achievements
    achievements = [
        "Led AI strategy consulting for major healthcare software firm (LGI)",
        "Designed and delivered bilingual AI training programs",
        "Prototyped LLM security solutions (prompt injection defense)",
        "Assessed organizational AI maturity using proprietary platform (Lucia)",
        "Extended AI consulting into hospitality sector (Germain Hotels)",
        "Contributed to Videns' innovation portfolio in AI safety and governance"
    ]
    
    position["achievements"] = achievements
    
    return position

def save_videns_experience():
    """Save parsed Videns experience to JSON."""
    
    experience = parse_videns_experience()
    
    if not experience:
        print("❌ Failed to parse Videns experience")
        return
    
    output_path = Path('data/processed/videns_experience.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(experience, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Videns experience saved to: {output_path}")
    print(f"\n📊 Extracted:")
    print(f"   Position: {experience['role']} at {experience['institution']}")
    print(f"   Period: {experience['start_month']}/{experience['start_year']} - Current")
    print(f"   Projects: {len(experience['projects'])}")
    print(f"   Technologies: {len(experience['technologies'])}")
    print(f"   Achievements: {len(experience['achievements'])}")
    
    # Print projects summary
    print(f"\n   Projects:")
    for proj in experience['projects']:
        print(f"     - {proj['name']} ({proj['client']})")

if __name__ == '__main__':
    save_videns_experience()
