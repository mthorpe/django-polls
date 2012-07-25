from polls.models import Poll, Answer, UserAnswer
from django.contrib import admin
    
#Poll   
admin.site.register(Poll)

#Answer
admin.site.register(Answer)

#UserAnswer
admin.site.register(UserAnswer)