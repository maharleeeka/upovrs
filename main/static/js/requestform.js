var i = 1;

function repeat() {
  var div = document.getElementById('schedule'),
    clone = div.cloneNode(true); // true means clone all childNodes and all event handlers
	clone.id = "schedule1";
	document.body.appendChild(clone);
}


function dateAdded() {
  /* by charie: PLEASE DO NOT MODIFY THIS FUNCTION. Will be minified further */

  /*get the input values*/
  var date = document.getElementsByName('date_needed')[0].value;
  var timeFrom = document.getElementsByName('time_from')[0].value;
  var timeTo = document.getElementsByName('time_to')[0].value;

  /* create new elements on html*/
  var iDiv = document.createElement('div');
  var input_1 = document.createElement('input');
  var input_2 = document.createElement('input');
  var input_3 = document.createElement('input');
  var btn = document.createElement ('span');
  
  /* set id and class for div*/
  iDiv.id = 'added_date_' + i;
  iDiv.className = 'col-md-12 block';

  /* create name attribute for the input tags*/
  var att_1 = document.createAttribute('name');
  var att_2 = document.createAttribute('name');
  var att_3 = document.createAttribute('name');
  var click = document.createAttribute('onclick');
  var role = document.createAttribute('role');

  /*set the inputs*/
  input_1.setAttributeNode(att_1);
  att_1.value = "date_needed";
  input_1.className = 'col-md-3';
  input_1.value = date;
 
  input_2.setAttributeNode(att_2);
  att_2.value = "time_from";
  input_2.className = 'col-md-3';
  input_2.value = timeFrom;

  input_3.setAttributeNode(att_3);
  att_3.value = "time_to";
  input_3.className = 'col-md-3';
  input_3.value = timeTo;  

  btn.setAttributeNode(click);
  btn.setAttributeNode(role);
  click.value = "this.parentNode.remove();";           /* remove date when click*/
  role.value = "button";
  btn.className = 'glyphicon glyphicon-remove';

  /* append input tags to div tag*/
  iDiv.appendChild(input_1);
  iDiv.appendChild(input_2);
  iDiv.appendChild(input_3);
  iDiv.appendChild(btn);

  /* append div tag to html body*/
   document.getElementById('added_date').appendChild(iDiv);
   i++;

}

function checkDateFields() {
  /*by charie: PLEASE DO NOT MODIFY THIS FUNCTION*/
  var i = 0;
  var input = document.getElementById('schedule').getElementsByTagName('input');

  for (i = 0; i < input.length; i++){
    if (input.item(i).value == ''){
      alert("Please fill fields needed for reservation date");
      break;
    }
  }

  if (i >= input.length){
    if (checkDate() == true){
      dateAdded();
    }
  }
}


function validateForm(){
	console.log('ja');
	var valid = true;
	var required = document.getElementsByClassName("required");
	for (var i=0; i < required.length; i++){
		if (required.item(i).value == ''){
			alert("Please fill all required fields");
			valid = false;
			break;
		}
	}

  //for equipment
  var x = document.getElementsByClassName("check");
  var y = document.getElementsByClassName("unit_field");

  for (var i=0; i < x.length; i++){
    if (x[i].checked == true && y[i].value == ''){
      alert("Please provide number of units for equipment to be rented.");
      valid = false;
      break;
    }
    if (!isInteger(y[i].value)) {
      alert("Must input integer only for the units.");
      valid = false;
      break;
    }
  }

	if (valid){
    valid = checkDate();

  	if(valid){
  		var form = document.getElementById("request_form");
  		form.submit();
  	}
  }
}


function checkDate() {
    var EnteredDate = document.getElementById("date_needed").value; //for javascript

    var EnteredDate = $("#date_needed").val(); // For JQuery
    var myDate = new Date(EnteredDate);
 
    var today = new Date();
    today.setDate(today.getDate() + 2);

    console.log(today + " " + myDate);

    if (myDate > today) {
        return true;
    }
    else {
        alert("Reservation must be done 3 days before your desired reservation date. ");
        return false;
    }
}

function enable() {
  var x = document.getElementsByClassName("unit_field");
  var y = document.getElementsByClassName("check");
  var i;
  
  for (i = 0; i < x.length; i++) {
      if(y[i].checked){
        x[i].disabled = false;
      }
      else{
        x[i].disabled = true;
      }
  }
    
}

function isInteger(x) {
        return x % 1 === 0;
}
