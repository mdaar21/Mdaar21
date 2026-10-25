import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('engine', Path(__file__).resolve().parents[1] / 'scripts/engine.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Engine = module.Engine


class ConsensusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.roster = self.root / 'experts.json'
        self.roster.write_text(json.dumps([{'id':f'e{i}', 'council':f'c{i//5}', 'role':f'r{i}', 'personality':'skeptical', 'criteria':['check']} for i in range(50)]))
        self.engine = Engine(self.root / 'project', self.roster)
        self.engine.init('Review a concrete artifact')
        self.artifact = self.root / 'solution.txt'; self.artifact.write_text('v1')
        self.proof = self.root / 'proof.txt'; self.proof.write_text('test log')
        self.engine.mutate('snapshot', {'version':'v1', 'files':[str(self.artifact)]})
        self.engine.mutate('evidence', {'id':'proof','file':str(self.proof),'description':'Observed test execution'})

    def register(self, i=0):
        self.engine.mutate('register', {'expert':f'e{i}', 'runtime':f'actual-runtime-{i}'})

    def vote(self, i=0, decision='APPROVE', evidence=None, **kwargs):
        current = self.engine.state(self.engine.load())['current']
        return self.engine.mutate('vote', dict(version=current['version'], digest=current['digest'], expert=f'e{i}', decision=decision, reason='Inspected artifact and measured result', evidence=['proof'] if evidence is None else evidence, **kwargs))

    def approve_all(self):
        for i in range(50): self.register(i); self.vote(i)
        for stage in module.STAGES: self.engine.mutate('stage', {'name':stage,'evidence':['proof']})

    def test_initial_state_pending_not_silent_approval(self):
        r = self.engine.report()
        self.assertEqual(r['Consensus Status'], 'PENDING')
        self.assertEqual(r['Experts Approved'], '0/50')
        self.assertEqual(len(r['Experts Missing']), 50)

    def test_unregistered_or_unknown_expert_cannot_vote(self):
        with self.assertRaisesRegex(ValueError, 'registered'): self.vote()
        with self.assertRaises(ValueError): self.engine.mutate('register', {'expert':'fake','runtime':'foo'})

    def test_runtime_unique_and_nonempty(self):
        self.register()
        with self.assertRaisesRegex(ValueError,'unique'): self.engine.mutate('register', {'expert':'e1','runtime':'actual-runtime-0'})
        with self.assertRaisesRegex(ValueError,'nonempty'): self.engine.mutate('register', {'expert':'e1','runtime':'  '})
        with self.assertRaises(ValueError): self.register()

    def test_approval_requires_actual_unchanged_evidence(self):
        self.register()
        with self.assertRaises(ValueError): self.vote(evidence=[])
        with self.assertRaises(ValueError): self.vote(evidence=['invented'])
        self.proof.write_text('altered')
        with self.assertRaises(ValueError): self.vote()

    def test_rejection_and_abstention_are_recorded(self):
        self.register(); self.vote(decision='REJECT',evidence=[])
        self.assertEqual(self.engine.report()['Consensus Status'],'BLOCKED')
        self.register(1); self.vote(1,decision='ABSTAIN',evidence=[])
        self.assertEqual(self.engine.report()['Experts Abstained'],['e1'])

    def test_vote_change_requires_reason(self):
        self.register(); self.vote(decision='REJECT')
        with self.assertRaises(ValueError): self.vote()
        with self.assertRaises(ValueError): self.vote(change_code='GROUP_PRESSURE',change_reason='others agree')
        self.vote(change_code='EVALUATION_ERROR',change_reason='Rechecked calculation and corrected error')
        self.assertEqual(len(self.engine.report()['Changed Votes']),1)
        self.assertEqual(len(self.engine.load()['events']),6)

    def test_only_fifty_approvals_and_stages_approve(self):
        for i in range(50): self.register(i); self.vote(i)
        self.assertEqual(self.engine.report()['Consensus Status'],'PENDING')
        for stage in module.STAGES: self.engine.mutate('stage', {'name':stage,'evidence':['proof']})
        self.assertEqual(self.engine.report()['Consensus Status'],'APPROVED')

    def test_new_version_discards_old_consensus(self):
        self.approve_all()
        self.artifact.write_text('v2')
        self.engine.mutate('snapshot', {'version':'v2','files':[str(self.artifact)]})
        r=self.engine.report()
        self.assertEqual(r['Experts Approved'],'0/50')
        self.assertEqual(r['Consensus Status'],'PENDING')
        with self.assertRaises(ValueError): self.vote()
        self.vote(change_code='SOLUTION_CHANGED',change_reason='Independently reviewed new implementation')
        self.assertEqual(self.engine.report()['Experts Approved'],'1/50')

    def test_stale_import_and_missing_version_rejected(self):
        self.register()
        old = self.engine.state(self.engine.load())['current']
        self.artifact.write_text('v2')
        self.engine.mutate('snapshot', {'version':'v2','files':[str(self.artifact)]})
        payload = dict(expert='e0', decision='APPROVE', reason='Reviewed earlier snapshot', evidence=['proof'])
        with self.assertRaisesRegex(ValueError,'version and digest'):
            self.engine.mutate('vote',payload)
        with self.assertRaisesRegex(ValueError,'version and digest'):
            self.engine.mutate('vote',dict(payload,version=old['version'],digest=old['digest']))
        current = self.engine.state(self.engine.load())['current']
        with self.assertRaisesRegex(ValueError,'version and digest'):
            self.engine.mutate('vote',dict(payload,version=current['version'],digest=old['digest']))
        self.assertEqual(self.engine.report()['Experts Approved'],'0/50')

    def test_snapshot_version_immutable(self):
        with self.assertRaises(ValueError): self.engine.mutate('snapshot', {'version':'v1','files':[str(self.artifact)]})

    def test_artifact_tamper_blocks_consensus(self):
        self.approve_all(); self.artifact.write_text('changed after review')
        r=self.engine.report()
        self.assertEqual(r['Consensus Status'],'BLOCKED')
        self.assertEqual(r['Changed Artifacts'],[str(self.artifact)])

    def test_evidence_tamper_blocks_consensus(self):
        self.approve_all(); self.proof.unlink()
        self.assertEqual(self.engine.report()['Consensus Status'],'BLOCKED')
        self.assertEqual(self.engine.report()['Experts Approved'],'0/50')

    def test_objection_resolution_requires_evidence(self):
        self.approve_all()
        self.engine.mutate('objection', {'id':'bug','expert':'e0','severity':'HIGH','reason':'Mismatch found','evidence':['proof']})
        self.assertEqual(self.engine.report()['Consensus Status'],'BLOCKED')
        with self.assertRaises(ValueError): self.engine.mutate('resolve', {'id':'bug','reason':'fixed','evidence':[]})
        self.engine.mutate('resolve', {'id':'bug','reason':'Reproduced and verified fix','evidence':['proof']})
        report=self.engine.report()
        self.assertEqual(report['Consensus Status'],'PENDING')
        self.assertEqual(report['Experts Approved'],'0/50')
        self.assertEqual(len(report['Experts Outdated']),50)
        for i in range(49): self.vote(i)
        self.assertEqual(self.engine.report()['Consensus Status'],'PENDING')
        self.assertEqual(self.engine.report()['Experts Approved'],'49/50')
        self.vote(49)
        self.assertEqual(self.engine.report()['Consensus Status'],'APPROVED')

    def test_unused_historical_evidence_does_not_block_new_version(self):
        self.approve_all()
        old_proof = self.proof
        self.artifact.write_text('v2')
        self.engine.mutate('snapshot', {'version':'v2','files':[str(self.artifact)]})
        self.proof = self.root / 'v2-proof.txt'; self.proof.write_text('new executed checks')
        self.engine.mutate('evidence', {'id':'v2-proof','file':str(self.proof),'description':'v2 test log'})
        for i in range(50):
            self.vote(i,evidence=['v2-proof'],change_code='SOLUTION_CHANGED',change_reason='Reviewed v2 independently')
        for stage in module.STAGES:
            self.engine.mutate('stage', {'name':stage,'evidence':['v2-proof']})
        old_proof.unlink()
        report=self.engine.report()
        self.assertEqual(report['Consensus Status'],'APPROVED')
        self.assertEqual(report['Invalid Evidence'],[])
        self.assertEqual(report['Historical Invalid Evidence'],['proof'])

    def test_objection_event_invalidates_votes_even_if_voted_before_resolution(self):
        self.approve_all()
        self.engine.mutate('objection', {'id':'bug','expert':'e0','severity':'LOW','reason':'New finding','evidence':['proof']})
        self.assertEqual(self.engine.report()['Experts Approved'],'0/50')
        for i in range(50): self.vote(i)
        self.assertEqual(self.engine.report()['Consensus Status'],'BLOCKED')
        self.engine.mutate('resolve', {'id':'bug','reason':'Verified resolution','evidence':['proof']})
        self.assertEqual(self.engine.report()['Experts Approved'],'0/50')
        self.assertEqual(self.engine.report()['Consensus Status'],'PENDING')

    def test_assignment_packets_hide_peer_reviews(self):
        self.register(); self.vote(decision='REJECT')
        out=self.root/'packets'; self.engine.assign(out)
        self.assertEqual(len(list(out.glob('*.json'))),50)
        packet=json.loads((out/'e0.json').read_text())
        self.assertNotIn('votes',packet); self.assertNotIn('runtimes',packet)
        self.assertEqual(packet['expert']['id'],'e0')
        self.assertEqual(packet['evidence_catalog'][0]['id'],'proof')

    def test_roster_mutation_detected(self):
        self.roster.write_text(self.roster.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'Roster changed'): self.engine.report()

    def test_event_mutation_detected(self):
        data=json.loads(self.engine.path.read_text())
        data['events'][0]['payload']['task']='rewrite'
        self.engine.path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'integrity'): self.engine.report()

    def test_missing_artifact_blocks_and_unknown_stage_rejected(self):
        self.artifact.unlink()
        self.assertEqual(self.engine.report()['Consensus Status'],'BLOCKED')
        with self.assertRaises(ValueError): self.engine.mutate('stage', {'name':'invented','evidence':['proof']})


if __name__ == '__main__': unittest.main()
