//var i = 0;
//var original = document.getElementById('schedule');

function repeat() {
  // var clone = original.cloneNode(true);
  // clone.id = "schedule" + ++i; 
  // original.parentNode.appendChild(clone);

  var div = document.getElementById('schedule'),
    clone = div.cloneNode(true); // true means clone all childNodes and all event handlers
	clone.id = "schedule1";
	document.body.appendChild(clone);
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

	if (valid){
    valid = checkDate();

  	if(valid){
  		var form = document.getElementById("request_form");
  		form.submit();
      var form2 = document.getElementById("rentedequipments_form");
      //form2.submit();
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

