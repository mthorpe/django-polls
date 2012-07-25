import datetime
from django import forms
from django.forms.models import inlineformset_factory
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, CheckboxInput
from polls.models import Poll, Answer


AnswerEditFormSet = inlineformset_factory(Poll, Answer, fields=('text','id',), extra=4, max_num=5)

class PollEditForm(forms.ModelForm):
    
    NUMBER_OF_SELECTIONS = (
        (0, 'No Limit'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    )
    
    allow_multiple_selections = forms.BooleanField(required=False)
    number_selections_allowed = forms.ChoiceField(choices=NUMBER_OF_SELECTIONS)
    
    def __init__(self, *args, **kwargs):

        super(PollEditForm, self).__init__(*args, **kwargs)
        
        #initialize number of selections
        if not self.instance.number_answers_allowed == 1:
            self.fields['number_selections_allowed'].initial = self.instance.number_answers_allowed
            self.fields['allow_multiple_selections'].initial = True        
    
    class Meta:
        model = Poll
        exclude = ('author', 'site', 'number_answers_allowed')
        widgets = {
            'results_displayed': forms.RadioSelect(),
        }
    
    def save(self, commit=True):
        
        p = super(PollEditForm, self).save(commit=False)

        #set number answers allowed
        if self.cleaned_data['allow_multiple_selections']:
            p.number_answers_allowed = self.cleaned_data['number_selections_allowed']
        else:
            p.number_answers_allowed = 1
        
        if commit:
            p.save()
            
        return p   

class VotingRadioForm(forms.Form):
    answers = forms.ChoiceField(widget=RadioSelect, required=True)
    
    def __init__(self, *args, **kwargs):
        
        choices = kwargs.pop('choices', None)
        user_input = kwargs.pop('user_input', False)
        super(VotingRadioForm, self).__init__(*args, **kwargs)
        
        if choices:     
            self.fields['answers'].choices = choices
            
        if user_input:
            self.fields['answers'].choices.append(('0', 'Other'))
    
class VotingCheckboxForm(forms.Form):
    answers = forms.MultipleChoiceField(widget=CheckboxSelectMultiple, required=True)
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        selected_answers = kwargs.pop('selected_answers', None)
        user_input = kwargs.pop('user_input', False)
        super(VotingCheckboxForm, self).__init__(*args, **kwargs)
        
        #for selected in 
        
        if choices:     
            self.fields['answers'].choices = choices
            self.fields['answers'].initial = selected_answers
        
        if user_input:
            self.fields['answers'].choices.append(('0', 'Others'))

class UserAnswerForm(forms.Form):
    user_answer = forms.CharField()