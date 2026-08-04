import random

class ParametricGenerator:
    """Offline Parametric Question Instantiator & Anti-Repetition Engine."""

    def __init__(self):
        self.used_history = set() # Track question IDs used in recent 5 attempts

    def instantiate_question(self, q_raw):
        """Instantiates parametric variables if template contains placeholder markers."""
        q = dict(q_raw)
        
        # Check if question has parametric formula
        if "param_template" in q:
            # Example parametric boolean or numeric generator
            val_a = random.choice([0, 1])
            val_b = random.choice([0, 1])
            ans = val_a ^ val_b # XOR
            
            q["question"] = q["question"].replace("{A}", str(val_a)).replace("{B}", str(val_b))
            q["options"] = ["Output 0", "Output 1"]
            q["correct_answer"] = [0 if ans == 0 else 1]
            q["explanation"] = f"For input A={val_a}, B={val_b}, XOR operation yields {ans}."

        return q

    def filter_anti_repetition(self, questions, set_size=30):
        available = [q for q in questions if q["question_id"] not in self.used_history]
        if len(available) < set_size:
            self.used_history.clear() # Reset if database exhausted
            available = questions

        chosen = random.sample(available, min(set_size, len(available)))
        for q in chosen:
            self.used_history.add(q["question_id"])

        return chosen
