import math
import random
import unittest

from conversation_dropoff.analysis import Turn, aggregate, detect, parse_transcript, user_turns


def rows(means, ns=None, turns=None):
    return [{'turn': k, 'n': n, 'mean_words': mean} for k,n,mean in
            zip(turns or range(1,len(means)+1), ns or [120]*len(means), means)]


class ParserTests(unittest.TestCase):
    def test_publisher_ai_label_is_not_counted_as_user_text(self):
        messages, issues = parse_transcript('Assistant: Welcome.\n\nUser: Yes.\n\nAI: Tell me more.\n\nUser: Here is my answer.\n')
        turns = user_turns('example','synthetic',messages)
        self.assertEqual([t.words for t in turns],[1,4])
        self.assertEqual([t.final for t in turns],[False,True])
        self.assertEqual(issues,[])

    def test_wrapped_response_and_apostrophe(self):
        messages,_ = parse_transcript("Assistant: Hello.\nUser: I don't\nstop here.\nAI: Thanks.")
        self.assertEqual(user_turns('x','fake',messages)[0].words,4)

    def test_unknown_prefix_rejected(self):
        with self.assertRaises(ValueError):
            parse_transcript('Unknown speaker: Hello.\nUser: A response.')

    def test_non_alternating_roles_flagged(self):
        _,issues = parse_transcript('User: One.\nUser: Two.\nAI: Thanks.')
        self.assertIn('consecutive_same_role',issues)


class DetectionTests(unittest.TestCase):
    def test_flat_and_increasing_controls(self):
        for series in [[80]*8,list(range(10,90,10)),[0]*8]:
            self.assertTrue(all(v is None for v in detect(rows(series))['methods'].values()))

    def test_known_step_decline(self):
        result=detect(rows([80,80,80,80,30,30,30]))['methods']
        self.assertTrue(all(v['turn']==5 for v in result.values()))
        self.assertAlmostEqual(result['percentage']['score'],-62.5)

    def test_positive_scale_invariance(self):
        a=detect(rows([20,40,50,30,20]))['methods']
        b=detect(rows([200,400,500,300,200]))['methods']
        for key in a:
            self.assertEqual(a[key]['turn'],b[key]['turn'])
            self.assertAlmostEqual(a[key]['score'],b[key]['score'])

    def test_sparse_and_missing_turns_are_not_bridged(self):
        result=detect(rows([80,1,30],ns=[120,5,120]))
        self.assertTrue(all(v is None for v in result['methods'].values()))
        self.assertEqual(result['excluded_turns'],[2])
        self.assertTrue(all(v is None for v in detect(rows([80,30],turns=[1,3]))['methods'].values()))

    def test_invalid_summaries_fail(self):
        for series in [rows([-1,2]),rows([math.nan,2]),rows([2,1],turns=[1,1])]:
            with self.assertRaises(ValueError):detect(series)
        with self.assertRaises(ValueError):detect(rows([1,0]),0)

    def test_noisy_flat_can_still_flag_a_turn(self):
        # A largest-change heuristic will flag random noise. It is not a classifier.
        rng=random.Random(19)
        series=[80+rng.randint(-4,4) for _ in range(12)]
        self.assertIsNotNone(detect(rows(series))['methods']['percentage'])


class AggregationTests(unittest.TestCase):
    def test_per_conversation_final_response_exclusion(self):
        ts=[Turn('a','x',1,80,False),Turn('a','x',2,1,True),
            Turn('b','x',1,80,False),Turn('b','x',2,80,False),Turn('b','x',3,1,True)]
        self.assertEqual(aggregate(ts)[1]['mean_words'],40.5)
        self.assertEqual(aggregate(ts,'exclude_final')[1]['mean_words'],80)

    def test_fixed_cohort_keeps_same_conversations(self):
        ts=[Turn('long','x',k,80,k==12) for k in range(1,13)]
        ts.extend(Turn('short','x',k,10,k==3) for k in range(1,4))
        result=aggregate(ts,'fixed_cohort_10')
        self.assertEqual(len(result),10)
        self.assertTrue(all(r['n']==1 and r['mean_words']==80 for r in result))


if __name__=='__main__':unittest.main()
