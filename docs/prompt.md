Using the attached Requirements and Technical Implementation Documents (version 1.0), implement Phase 1 of the video pipeline in Python: the Prep Module (prep_audio.py).

- Focus: Load song WAV, detect beats/onsets with LibROSA, run Rhubarb for phonemes (simulate subprocess if binary unavailable—output mock DAT), parse lyrics TXT to timed words.
- Output: JSON with beats/phonemes/timed_words; include sample parser stub for lyrics.
- Test in sandbox: Generate a mock WAV (use numpy.sin for 5s tone), run functions, print JSON.
- Make Windows 11-friendly (os.path, cross-platform paths).
- Provide full code file, unit test snippet (e.g., assert beats len >0), and run log.

Once done, confirm for Phase 2: Orchestrator + Blender stub.