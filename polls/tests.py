import datetime
import unittest

from django.test import TestCase
from django.db.models import Sum

from django.contrib.auth.models import User
from django.utils import timezone, unittest
from datetime import timedelta
from django.core.urlresolvers import reverse

from polls.models import *
from polls.forms import *


#Helper function to create a poll with answers
def create_sample_poll(user, site):
    
    answer_set = []
    
    p = Poll.objects.create(
        question = 'Who is the biggest troll?',
        start_date = '2012-07-01 09:00',
        end_date = '2012-07-30 9:00',
        results_require_voting = True,
        results_displayed = 'Percentage',
        repeat_voting = 'Unlimited',
        number_answers_allowed = 1,
        randomize_answer_order = True,
        allow_user_answers = False,
        registration_required = False,
        author = user,
        site = site
    )
    
    answer_set.append(Answer.objects.create(
        poll = p,
        text = 'Nick',
        votes = 20
        )
    )
    
    answer_set.append(Answer.objects.create(
        poll = p,
        text = 'Ben',
        votes = 40
        )
    )
    
    answer_set.append(Answer.objects.create(
        poll = p,
        text = 'Lunchbox',
        votes = 50
        )
    )
    
    return p

class PollTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(pk=1)
        self.user = User.objects.create_user('user', 'mail@example.com', 'password')
        self.user.is_staff = True
        self.user.save()
        
    def test_create_poll(self):
        self.client.login(username='user', password='password')
        #Valid poll
        post_dict = {
            'question':'Who is the biggest troll?',
            'start_date': '2012-07-01 09:00',
            'end_date': '2012-07-30 9:00',
            'results_require_voting': True,
            'results_displayed': 'Percentage',
            'repeat_voting': 'Unlimited',
            'number_selections_allowed': 0,
            'randomize_answer_order': True,
            'allow_user_answers': False,
            'registration_required': False,
            'author': self.user,
            'site': self.site,
            'answers-0-text': 'Nick',
            'answers-1-text': 'Lunchbox',
            'answers-2-text': 'Ben',
            'answers-TOTAL_FORMS': u'3',
            'answers-INITIAL_FORMS': u'0',
            'answers-MAX_NUM_FORMS': u'',
        }
        
        response = self.client.post(reverse('polls_poll_create'), post_dict)
        #Should redirect to poll detail view
        self.assertEquals(response.status_code, 302)
        
    def test_poll_edit_form(self):
        
        #Valid Form
        pf = PollEditForm({
            'question':'Who is the biggest troll?',
            'start_date': '2012-07-01 09:00',
            'end_date': '2012-07-30 9:00',
            'results_require_voting': True,
            'results_displayed': 'Percentage',
            'repeat_voting': 'Unlimited',
            'allow_multiple_selections': True,
            'number_selections_allowed': 0,
            'randomize_answer_order': True,
            'allow_user_answers': False,
            'registration_required': False,
        })
        self.assertTrue(pf.is_valid())
        
        #Form without a question should not validate
        pf = PollEditForm({
            'question':'',
            'start_date': '2012-07-01 09:00',
            'end_date': '2012-07-30 9:00',
            'results_require_voting': True,
            'results_displayed': 'Percentage',
            'repeat_voting': 'Unlimited',
            'allow_multiple_selections': True,
            'number_selections_allowed': 0,
            'randomize_answer_order': True,
            'allow_user_answers': False,
            'registration_required': False,
        })
        self.assertFalse(pf.is_valid())
        
        #Form without an end date should not validate
        pf = PollEditForm({
            'question':'Who is the biggest troll?',
            'start_date': '2012-07-01 09:00',
            'end_date': '',
            'results_require_voting': True,
            'results_displayed': 'Percentage',
            'repeat_voting': 'Unlimited',
            'allow_multiple_selections': True,
            'number_selections_allowed': 0,
            'randomize_answer_order': True,
            'allow_user_answers': False,
            'registration_required': False,
        })
        self.assertFalse(pf.is_valid())
        
    def test_answer_edit_formset(self):
        
        #Valid Form
        af = AnswerEditFormSet({
            'answers-0-text': 'Nick',
            'answers-1-text': 'Lunchbox',
            'answers-2-text': 'Ben',
            'answers-TOTAL_FORMS': u'1',
            'answers-INITIAL_FORMS': u'0',
            'answers-MAX_NUM_FORMS': u'',
        })
        self.assertTrue(af.is_valid())
        
    def test_user_answer_form(self):
        
        #Valid Form
        ua = UserAnswerForm({
            'user_answer': 'James',
        }) 
        self.assertTrue(ua.is_valid())
        
    def test_delete_poll(self):
        self.client.login(username='user', password='password')
        poll = create_sample_poll(self.user, self.site)
        
        #Delete the poll
        response = self.client.post(reverse('polls_poll_delete', kwargs={
            'poll_id': poll.id,
        }))
        self.assertEquals(response.status_code, 302)
    
    def test_reset_poll(self):
        self.client.login(username='user', password='password')
        poll = create_sample_poll(self.user, self.site)
        poll.answers_list = poll.answers.all()
        
        #Reset the poll
        response = self.client.post(reverse('polls_poll_reset', kwargs={
            'poll_id': poll.id,
        }))
        #Total_votes after reset should be zero
        total_votes = poll.answers_list.aggregate(Sum('votes'))['votes__sum']
        
        self.assertEquals(total_votes, 0)
    
    
    def test_poll_voting(self):
        self.client.login(username='user', password='password')
        #Create Poll
        poll = create_sample_poll(self.user, self.site)
        
        #Post a vote
        response = self.client.post(reverse('polls_ajax_poll_detail', kwargs={
            'poll_id': poll.id,
        }), {'answers': 1,})
        
        answer = Answer.objects.get(pk=1)
        #Votes should equal 21 (1 + the number set at - 20)
        self.assertEquals(answer.votes, 21)
        self.assertEquals(response.status_code, 302)
        
        #Post without a vote
        response = self.client.post(reverse('polls_ajax_poll_detail', kwargs={
            'poll_id': poll.id,
        }))
        self.assertEquals(response.status_code, 200)
        
        #Post too many votes
        response = self.client.post(reverse('polls_ajax_poll_detail', kwargs={
            'poll_id': poll.id,
        }), {'answers': [1, 2],})
        self.assertEquals(response.status_code, 200)
  
        
        