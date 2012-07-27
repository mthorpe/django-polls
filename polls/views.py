import datetime
import time
import csv

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.db.models import Sum
from django.contrib.sites.models import get_current_site
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

from datetime import timedelta

from polls.forms import PollEditForm, AnswerEditFormSet, VotingRadioForm, VotingCheckboxForm
from polls.forms import UserAnswerForm
from polls.models import Poll, Answer, UserAnswer
from polls.templatetags.polls_extras import percentage

@login_required    
def poll_edit(request, poll_id=None):
    """
    Used to edit or create polls. Also called when user copies poll
    """
    site = get_current_site(request)
    author = request.user
    
    try:
        poll = Poll.objects.get(pk=poll_id)
        #need editing for answer formset validation
        editing = True
    except Poll.DoesNotExist:
        poll = None
        editing = False

    #When creating
    if request.method == 'POST':
        
        poll_form = PollEditForm(request.POST, instance=poll)
        
        if poll_form.is_valid():
            poll = poll_form.save(commit=False)
            poll.author = author
            poll.site = site
            answer_formset = AnswerEditFormSet(request.POST, instance=poll)
                
            #the answer formset must be valid and 
            #the answers must change (no blanks) OR user must be editing
            if editing or answer_formset.has_changed() and answer_formset.is_valid():
                poll.save()
                answer_formset.save()
                return HttpResponseRedirect(reverse('polls_ajax_poll_detail', args=(poll.id,)))

        #If any errors, rerender the page with error warning
        return render(request, 'polls/poll_edit.html', {
            'poll_form': poll_form,
            'answer_formset': answer_formset,
            'errors': True,
        })
         
    #When copying
    elif request.GET.get('copy_id'):
        poll = get_object_or_404(Poll, pk=request.GET['copy_id'])
        
        if not poll.number_answers_allowed == 1:
            poll.allow_multiple_selections = True
        else:
            poll.allow_multiple_selections = False
            
        #Initial poll form data set to data from copied poll
        poll_form = PollEditForm(initial={'question': 'Copy of: ' + str(poll.question),
            'results_require_voting': poll.results_require_voting,
            'results_displayed': poll.results_displayed,
            'repeat_voting': poll.repeat_voting,
            'allow_multiple_selections': poll.allow_multiple_selections,
            'number_selections_allowed': poll.number_answers_allowed,
            'randomize_answer_order': poll.randomize_answer_order,
            'allow_user_answers': poll.allow_user_answers,
            'registration_required': poll.registration_required,}
        )
        
        answers = poll.answers.values()
        answer_formset = AnswerEditFormSet(initial=answers)
    #Creating or editing
    else:
        poll_form = PollEditForm(instance=poll)
        answer_formset = AnswerEditFormSet(instance=(poll or Poll()))
    
    return render(request, "polls/poll_edit.html", {
        'poll_form': poll_form,
        'answer_formset': answer_formset,
        'errors': False,
    })
    
def poll_results(request, poll_id=None):  
    #Check if the poll id exists
    poll = get_object_or_404(Poll, pk=poll_id)
    poll.answers_list = poll.answers.all()
    poll.user_answers_list = poll.user_answers.all()
    
    #To create percentage - need total votes for entire poll
    poll.total_votes = poll.answers_list.aggregate(Sum('votes'))['votes__sum']
    
    #Check for session that says user just voted
    if not 'polls-just-voted' in request.session:
        just_voted_message = False
    else:
        just_voted_message = True
        #delete the session
        del request.session['polls-just-voted']
        
    #Check for session that says user is unable to vote_again
    if not 'polls-already-voted' in request.session:
        already_voted_message = False
    else:
        already_voted_message = True
        #delete the session
        del request.session['polls-already-voted']
    
    #'Other' only displayed in results if user answers are allowed
    if poll.allow_user_answers:
        poll.other_total = poll.user_answers_list.count()
        #include user answers in poll vote total
        poll.total_votes += poll.other_total
        
    return render(request, "polls/poll_results.html", {
        'poll': poll,
        'just_voted_message': just_voted_message,
        'already_voted_message': already_voted_message,
    })
    
def ajax_poll_detail(request, poll_id):
    """
    This is where the user can vote and see results.
    """
    #delete session - for testing
    #del request.session['polls-voting-history']
    now = timezone.now()    
    next_vote_date = None
    
    #Check if the poll id exists
    poll = get_object_or_404(Poll, pk=poll_id)
    answers = poll.answers.all()
    
    #check poll is closed
    if now > poll.end_date or now < poll.start_date:
        poll.closed = True
        return render(request, "polls/ajax_poll_detail.html", {
            'poll': poll,
        })
                
    #When user votes
    if request.method == 'POST':
        #Check an answer was selected
        selected = request.POST.getlist('answers')        
        
        #If no answer selected
        if not selected:
            return render(request, 'polls/ajax_poll_detail.html', {
                'poll': poll,
                'poll_voting_form': poll_voting_form,
                'user_answer_form': user_answer_form,
                'no_choice_error': True,
            })
        #Answers selected
        else:
            #Selected answers is within limit (0 == unlimited selections)
            if poll.number_answers_allowed == 0 or len(selected) <= poll.number_answers_allowed:
                
                for answer_id in selected:
                    #Answer was not a user answer
                    if not answer_id == '0':
                        selected_answer = answers.get(pk=answer_id)
                        selected_answer.votes += 1
                        selected_answer.save()
                    #Answer was a user answer
                    else:
                        user_answer = UserAnswer.objects.create(poll=poll, text=request.POST['user_answer'])
                
                if poll.repeat_voting == "Daily":
                    #Add 1 day
                    next_vote_date = now + timedelta(days=1)
                elif poll.repeat_voting == "Weekly":
                    #Days need for it to be start of week (Monday)
                    next_vote_date = now + timedelta(weeks=1) 
                elif poll.repeat_voting == "Once":
                    #the day after the end of the poll
                    next_vote_date = poll.end_date + timedelta(days=1)
                
                #add key, value to dictionary
                request.session['polls-voting-history'][poll.id] = next_vote_date
                
                #If the poll lasts longer than a month, set the expiration date to the end of the poll
                one_month = now + timedelta(days=30)
                if(poll.end_date > one_month):
                    request.session.set_expiry(poll.end_date)
                else:
                    request.session.set_expiry(now + timedelta(days=30))                
            #Selected answers over limit
            else:
                #Keep track of which selections were made
                #Form needs to keep user answers selected
                initial_selected = {}
                for selection in selected:
                    initial_selected[selection] = True
                
                user_answer_form = None
                #Only need for checkboxes... radio buttons can't be over limit
                if not poll.number_answers_allowed == 1:
                    poll_voting_form = VotingCheckboxForm(choices=answer_choices, user_input=False, selected_answers=initial_selected)
                    if poll.allow_user_answers:
                        poll_voting_form = VotingCheckboxForm(choices=answer_choices, user_input=True, selected_answers=initial_selected)
                        user_answer_form = UserAnswerForm()
                
                return render(request, 'polls/ajax_poll_detail.html', {
                    'poll': poll,
                    'poll_voting_form': poll_voting_form,
                    'user_answer_form': user_answer_form,
                    'too_many_answers_error': True,
                })
        
        #set just voted session variable to true
        request.session['polls-just-voted'] = True
        #When results will be displayed after voting
        if not poll.results_displayed  == 'None':
            return HttpResponseRedirect(reverse('polls_poll_results', args=(poll_id,)))
    
    #GET Request
    #Assume user can vote until session info is checked
    can_vote = True
    #session information
    request.session.setdefault('polls-voting-history', None);
    #Determine if user has voted in this poll
    if poll.id in request.session['polls-voting-history']:
        next_vote_date = request.session['polls-voting-history'][poll.id]
        #None means user can vote unlimited
        if next_vote_date:
            #Compare date to now for voting eligibility
            if now.date <= next_vote_date.date:
                can_vote = False
    
    #if unable to vote, set already voted session variable to true
    if not can_vote:
        request.session['polls-already-voted'] = True
        return HttpResponseRedirect(reverse('polls_poll_results', args=(poll_id,))) 
    elif can_vote or poll.repeat_voting == 'Unlimited' or not request.session['polls-already-voted'] or not next_vote_date:
        
        #Put answers in a tuple and pass into the form
        answer_choices = []
        for answer in answers:
            answer_choices.append((answer.id, answer.text))            
        
        user_answer_form = None
        #Determine which form to display based on how many answers user is allowed to select
        if not poll.number_answers_allowed == 1:
            poll_voting_form = VotingCheckboxForm(choices=answer_choices, user_input=False)
            if poll.allow_user_answers:
                poll_voting_form = VotingCheckboxForm(choices=answer_choices, user_input=True)
                user_answer_form = UserAnswerForm()
        else:
            poll_voting_form = VotingRadioForm(choices=answer_choices, user_input=False)
            if poll.allow_user_answers:
                poll_voting_form = VotingRadioForm(choices=answer_choices, user_input=True)
                user_answer_form = UserAnswerForm()

        #randomizing answer order
        if poll.randomize_answer_order:
            #randomly order answers
            answers = answers.order_by('?')

        #If user just voted, display message
        #Check for session that says user just voted
        if not 'polls-just-voted' in request.session:
            just_voted_message = False
        else:
            just_voted_message = True
            #delete the session
            del request.session['polls-just-voted']               
        
        return render(request, "polls/ajax_poll_detail.html", {
            'poll': poll,
            'poll_voting_form': poll_voting_form,
            'user_answer_form': user_answer_form,
            'just_voted_message': just_voted_message,
        })  

@login_required
def poll_landing(request):
    """
    This is the poll listing for all admin
    """
    site = get_current_site(request)
    polls = Poll.objects.filter(site=site.id)
    now = timezone.now()
    
    listing = []
    
    for poll in polls:
        poll.answers_list = poll.answers.all()
        poll.user_answers_list = poll.user_answers.all()
        
        #poll open
        if now <= poll.end_date and poll.start_date <= now:
            poll.status = "Open"
        else:
            poll.status = "Closed"
            
        #user poll
        if poll.author == request.user:
            poll.user_poll = True
        else:
            poll.user_poll = False
        
        #Set total votes, needed for percentages
        if not poll.answers_list.aggregate(Sum('votes'))['votes__sum'] == None:
            poll.total_votes = poll.answers_list.aggregate(Sum('votes'))['votes__sum']
        else:
            poll.total_votes = 0
        
        #'Other' only displayed in results if user answers are allowed
        if poll.allow_user_answers:
            poll.other_total = poll.user_answers_list.count()
            #include user answers in poll vote total
            poll.total_votes += poll.other_total
        
        #Create the list of polls
        listing.append({"poll": poll,})
    
    return render(request, "polls/poll_landing.html", {
        'listing': listing,
    })

@login_required
def poll_report(request, poll_id):
    """
    This is the admin results/report view
    """
    #Check if the poll exists
    poll = get_object_or_404(Poll, pk=poll_id)
    poll.answers_list = poll.answers.all()
    poll.user_answers_list = poll.user_answers.all()

    #To create percentage - need total votes for entire poll
    poll.total_votes = poll.answers_list.aggregate(Sum('votes'))['votes__sum']

    #'Other' only displayed in results if user answers are allowed
    if poll.allow_user_answers:
        poll.other_total = poll.user_answers_list.count()
        #include user answers in poll vote total
        poll.total_votes += poll.other_total
            
    return render(request, "polls/poll_report.html", {
        'poll': poll,
    }) 

@login_required
def poll_delete(request, poll_id):
    """
    Deleting a poll
    """
    if request.method == 'POST':
        #Check if the pollexists
        poll = get_object_or_404(Poll, pk=poll_id)
        poll.delete()
    
        return HttpResponseRedirect(reverse('polls_poll_landing'))    
    return HttpResponseBadRequest("Not a POST request or bad POST data.")
  
@login_required
def poll_reset(request, poll_id):
    """
    Reset poll votes to 0
    """
    if request.method == 'POST':
        #Check if poll exists
        poll = get_object_or_404(Poll, pk=poll_id)
        #reset answers to 0 votes
        poll.answers.all().update(votes=0)
         #Delete all user answers
        user_answers = poll.user_answers.all().delete()
        
        return HttpResponseRedirect(reverse('polls_poll_report', args=(poll_id,)))
    return HttpResponseBadRequest("Not a POST request or bad POST data.")

@login_required
def poll_export_csv(request, poll_id):
    """
    Used to export the report to CSV
    
    **Need to know what should be included in the document
    """
    poll = get_object_or_404(Poll, pk=poll_id)
    answers = poll.answers.all()
    
    total_votes = answers.aggregate(Sum('votes'))['votes__sum']
    if total_votes == None:
        total_votes = 0
    
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=pollresults.csv'
    
    writer = csv.writer(response)
    writer.writerow(['Question: ' + str(poll.question)])
    writer.writerow(['Answer', 'Count', 'Percent'])
    
    for answer in answers:
        writer.writerow([answer.text, answer.votes, percentage(answer.votes, total_votes)])
    
    return response
        
        
        
        
        