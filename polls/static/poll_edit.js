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
        totalForms = $('id_answers-TOTAL_FORMS');
        
        if (answerList) {
            sortables = new Sortables('#sortable-answer-list UL', {
                clone: true,
                handle: true,
                revert: true,
                opacity: 0.7,
                onComplete: function () {
                    answerOrder();
                }
            });
            
            answerList.getChildren('li').each(function(li) {
                li.getChildren('input').each(function(input) {
                    //If the checkbox is selected, don't show the list element
                    if (input.type == 'checkbox') {
                        if (input.checked == true) {
                            //hide the list element
                            li.hide();
                        }
                    }
                });
            });
        }
        
        addAnswerButton = $('add-answer-button');
        if (addAnswerButton) {
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
            
            //new checkbox field
            var newCheckbox = new Element('input', {
                id: 'id_answers-' + totalForms.value + '-DELETE',
                type: 'checkbox',
                name: 'answers-' + totalForms.value + '-DELETE',
            }).inject(newListElement);
            
            //new order field
            var newOrderField = new Element('input', {
                id: 'id_answers-' + totalForms.value + '-ORDER',
                type: 'text',
                name: 'answers-' + totalForms.value + '-ORDER',
            }).inject(newListElement);
            
            //new delete button
            var newDeleteButton = new Element('input', {
                id: Number(totalForms.value),
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
            }).inject(newListElement);
            
            var hiddenPoll = new Element('input', {
                type: 'hidden',
                name: 'answers-' + totalForms.value + '-poll',
                id: 'id_answers-' + totalForms.value + '-poll'
            }).inject(newListElement);
            
            //Off by 1 element numbers, increment by 1 after adding elements
            elementNumber = Number(totalForms.value) + 1;
            totalForms.setProperty('value', elementNumber);
        }
        
        var deleteAnswerField = function (element) {
            
            //answer id #
            answerId = Number(element.id);
            
            //parent is the list element
            var parent = element.getParent();
            //hide the element
            parent.hide();
            
            deleteCheckbox = $('id_answers-' + answerId + '-DELETE');
            //selecting the checkbox uses built in functionality from django
            deleteCheckbox.setProperty('checked', true);
            
            //Off by 1 element numbers, decrease by 1 after deleting elements
            elementNumber = Number(totalForms.value) - 1;
            totalForms.setProperty('value', elementNumber);
        }
        
        var answerOrder = function () {
            order = 1;
            answerList.getChildren('li').each(function(li) {
                li.getChildren('input').each(function(input) {
                    //set the order value
                    if (input.type == 'text') {
                        //ignore blank fields
                        if (input.value) {
                            if (input.id.substr(-5,5) == 'ORDER') {
                                input.setProperty('value', order);
                                order = order + 1;
                            }
                        }
                    }
                });
            });
        }
    } 
});
