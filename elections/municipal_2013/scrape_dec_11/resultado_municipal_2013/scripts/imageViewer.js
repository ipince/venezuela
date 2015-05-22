var imageToShow;
var divImage;
var globalWidth;
var globalHeight;
function initViewer(imagePath,imageDiv,thumbId,titleDiv,imageId,widthPrinted,heightPrinted){
	imageToShow = imagePath;
	divImage = imageDiv; 	
	globalWidth = widthPrinted;
	globalHeight = heightPrinted;

	var $ = jQuery;
            $(document).ready(function(){
                  var iv1 = $("#"+divImage).iviewer(
                  {
                     	src: imageToShow,
			widthPrinted:globalWidth,
			heigthPrinted:globalHeight
 			
                  });

           $("#"+divImage+" > a").html('');//removes the text from the anchor
		   $("#"+divImage).attr("class","viewer");
	   	   $("#"+thumbId).attr("style","display:none"); 
	   	   $("#"+titleDiv).attr("style","display:block");
	   	   $("#"+imageId).attr("style","display:none"); 	   	
            });
}          
 

