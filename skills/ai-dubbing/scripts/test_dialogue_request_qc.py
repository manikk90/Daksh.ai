"""Synthetic offline REST contract tests; never voice auditions."""
import copy
import unittest

import dialogue_request_qc as qc


class DialogueRequestTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'model_id': 'eleven_v4', 'inputs': [{'text': '[softly] माता', 'voice_id': 'fixture_only'}]}

    def test_explicit_approved_model(self):
        for model in ('eleven_v3', 'eleven_v4'):
            self.payload['model_id'] = model
            self.assertEqual(qc.inspect(self.payload), [])

    def test_missing_model_does_not_silently_select_v3(self):
        del self.payload['model_id']
        self.assertIn('Pin model_id', '\n'.join(qc.inspect(self.payload)))

    def test_turbo_is_not_assumed_rest_compatible(self):
        self.payload['model_id'] = 'eleven_v4_turbo'
        self.assertTrue(qc.inspect(self.payload))

    def test_exact_text_limit_and_overflow(self):
        for size, fails in ((2000, False), (2001, True)):
            self.payload['inputs'][0]['text'] = 'म' * size
            self.assertEqual(bool(qc.inspect(self.payload)), fails)

    def test_counts_tags_and_multiple_turns(self):
        self.payload['inputs'] = [{'text': '[softly] ' + 'x' * 991, 'voice_id': 'a'},
                                  {'text': 'y' * 1001, 'voice_id': 'b'}]
        self.assertIn('2000', '\n'.join(qc.inspect(self.payload)))

    def test_voice_limit_not_turn_limit(self):
        self.payload['inputs'] *= 11
        self.assertFalse(qc.inspect(self.payload))
        self.payload['inputs'] = [{'text': 'माता', 'voice_id': f'fixture_{i}'} for i in range(10)]
        self.assertFalse(qc.inspect(self.payload))
        self.payload['inputs'].append({'text': 'माता', 'voice_id': 'fixture_11'})
        self.assertTrue(qc.inspect(self.payload))

    def test_empty_and_malformed_payloads(self):
        for payload in ([], None, {}, {'inputs': []}, {'inputs': [None]},
                        {'inputs': [{'text': 'माता', 'voice_id': None}]}):
            with self.subTest(payload=payload):
                self.assertTrue(qc.inspect(payload))

    def test_context_text_boundary(self):
        for field in ('previous_text', 'future_text'):
            self.payload[field] = 'म' * 100
            self.assertFalse(qc.inspect(self.payload))
            self.payload[field] += 'म'
            self.assertTrue(qc.inspect(self.payload))
            del self.payload[field]

    def test_context_ids_boundary(self):
        for field in ('previous_request_ids', 'next_request_ids'):
            self.payload[field] = ['fixture1', 'fixture2', 'fixture3']
            self.assertFalse(qc.inspect(self.payload))
            self.payload[field].append('fixture4')
            self.assertTrue(qc.inspect(self.payload))
            del self.payload[field]

    def test_invalid_context_types(self):
        for field, value in (('previous_text', 100), ('future_text', []), ('next_request_ids', 'id'),
                             ('previous_request_ids', [None]), ('next_request_ids', [''])):
            candidate = copy.deepcopy(self.payload)
            candidate[field] = value
            self.assertTrue(qc.inspect(candidate))

    def test_dictionary_count_boundary(self):
        self.payload['pronunciation_dictionary_locators'] = [{'id': 'fixture'}] * 3
        self.assertFalse(qc.inspect(self.payload))
        self.payload['pronunciation_dictionary_locators'].append({'id': 'fixture4'})
        self.assertTrue(qc.inspect(self.payload))

    def test_effects_and_query_format_checked_together(self):
        self.payload['audio_effects'] = {'pan': 0.1}
        self.assertTrue(qc.inspect(self.payload, 'pcm_44100'))
        self.assertFalse(qc.inspect(self.payload, 'wav_44100'))

    def test_payload_is_not_modified_or_approved(self):
        before = copy.deepcopy(self.payload)
        qc.inspect(self.payload)
        self.assertEqual(before, self.payload)


if __name__ == '__main__':
    unittest.main()
