var myVar;
var statusFilePath = "../../search/status.json";
var searchBoxPath = "../../search/templates/searchBox.html";
var legalPathDocument = "../../legalDocuments/";

var totalHeight;
var emptyHeight;
var passed = false;

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

/*  timer that checks if the indexation process is done */
function checkSearchComponentAvailability() {
	if (fileExists(statusFilePath)) {
		$.getJSON(statusFilePath, function(config) {
			status = config.status;
			if (config.status) {
				var text = $("#searchBox").html();
				if (!text) {
					$("#searchBox").load(searchBoxPath,function() {
						$("#searchBox").attr("style","display:block;text-align: right;");
						resizeApplication();
					});
				}
			} else {
				$("#searchBox").html("");
				resizeApplication();
			}
		});
	}
}

function resizeApplication() {
	if (!passed) {
		var myHeight = $('#wraperArea').height();
		$('#wraperArea').height('auto');
		var bodyheight = $(document).height();
		var mainWrapperHeight = $("#container").height();
		var windowHeight = $(window).height();
		var maxHeight = Math.max(bodyheight,windowHeight);
		totalHeight = 0;
		emptyHeight = 0;
		$('#wraperArea').siblings().each(function( index, value ){
			var div = jQuery(value);
			var h = div.height();
			totalHeight += h;
			if ($('#wraperArea').siblings().length == (index + 1)) {
				var totHeight = Math.ceil(totalHeight) + myHeight;
				emptyHeight = mainWrapperHeight - totHeight;
				maxHeight -= Math.ceil(totalHeight);
				newHeight = maxHeight - emptyHeight - 1;
				$('#wraperArea').height(newHeight+'px');
			}
		});
		passed = true;
	}
}
function showLink() {
	var showLink = false;
	var link = "../../legalDocuments/documentos.html?c=";
	if(fileExists(configurationPath)){
		var contests = $('div[id^=contestCodeTag]');
		var length = contests.length;
		for (var i = 0; i < length; i++) {
			var div = jQuery($('div[id^=contestCodeTag]')[i]);
			var contest = div.attr('id').substring(15);
			link += contest;
			if (i < (length - 1) ) {
				link += ",";
			}
			legalPathContest = legalPathDocument + contest;
			if(fileExists(legalPathContest)){
				showLink = true;
			}
		}
		if (!showLink) {
			$('#legalDocumentLink').css('visibility','hidden');
		} else {
			$('#legalDocumentLink').attr('href',link);
			$('#legalDocumentLink').css('visibility','visible');
		}
	} else {
		$('#legalDocumentLink').css('visibility','hidden');
	}
}

$(document).ready(function() {
	checkSearchComponentAvailability();
	showLink();
});	