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
            sortables = new Sortables('#sortable-answer-list UL', {
                clone: true,
                handle: true,
                revert: true,
                opacity: 0.7,
                onComplete: function () {
                    answerOrder();
                }
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
            
            //answer id # - off by 1
            answerId = Number(element.id);
            
            //parent is the list element
            var parent = element.getParent();
            //destroying parent, removing elements
            //parent.destroy();
            parent.hide();
            
            deleteCheckbox = $('id_answers-' + answerId + '-DELETE');
            deleteCheckbox.setProperty('checked', true);
            
            //Off by 1 element numbers, decrease by 1 after deleting elements
            elementNumber = Number(totalForms.value) - 1;
            totalForms.setProperty('value', elementNumber);
            
            //reorderAnswers
            //reorderAnswers();
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
        
        /*var reorderAnswers = function () {
            //id's start at 0 and increment after the last hidden element is reached.
            count = 0;
            answerList.getChildren('li').each(function(li) {
                li.getChildren('input').each(function(input) {
                    //rename the id's and names of the input elements after sorting
                   if (input.type == 'text') {
                       //ignore blank fields
                        if (input.value) {
                            if (input.id.substr(-4,4) == 'text') {
                                input.setProperties({
                                    'id': 'id_answers-' + count + '-text',
                                    'name': 'answers-' + count + '-text'
                                });
                            } else if (input.id.substr(-5,5) == 'ORDER') {
                                //input.setProperty('id', 'id_answers-' + count+1 + '-ORDER');
                                //input.setProperty('name', 'answers-' + count+1 + '-ORDER');
                                order = count + 1;
                                //input.setProperty('value', order);
                                console.log(input);
                                input.removeProperty('value');
                                input.setProperty('value',order);
                                console.log(input.value);
                            }
                        }
                    } else if (input.type == 'button') {
                        input.setProperty('id', count);
                    } else if (input.type == 'checkbox') {
                        input.setProperty('id', 'id_answers-' + count + '-DELETE');
                        input.setProperty('name', 'answers-' + count + '-DELETE');
                    } else if (input.type == 'hidden') {
                        //Two hidden fields. Need to know if it's id or poll
                        if (input.id.substr(-2,2) == 'id') {
                            input.setProperty('id', 'id_answers-' + count + '-id');
                            input.setProperty('name', 'answers-' + count + '-id');
                        } else {
                            input.setProperty('id', 'id_answers-' + count + '-poll');
                            input.setProperty('name', 'answers-' + count + '-poll');
                            count = count + 1;
                        }
                    }
                });
            });
        }*/
        
         pollEditForm.addEvent('submit', function (evt) {
             
            // reorderAnswers();
             //evt.stop();
         });
    } 
});
