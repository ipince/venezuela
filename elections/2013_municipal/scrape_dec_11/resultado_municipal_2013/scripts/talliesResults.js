
var myTable;
var globalTableName;
var CAFound = false;
var globalShowTally = false;
var globalShowTallyImage = false;
var globalPathImage;

var configurationPath = "../../data/tallyConfiguration.json";
var globalPathDocument="../../talliesImages/";
var globalPathContest;
var globalPathDocumentTally="/STATION_TALLY_WITHOUT_PARTY_ENDORSEMENT/";
var globalPathImageTally;
var tallyFormat = ".jpg";
var tallyWidth=500;
var tallyHeight=600;
var	showTallyImage = true;
var	showTallyPopUp = false;
var	showTallyOtherTab = false;
var globalPrintedWidth;
var globalPrintedHeight;

function displayTally(name,lvgCode,contest,pathTally,pathImage,tableName,showTally,showImage,divImageDetail){
	globalTableName = tableName;
	globalShowTally = showTally;
	globalShowTallyImage = showImage;
	globalPathImage = pathImage;
	globalPathImageTally = globalPathDocument;
	
	/*Load configuration file */
	if(fileExists(configurationPath)){
		$.getJSON(configurationPath, function(config) {
			globalPathDocument = config.globalPathDocument;
			tallyWidth = config.tallyWidth;
			tallyHeight = config.tallyHeight;
			showTallyImage = config.showTallyImage;
			showTallyPopUp = config.showTallyPopUp;
			showTallyOtherTab = config.showTallyOtherTab;
			globalPrintedWidth = config.globalPrintedWidth;
			globalPrintedHeight = config.globalPrintedHeight;

			if($("#"+name).is(':visible')){
				$("#"+name).hide('slow');
				$("#"+divImageDetail+"_"+contest).show('slow');
				return;
			}

			myTable = document.getElementById(globalTableName);
			if(myTable.childElementCount <= 1){	
				d3.json(pathTally, function(tally){ 
					if(tally != undefined ){
						addTally(tally,contest);
						$("#"+name).show('slow');
					}			
			
					// Reset the globalName
					globalTableName="";
				});
			}else{
		
				$("#"+name).show('slow');
			}
	
			$("#"+divImageDetail+"_"+contest).hide('slow');

		});
	}

}

function addTally(tally,contest){

	myTable = document.getElementById(globalTableName);
	
	/* Add tally type */
	addTallyType(myTable,tally);

	/* Add global vars */
	addTallyGlobalParameters(myTable,tally);
	
	/* Add option register */
	if(globalShowTally){
		if(tally.optionsRegister != undefined && tally.optionsRegister.length > 0){
			for(var i=0;i<tally.optionsRegister.length;i++){
				var option = tally.optionsRegister[i];
				addOptionRegister(option,myTable);
			}
		}
	}
	
	/* Add tally info */
		addTallyInformation(myTable,tally);
	
	/* Add image */
	if(globalShowTallyImage){
		addTallyImage(myTable,tally,contest);
	}

}

function addOptionRegister(option,myTable){
   	var newTR = document.createElement("tr");
	newTR.setAttribute('class','tblightrow');

   	var ballotName = document.createElement("td");
   	ballotName.setAttribute('class','lightRowContent');
   	ballotName.setAttribute('align','left');
   	ballotName.setAttribute('width','60%');
   	ballotName.innerHTML = option.ballotName;;

	
   	var partyName = document.createElement("td");
	partyName.setAttribute('class','lightRowContent');
	partyName.setAttribute('align','left');
	partyName.setAttribute('width','30%');    	
	partyName.innerHTML = option.partyAbb;

   	var votes = document.createElement("td");
	votes.setAttribute('class','lightRowContent');
	votes.setAttribute('align','right');
	votes.setAttribute('width','10%');    	
	votes.innerHTML = option.amount;
   
	newTR.appendChild(ballotName);  
	newTR.appendChild(partyName);  
	newTR.appendChild(votes);  

	myTable.appendChild(newTR);
}


function addTallyImage(myTable,tally, contest){

	var href=globalPathImage;
	var exist = fileExists(href);

	if(exist){
		myTable = document.getElementById(globalTableName);
	
		/* Add the tally link */
		var newTR = document.createElement("tr");
		newTR.setAttribute('class','tblightrow');
		newTR.setAttribute('class','tblightrow');

	   	var tallyImageTd = document.createElement("td");
	   	tallyImageTd.setAttribute('class','lightRowContent');
	   	tallyImageTd.setAttribute('align','center');
	   	tallyImageTd.setAttribute('width','100%');
	   	tallyImageTd.setAttribute('colspan','3');


		/* Open a new tab */
	   	if(showTallyOtherTab){
	   		tallyImageTd.innerHTML = "<a target='_blank' href='"+href+"'> Imagen del acta </a>";	   		
	   	}


		/* Open a popup */
	   	if(showTallyPopUp){
			tallyImageTd.innerHTML = "<a id='imageTallyLink_"+contest+"' href='#' onclick='Popup=window.open(\""+href+"\",\"Popup\",\"toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width="+tallyWidth+",height="+tallyHeight+",left=430,top=23\"); return false;'> Imagen del acta </a>";	   		
	   	}


		/* put the image embbebed in the HTML */
	   	if(showTallyImage){
			var tallyMockRef = '../../styles/default/images/acta.jpg'
				
				tallyImageTd.innerHTML = "<div>" +
				"<img id='imageTallyImg_"+contest+"' src='../../styles/default/images/acta.jpg' class='thumb' height='100' width='75' onclick='javascript:initViewer(\""+href+"\",\"imageTallyLink_"+contest+",\"imageThumb\",\"tallyImageTitle_"+contest+"\",\"imageTallyImg_"+contest+"\","+globalPrintedWidth+","+globalPrintedHeight+")'/>" +
				"<div id='tallyImageTitle_"+contest+"' style='display:none'><b></br><a href='javascript:hideViewer(\"wrapper_"+contest+"\",\"imageTallyImg_"+contest+"\")' >Imagen del Acta</a></b></div></div>"+
				"<div id='imageThumb'></div><div id='wrapper_"+contest+"' class='wrapper'><div id='imageTallyLink_"+contest+"' class='iviewer_cursor'/><a id='imageTallyLink_"+contest+"' href='javascript:initViewer(\""+href+"\",\"imageTallyLink_"+contest+"\",\"imageThumb\",\"tallyImageTitle_"+contest+"\",\"imageTallyImg_"+contest+"\","+globalPrintedWidth+","+globalPrintedHeight+")'>Cargar imagen del acta</a></div>";	      
		}

		newTR.appendChild(tallyImageTd);  
		myTable.appendChild(newTR);
		initThumb();
	}
   	
}

function hideViewer(name,imageId){
	if($("#"+name).is(':visible')){
		$("#"+name).hide('slow');
   	    $("#"+imageId).show('slow');
   	    $("#"+imageId).attr("onclick","hideViewer(\""+name+"\",\""+imageId+"\")");
	}else{
		$("#"+name).show('slow');
   	    $("#"+imageId).hide('slow'); 
	}
}

function initThumb(){

	$(document).ready(function() {
		$(".thumb").thumbs();
	});
}

function addTallyGlobalParameters(myTable,tally){
   	var newTR = document.createElement("tr");
	newTR.setAttribute('class','tblightrow');

   	var tallyImageTd = document.createElement("td");
   	tallyImageTd.setAttribute('class','lightRowContent');
   	tallyImageTd.setAttribute('align','center');
   	tallyImageTd.setAttribute('width','100%');
   	tallyImageTd.setAttribute('colspan','3');
	tallyImageTd.setAttribute('style','font-weight: bolder');
   	tallyImageTd.innerHTML = tally.number;

	   
	newTR.appendChild(tallyImageTd);  
	myTable.appendChild(newTR);
}

function addTallyType(myTable,tally){
	var newTR = document.createElement("tr");
	newTR.setAttribute('class','tblightrow');

   	var tallyTypeTd = document.createElement("td");
   	tallyTypeTd.setAttribute('class','lightRowContent');
   	tallyTypeTd.setAttribute('align','left');
   	tallyTypeTd.setAttribute('width','100%');
   	tallyTypeTd.setAttribute('colspan','3');
	tallyTypeTd.setAttribute('style','font-weight: bolder');

	if(tally.type=="MANUAL"){
		tallyTypeTd.innerHTML = "Acta recibida de forma: MANUAL";
	} else {
		tallyTypeTd.innerHTML = "Acta recibida de forma: AUTOMATIZADA";
	}
	   
	newTR.appendChild(tallyTypeTd);
	myTable.appendChild(newTR);
}

function addLastCATr(){
	myTable = document.getElementById(globalTableName);
	var newTR = document.createElement("tr");
	newTR.setAttribute('class','tblightrow');
	
	var caInformation = document.createElement("td");
   	caInformation.setAttribute('class','lightRowContent');
   	caInformation.setAttribute('align','left');
  	caInformation.setAttribute('colspan','5');
   	caInformation.setAttribute('width','100%');
   	caInformation.innerHTML = "<font color='#990000'> * </font> Opciones con cambios de alianza";

	newTR.appendChild(caInformation);  
	myTable.appendChild(newTR);
}

function fileExists(fileLocation) {
    var response = $.ajax({
        url: fileLocation,
        type: 'HEAD',
        async: false
    }).status;
	if(response == "404"){
		return false;
	}

	return true;
}

function addTallyInformation(myTable,tally){
   	var newTR = document.createElement("tr");
  	var newTR2 = document.createElement("tr");
	newTR.setAttribute('class','tblightrow');
	newTR2.setAttribute('class','tblightrow');

	/* NULL VOTES*/	
   	var tallyNullTd = document.createElement("td");
   	tallyNullTd.setAttribute('class','lightRowContent');
   	tallyNullTd.setAttribute('align','left');
   	tallyNullTd.setAttribute('width','100%');
   	tallyNullTd.setAttribute('colspan','3');
   	tallyNullTd.setAttribute('style','font-weight: bolder');
   	tallyNullTd.innerHTML = "Votos Nulos: "+tally.nullVotesAmount + tally.emptyVotesAmount;
   	
   	/* Printed Voters */	
   	var tallyVotersTd = document.createElement("td");
	var voters = parseInt(tally.votersAmount) + parseInt(tally.printedVotesAmount);
   	tallyVotersTd.setAttribute('class','lightRowContent');
   	tallyVotersTd.setAttribute('align','left');
   	tallyVotersTd.setAttribute('colspan','3');
   	tallyVotersTd.setAttribute('width','100%');
   	tallyVotersTd.setAttribute('style','font-weight: bolder');
   	tallyVotersTd.innerHTML = "Electores recibidos según el cuaderno: "+voters ;
   	
	newTR.appendChild(tallyNullTd);
	newTR2.appendChild(tallyVotersTd);

	myTable.appendChild(newTR);
	myTable.appendChild(newTR2);
}
