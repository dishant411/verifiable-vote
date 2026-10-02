"""Synthetic fixture and public-evidence export using unmodified Helios APIs."""
import json
import uuid
from pathlib import Path
from helios.models import Election, Voter, CastVote, Trustee
from helios_auth.models import User
from helios.views import ELGAMAL_PARAMS
from helios.workflows.homomorphic import EncryptedVote

ROOT = Path(__file__).resolve().parents[1]

def create(short_name):
    admin, _ = User.objects.get_or_create(user_type='devlogin', user_id='user@example.com',
        defaults={'name': 'Synthetic Demo Administrator', 'info': {'email': 'admin@example.invalid'}})
    election_uuid = str(uuid.uuid4())
    election, created = Election.get_or_create(short_name=short_name, uuid=election_uuid,
        cast_url=f'http://localhost:8000/helios/elections/{election_uuid}/cast',
        name='SYNTHETIC RESEARCH DEMO: Community garden',
        description='Test accounts only. Revoting allowed; latest valid ballot counts. Not for government elections.', admin=admin)
    if not created:
        return election
    election.openreg = False
    election.use_voter_aliases = True
    election.questions = [{'answers': ['Garden', 'Library'], 'answer_urls': [None, None],
        'choice_type': 'approval', 'min': 0, 'max': 1, 'question': 'Which test project?',
        'short_name': 'Test project', 'result_type': 'absolute', 'tally_type': 'homomorphic'}]
    election.save()
    election.generate_trustee(ELGAMAL_PARAMS)
    for index, name in enumerate(['alice', 'bob'], 1):
        voter = Voter(election=election, uuid=str(uuid.uuid4()), voter_login_id=name,
            voter_name=f'Synthetic {name}', voter_email=f'{name}@example.invalid', alias=f'V{index}')
        voter.generate_password()
        voter.save()
    election.freeze()
    return election

def cast(election, voter, choice):
    # The synthetic driver encrypts in Python. Real voter UI uses the upstream browser booth.
    encrypted = EncryptedVote.fromElectionAndAnswers(election, [[choice]])
    ballot = CastVote(voter=voter, vote=encrypted, vote_hash=encrypted.hash)
    ballot.save()
    if not ballot.verify_and_store():
        raise ValueError('Upstream ballot verification failed')
    return ballot

def export(election):
    if not election.result_released_at:
        raise ValueError('Release the tally before exporting')
    return {'protocolVersion': 'verifiable-vote/helios-demo/v1',
        'election': election.ld_object.toJSONDict(), 'electionFingerprint': election.hash,
        'ballots': [{'alias': v.alias, 'tracker': v.vote_hash, 'vote': v.vote.ld_object.toJSONDict()}
            for v in election.voter_set.exclude(vote=None).order_by('alias')],
        'trustees': [t.ld_object.toJSONDict() for t in Trustee.get_by_election(election)],
        'encryptedTally': election.encrypted_tally.ld_object.toJSONDict(),
        'result': election.result}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['seed', 'sample', 'export'])
    parser.add_argument('--short-name', default='synthetic-demo-v2')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.action == 'export':
        election = Election.objects.get(short_name=args.short_name)
    else:
        election = create(args.short_name)
    if args.action == 'seed':
        path = ROOT / '.runtime/credentials.json'
        path.write_text(json.dumps({v.voter_login_id: v.voter_password for v in election.voter_set.all()}, indent=2))
        path.chmod(0o600)
        print(f'Open http://localhost:8000/helios/e/{election.short_name}')
        print('Synthetic voter credentials saved locally in .runtime/credentials.json; never publish this file.')
        print('Administrator: use upstream Dev Login. Email delivery is disabled.')
        return
    if args.action == 'sample' and not election.result_released_at:
        voters = list(election.voter_set.order_by('voter_login_id'))
        cast(election, voters[0], 0)
        voters[0].refresh_from_db()
        cast(election, voters[0], 1)  # revote replaces the first ballot
        cast(election, voters[1], 0)
        election.compute_tally()
        election.helios_trustee_decrypt()
        election.combine_decryptions()
        election.release_result()
        election.save()
        if election.result != [[1, 1]]:
            raise ValueError('Unexpected tally')
    destination = args.output or ROOT / 'evidence/sample-election.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(export(election), indent=2))
    print(f'Public synthetic evidence: {destination}')
    print(f'Election fingerprint: {election.hash}')
    print(f'Result: {election.result}')

if __name__ == '__main__':
    main()
