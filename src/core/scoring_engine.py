class ScoringEngine:
    """Computes exam score, accuracy, negative marking, and grades."""
    
    def __init__(self, correct_marks=1.0, negative_marks=0.25, enable_negative=True, pass_pct=60.0):
        self.correct_marks = correct_marks
        self.negative_marks = negative_marks if enable_negative else 0.0
        self.pass_pct = pass_pct

    def evaluate_exam(self, questions, user_answers, time_taken_sec=0):
        total_questions = len(questions)
        correct_count = 0
        wrong_count = 0
        skipped_count = 0

        topic_stats = {} # module -> {"correct": 0, "total": 0}
        bloom_stats = {} # bloom -> {"correct": 0, "total": 0}
        detailed_eval = []

        for q in questions:
            q_id = q["question_id"]
            mod = q.get("module", "General")
            bloom = q.get("bloom_level", "Understand")

            if mod not in topic_stats: topic_stats[mod] = {"correct": 0, "total": 0}
            if bloom not in bloom_stats: bloom_stats[bloom] = {"correct": 0, "total": 0}
            
            topic_stats[mod]["total"] += 1
            bloom_stats[bloom]["total"] += 1

            user_ans = user_answers.get(q_id, None)
            correct_ans = q.get("correct_answer", [])

            is_correct = False
            is_skipped = (user_ans is None or user_ans == [] or user_ans == "")

            if not is_skipped:
                if isinstance(user_ans, list) and isinstance(correct_ans, list):
                    is_correct = (sorted(user_ans) == sorted(correct_ans))
                else:
                    is_correct = (str(user_ans).strip().lower() == str(correct_ans[0]).strip().lower() if correct_ans else False)

            if is_skipped:
                skipped_count += 1
                status = "SKIPPED"
            elif is_correct:
                correct_count += 1
                topic_stats[mod]["correct"] += 1
                bloom_stats[bloom]["correct"] += 1
                status = "CORRECT"
            else:
                wrong_count += 1
                status = "WRONG"

            detailed_eval.append({
                "question_id": q_id,
                "question": q.get("question", ""),
                "user_answer": user_ans,
                "correct_answer": correct_ans,
                "status": status,
                "explanation": q.get("explanation", ""),
                "formula": q.get("formula", ""),
                "module": mod,
                "bloom": bloom,
                "reference_topic": q.get("reference_topic", ""),
                "simulation_link": q.get("simulation_link", "")
            })

        max_possible_score = total_questions * self.correct_marks
        raw_score = (correct_count * self.correct_marks) - (wrong_count * self.negative_marks)
        raw_score = max(0.0, raw_score) # floor at 0

        pct = (raw_score / max_possible_score * 100.0) if max_possible_score > 0 else 0.0

        if pct >= 90: grade = "A+"
        elif pct >= 80: grade = "A"
        elif pct >= 70: grade = "B"
        elif pct >= 60: grade = "C"
        else: grade = "F"

        is_passed = (pct >= self.pass_pct)

        # Topic Breakdown Accuracy
        topic_analysis = {}
        weak_topics = []
        for mod, st in topic_stats.items():
            t_pct = (st["correct"] / st["total"] * 100.0) if st["total"] > 0 else 0.0
            topic_analysis[mod] = round(t_pct, 1)
            if t_pct < 70.0:
                weak_topics.append({"module": mod, "accuracy": round(t_pct, 1)})

        return {
            "total_questions": total_questions,
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "skipped_count": skipped_count,
            "max_score": max_possible_score,
            "raw_score": round(raw_score, 2),
            "percentage": round(pct, 1),
            "grade": grade,
            "is_passed": is_passed,
            "time_taken_sec": time_taken_sec,
            "topic_analysis": topic_analysis,
            "bloom_analysis": bloom_stats,
            "weak_topics": weak_topics,
            "detailed_eval": detailed_eval
        }
