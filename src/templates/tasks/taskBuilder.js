<script src="/static/jquery-2.1.1.min.js"></script>
<script type="text/javascript">
  $(document).ready(function(){
    initEditTask();
    makeDroppable($('div.elementWell'));

    // fills in courses in the submission dropdown
    getCoursesTeaching();

    $("div.element").draggable({
      scroll: false,
      revert: true,
      distance: 25,
      appendTo: 'body',
      helper: 'clone'
    });

    $('#preview').click(function(){
      if (answerKeyCompleted() == false){
        $("#key_alert").show();
      }
      else {
        $('.EDIT_ONLY').toggle();
        $('.TAKE_ONLY').toggle();
        $('.delete-if-empty').each(function(){
          var toCheck;
          if($(this).hasClass('panel-heading')){
            toCheck = $(this).find('h3');
          } else if($(this).hasClass('question-content')){
            toCheck = $(this).find('textarea')
          } else{
            toCheck = $(this)
          }
          if(toCheck.html().trim().length == 0){
            $(this).hide();
          }
        });
        if ($(this).text() == "Preview"){
          $(this).text("Edit");
        }
        else {
          $(this).text("Preview");
        }
      }      
    });

    $('#delete-all').click(function(){
      $('button.delete-question').each(function(){
        deleteAllQuestions();
      });
    });

    $("#taskDueDate").datepicker();
    $("#taskDueTime").timepicker();

    $('#submission-modal-form').submit(function(event) {
        // dont' reload the page on form submit
        event.preventDefault();
    });
  });
</script>