addEvent('domready', function () {
    //Script for removing number of selections allowed dropdown,
    //unless the allow multiple selections box is checked
    pollEditForm = $('create-poll-form');
    if (pollEditForm) {
        allowMultipleSelections = $('id_allow_multiple_selections');
        numberSelectionsAllowed = $('id_number_selections_allowed');
        if (allowMultipleSelections) {
            
            if (allowMultipleSelections.checked) {
                numberSelectionsAllowed.show();                
            } else {
                numberSelectionsAllowed.hide(); 
            }
            
            allowMultipleSelections.addEvent('click', function (evt) {
                numberSelectionsAllowed.toggle();
            });
        }
        
        answerList = $('answer-list');
        
        if (answerList) {
            new Sortables('#sortable-answer-list UL', {
                clone: true,
                handle: true,
                revert: true,
                opacity: 0.7
            });
        }
        
        addAnswerButton = $('add-answer-button');
        if (addAnswerButton) {
            totalForms = $('id_answers-TOTAL_FORMS');
            
            addAnswerButton.addEvent('click', function () {
                addAnswerField(answerList, totalForms);
            });
        }
        
        deleteAnswerButtons = $$('.delete-answer-button');
        if (deleteAnswerButtons) {
            deleteAnswerButtons.addEvent('click', function () {
                deleteAnswerField(this);
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
