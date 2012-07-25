addEvent('domready', function () {
    $$('.poll-to-load').each(function (el) {
        var pollId = el.get('data-poll-id');
        
        //Display the poll within the div
        var pollRequest = new Request.HTML({
            url: '/polls/' + pollId + '/',
            update: el,
            method: 'get',
            onSuccess: function () {
                //Add functionality for Poll Form
                pollFormVoting(el, pollId, pollRequest);
                //Add functionality for View Results Link
                viewResults(el, pollId, pollRequest);
            }
        });
        pollRequest.send();
    });
    
    //Display the voting form within div (el)
    var pollFormVoting = function (el, pollId, pollRequest) {
        var pollForm = $('poll-form');
        if (pollForm) {
            pollForm.addEvent('submit', function (evt) {
                evt.stop();
                var voteRequest = new Request.HTML({
                    url: '/polls/' + pollId + '/',
                    update: el,
                    onSuccess: function () {
                        backToPoll(pollRequest);
                        pollFormVoting(el, pollId, pollRequest);
                        viewResults(el, pollId, pollRequest);
                    }
                });
                voteRequest.post(pollForm);
            });
        };
    };
    
    //Display the view results within the div (el)
    var viewResults = function (el, pollId, pollRequest) {
        var resultsLink = $('view-results-link');
        if (resultsLink) {
            resultsLink.addEvent('click', function (evt) {
                evt.stop();
                var resultsRequest = new Request.HTML({
                    url: '/polls/' + pollId + '/results/',
                    update: el,
                    method: 'get',
                    onSuccess: function () {
                        backToPoll(pollRequest);
                    }
                });
                resultsRequest.send();
            });
        }
    };
    
    //Display the back to poll link within the div
    var backToPoll = function (pollRequest) {    
        var backToPollLink = $('back-to-poll-link');
        if (backToPollLink) {
            backToPollLink.addEvent('click', function (evt) {
                evt.stop();
                pollRequest.send();
            });
        }
    };
    
    //Script for removing number of selections allowed dropdown,
    //unless the allow multiple selections box is checked
    pollEditForm = $('create-poll-form');
    if (pollEditForm) {
        allowMultipleSelections = $('id_allow_multiple_selections');
        numberSelectionsAllowed = $('id_number_selections_allowed');
        if (allowMultipleSelections) {
            
            if (allowMultipleSelections.checked) {
                numberSelectionsAllowed.style.display = '';                
            } else {
                numberSelectionsAllowed.style.display = 'none'; 
            }
            
            allowMultipleSelections.addEvent('click', function (evt) {
                if (allowMultipleSelections.checked) {
                    numberSelectionsAllowed.style.display = '';
                } else {
                    numberSelectionsAllowed.style.display = 'none';
                }
            });
        }
        
        addAnswerButton = $('add-answer-button');
        if (addAnswerButton) {
            
            answerList = $('answer-list');
            totalForms = $('id_answers-TOTAL_FORMS');
            
            addAnswerButton.addEvent('click', function () {
                addAnswerField(answerList, totalForms);
            });
        }
        
        deleteAnswerButtons = $$('.delete-answer-button');
        if (deleteAnswerButtons) {
            deleteAnswerButtons.addEvent('click', function (evt) {
                deleteButton = $(evt.target.id);
                deleteAnswerField(deleteButton);
            });
        }
        
        var addAnswerField = function (parent, totalForms) {            
            //new list element
            var newListElement = new Element('li').inject(parent);
            
            //new input field
            var newField = new Element('input', {
                id: 'id_answers-' + totalForms.value + '-text',
                type: 'text',
                name: 'answers-' + totalForms.value + '-text',
                maxlength: '500'
            }).inject(newListElement);
            
            //new delete button - id off by 1
            var newDeleteButton = new Element('input', {
                id: Number(totalForms.value) + 1,
                class: 'delete-answer-button',
                type: 'button',
                value: 'Delete',
                events: {
                    click: function () {
                        deleteAnswerField(newDeleteButton);
                    }
                }
            }).inject(newListElement);
            
            //hidden elements (id and poll)
            var hiddenId = new Element('input', {
                type: 'hidden',
                name: 'answers-' + totalForms.value + '-id',
                id: 'id_answers-' + totalForms.value + '-id'
            }).inject(parent);
            
            var hiddenPoll = new Element('input', {
                type: 'hidden',
                name: 'answers-' + totalForms.value + '-poll',
                id: 'id_answers-' + totalForms.value + '-poll'
            }).inject(parent);
            
            //Off by 1 element numbers, increment by 1 after adding elements
            elementNumber = Number(totalForms.value) + 1;
            totalForms.setProperty('value', elementNumber);
        }
        
        var deleteAnswerField = function (element) {
            //answer id # - off by 1
            answerId = Number(element.id) - 1;
            
            //parent is the list element
            var parent = element.getParent();
            //destroying parent, automatically removes input element and delete button
            parent.destroy();
           
            //Hidden elements (id and poll) need to be removed
            answerIdField = $('id_answers-' + answerId + '-id');
            if (answerIdField) {
                answerIdField.destroy();
            }
            answerPollField = $('id_answers-' + answerId + '-poll');
            if (answerPollField) {
                answerPollField.destroy();
            }
        }
    }
});