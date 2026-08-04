import numpy as np
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.figure import Figure

class AnalyticsEngine:
    """Generates analytics, topic heatmaps, radar profiles & Matplotlib performance charts."""

    @staticmethod
    def create_score_pie_chart(correct, wrong, skipped):
        fig = Figure(figsize=(3.5, 2.8), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0B1020')

        labels = ['Correct', 'Wrong', 'Skipped']
        sizes = [correct, wrong, skipped]
        colors = ['#10B981', '#EF4444', '#64748B']
        
        # Filter zero slices
        non_zero = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
        if non_zero:
            l_fn, s_fn, c_fn = zip(*non_zero)
            wedges, texts, autotexts = ax.pie(
                s_fn, labels=l_fn, colors=c_fn, autopct='%1.0f%%',
                startangle=140, textprops=dict(color='#F8FAFC', fontsize=9, fontweight='bold')
            )
            for at in autotexts:
                at.set_color('#FFFFFF')
        else:
            ax.text(0.5, 0.5, 'No Data', color='#94A3B8', ha='center', va='center')

        ax.set_title("Response Breakdown", color="#06B6D4", fontsize=10, fontweight="bold")
        return fig

    @staticmethod
    def create_topic_bar_chart(topic_analysis):
        fig = Figure(figsize=(4.5, 2.8), dpi=100)
        fig.patch.set_facecolor('#0B1020')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0F172A')

        topics = list(topic_analysis.keys())
        scores = list(topic_analysis.values())

        y_pos = np.arange(len(topics))
        bar_colors = ['#10B981' if s >= 70 else ('#F59E0B' if s >= 50 else '#EF4444') for s in scores]

        bars = ax.barh(y_pos, scores, color=bar_colors, height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(topics, color='#94A3B8', fontsize=8)
        ax.set_xlim(0, 100)
        ax.set_xlabel('Accuracy (%)', color='#94A3B8', fontsize=8)
        ax.axvline(60, color='#38BDF8', linestyle='--', alpha=0.6, label='Pass (60%)')
        ax.set_title("Topic Mastery Breakdown", color="#06B6D4", fontsize=10, fontweight="bold")
        ax.tick_params(colors='#94A3B8')
        ax.grid(True, color='#1E293B', linestyle=':', axis='x')
        fig.tight_layout()
        return fig

    @staticmethod
    def calculate_recovery_plan(weak_topics):
        recommendations = []
        total_time = 0

        for wt in weak_topics:
            mod = wt["module"]
            acc = wt["accuracy"]
            est_min = int((100 - acc) * 0.5) + 10 # Estimated time algorithm
            total_time += est_min

            recommendations.append({
                "module": mod,
                "accuracy": acc,
                "theory_lesson": f"Review Theory on '{mod}'",
                "simulation": f"Run Interactive Simulation for '{mod}'",
                "estimated_time_min": est_min
            })

        return recommendations, total_time
