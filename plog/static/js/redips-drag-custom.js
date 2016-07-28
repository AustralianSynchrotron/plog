/*jslint white: true, browser: true, undef: true, nomen: true, eqeqeq: true, plusplus: false, bitwise: true, regexp: true, strict: true, newcap: true, immed: true, maxerr: 14 */
/*global window: false, REDIPS: true */

/* enable strict mode */
"use strict";

// define redipsInit variable
var redips = {};

// redips initialization
redips.init = function () {
	var rd = REDIPS.drag,	// reference to the REDIPS.drag class
		divDrag = document.getElementById('redips-drag'); // reference to the drag region
	// DIV container initialization
	rd.init();
	// elements could be cloned with pressed SHIFT key
	rd.clone.keyDiv = true;
	// define text source elements for the text-only row (element ID and class name of the last row)
	rd.only.div.text_only = 'text_only';
	rd.only.div.text_only = 'text_only';
	rd.only.other = 'deny';
	rd.event.cloned = function () {
		var clonedID = rd.obj.id; //cloned id
		if ('text_only'.localeCompare(clonedID.substr(0,9)) === 0) {
			rd.only.div[clonedID] = 'text_only';
		}
	};
};


// add onload event listener
if (window.addEventListener) {
	window.addEventListener('load', redips.init, false);
}
else if (window.attachEvent) {
	window.attachEvent('onload', redips.init);
}