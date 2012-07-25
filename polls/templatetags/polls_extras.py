from django import template

register = template.Library()

@register.filter
def percentage(fraction, total):
    try:
        #The percentage with 1 decimal and include a % sign
        return "%.1f%%" % ((float(fraction) / float(total))*100)
    except ValueError:
        return ''
    except ZeroDivisionError:
        return 0

@register.filter
def next_vote_time(poll_repeat_voting):
    if poll_repeat_voting == 'Daily':
        vote_again = 'You can vote again tomorrow.'
    elif poll_repeat_voting == 'Weekly':
        vote_again = 'You can vote again next week.'
    elif poll_repeat_voting == 'Unlimited':
        vote_again = 'You can vote again anytime.'
    else:
        vote_again = ''
        
    return vote_again