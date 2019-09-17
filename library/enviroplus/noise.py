import sounddevice
import numpy
import math

class Noise():
    def __init__(
        self,
        sample_rate=16000,
        duration=0.5):

        self.duration = duration
        self.sample_rate = sample_rate

    def get_amplitudes_at_frequency_ranges(self, ranges):
        recording = self._record()
        magnitude = numpy.abs(numpy.fft.rfft(recording[:, 0], n=self.sample_rate))
        result = []
        for r in ranges:
            start, end = r
            result.append(numpy.mean(magnitude[start:end]))
        return result

    def get_amplitude_at_frequency_range(self, start, end):
        n = self.sample_rate // 2
        if start > n or end > n:
            raise ValueError("Maxmimum frequency is {}".format(n))

        recording = self._record()
        magnitude = numpy.abs(numpy.fft.rfft(recording[:, 0], n=self.sample_rate))
        return numpy.mean(magnitude[start:end])

    def get_noise_profile(
        self,
        noise_floor=100,
        low=0.12,
        mid=0.36,
        high=None):

        if high is None:
            high = 1.0 - low - mid

        recording = self._record()
        magnitude = numpy.abs(numpy.fft.rfft(recording[:, 0], n=self.sample_rate))

        sample_count = (self.sample_rate // 2) - noise_floor

        mid_start = noise_floor + int(sample_count * low)
        high_start = mid_start + int(sample_count * mid)
        noise_ceiling = high_start + int(sample_count * high)

        amp_low = numpy.mean(magnitude[self.noise_floor:mid_start])
        amp_mid = numpy.mean(magnitude[mid_start:high_start])
        amp_high = numpy.mean(magnitude[high_start:noise_ceiling])
        amp_total = (low + mid + high) / 3.0

        return amp_low, amp_mid, amp_high, amp_total

    def _record(self):
        return sounddevice.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            blocking=True,
            channels=1,
            dtype='float64'
        )

