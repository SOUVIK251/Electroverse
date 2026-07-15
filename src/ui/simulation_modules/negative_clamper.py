import numpy as np

class NegativeClamperSimulation:
    """Simulation module for Negative Clamper circuit."""
    
    def __init__(self, parent_scope):
        self.parent = parent_scope
        
    def get_oscilloscope_waveforms(self, time_axis):
        # Query current control parameters from the scope
        freq = self.parent.ch1_freq
        amp = self.parent.ch1_amp
        phase = self.parent.ch1_phase
        noise_lvl = self.parent.noise_lvl
        
        # CH1: Original input sine wave (no offset to avoid feedback loop)
        phi = np.radians(phase)
        ch1 = amp * np.sin(2.0 * np.pi * freq * time_axis + phi)
        if noise_lvl > 0:
            ch1 += np.random.normal(0, noise_lvl * amp * 0.4, len(time_axis))
            
        # CH2: Negative clamped output (shifted down so max peak is at 0.0V)
        ch2 = ch1 - np.max(ch1)
        
        return {
            "ch1": ch1,
            "ch2": ch2,
            "sampling_rate": 250000.0,
            "time_axis": time_axis
        }
