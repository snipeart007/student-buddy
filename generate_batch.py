import json
import random

def generate_sample(archetype):
    subjects_pool = {
        "Medical": ["Anatomy", "Biochemistry", "Pathology", "Pharmacology"],
        "Law": ["Constitutional Law", "Criminal Law", "Torts", "Contracts"],
        "Engineering": ["Calculus", "Thermodynamics", "Statics", "Circuit Analysis"],
        "Arts": ["Art History", "Oil Painting", "Sculpture", "Digital Media"],
        "High School": ["Algebra II", "World History", "Biology", "English Literature"],
        "CS": ["Algorithms", "Data Structures", "Operating Systems", "Networking"]
    }
    
    education_pool = {
        "Medical": "MD Program, Year 2",
        "Law": "JD Program, Year 1",
        "Engineering": "B.Sc Mechanical Engineering, Year 3",
        "Arts": "BFA in Fine Arts, Year 4",
        "High School": "Grade 11 Student",
        "CS": "B.Sc Computer Science, Year 3"
    }

    sub = subjects_pool.get(archetype, ["General Study"])
    edu = education_pool.get(archetype, "Undergraduate Student")
    
    # Randomize state
    stress = random.uniform(0.1, 0.9)
    burnout = random.uniform(0.1, 0.9)
    urgency = random.uniform(0.1, 0.9)
    
    # Logic for weights (simple baseline, will be refined by the model if I use it to generate)
    # But I can make the script "smart" enough for a first pass
    
    query_templates = [
        "I have a big exam in {sub} tomorrow and I feel like I know nothing.",
        "How can I better balance my {sub} workload with my part-time job?",
        "I'm feeling really overwhelmed by the amount of reading for {sub}.",
        "I want to improve my grades in {sub}, what study techniques do you recommend?",
        "I'm thinking of dropping {sub} because it's too hard.",
        "I haven't slept in 48 hours because of my {sub} project."
    ]
    
    query = random.choice(query_templates).format(sub=random.choice(sub))
    
    # Heuristic for weights
    m_weight = 0.5
    a_weight = 0.5
    risk = "low"
    
    if "haven't slept" in query or stress > 0.8:
        m_weight = 0.8
        a_weight = 0.2
        risk = "high"
    elif "tomorrow" in query or urgency > 0.8:
        m_weight = 0.3
        a_weight = 0.7
        risk = "medium"
        
    sample = {
        "instruction": "You are a Policy / Weighting Agent. Your role is orchestration and routing. Analyze the provided student_state and current_query to estimate severity. Assign weights to Mental Health vs Academic advice (0.0 to 1.0). Classify the interaction mode and detect escalation conditions.",
        "input": {
            "student_state": {
                "academic": {
                    "current_education": edu,
                    "current_grades": {"GPA": round(random.uniform(2.5, 4.0), 2)},
                    "subjects": sub,
                    "exams_preparing_for": [{"name": "Midterm", "date": "2023-11-15", "target_score": 85}],
                    "academic_strengths": ["Critical thinking"],
                    "academic_weaknesses": ["Time management"],
                    "education_goals": "Graduate with honors"
                },
                "mental_health": {
                    "stress_level": round(stress, 2),
                    "burnout_level": round(burnout, 2),
                    "anxiety": round(random.uniform(0.1, 0.9), 2)
                },
                "behavioral": {
                    "urgency": round(urgency, 2),
                    "panic_indicators": round(random.uniform(0.1, 0.9), 2)
                }
            },
            "current_query": query
        },
        "output": {
            "mental_weight": round(m_weight, 2),
            "academic_weight": round(a_weight, 2),
            "mode": "coaching" if risk == "low" else "intervention",
            "risk_level": risk
        }
    }
    return sample

with open("batch.jsonl", "w") as f:
    archetypes = ["Medical", "Law", "Engineering", "Arts", "High School", "CS"]
    for i in range(100):
        arch = random.choice(archetypes)
        sample = generate_sample(arch)
        f.write(json.dumps(sample) + "\n")
