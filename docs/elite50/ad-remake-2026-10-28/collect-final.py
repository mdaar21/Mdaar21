"""Import fifty actual preserved final responses through the ledger CLI.

This script does not generate, edit, translate or override reviewer decisions.
Run once after the actual host contexts finish; it verifies the frozen files.
"""
from pathlib import Path
import collections
import hashlib
import json
import subprocess

PROJECT=Path(__file__).resolve().parent
ROOT=PROJECT.parents[2]
ENGINE=ROOT/'.agents/skills/elite50/scripts/engine.py'
VIDEO=ROOT/'creative/voice-ad-premium-v12'
def run(*args):
    result=subprocess.run(['python',str(ENGINE),*args,'--project',str(PROJECT)],capture_output=True,text=True,check=True)
    return json.loads(result.stdout)
def evidence(eid,path,description):
    return run('evidence','--id',eid,'--file',str(path),'--description',description)

candidate=json.loads((PROJECT/'candidate.json').read_text())
roster=json.loads((ROOT/'.agents/skills/elite50/references/experts.json').read_text())
identities=json.loads((PROJECT/'runtime-assignments.json').read_text())
assert len(identities)==len({x[0] for x in identities})==len({x[1] for x in identities})==50
assert {x[0] for x in identities}=={x['id'] for x in roster}
assert all(hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()==f['sha256'] for f in candidate['files'])
responses=[]
for item in roster:
    path=PROJECT/'reviews'/(item['id']+'.json')
    data=json.loads(path.read_text())
    assert data['expert']==item['id']
    assert data['version']==candidate['version'] and data['digest']==candidate['digest']
    assert data['decision'] in ['APPROVE','REJECT','NEEDS_EVIDENCE','ABSTAIN']
    assert isinstance(data['reason'],str) and data['reason'].strip()
    responses.append((path,data))
assert len(responses)==50

for eid,path,description in [
    ('frozen-candidate',PROJECT/'candidate.json','Exact frozen media, source and player files; all hashes rechecked'),
    ('actual-runtimes',PROJECT/'runtime-assignments.json','Fifty distinct actual host-returned reviewer context names, one per roster identity'),
    ('final-task',PROJECT/'final-packet.json','Shared independent final task, frozen version, criteria and capability limits'),
    ('claim-map',PROJECT/'evidence/claim-map.json','Owner price and product claim to source mapping'),
    *[('actual-'+f.replace('.','-'),VIDEO/'reports'/f,'Executed check record or actual inspected artifact, not a proposed test') for f in [
        'check-final.json','source-browser.json','encoded-validation.json','player-browser.json','live-verification.json',
        'motion-playback.json','audio-edit.json','voice-separation.json','edited-asr.json','book-links.json',
        'encoded-contact.jpg','encoded-handoffs.jpg']],
]:
    evidence(eid,path,description)
for path,data in responses:
    evidence('review-'+data['expert'],path,'Unmodified actual independent expert final response, decision, reasons and limitations')

# Preserve the actual unresolved objection instead of treating missing audition
# as a defect proven by waveform/ASR, or fabricating unanimous approval.
run('objection','--id','perceptual-audio-verification','--expert','marketing-4','--severity','MEDIUM',
    '--reason','Natural narration, speech/caption correspondence and absence of audible residual source background have no human listening evidence. This is an evidence gap, not an observed finding that the track sounds poor.',
    '--evidence','review-marketing-4','review-research-2','actual-audio-edit-json','actual-voice-separation-json')

counts=collections.Counter(data['decision'] for _,data in responses)
by_council={}
for item in roster:
    data=next(d for _,d in responses if d['expert']==item['id'])
    row=by_council.setdefault(item['council'],collections.Counter())
    row[data['decision']]+=1
summary={'version':candidate['version'],'digest':candidate['digest'],'participants':50,'actualIndependentContexts':50,
         'decisions':dict(counts),'councils':{k:dict(v) for k,v in by_council.items()},
         'frozenFiles':len(candidate['files']),'frozenFileHashesUnchanged':True,
         'meaning':'Production review decisions with stated scope; not human audition, legal certification or measured audience effectiveness.',
         'rows':[{'expert':d['expert'],'decision':d['decision'],'score':d.get('score'),'reason':d['reason']} for _,d in responses]}
(PROJECT/'decision-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
evidence('decision-summary',PROJECT/'decision-summary.json','Arithmetic from fifty actual reviewer responses; no simulated or changed verdicts')
audit={'version':candidate['version'],'digest':candidate['digest'],'frozenFiles':len(candidate['files']),
       'allFrozenHashesMatch':True,'registeredActualDistinctHostContexts':50,'independentResponses':50,
       'allTenCouncilsParticipated':len(by_council)==10,'allResponseVersionsAndDigestsMatch':True,
       'decisions':dict(counts),'votesChanged':0,'votesCoerced':False,'sourceChangedDuringVoting':False,
       'openCondition':'Human listening evidence remains unavailable. Deliver usable revised ad with explicit incomplete approval status.',
       'identityLimits':'Runtime names are trusted coordinator attestations from actual host calls, not cryptographic identity proof.'}
(PROJECT/'evidence/system-final-audit-complete.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
evidence('final-audit-complete',PROJECT/'evidence/system-final-audit-complete.json','Executed final fifty-context/version/hash audit with unresolved condition retained')
run('stage','--name','final-audit','--evidence','final-audit-complete','decision-summary','actual-runtimes')

# Faithful imports occur after objection registration. No approval is inferred
# from silence, absence or agreement of other reviewers.
for _,data in responses:
    run('vote','--expert',data['expert'],'--version',data['version'],'--digest',data['digest'],
        '--decision',data['decision'],'--reason',data['reason'],'--evidence','review-'+data['expert'],
        'frozen-candidate','actual-encoded-validation-json','actual-live-verification-json')
report=run('report','--output',str(PROJECT/'engine-report.json'))
assert not report['Experts Missing'] and not report['Experts Outdated']
assert not report['Changed Artifacts'] and not report['Invalid Evidence'] and not report['Missing Stages']
print(json.dumps({key:report[key] for key in ['Experts Approved','Experts Rejected','Experts Requiring Evidence',
                                            'Experts Missing','Consensus Status','Changed Artifacts','Invalid Evidence']},ensure_ascii=False,indent=2))
