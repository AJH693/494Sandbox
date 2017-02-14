<script type="text/javascript">  
  var supplementaryInformationTimes = {}; 
  var supplementaryInformationMinTimes = {};
  var supplementaryInformationOrder = [];
  var informationForXML = [];
  function answerKeyCompleted(){
    var ret = true;
    $('.automatic-grading').each(function(){
          var question = $(this);
          if (question.hasClass('not-graded')){
            return;
          }
          if (question.find(':radio:checked').length == 0){
            ret = false;
          }
    })
    return ret;
  }

  function hideAnswerKeyAlertIfAppropriate(){
    if (answerKeyCompleted()){
      $("#key_alert").hide();
    }
  }

  function allFilesUploaded(){
    var ret = true;
    $('.supplementary-target').each(function(){
      var url_field = $(this).find('div.wp-file-text');
      if(url_field.length > 0 && url_field.html().trim().length < 5){
        ret = false;
      }
    })
    return ret;
  }

  function hideFileAlertIfAppropriate(){
    if (allFilesUploaded()){
      $("#file_alert").hide();
    }
  }

  function createElement(elementWell, elementToCreate){
      $('#elementWell').css("height","100px");
      $('#elementWell').html("<br><br>Add more elements here.");
      elementWell.before("<div class='elementTarget'></div>");
      var target = elementWell.parent().find(".elementTarget").first();
      target.load("/" + elementToCreate.data('filepath'));
      target.hide().fadeIn(700);
      target.removeClass('elementTarget');
      return target;
  }
  function makeDroppable(element){
    element.droppable({
      drop: function(event, ui){
        var elementWell = $(this);
        var element = ui.draggable;
        var newElement = createElement(elementWell, element);
        makeDroppable(newElement);     
      }
    })
  }
  function getVideoURL(original){
    // will likely need to add more url handlers later, 
    // for now we support youtube urls
    if(original.indexOf("<iframe") >= 0){
      var src = original.substring(original.indexOf('src="')+5);
      src = src.substring(0,src.indexOf('"'));
      return src;
    } else if(original.indexOf("watch?v=") >= 0){
      return original.replace("watch?v=","embed/")
    } else {
      return original;
    }
  }

  function updateVideoSRC(changeEvent){
    var src = getVideoURL($(changeEvent).val());
    $(changeEvent).parent().find('.wp-video-panel').attr("src", src)
  }
  function modalTiming(event){
    var endDate = new Date();
    var endTime = endDate.getTime();
    var duration = endTime - event.data.startTime;
    $('.modal').data("supplementaryDuration",duration/1000);
    if(supplementaryInformationTimes[event.data.modalID]){
          supplementaryInformationTimes[event.data.modalID] = supplementaryInformationTimes[event.data.modalID] + duration/1000;
    }else{
          supplementaryInformationTimes[event.data.modalID] = duration/1000;
    }
    var xmlData = {};
    xmlData['start'] = event.data.startTime;
    xmlData['end'] = endTime;
    xmlData['id'] = event.data.modalID;
    informationForXML.push(xmlData);
    $('.modal').off('hide.bs.modal');       
    
  }

  function showSubmitModal(){
    showModal('submission-modal');
  }

  function showModal(idToShow){
    if (answerKeyCompleted() == false){
      $('#key_alert').show();
    }
    else if(allFilesUploaded() == false){
      $('#file_alert').show();
    }
    else {
      $("#"+idToShow).find('.modal').modal('toggle');
    }
  }
  function clickVideo(clkevent){
    var src = $(clkevent).parent().find('.wp-video-panel').attr('src');
    $(clkevent).parent().find('iframe').attr('src', src);
    var modal = $(clkevent).parent().find('.modal');
    modal.modal('toggle');
    var startDate = new Date();
    $('.modal').data("supplementaryDuration",startTime);
    $('.modal').on('hidden.bs.modal', function () {
      $('iframe').attr('src', $('iframe').attr('src'));
    }); 
    var modalID = $(modal).attr('id');
    var startTime = startDate.getTime();
    supplementaryInformationOrder.push($(modal).attr('id'));
    $('.modal').on('hide.bs.modal', {startTime: startTime, modalID: modalID}, modalTiming);
  }
  function clickImage(clkevent){
    console.log($(clkevent).parent().find('img').attr('src'));
    var src = $(clkevent).parent().find('img').attr('src');
    $(clkevent).parent().find('iframe').attr('src', src);
    var modal = $(clkevent).parent().find('.modal');
    modal.modal('toggle');    
    var startDate = new Date();
    $('.modal').on('hidden.bs.modal', function () {
      $('iframe').attr('src', $('iframe').attr('src'));
    });
    var modalID = $(modal).attr('id');
    var startTime = startDate.getTime();
    supplementaryInformationOrder.push($(modal).attr('id'));
    $('.modal').on('hide.bs.modal', {startTime: startTime, modalID: modalID}, modalTiming);

  }
  function clickFile(clkevent){
    var src = $(clkevent).parent().find('.wp-file-title-label').attr('src');
    console.log(src);
    $(clkevent).parent().find('iframe').attr('src', src);
    var modal = $(clkevent).parent().find('.modal');
    modal.modal('toggle');    
    var startDate = new Date();    
    $('.modal').on('hidden.bs.modal', function () {
      $('iframe').attr('src', $('iframe').attr('src'));
    });
    var modalID = $(modal).attr('id');
    var startTime = startDate.getTime();
    supplementaryInformationOrder.push($(modal).attr('id'));
    $('.modal').on('hide.bs.modal', {startTime: startTime, modalID: modalID}, modalTiming);

  }

  function setBtnWidth(ctx, newSize){
    var newClass = 'col-md-' + Math.floor(12/newSize);
    var container = $(ctx).closest('div.question-parent');
    $(container).find('.wp-supplementary').each(function(){
      var cur = $(this).find('.panel-body')
      $(cur).removeClass('col-md-2')
      $(cur).removeClass('col-md-3')
      $(cur).removeClass('col-md-4') 
      $(cur).removeClass('col-md-6') 
      $(cur).removeClass('col-md-12') 
      $(cur).addClass(newClass)
    })
  }

  function addSuppElement(ctx, appendID){
    var toAppend = $(ctx).closest('.panel-body').find('.supplementary-target');
    var html = $(appendID).html();
    html = html.replace("nextID", getNextID('supplementary'));
    html = html.replace("nextMinTimeID", getNextID('minTime'));
    toAppend.append(html);
  }
  function addVideo(ctx){
    addSuppElement(ctx, '#wp-video-template')
  };
  function addAudio(ctx){
    addSuppElement(ctx, '#wp-audio-template')
  };
  function addText(ctx){
    addSuppElement(ctx, '#wp-text-template')
  };
  //Also used for other file upload
  function addImage(ctx){
    addSuppElement(ctx, '#wp-image-template')
  };
  function addOtherFile(ctx){
    addSuppElement(ctx, '#wp-file-template')
  };
  function addTextLabel(ctx){
    addSuppElement(ctx, '#wp-text-label-template')
  };

  function upload(f, onsuccess){
    if($(f).find('input:file').val().trim().length < 5){
      console.log("Nothing selected");
      // the user didn't select anything in the file chooser window. exit.
      return;
    }
    var form_data = new FormData(f);
    var uploadUrl = '/upload/{{ session.userid }}';
    $.ajax({
        type: 'POST',
        url: uploadUrl,
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: onsuccess,
    });
  }

  function uploadImageFile(f) {
    var onsuccess = function(data) {
      var src = $(f).find('input').val();
      src = src.split("\\")[2]
      $(f).find('.wp-file-text').html(src)
      src = "/static/uploads/{{ session.userid }}/" + src;
      $(f).closest('div.wp-image').find('img').attr("src", src);
      hideFileAlertIfAppropriate();
    }

    upload(f, onsuccess);
  }

  function uploadFile(f) {
    var onsuccess = function(data) {
      var src = $(f).find('input.wp-file-src').val();
      src = src.split("\\")[2];
      $(f).find('.wp-file-text').html(src)
      src = "/static/uploads/{{ session.userid }}/" + src;
      $(f).parent().parent().find('h3').first().attr("src", src);
      hideFileAlertIfAppropriate();
    }

    upload(f, onsuccess);
  }

  function uploadAndEmbedFile(f) {
    var onsuccess = function(data){
      var src = $(f).find('input.wp-file-src').val();
      src = src.split("\\")[2];
      $(f).find('.wp-file-text').html(src)
      src = "/static/uploads/{{ session.userid }}/" + src;
      // set the iframe src to the path of where the file was uploaded
      $(f).closest('.panel-body').find('iframe').first().prop('src', src);
      hideFileAlertIfAppropriate();
    }    

    upload(f, onsuccess)
  }

  function changeTitle(element){
    $(element).closest('div.wp-file').find('h3').text($(element).val());
  }

  function textChange1Parent(element){
    var id_str = "#p_" + $(element).attr('id');
    $(element).parent().find(id_str).text($(element).val());
  }
  function textChange(element){
    var id_str = "#p_" + $(element).attr('id');
    $(element).parent().parent().find(id_str).text($(element).val());
  }
  function textChangeBySibling(element){
    var id_str = "#p_" + $(element).attr('id');
    $(element).next('p').text($(element).val());
  }

  function adjustHeight(input, toAdjust) {
    var newHeight = $(input).val() + "%"
    $(toAdjust).find('iframe').css('height', newHeight)
  }

  function copyTextToInput(textfield, inputfield, parentDepth){
    if(arguments.length == 2){
      $(textfield).each(function(){
        var textfield_content = $(this).text();
        $(this).parent().find(inputfield).val(textfield_content);
      })
    }
    else if(arguments.length == 3){
      $(textfield).each(function(){
        var textfield_content = $(this).text();
        var cur = $(this);
        for(i = 0; i < parentDepth; i++){
          cur = cur.parent();
        }
        cur.find(inputfield).val(textfield_content);
      })      
    }
  }

  function initEditTask(){
    $('.EDIT_ONLY').show();
    $('.PREVIEW_ONLY').show();
    $('.TAKE_ONLY').hide();
    $('#preview').text("Preview");
    
    // <p> elements --> <input> fields
    copyTextToInput('p.question-content', '#body');
    copyTextToInput('p.multichoice-content', 'input.form-control');
    copyTextToInput('#p_title', 'input.form-control');
    copyTextToInput('.wp-pair-text', '.wp-pair-input');
    copyTextToInput('.wp-pair-text-2', '.wp-pair-input-2', 2);
    
    // wp-video-panel attr src --> .wp-video-src
    $('.wp-video-panel').each(function(){
      var src = $(this).attr('src');
      $(this).parent().find('.wp-video-src').val(src);
    })

    // supp material duration --> input field
    {% if supplementary %}
      var supplementary = {{ supplementary }}
      for(var id in supplementary){
        $('#' + supplementary[id].inputID).val(supplementary[id].time)
      }
    {% endif %}

    // select all the auto-graded options selected previously
    {% if correct_options %}
      var answers = {{ correct_options }}
      for(var i in answers){
        $('#' + answers[i].correctOption).prop('checked', true);
      }
    {% endif %}

    applyQuestionJS();
    applyMultiChoiceJS();
  }

  function applyMultiChoiceJS(){
    $('.multipleChoice').each(function(){
      $(".glyphicon-trash").click(function(){
        $(this).closest("div").parent().remove();
      });
      var mcID = '#' + $(this).prop("id")
      $(mcID).parent().find('.new-response').click(function(){
        addRadioResponse(mcID);
      })
    })
  }

  function applyQuestionJS(){
    $('.delete-question').click(function(){
      var row = $(this).closest('.row');
      row.fadeOut(200, function(){
        row.remove();
        hideAnswerKeyAlertIfAppropriate();
        hideFileAlertIfAppropriate();
      });
      if($(".question-parent").length <= 1){
        $('#elementWell').css("height","300px");
        $('#elementWell').html("<br><br>To begin, drag elements onto the screen.");
      }
    });
    $('.delete-header').click(function(){
      $(this).closest('.panel-heading').fadeOut();
    });
    $('.TAKE_ONLY').hide();

    $('#notSet').attr('id', getNextID('question'));
  }

  function getNextID(baseID){
    var nextID = 0;
    while($('#' + baseID + nextID).length == 1)
      nextID++;
    return baseID + nextID;
  }

  function addRadioResponse(ctx){
    var toAdd = "<div><div class='input-group'>" 
      + $(ctx).find(".radioResponse").html() 
      + "</div><br></div>";
    $(ctx).append(toAdd);
    $(ctx).find(":radio").last().attr('id', getNextID('choice'));
    $(".glyphicon-trash").click(function(){
      $(this).closest("div").parent().remove();
    });
  };

  function getCoursesTeaching(){
    $.ajax({
      url         :'{{ url_for("courses_teaching")}}',
      type        :"GET",
      success     :function(result) {
          var coursesList = $.parseJSON(result);
          
          var strCoursesList="";
          for(var i=0; i < coursesList.length;i++){
              url = "{{url_for('view_course', courseID='')}}";
              url += coursesList[i].id + 1000;
              strCoursesList+="<option id='" + coursesList[i].id + "' value='"+coursesList[i].name+"'>";
              strCoursesList+=coursesList[i].name;
              strCoursesList+="</option>";
          }
          if(coursesList.length == 0){
              strCoursesList+="<option disabled>No Courses</option>";
          }
          $('#taskbuilder_viewable_courses').html(strCoursesList);
      }
    });
  }

  function deleteAllQuestions(){
    $('#elementWell').css("height","300px");
    $('#elementWell').html("<br><br>To begin, drag elements onto the screen.");
    $('#questionList').find('.question-parent').each(function(){
      var toDel = $(this);
      toDel.fadeOut(200, function(){toDel.remove()});
    });
  }

  function submitClicked() {
      var xmlData = []
      var suppIndex = 0;
      $('.supplementary-target').first().find('.wp-supplementary').each(function(){
        var xd = {};
        xd['text'] = $(this).find('h3').text();
        xd['id'] = $(this).find('.modal').attr('id');
        var c = $(this).find('.panel-body').first().attr('class');
        var index = c.search('col-md');
        var size = parseInt(c.charAt(index+7));
        var columnsPerRow = 12/size;
        xd['row'] = Math.floor(suppIndex/columnsPerRow);
        xd['col'] = suppIndex % columnsPerRow;
        xmlData.push(xd);
        suppIndex += 1;
      })
      $('[id^=minTime]').each(function(){
        var thisID = $(this).prop('id');
        var index = parseInt(thisID.split("minTime")[1]);
        var time = parseInt($('#' + thisID).val());
        if(time <= 0)
          return;
        var d = {};
        d['id'] = "supplementary" + index;
        d['inputID'] = thisID;
        d['time'] = time;
        d['title'] = $('#' + thisID).parent().find('#title').val()
        supplementaryInformationMinTimes["supplementary" + index] = d;
      })
      var questions = [];
      $('.automatic-grading').each(function(){
          var question = $(this);
          var data = {};
          data['options'] = [];
          data['not-graded'] = $(this).hasClass('not-graded');
          data['questionID'] = question.attr('id');
          question.find(':radio:visible').each(function(){
            data['options'].push($(this).attr('id'));
          });
          data['correctOption'] = question.find(':radio:checked').attr('id');
          data['correctOptionText'] = question.find(':radio:checked').parent().parent().find('p').text();
          questions.push(data);
      })
      var data = {};
      data['html'] = $('#questionList').html();
      data['questions'] = questions;
      data['supplementary'] = supplementaryInformationMinTimes;
      data['course_id'] = $('#taskbuilder_viewable_courses option:selected').prop('id')
      data['taskTitle'] = $('#taskTitle').val()
      data['xmlData'] = xmlData;

      // Construct a JS date object
      var date = $('#taskDueDate').val().split('/');
      var hoursMins = $('#taskDueTime').val().split(':');
      var hours = parseInt(hoursMins[0]);
      if(hoursMins[1].indexOf('pm') > -1 || hoursMins[1].indexOf('PM') > -1)
        hours = 12 + parseInt(hoursMins[0]);
      var mins = parseInt(hoursMins[1].substring(0,2));
      var dueOn = new Date(date[2], parseInt(date[0])-1, date[1], hours, mins, 0, 0).getTime();
      data['taskDue'] = dueOn;

      {% if task_id %}
        var postURL = "{{ url_for('taskBuilder_edit', taskID=task_id)}}"
      {% else %}
        var postURL = '{{ url_for("taskBuilder") }}'
      {% endif %}

      $.ajax({
          url: postURL,
          type: 'POST',
          contentType: 'application/json',
          data: JSON.stringify(data),
          success: function(data){
            window.location.href='{{url_for("home")}}';
          },
          error: function(data){
              console.log(data);
          }
      });
  }

</script>
