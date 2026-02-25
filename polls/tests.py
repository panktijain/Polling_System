from django.test import TestCase, Client
from django.urls import reverse
from .models import Poll, Option


class PollModelTest(TestCase):
    def setUp(self):
        self.poll = Poll.objects.create(question="Test Poll?")
        self.opt1 = Option.objects.create(poll=self.poll, text="Option A", vote_count=3)
        self.opt2 = Option.objects.create(poll=self.poll, text="Option B", vote_count=7)

    def test_poll_str(self):
        self.assertEqual(str(self.poll), "Test Poll?")

    def test_option_str(self):
        self.assertEqual(str(self.opt1), "Option A")

    def test_total_votes(self):
        self.assertEqual(self.poll.total_votes(), 10)

    def test_total_votes_no_options(self):
        poll = Poll.objects.create(question="Empty poll?")
        self.assertEqual(poll.total_votes(), 0)

    def test_option_percentage(self):
        self.assertEqual(self.opt1.percentage(10), 30.0)
        self.assertEqual(self.opt2.percentage(10), 70.0)

    def test_option_percentage_zero_total(self):
        self.assertEqual(self.opt1.percentage(0), 0)

    def test_poll_is_active_default(self):
        self.assertTrue(self.poll.is_active)

    def test_vote_count_default(self):
        opt = Option.objects.create(poll=self.poll, text="New option")
        self.assertEqual(opt.vote_count, 0)


class PollListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.active_poll = Poll.objects.create(question="Active Poll?", is_active=True)
        self.inactive_poll = Poll.objects.create(question="Inactive Poll?", is_active=False)

    def test_poll_list_shows_active_polls(self):
        response = self.client.get(reverse('poll_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Poll?")
        self.assertNotContains(response, "Inactive Poll?")

    def test_poll_list_no_polls(self):
        Poll.objects.all().delete()
        response = self.client.get(reverse('poll_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No active polls")


class PollDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.poll = Poll.objects.create(question="Detail Poll?")
        self.opt = Option.objects.create(poll=self.poll, text="Option 1")
        self.inactive_poll = Poll.objects.create(question="Inactive?", is_active=False)

    def test_poll_detail_active(self):
        response = self.client.get(reverse('poll_detail', args=[self.poll.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Poll?")
        self.assertContains(response, "Option 1")

    def test_poll_detail_inactive_forbidden(self):
        response = self.client.get(reverse('poll_detail', args=[self.inactive_poll.id]))
        self.assertEqual(response.status_code, 403)

    def test_poll_detail_not_found(self):
        response = self.client.get(reverse('poll_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_poll_detail_no_options(self):
        poll = Poll.objects.create(question="No options poll?")
        response = self.client.get(reverse('poll_detail', args=[poll.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No options available")


class VoteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.poll = Poll.objects.create(question="Vote Poll?")
        self.opt1 = Option.objects.create(poll=self.poll, text="Yes")
        self.opt2 = Option.objects.create(poll=self.poll, text="No")
        self.inactive_poll = Poll.objects.create(question="Inactive?", is_active=False)

    def test_vote_increments_count(self):
        self.client.post(reverse('vote', args=[self.poll.id]), {'option': self.opt1.id})
        self.opt1.refresh_from_db()
        self.assertEqual(self.opt1.vote_count, 1)

    def test_vote_redirects_to_results(self):
        response = self.client.post(reverse('vote', args=[self.poll.id]), {'option': self.opt1.id})
        self.assertRedirects(response, reverse('poll_results', args=[self.poll.id]))

    def test_double_vote_blocked(self):
        self.client.post(reverse('vote', args=[self.poll.id]), {'option': self.opt1.id})
        response = self.client.post(reverse('vote', args=[self.poll.id]), {'option': self.opt2.id})
        self.assertContains(response, "already voted")
        self.opt2.refresh_from_db()
        self.assertEqual(self.opt2.vote_count, 0)

    def test_vote_without_option_shows_error(self):
        response = self.client.post(reverse('vote', args=[self.poll.id]), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "select an option")

    def test_vote_inactive_poll_forbidden(self):
        response = self.client.post(reverse('vote', args=[self.inactive_poll.id]), {'option': 1})
        self.assertEqual(response.status_code, 403)

    def test_vote_not_found(self):
        response = self.client.post(reverse('vote', args=[9999]), {'option': 1})
        self.assertEqual(response.status_code, 404)

    def test_get_vote_redirects(self):
        response = self.client.get(reverse('vote', args=[self.poll.id]))
        self.assertRedirects(response, reverse('poll_detail', args=[self.poll.id]))


class PollResultsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.poll = Poll.objects.create(question="Results Poll?")
        self.opt1 = Option.objects.create(poll=self.poll, text="A", vote_count=5)
        self.opt2 = Option.objects.create(poll=self.poll, text="B", vote_count=5)

    def test_results_page(self):
        response = self.client.get(reverse('poll_results', args=[self.poll.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Results Poll?")
        self.assertContains(response, "50.0%")

    def test_results_zero_votes(self):
        poll = Poll.objects.create(question="No votes?")
        Option.objects.create(poll=poll, text="Option", vote_count=0)
        response = self.client.get(reverse('poll_results', args=[poll.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0%")

    def test_results_not_found(self):
        response = self.client.get(reverse('poll_results', args=[9999]))
        self.assertEqual(response.status_code, 404)
