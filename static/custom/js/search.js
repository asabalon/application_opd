/*
* Function that changes type of search to be executed for a type of record.
*
* @param {string} search_type - search type value
* @param {string} search_type_label - display value for chosen search type
* @param {string} list_item_id - list node id containing chosen search type
* @return None
*/
function change_search_type(search_type, search_type_label, list_item_id) {
    document.getElementById('id_search_type').value = search_type;
    document.getElementById('search_type_label').innerHTML = search_type_label;

    var selected_item = document.getElementById(list_item_id);
    var list_items = selected_item.parentElement.getElementsByTagName('li');

    for (i = 0; i < list_items.length; i++) {
        list_items[i].hidden = false;
    }

    selected_item.hidden = true;
}

/*
* Hides chosen search type node in the list upon loading of page
*
* @param    None
* @return   None
*/
function search_onload_function() {
    var search_type = document.getElementById('id_search_type').value;

    if (search_type != null) document.getElementById('search_type_item_' + search_type).hidden = true;
}