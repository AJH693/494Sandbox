<script src="/static/jquery-2.1.1.min.js"></script>
<script type="text/javascript">

  $(document).ready(function(){
    $('.EDIT_ONLY').remove();
    $('.PREVIEW_ONLY').remove();
    // Don't show the questionList until after the EDIT_ONLY and PREVIEW_ONLY items are removed
    $('#questionList').show();
    
    $('#submit').click(function(){
      var automaticQuestions = [];
      var manualQuestions = [];
      $('.automatic-grading').each(function(){
        var question = $(this);
        var data = {};
        data['options'] = [];
        data['not-graded'] = $(this).hasClass('not-graded');
        data['questionID'] = question.attr('id');
        data['questionContent'] = question.find(".question-content").text();
        question.find(':radio:visible').each(function(){
          data['options'].push($(this).attr('id'));
        });
        data['selectedOption'] = question.find(':radio:checked').attr('id');
        data['selectedOptionText'] = question.find(':radio:checked').parent().next('p').text();
        automaticQuestions.push(data);
      });
      $('.manual-grading').each(function(){
        var question = $(this);
        var data = {};
        data['not-graded'] = $(this).hasClass('not-graded');
        data['questionID'] = question.attr('id');
        data['response'] = question.find('#student-response').val();
        data['questionContent'] = question.find(".question-content").text();
        data['correctness'] = -1;
        data['critical'] = null;
        manualQuestions.push(data);
      });
      var endTaskTime = new Date();
      console.log(endTaskTime);
      var totalTaskTime = endTaskTime.getTime() - startTaskTime.getTime();
      var data = {};
      data['automatic_questions'] = automaticQuestions;
      data['supplementary'] = supplementaryInformationTimes;
      data['supplementaryOrder'] = supplementaryInformationOrder;
      data['manual_questions'] = manualQuestions;
      data['startTaskTime'] = getFormattedDatetime(startTaskTime);
      data['endTaskTime'] = getFormattedDatetime(endTaskTime);
      data['totalTaskTime'] = totalTaskTime/1000;
      data['xmlData'] = informationForXML;
      $.ajax({
        url: window.location.pathname,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success:  function(data) {
          window.location.href='{{url_for("home")}}'
        },
        error: function(data){
          console.log(data);
        }
      });
    });
    var startTaskTime = new Date();
  });
  function getFormattedDatetime(time) {
    var month = ('0' + (time.getMonth() + 1)).slice(-2)
        date = ('0' + time.getDate()).slice(-2),
        year = time.getFullYear();
    return month + '/' + date + '/' + year + ' ' + time.toLocaleTimeString();

  };
 
</script>