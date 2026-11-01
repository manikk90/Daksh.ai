#!/usr/bin/env python3
"""Regression fixtures only: no real casting, native review or voice generation."""
import copy
import hashlib
import tempfile
import unittest
import wave
from pathlib import Path

import cue_qc as qc


class CuePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        audio = self.root / 'fixture.wav'
        with wave.open(str(audio), 'wb') as out:
            out.setnchannels(1); out.setsampwidth(2); out.setframerate(8000)
            out.writeframes(b'\0\0' * 800)
        self.data = {'project_id': 'synthetic_fixture', 'picture_version': 'pic1', 'source_version': 'src1',
                     'cues': [{'cue_id': 'a', 'character_id': 'anjana', 'language': 'Haryanvi',
                     'track_id': 'anjana', 'source_text': 'माता मेरी साँस',
                     'approved_localized_text': 'माता मेरी साँस', 'render_text': '[softly] माता... मेरी साँस',
                     'word_lock': True, 'route': 'fixture_only', 'model_id': 'eleven_v4', 'voice_id': 'fixture_only',
                     'voice_settings': {'stability': 0.5}, 'start_s': 0, 'end_s': 2,
                     'measured_duration_s': 0.1, 'approved_take_id': 'synthetic_take',
                     'audio_path': 'fixture.wav', 'audio_sha256': hashlib.sha256(audio.read_bytes()).hexdigest(),
                     'capability_evidence': {'status': 'confirmed', 'account_verified': True,
                         'checked_at': 'fixture_only', 'reference': 'synthetic_test_not_real_access'}}]}
        self.approve_fixture()

    def approve_fixture(self):
        for cue in self.data['cues']:
            cue['reviews'] = {stage: {'status': 'approved', 'fingerprint': qc.fingerprint(self.data, cue),
                                    'reviewer': 'synthetic_fixture', 'evidence_ref': 'test_only_not_real_review'}
                              for stage in qc.REVIEW_STAGES}

    def messages(self, phase='release'):
        return '\n'.join(f['message'] for f in qc.inspect(self.data, phase, self.root))

    def test_complete_metadata_is_not_audio_certificate(self):
        self.assertTrue(qc.report(self.data, 'release', self.root)['release_metadata_complete'])

    def test_empty_cues(self):
        self.data['cues'] = []
        self.assertIn('Empty cue list', self.messages())

    def test_wrong_root_schema(self):
        self.assertTrue(qc.report([])['errors'])

    def test_string_word_lock(self):
        self.data['cues'][0]['word_lock'] = 'true'
        self.assertIn('must be a boolean', self.messages())

    def test_reordered_words(self):
        self.data['cues'][0]['render_text'] = '[softly] मेरी माता साँस'
        self.assertIn('Locked spoken words', self.messages())

    def test_combining_mark_change(self):
        self.data['cues'][0]['render_text'] = '[softly] मत मेरी साँस'
        self.assertIn('Locked spoken words', self.messages())

    def test_malformed_tag(self):
        self.data['cues'][0]['render_text'] = '[softly माता मेरी साँस'
        self.assertIn('Malformed', self.messages())

    def test_non_english_tag(self):
        self.data['cues'][0]['render_text'] = '[धीरे] माता मेरी साँस'
        self.assertIn('English direction', self.messages())

    def test_setting_range(self):
        self.data['cues'][0]['voice_settings']['stability'] = 9
        self.assertIn('0 to 1', self.messages())

    def test_legacy_v4_speed(self):
        self.data['cues'][0]['voice_settings']['speed'] = 1.2
        self.assertIn('Unsupported v4', self.messages())

    def test_nonfinite_time(self):
        self.data['cues'][0]['end_s'] = float('nan')
        self.assertIn('Invalid start/end', self.messages())

    def test_overflow(self):
        self.data['cues'][0]['measured_duration_s'] = 3
        self.assertIn('exceeds slot', self.messages())

    def test_stale_tone_approval(self):
        self.data['cues'][0]['render_text'] = '[crying] माता मेरी साँस'
        self.assertIn('approval is stale', self.messages())

    def test_changed_audio_bytes(self):
        (self.root / 'fixture.wav').write_bytes(b'changed_fixture')
        self.assertIn('do not match', self.messages())

    def test_missing_file(self):
        (self.root / 'fixture.wav').unlink()
        self.assertIn('unavailable', self.messages())

    def test_review_evidence_missing(self):
        self.data['cues'][0]['reviews']['native']['evidence_ref'] = None
        self.assertIn('no reviewer/evidence', self.messages())

    def test_unverified_capability(self):
        self.data['cues'][0]['capability_evidence']['status'] = 'unverified'
        self.assertIn('has not been confirmed', self.messages())

    def test_draft_and_release_gate(self):
        self.data['cues'][0]['voice_id'] = None
        self.assertFalse(qc.report(self.data, 'draft', self.root)['errors'])
        self.assertTrue(qc.report(self.data, 'release', self.root)['errors'])

    def add_second(self):
        second = copy.deepcopy(self.data['cues'][0]); second['cue_id'] = 'b'
        self.data['cues'].append(second)
        self.approve_fixture()

    def test_same_track_overlap(self):
        self.add_second()
        self.assertIn('Unmarked same-track overlap', self.messages())

    def test_intentional_overlap(self):
        self.add_second()
        for cue in self.data['cues']: cue['overlap_group'] = 'approved_crossfade'
        self.approve_fixture()
        self.assertNotIn('Unmarked same-track overlap', self.messages())

    def test_other_language_track_is_separate(self):
        self.add_second(); self.data['cues'][1]['language'] = 'Hindi'
        self.assertNotIn('Unmarked same-track overlap', self.messages())

    def test_context_change_invalidates_dependent(self):
        self.add_second(); self.data['cues'][1]['context_ref_ids'] = ['a']
        before = qc.fingerprint(self.data, self.data['cues'][1])
        self.data['cues'][0]['render_text'] = '[tearful] माता मेरी साँस'
        self.assertNotEqual(before, qc.fingerprint(self.data, self.data['cues'][1]))

    def test_missing_context_reference(self):
        self.data['cues'][0]['context_ref_ids'] = ['missing']
        self.assertIn('existing other cues', self.messages())

    def test_duplicate_ids(self):
        self.data['cues'].append(copy.deepcopy(self.data['cues'][0]))
        self.assertIn('Duplicate cue_id', self.messages())

    def test_no_approval_minted(self):
        self.data['cues'][0]['reviews'] = {}
        before = copy.deepcopy(self.data)
        qc.report(self.data, 'release', self.root)
        self.assertEqual(self.data, before)

    def test_execution_option_change_invalidates_reviews(self):
        for field, value in {'audio_effects': {'pan': 0.2}, 'output_format': 'wav_44100',
                             'api_endpoint': '/v1/text-to-dialogue',
                             'request_options': {'use_pvc_as_ivc': True}}.items():
            with self.subTest(field=field):
                candidate = copy.deepcopy(self.data)
                candidate['cues'][0][field] = value
                self.assertTrue(any('approval is stale' in f['message'] for f in qc.inspect(candidate, 'release', self.root)))

    def test_stereo_effects_incompatible_output(self):
        for fmt in ('pcm_44100', 'ulaw_8000', 'alaw_8000'):
            with self.subTest(fmt=fmt):
                self.assertTrue(qc.effects_errors({'environment_id': 'fixture', 'send_level': 0.1}, fmt))
                self.assertTrue(qc.effects_errors({'pan': -0.2}, fmt))

    def test_dry_pcm_and_centered_pan_allowed(self):
        self.assertFalse(qc.effects_errors(None, 'pcm_44100'))
        self.assertFalse(qc.effects_errors({'environment_id': 'fixture', 'send_level': 0, 'pan': 0}, 'pcm_44100'))

    def test_stereo_wav_mp3_not_blocked(self):
        for fmt in ('wav_44100', 'mp3_44100_128'):
            self.assertFalse(qc.effects_errors({'pan': 0.4}, fmt))

    def test_effects_schema_and_nonfinite_values(self):
        for value in ([], 'reverb', {'pan': True}, {'send_level': float('nan')}, {'pan': '0'}):
            with self.subTest(value=value):
                self.assertTrue(qc.effects_errors(value))

    def test_manifest_effects_gate(self):
        self.data['cues'][0].update(audio_effects={'pan': 0.4}, output_format='pcm_44100')
        self.assertIn('incompatible', self.messages('draft'))


if __name__ == '__main__':
    unittest.main()
