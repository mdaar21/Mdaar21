#!/usr/bin/env python3
"""Elite50 local audit ledger. Runtime identities are trusted operator attestations.
File hashes protect consistency, not identity authenticity or hostile local edits.
"""
import argparse
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile

DECISIONS = {'APPROVE', 'REJECT', 'NEEDS_EVIDENCE', 'ABSTAIN'}
CHANGE_CODES = {'NEW_EVIDENCE', 'EVALUATION_ERROR', 'SOLUTION_CHANGED', 'TEST_PASSED', 'NEW_RISK'}
STAGES = {'testing', 'devils-advocate', 'red-team', 'evidence-verification', 'performance-comparison', 'final-audit'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def required(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be nonempty')
    return value.strip()


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix='.elite50-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class Engine:
    def __init__(self, project, roster=None):
        self.root = Path(project).resolve()
        self.path = self.root / 'elite50-state.json'
        self.roster_path = Path(roster or Path(__file__).resolve().parent.parent / 'references/experts.json')
        self.roster = json.loads(self.roster_path.read_text())
        if len(self.roster) != 50 or len({x['id'] for x in self.roster}) != 50:
            raise ValueError('Roster must contain exactly 50 unique experts')
        self.ids = {x['id'] for x in self.roster}

    @contextlib.contextmanager
    def lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / '.elite50.lock').open('a') as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def load(self):
        data = json.loads(self.path.read_text())
        if data['roster_sha256'] != digest(self.roster_path):
            raise ValueError('Roster changed since initialization')
        previous = None
        for index, event in enumerate(data['events']):
            payload = {k: v for k, v in event.items() if k != 'event_hash'}
            actual = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            if event['seq'] != index + 1 or event['previous_hash'] != previous or event['event_hash'] != actual:
                raise ValueError('Ledger integrity failure')
            previous = actual
        return data

    def append(self, data, kind, payload):
        events = data['events']
        event = dict(seq=len(events) + 1, timestamp=now(), kind=kind, payload=payload,
                     previous_hash=events[-1]['event_hash'] if events else None)
        event['event_hash'] = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
        events.append(event)
        atomic_json(self.path, data)
        return event

    def init(self, task):
        with self.lock():
            if self.path.exists():
                raise ValueError('Project already initialized')
            data = {'schema': 1, 'roster_sha256': digest(self.roster_path), 'events': []}
            return self.append(data, 'init', {'task': required(task, 'task')})

    @staticmethod
    def state(data):
        state = dict(task='', current=None, snapshots={}, evidence={}, runtimes={}, votes=[], objections={}, stages={})
        for event in data['events']:
            p, kind = event['payload'], event['kind']
            if kind == 'init': state['task'] = p['task']
            elif kind == 'snapshot':
                state['snapshots'][p['version']] = p
                state['current'] = p
            elif kind == 'evidence': state['evidence'][p['id']] = p
            elif kind == 'register': state['runtimes'][p['expert']] = p['runtime']
            elif kind == 'vote': state['votes'].append(dict(p, timestamp=event['timestamp'], seq=event['seq']))
            elif kind == 'objection': state['objections'][p['id']] = dict(p, resolved=False)
            elif kind == 'resolve': state['objections'][p['id']].update(resolved=True, resolution=p)
            elif kind == 'stage': state['stages'][(p['version'], p['name'])] = p
        return state

    @staticmethod
    def valid_file(record):
        try: return digest(record['path']) == record['sha256']
        except OSError: return False

    def evidence_ok(self, state, ids, require=True):
        if require and not ids: raise ValueError('Evidence required')
        for item in ids:
            if item not in state['evidence'] or not self.valid_file(state['evidence'][item]):
                raise ValueError('Missing or changed evidence: ' + item)

    def mutate(self, kind, payload):
        with self.lock():
            data = self.load()
            s = self.state(data)
            p = dict(payload)
            if kind == 'snapshot':
                version = required(p['version'], 'version')
                if version in s['snapshots']: raise ValueError('Version is immutable; use a new version')
                files = sorted({str(Path(f).resolve()) for f in p.pop('files')})
                if not files: raise ValueError('Explicit solution files required')
                records = [{'path': f, 'sha256': digest(f)} for f in files]
                p.update(version=version, files=records, digest=hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest())
            elif kind == 'evidence':
                required(p['id'], 'id'); required(p['description'], 'description')
                if p['id'] in s['evidence']: raise ValueError('Evidence IDs are immutable')
                path = str(Path(p.pop('file')).resolve())
                p.update(path=path, sha256=digest(path))
            elif kind == 'register':
                if p['expert'] not in self.ids: raise ValueError('Unknown expert')
                runtime = required(p['runtime'], 'runtime')
                if p['expert'] in s['runtimes']: raise ValueError('Expert already registered')
                if runtime in s['runtimes'].values(): raise ValueError('Runtime must be unique per expert')
                p['runtime'] = runtime
                p['identity_basis'] = 'trusted-operator-attestation'
            else:
                if not s['current']: raise ValueError('Snapshot required')
                if kind == 'vote':
                    if p.get('version') != s['current']['version'] or p.get('digest') != s['current']['digest']:
                        raise ValueError('Reviewer version and digest must match current snapshot')
                else:
                    p.update(version=s['current']['version'], digest=s['current']['digest'])
                if kind in {'vote', 'objection'}:
                    if p['expert'] not in self.ids or p['expert'] not in s['runtimes']:
                        raise ValueError('Expert requires registered independent runtime')
                    p['runtime'] = s['runtimes'][p['expert']]
                    required(p['reason'], 'reason')
                if kind == 'vote':
                    if p['decision'] not in DECISIONS: raise ValueError('Invalid decision')
                    self.evidence_ok(s, p.get('evidence', []), p['decision'] == 'APPROVE')
                    prior = next((v for v in reversed(s['votes']) if v['expert'] == p['expert']), None)
                    changed = prior and (prior['decision'] != p['decision'] or prior['version'] != p['version'])
                    if changed and (p.get('change_code') not in CHANGE_CODES or not (p.get('change_reason') or '').strip()):
                        raise ValueError('Vote/version change requires accepted code and explanation')
                    if p.get('change_code') and p['change_code'] not in CHANGE_CODES: raise ValueError('Invalid change code')
                elif kind == 'objection':
                    required(p['id'], 'id')
                    if p['id'] in s['objections']: raise ValueError('Duplicate objection')
                    if p['severity'] not in {'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'}: raise ValueError('Invalid severity')
                    self.evidence_ok(s, p.get('evidence', []))
                elif kind == 'resolve':
                    if p['id'] not in s['objections'] or s['objections'][p['id']]['resolved']: raise ValueError('No open objection')
                    required(p['reason'], 'reason'); self.evidence_ok(s, p.get('evidence', []))
                elif kind == 'stage':
                    if p['name'] not in STAGES: raise ValueError('Unknown stage')
                    self.evidence_ok(s, p.get('evidence', []))
                else: raise ValueError('Unknown event kind')
            return self.append(data, kind, p)

    def assign(self, output):
        with self.lock():
            s = self.state(self.load())
            if not s['current']: raise ValueError('Snapshot required')
            output = Path(output)
            output.mkdir(parents=True, exist_ok=True)
            for expert in self.roster:
                packet = {'expert': expert, 'task': s['task'], 'solution': s['current'],
                          'evidence_catalog': list(s['evidence'].values()),
                          'instructions': 'Evaluate independently using your criteria. Do not read other initial reviews or votes. Return decision, concrete reasons, inspected evidence, and tests. Never invent evidence. Register actual independent runtime before recording votes.'}
                atomic_json(output / (expert['id'] + '.json'), packet)
            return {'packets': 50, 'output': str(output.resolve())}

    def report(self):
        with self.lock():
            data = self.load(); s = self.state(data); current = s['current']
            latest = {}
            for vote in s['votes']:
                if current and vote['version'] == current['version'] and vote['digest'] == current['digest']:
                    latest[vote['expert']] = vote
            # New objections and their resolution invalidate earlier approvals; only
            # actual fresh reviewer events can restore unanimous consensus.
            freshness_cutoff = max((e['seq'] for e in data['events'] if e['kind'] in {'objection', 'resolve'}), default=0)
            outdated = sorted(k for k, v in latest.items() if v['seq'] <= freshness_cutoff)
            all_current_votes = dict(latest)
            latest = {k: v for k, v in latest.items() if v['seq'] > freshness_cutoff}
            open_objections = [v for v in s['objections'].values() if not v['resolved']]
            active_evidence = set()
            for vote in all_current_votes.values():
                active_evidence.update(vote['evidence'])
            for (version, _), rec in s['stages'].items():
                if current and version == current['version']:
                    active_evidence.update(rec['evidence'])
            for objection in s['objections'].values():
                if not objection['resolved']:
                    active_evidence.update(objection['evidence'])
                elif current and objection['resolution']['version'] == current['version']:
                    active_evidence.update(objection['resolution']['evidence'])
            all_invalid = {k for k, v in s['evidence'].items() if not self.valid_file(v)}
            invalid_evidence = sorted(all_invalid & active_evidence)
            historical_invalid = sorted(all_invalid - active_evidence)
            invalid_artifacts = [f['path'] for f in current['files'] if not self.valid_file(f)] if current else []
            valid_approvals = []
            for expert, v in latest.items():
                if v['decision'] == 'APPROVE' and v['evidence'] and not set(v['evidence']) & set(invalid_evidence):
                    valid_approvals.append(expert)
            missing_stages = sorted(STAGES - {name for (version, name), rec in s['stages'].items()
                                      if current and version == current['version'] and not set(rec['evidence']) & set(invalid_evidence)})
            rejected = [k for k,v in latest.items() if v['decision'] == 'REJECT']
            approved = len(valid_approvals) == 50 and not open_objections and not invalid_artifacts and not invalid_evidence and not missing_stages
            status = 'APPROVED' if approved else 'BLOCKED' if rejected or open_objections or invalid_artifacts or invalid_evidence else 'PENDING'
            changes = [v for v in s['votes'] if v.get('change_code')]
            return {'title': 'THE ELITE 50 — FINAL REPORT', 'Task': s['task'],
                    'Participating Councils': sorted({x['council'] for x in self.roster if x['id'] in latest}),
                    'Solution Version': current['version'] if current else None,
                    'Solution Digest': current['digest'] if current else None,
                    'Experts Approved': f'{len(valid_approvals)}/50', 'Experts Rejected': rejected,
                    'Experts Requiring Evidence': [k for k,v in latest.items() if v['decision'] == 'NEEDS_EVIDENCE'],
                    'Experts Abstained': [k for k,v in latest.items() if v['decision'] == 'ABSTAIN'],
                    'Experts Missing': sorted(self.ids - all_current_votes.keys()),
                    'Experts Outdated': outdated, 'Fresh Votes Required After Event': freshness_cutoff,
                    'Changed Votes': changes, 'Reasons for Vote Changes': [v['change_reason'] for v in changes],
                    'Tests Executed': [p for (v,n),p in s['stages'].items() if current and v == current['version'] and n == 'testing'],
                    'Open Objections': open_objections, 'Missing Stages': missing_stages,
                    'Invalid Evidence': invalid_evidence, 'Historical Invalid Evidence': historical_invalid,
                    'Changed Artifacts': invalid_artifacts,
                    'Remaining Risks': ['Runtime identities are operator attestations, not cryptographic authentication.',
                                        'Local ledger hashes detect accidental edits; a privileged writer can rewrite history.',
                                        'Evidence content and domain correctness require actual expert review.'],
                    'Consensus Status': status, 'Final Decision': 'Deliver approved solution' if approved else 'Deliver available results with unresolved conditions',
                    'Audit Events': len(data['events']), 'Audit Head': data['events'][-1]['event_hash']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ['init', 'snapshot', 'evidence', 'register', 'assign', 'vote', 'objection', 'resolve', 'stage', 'report']:
        p = sub.add_parser(name); p.add_argument('--project', required=True)
        if name == 'init': p.add_argument('--task', required=True)
        if name == 'snapshot': p.add_argument('--version', required=True); p.add_argument('--files', nargs='+', required=True)
        if name == 'evidence':
            for f in ['id', 'file', 'description']: p.add_argument('--'+f, required=True)
        if name == 'register': p.add_argument('--expert', required=True); p.add_argument('--runtime', required=True)
        if name in ['assign', 'report']: p.add_argument('--output', required=name == 'assign')
        if name in ['vote', 'objection']: p.add_argument('--expert', required=True)
        if name in ['vote', 'objection', 'resolve']: p.add_argument('--reason', required=True)
        if name in ['vote', 'objection', 'resolve', 'stage']: p.add_argument('--evidence', nargs='*', default=[])
        if name == 'vote':
            p.add_argument('--version', required=True)
            p.add_argument('--digest', required=True)
            p.add_argument('--decision', choices=sorted(DECISIONS), required=True)
            p.add_argument('--change-code', choices=sorted(CHANGE_CODES)); p.add_argument('--change-reason')
        if name in ['objection', 'resolve']: p.add_argument('--id', required=True)
        if name == 'objection': p.add_argument('--severity', choices=['LOW','MEDIUM','HIGH','CRITICAL'], required=True)
        if name == 'stage': p.add_argument('--name', choices=sorted(STAGES), required=True)
    a = vars(parser.parse_args()); command = a.pop('command'); engine = Engine(a.pop('project'))
    try:
        if command == 'init': result = engine.init(**a)
        elif command == 'assign': result = engine.assign(**a)
        elif command == 'report':
            result = engine.report()
            if a['output']: atomic_json(a['output'], result)
        else: result = engine.mutate(command, a)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, str(error)+'\n')

if __name__ == '__main__': main()
