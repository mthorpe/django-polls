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
