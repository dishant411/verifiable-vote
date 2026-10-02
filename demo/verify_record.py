"""Offline orchestration of upstream Helios proof checks; no new cryptography."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from helios.crypto.utils import hash_b64
from helios import utils
from helios.datatypes import LDObject
from helios.crypto import algs
from helios.workflows.homomorphic import Tally

class VerificationError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise VerificationError(message)

def decode(value, kind):
    return LDObject.fromDict(value, type_hint='legacy/' + kind).wrapped_obj

def verify(record, expected_fingerprint=None, tracker=None):
    require(record['protocolVersion'] == 'verifiable-vote/helios-demo/v1', 'Unsupported format')
    raw = record['election']
    election = SimpleNamespace(**raw)
    election.public_key = decode(raw['public_key'], 'EGPublicKey')
    election.hash = hash_b64(utils.to_json(raw))
    require(election.hash == record['electionFingerprint'], 'Manifest fingerprint mismatch')
    if expected_fingerprint:
        require(election.hash == expected_fingerprint, 'Unexpected election fingerprint')
    require(not election.openreg, 'Only closed-roster demo records supported')
    require(len(election.questions) == 1 and len(election.questions[0]['answers']) == 2,
        'Only one two-option demo question supported')
    question = election.questions[0]
    require(question['tally_type'] == 'homomorphic' and question['min'] == 0 and question['max'] == 1,
        'Unsupported question rules')
    require(0 < len(record['ballots']) <= 100, 'Expected 1..100 counted demo ballots')
    tally = Tally(election=election)
    aliases, trackers = set(), set()
    for entry in record['ballots']:
        require(set(entry) == {'alias', 'tracker', 'vote'}, 'Unexpected ballot metadata')
        require(entry['alias'] not in aliases, 'Duplicate counted alias')
        aliases.add(entry['alias'])
        vote_data = entry['vote']
        require(set(vote_data) == {'answers', 'election_hash', 'election_uuid'}, 'Unexpected ballot fields')
        require(len(vote_data['answers']) == len(election.questions), 'Wrong question count')
        for answer, question in zip(vote_data['answers'], election.questions):
            require(set(answer) == {'choices', 'individual_proofs', 'overall_proof'}, 'Plaintext/randomness or unexpected fields')
            require(len(answer['choices']) == len(question['answers']) == len(answer['individual_proofs']), 'Wrong choice count')
        vote = decode(vote_data, 'EncryptedVote')
        require(vote.hash == entry['tracker'], 'Ballot tracker mismatch')
        require(entry['tracker'] not in trackers, 'Duplicate counted ballot')
        trackers.add(entry['tracker'])
        require(vote.verify(election), 'Ballot proof or election binding failed')
        tally.add_vote(vote, verify_p=False)
    require(tally.ld_object.toJSONDict() == record['encryptedTally'], 'Encrypted aggregate mismatch')
    require(len(record['trustees']) == 1, 'Only single-trustee synthetic demo supported')
    trustees = [SimpleNamespace(public_key=decode(t['public_key'], 'EGPublicKey'),
        pok=decode(t['pok'], 'DLogProof'),
        decryption_factors=[[int(x) for x in row] for row in t['decryption_factors']],
        decryption_proofs=[[decode(x, 'EGZKProof') for x in row] for row in t['decryption_proofs']])
        for t in record['trustees']]
    combined_key = None
    for trustee in trustees:
        require(trustee.public_key.verify_sk_proof(trustee.pok, algs.DLog_challenge_generator), 'Trustee key proof failed')
        combined_key = trustee.public_key if combined_key is None else combined_key * trustee.public_key
        require(tally.verify_decryption_proofs(trustee.decryption_factors, trustee.decryption_proofs,
            trustee.public_key, algs.EG_fiatshamir_challenge_generator), 'Decryption proof failed')
    require(LDObject.instantiate(combined_key, datatype='legacy/EGPublicKey').toJSONDict() == record['election']['public_key'], 'Trustee key combination mismatch')
    computed = tally.decrypt_from_factors([t.decryption_factors for t in trustees], election.public_key)
    require(computed == record['result'], 'Published result mismatch')
    if tracker:
        require(tracker in trackers, 'Tracker absent from counted ballots (possibly superseded)')
    return {'status': 'VERIFIED', 'countedBallots': tally.num_tallied, 'result': computed,
        'electionFingerprint': election.hash, 'trustedFingerprintProvided': bool(expected_fingerprint)}

def main():
    parser = argparse.ArgumentParser(description='Verify synthetic evidence without server/database/network access')
    parser.add_argument('record', type=Path)
    parser.add_argument('--expected-fingerprint')
    parser.add_argument('--tracker')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(json.loads(args.record.read_text()), args.expected_fingerprint, args.tracker), indent=2))
    except Exception as error:
        raise SystemExit(f'FAIL: {type(error).__name__}: {error}')

if __name__ == '__main__':
    main()
