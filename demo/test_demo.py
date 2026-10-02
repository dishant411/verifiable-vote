import copy
import json
from django.test import TestCase
from django.core.wsgi import get_wsgi_application
from webtest import TestApp
from helios.models import CastVote
from helios.workflows.homomorphic import EncryptedVote
from election_demo import create, cast, export, ROOT
from verify_record import verify, VerificationError

class DemoTests(TestCase):
    def setUp(self):
        self.election = create('integration-demo')
        self.voters = list(self.election.voter_set.order_by('voter_login_id'))

    def complete(self):
        old = cast(self.election, self.voters[0], 0)
        self.voters[0].refresh_from_db()
        current = cast(self.election, self.voters[0], 1)
        cast(self.election, self.voters[1], 0)
        self.election.compute_tally()
        self.election.helios_trustee_decrypt()
        self.election.combine_decryptions()
        self.election.release_result()
        self.election.save()
        return export(self.election), old.vote_hash, current.vote_hash

    def test_revote_tally_inclusion_and_superseded_tracker(self):
        record, old, current = self.complete()
        self.assertEqual(CastVote.objects.count(), 3)
        self.assertEqual(verify(record, self.election.hash, current)['result'], [[1, 1]])
        self.assertEqual(verify(record)['countedBallots'], 2)
        with self.assertRaises(VerificationError):
            verify(record, tracker=old)

    def test_tampering_rejected(self):
        record, _, _ = self.complete()
        def name(r): r['election']['name'] += ' changed'
        def ciphertext(r): r['ballots'][0]['vote']['answers'][0]['choices'][0]['beta'] = '1'
        def tracker(r): r['ballots'][0]['tracker'] = 'forged'
        def result(r): r['result'] = [[2, 0]]
        def proof(r): r['trustees'][0]['decryption_proofs'][0][0]['response'] = '1'
        def duplicate(r): r['ballots'].append(copy.deepcopy(r['ballots'][0]))
        def removed(r): r['ballots'].pop()
        def aggregate(r): r['encryptedTally']['num_tallied'] = 99
        def plaintext(r): r['ballots'][0]['vote']['answers'][0]['answer'] = [0]
        for mutation in [name, ciphertext, tracker, result, proof, duplicate, removed, aggregate, plaintext]:
            with self.subTest(mutation=mutation.__name__):
                changed = copy.deepcopy(record)
                mutation(changed)
                with self.assertRaises(VerificationError):
                    verify(changed, self.election.hash)
        with self.assertRaises(VerificationError):
            verify(record, 'wrong externally trusted fingerprint')

    def test_modified_ballot_with_recomputed_tracker_fails_crypto(self):
        from verify_record import decode
        record, _, _ = self.complete()
        record['ballots'][0]['vote']['answers'][0]['choices'][0]['beta'] = '1'
        record['ballots'][0]['tracker'] = decode(record['ballots'][0]['vote'], 'EncryptedVote').hash
        with self.assertRaisesRegex(VerificationError, 'proof'):
            verify(record)

    def test_http_password_eligibility_cast_and_closed_tally(self):
        app = TestApp(get_wsgi_application())
        prefix = f'/helios/elections/{self.election.uuid}'
        voter = self.voters[0]
        self.assertEqual(self.election.cast_url, 'http://localhost:8000' + prefix + '/cast')
        self.assertIn('cast_url', app.get(prefix).json)
        vote = EncryptedVote.fromElectionAndAnswers(self.election, [[0]])
        page = app.post(prefix + '/cast', {'encrypted_vote': vote.toJSON()}).follow()
        login = page.form
        login['voter_id'] = 'not-on-roster'
        login['password'] = 'invalid'
        page = login.submit()
        if page.status_int == 302:
            page = page.follow()
        self.assertEqual(CastVote.objects.count(), 0)
        login = page.form
        login['voter_id'] = voter.voter_login_id
        login['password'] = voter.voter_password
        page = login.submit()
        # Upstream login's cast_ballot flag casts on this POST.
        self.assertEqual(page.status_int, 302)
        voter.refresh_from_db()
        self.assertEqual(voter.vote_hash, vote.hash)
        self.assertEqual(CastVote.objects.filter(verified_at__isnull=False).count(), 1)
        app.get(prefix + '/cast_done')
        tracker_page = app.get('/helios/v/' + CastVote.objects.get().vote_tinyhash)
        if tracker_page.status_int == 302:
            tracker_page = tracker_page.follow()
        self.assertIn(vote.hash, tracker_page.text)
        self.election.compute_tally()
        page = app.post(prefix + '/cast', {'encrypted_vote': vote.toJSON()}).follow()
        self.assertIn('tallied', page.text.lower())
        self.assertEqual(CastVote.objects.count(), 1)

    def test_sample_public_export_contains_no_private_fields(self):
        record, _, _ = self.complete()
        forbidden = {'secret_key', 'secret', 'voter_password', 'voter_email', 'voter_login_id',
            'cast_ip', 'randomness', 'answer', 'private_key'}
        def inspect(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for child in value.values(): inspect(child)
            elif isinstance(value, list):
                for child in value: inspect(child)
        inspect(record)

    def test_offline_verifier_performs_no_database_queries(self):
        record = json.loads((ROOT / 'evidence/sample-election.json').read_text())
        with self.assertNumQueries(0):
            self.assertEqual(verify(record)['status'], 'VERIFIED')

    def test_directory_excludes_private_archived_and_incomplete_elections(self):
        from helios.models import Election
        from django.urls import reverse
        from django.utils import timezone
        for short_name, changes in [('private-card', {'private_p': True}),
                                    ('archived-card', {'archived_at': timezone.now()}),
                                    ('incomplete-card', {'uuid': ''})]:
            election = create(short_name)
            Election.objects.filter(pk=election.pk).update(**changes)
        page = self.client.get('/')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, reverse('election@view', args=[self.election.uuid]))
        self.assertEqual(len(page.context['elections']), 1)
        self.assertContains(page, '/demo-ui/design.css')
