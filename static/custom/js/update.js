/*
* Gets value of the selected area code from dropdown choice to update input prefix
*
* @param {string} source_id - search type value
* @param {string} target_id - display value for chosen search type
* @return None
*/
function changeAreaCodePrefix(source_id, target_id){
    document.getElementById(target_id).innerText = document.getElementById(source_id).selectedOptions[0].value;
}