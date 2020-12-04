/* CART JS */

// Selector string
let selector = "div.form-group input[name=quantityhidden";
let selector_stock = "div.form-group input[name=stock";

function counter_del(id)
{
    // Get text box name by concat selector + product_id
    name = selector.concat(id);

    // Finish the name string
    name = name.concat("]");

    // Read the value from quantity#prod_id
    document.querySelector(name).value = 0;
}

function counter_add(id)
{
    // Get text box name by concat selector + product_id
    name = selector.concat(id);

    // Finish the name string
    name = name.concat("]");

    stock = selector_stock.concat(id);
    stock = stock.concat("]");

    // Check if quantity selected is equal/less than product stock
    if (document.querySelector(name).value < document.querySelector(stock).value)
    {
        // Read the value from quantity#prod_id
        document.querySelector(name).value ++;
    }
}

function counter_min(id)
{
    // Get text box name by concat selector + product_id
    name = selector.concat(id);

    // Finish the name string
    name = name.concat("]");

    // Value can't be lower than 0
    if (document.querySelector(name).value >= 1)
    {
        document.querySelector(name).value --;
    }
}

/*----------------------------------------------------------------------------------------------*/


/* CHECK OUT JS */

// Hide or show Billing address depending on the user selection
    function show_billing(){

        let states = "</option><option>Alabama</option><option>Alaska</option><option>Arizona</option>\
    	<option>Arkansas</option><option>California</option><option>Colorado</option><option>Connecticut</option><option>Delaware</option>\
    	<option>Florida</option><option>Georgia</option><option>Hawaii</option><option>Idaho</option><option>Illinois</option><option>Indiana</option>\
    	<option>Iowa</option><option>Kansas</option><option>Kentucky</option><option>Louisiana</option><option>Maine</option><option>Maryland</option>\
    	<option>Massachusetts</option><option>Michigan</option><option>Minnesota</option><option>Mississippi</option><option>Missouri</option>\
    	<option>Montana</option><option>Nebraska</option><option>Nevada</option><option>New Hampshire</option><option>New Jersey</option>\
    	<option>New Mexico</option><option>New York</option><option>North Carolina</option><option>North Dakota</option><option>Ohio</option>\
    	<option>Oklahoma</option><option>Oregon</option><option>Pennsylvania</option><option>Rhode Island</option><option>South Carolina</option>\
    	<option>South Dakota</option><option>Tennessee</option><option>Texas</option><option>Utah</option><option>Vermont</option><option>Virginia</option>\
    	<option>Washington</option><option>West Virginia</option><option>Wisconsin</option><option>Wyoming</option>"

    	let provinces = "</option><option>Ciudad de Buenos Aires</option><option>Buenos Aires</option>\
    	<option>Catamarca</option><option>Chaco</option><option>Chubut</option><option>Córdoba</option><option>Corrientes</option>\
    	<option>Entre Ríos</option><option>Formosa</option><option>Jujuy</option><option>La Pampa</option><option>La Rioja</option>\
    	<option>Mendoza</option><option>Misiones</option><option>Neuquén</option><option>Río Negro</option><option>Salta</option>\
    	<option>San Juan</option><option>San Luis</option><option>Santa Cruz</option><option>Santa Fe</option><option>Santiago del Estero</option>\
    	<option>Tierra del Fuego</option><option>Tucumán</option>"


        if(document.querySelector('#same-address').checked == true)
            {
                document.querySelector("#billing_address").value = document.querySelector("#address").value;
                document.querySelector("#billing_address2").value = document.querySelector("#address2").value;
                document.querySelector("#billing_zip").value = document.querySelector("#zip").value;
                document.querySelector("#billing_firstName").value = document.querySelector("#firstName").value;
                document.querySelector("#billing_lastName").value = document.querySelector("#lastName").value;
                if (shipping_country_value == "Argentina")
        	    {
        		    document.querySelector('#billing_label_state').innerHTML = "Province";
        	        document.querySelector('#billing_state').innerHTML = provinces;
        	    }
            	else
        	    {
        	        document.querySelector('#billing_label_state').innerHTML = "State";
        		    document.querySelector('#billing_state').innerHTML = states;
        	    }


                document.querySelector("#billing_country").value = document.querySelector("#country").value;
                document.querySelector("#billing_state").value = document.querySelector("#state").value;

                document.querySelector("#billing_data").style.display = 'none';
            }
        else
            {
                document.querySelector("#billing_data").style.display = 'block';
                document.querySelector("#billing_address").value = '';
                document.querySelector("#billing_address2").value = '';
                document.querySelector("#billing_zip").value = '';
                document.querySelector("#billing_firstName").value = '';
                document.querySelector("#billing_lastName").value = '';
                document.querySelector("#billing_country").value ='';
                document.querySelector("#billing_state").value = '';
            }


    }


// Hide card input fields if option is paypal
document.querySelector('#paypal').onclick = function() {
document.querySelector('#cc-name').style.display = "none";
document.querySelector('#cc-number').style.display = "none";
document.querySelector('#cc-expiration').style.display = "none";
document.querySelector('#cc-cvv').style.display = "none";
document.querySelector('#cc-name_label').style.display = "none";
document.querySelector('#cc-number_label').style.display = "none";
document.querySelector('#cc-expiration_label').style.display = "none";
document.querySelector('#cc-cvv_label').style.display = "none";
document.querySelector('#cc-name_small').style.display = "none";
document.querySelector('#cc-feedback_name').style.display = "none";
document.querySelector('#cc-feedback_number').style.display = "none";
document.querySelector('#cc-feedback_exp').style.display = "none";
document.querySelector('#cc-feedback_cvv').style.display = "none";

document.querySelector('#cc-name').value = "1";
document.querySelector('#cc-number').value = "1";
document.querySelector('#cc-expiration').value = "1";
document.querySelector('#cc-cvv').value = "1";

document.querySelector('#bt_mdn_place_order').innerHTML = "Continue with Paypal & Place Order";
}

// Show card input fields if option is credit
document.querySelector('#credit').onclick = function() {
document.querySelector('#cc-name').style.display = "block";
document.querySelector('#cc-number').style.display = "block";
document.querySelector('#cc-expiration').style.display = "block";
document.querySelector('#cc-cvv').style.display = "block";
document.querySelector('#cc-name_label').style.display = "block";
document.querySelector('#cc-number_label').style.display = "block";
document.querySelector('#cc-expiration_label').style.display = "block";
document.querySelector('#cc-cvv_label').style.display = "block";
document.querySelector('#cc-feedback_name').style.display = "block";
document.querySelector('#cc-feedback_number').style.display = "block";
document.querySelector('#cc-feedback_exp').style.display = "block";
document.querySelector('#cc-feedback_cvv').style.display = "block";

document.querySelector('#cc-name').value = "";
document.querySelector('#cc-number').value = "";
document.querySelector('#cc-expiration').value = "";
document.querySelector('#cc-cvv').value = "";

document.querySelector('#bt_mdn_place_order').innerHTML = "Place Order";
}

// Show card input fields if option is debit
document.querySelector('#debit').onclick = function() {
document.querySelector('#cc-name').style.display = "block";
document.querySelector('#cc-number').style.display = "block";
document.querySelector('#cc-expiration').style.display = "block";
document.querySelector('#cc-cvv').style.display = "block";
document.querySelector('#cc-name_label').style.display = "block";
document.querySelector('#cc-number_label').style.display = "block";
document.querySelector('#cc-expiration_label').style.display = "block";
document.querySelector('#cc-cvv_label').style.display = "block";
document.querySelector('#cc-feedback_name').style.display = "block";
document.querySelector('#cc-feedback_number').style.display = "block";
document.querySelector('#cc-feedback_exp').style.display = "block";
document.querySelector('#cc-feedback_cvv').style.display = "block";

document.querySelector('#cc-name').value = "";
document.querySelector('#cc-number').value = "";
document.querySelector('#cc-expiration').value = "";
document.querySelector('#cc-cvv').value = "";

document.querySelector('#bt_mdn_place_order').innerHTML = "Place Order";
}


/* COUNTRY AND STATE/PROVINCE */

function country_name(){

	let states = "</option><option>Alabama</option><option>Alaska</option><option>Arizona</option>\
	<option>Arkansas</option><option>California</option><option>Colorado</option><option>Connecticut</option><option>Delaware</option>\
	<option>Florida</option><option>Georgia</option><option>Hawaii</option><option>Idaho</option><option>Illinois</option><option>Indiana</option>\
	<option>Iowa</option><option>Kansas</option><option>Kentucky</option><option>Louisiana</option><option>Maine</option><option>Maryland</option>\
	<option>Massachusetts</option><option>Michigan</option><option>Minnesota</option><option>Mississippi</option><option>Missouri</option>\
	<option>Montana</option><option>Nebraska</option><option>Nevada</option><option>New Hampshire</option><option>New Jersey</option>\
	<option>New Mexico</option><option>New York</option><option>North Carolina</option><option>North Dakota</option><option>Ohio</option>\
	<option>Oklahoma</option><option>Oregon</option><option>Pennsylvania</option><option>Rhode Island</option><option>South Carolina</option>\
	<option>South Dakota</option><option>Tennessee</option><option>Texas</option><option>Utah</option><option>Vermont</option><option>Virginia</option>\
	<option>Washington</option><option>West Virginia</option><option>Wisconsin</option><option>Wyoming</option>"

	let provinces = "</option><option>Ciudad de Buenos Aires</option><option>Buenos Aires</option>\
	<option>Catamarca</option><option>Chaco</option><option>Chubut</option><option>Córdoba</option><option>Corrientes</option>\
	<option>Entre Ríos</option><option>Formosa</option><option>Jujuy</option><option>La Pampa</option><option>La Rioja</option>\
	<option>Mendoza</option><option>Misiones</option><option>Neuquén</option><option>Río Negro</option><option>Salta</option>\
	<option>San Juan</option><option>San Luis</option><option>Santa Cruz</option><option>Santa Fe</option><option>Santiago del Estero</option>\
	<option>Tierra del Fuego</option><option>Tucumán</option>"

	shipping_country_value = document.querySelector('#country').value;

	if (shipping_country_value == "Argentina")
	    {
	    document.querySelector('#state').innerHTML = provinces;
		document.querySelector('#label_state').innerHTML = "Province";
	    }
	else
	    {
	    document.querySelector('#label_state').innerHTML = "State";
		document.querySelector('#state').innerHTML = states;
	    }

    billing_country_value = document.querySelector('#billing_country').value;

	if (billing_country_value == "Argentina")
	    {
		document.querySelector('#billing_state').innerHTML = provinces;
		document.querySelector('#billing_label_state').innerHTML = "Province";
	    }
	else
	    if (billing_country_value == "United States")
	    {
		    document.querySelector('#billing_state').innerHTML = states;
            document.querySelector('#billing_label_state').innerHTML = "State";
	    }
}

/*----------------------------------------------------------------------------------------------*/

