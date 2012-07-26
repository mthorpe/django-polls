from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


class Poll(models.Model):
    
    REPEAT_VOTING_CHOICES = (
        ('Unlimited', 'unlimited'),
        ('Daily', 'once per day'),
        ('Weekly', 'once per week'),
        ('Once', 'once'),
    )
    
    RESULTS_DISPLAYED_CHOICES = (
        ('Votes', 'Show Results (# of votes)'),
        ('Percentage', 'Show Results as percentage'),
        ('None', 'Don\'t Show Results'),
    )
    
    NUMBER_OF_SELECTIONS = (
        (0, 'No Limit'),
        (1, 'one'),
        (2, 'two'),
        (3, 'three'),
        (4, 'four'),
        (5, 'five'),
        (6, 'six'),
        (7, 'seven'),
        (8, 'eight'),
        (9, 'nine'),
        (10, 'ten'),
    )
    
    question = models.CharField(max_length=500)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    results_require_voting = models.BooleanField(default=True)
    results_displayed = models.CharField(max_length=10, choices=RESULTS_DISPLAYED_CHOICES, blank=False, default='Percentage')
    
    repeat_voting = models.CharField(max_length=9, choices=REPEAT_VOTING_CHOICES, blank=False, default='Daily')
    
    number_answers_allowed = models.IntegerField(choices=NUMBER_OF_SELECTIONS, blank=False, default=1)
    randomize_answer_order = models.BooleanField(default=False)
    allow_user_answers = models.BooleanField(default=False)
    
    registration_required = models.BooleanField(default=False)    
        
    author = models.ForeignKey(User)
    site = models.ForeignKey(Site)
    
    def __unicode__(self):
        return self.question
 

class Answer(models.Model):
    poll = models.ForeignKey(Poll, related_name='answers')
    text = models.CharField(max_length=500, blank=False)
    votes = models.IntegerField(default=0)
    
    class Meta:
        order_with_respect_to = 'poll'
    
    def __unicode__(self):
        return '%s : %s (Poll: %s)' % (self.id, self.text, self.poll)

    
class UserAnswer(models.Model):
    poll = models.ForeignKey(Poll, related_name='user_answers')
    text = models.CharField(max_length=500)
    
    def __unicode__(self):
        return '%s (Poll: %s)' % (self.text, self.poll)
    
    