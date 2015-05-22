/*
 *
 * Copyright (c) 2006-2010 Joan Piedra (http://joanpiedra.com)
 * Licensed under the MIT License:
 * http://www.opensource.org/licenses/mit-license.php
 * 
 */
(function($) {

/*
 * Converts image and link elements to thumbnails
 *
 * @name     $.fn.thumbs
 * @author   Joan Piedra (http://joanpiedra.com)
 * @example  $('.thumb').thumbs();
 *
 */
$.fn.thumbs = function(options) {
	var $thumbs = this;
	
	if (options == 'destroy') {
		return Thumbs.destroy($thumbs);
	}
	
	if( $thumbs.data('thumbs') ) {
		return $thumbs;
	}
	
	var center = {},
	defaults = {
		center: true,
		classNames: {
			center: 'thumb-center',
			container: 'thumb-container',
			icon: 'thumb-icon',
			img: 'thumb-img',
			inner: 'thumb-inner',
			strip: 'thumb-strip'
		},
		html: '<span class="%container%"><span class="%inner%"><span class="%img%"></span><span class="%strip%">%strip_content%</span><span class="%icon%"></span></span></span>',
		strip: true
	};
	
	options = $.extend(true, {}, defaults, options);
	
	return $thumbs.each(function(){
		var $thumb = $(this),
		c = options.classNames,
		clone = $thumb.clone(true),
		html = new String(options.html),
		centered = false,
		strip = '';
		
		for (className in c) {
			var newClassName = c[className];
			
			if ( options.center && !centered && className == 'container' ) {
				newClassName = c.container + ' ' + c.center;
				centered = true;
			}
			
			html = html.replace('%' + className + '%', newClassName);
		}
		
		if (options.strip) {
			strip = $thumb.is('img') ? $thumb.attr('alt') : $thumb.find('img').attr('alt');
			strip = strip != undefined ? strip : $thumb.attr('title');
			strip = strip != undefined ? strip : '';
		}
		
		html = html.replace('%strip_content%', strip);
		
		$thumb.wrap( html );
		
		if (options.center) {
			Thumbs.centerImg( $thumb );
		}
		
		var data = {
			'container': $thumb.parents('.' + c.container),
			'raw': clone
		};
		
		$thumb.data('thumbs', data);
	});
};


var Thumbs = {

	/*
	 * Private: Absolute positions the image in the center of the thumbnail frame
	 *
	 * @name     thumbs.centerImg
	 * @author   Joan Piedra (http://joanpiedra.com)
	 * @example  Thumbs.centerImg($thumb);
	 *
	 */
	centerImg: function($thumb) {
		var $img = $thumb.is('img') ? $thumb : $thumb.find('img'),
		css = {
			left: '-' + ( parseInt( $img.css('width') ) / 2 ) + 'px',
			top: '-' + ( parseInt( $img.css('height') ) / 2 ) + 'px'
		};
	
		$img.css( css );
	
		return $thumb;
	},

	/*
	 * Private: Removes all the added thumbnail html
	 *
	 * @name     thumbs.destroy
	 * @author   Joan Piedra (http://joanpiedra.com)
	 * @example  Thumbs.destroy($thumbs);
	 *
	 */
	destroy: function($thumbs) {
		$thumbs.each(function(index) {
			var $thumb = $(this),
			data = $thumb.data('thumbs');
			
			if (!data) {
				return;
			}
			
			data.container.after(data.raw).remove();
		});
	}

}

})(jQuery);