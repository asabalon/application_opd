/*
*
* Function that adds an offset to textarea parent elements
*
* @param    None
* @return   None
*
*/
function format_textarea() {
    var text_areas = document.getElementsByTagName('textarea');

    for (i = 0; i < text_areas.length; i++) {
        text_areas[i].parentElement.className += ' col-xs-offset-6';
    }
}