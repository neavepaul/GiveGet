$(document).ready(function() {

    let intendedReceipients = [];
    let itemType_id = "";

    $("#itemTypes").hide();
    $("#receipientsContainer").hide();


    $.getJSON('/item-types', function(data, status){

        $("#cbItemTypes").find("option").remove();
        $('<option>').val("").text("Select Item").attr("selected",true).attr("disabled",true)
        .appendTo($("#cbItemTypes"));
        $.each(data, function (key, value) {
            // Checkbox
            var li = $('<li style="margin-left:100px;"><input class="checkbox" style="margin-left:5px;" type="checkbox" name="' + value.id + '" id="' + value.id + '"/>' +
                       '<label style="margin-left:20px;" for="' + value.id + '"></label></li>');
            li.find('label').text(value.title);
            $('#itemTypesList').append(li);

            // Combobox
            $('<option>').val(value.id).text(value.title).appendTo($("#cbItemTypes"));
        })
    });

    $('input[type=radio][value=donate]').on('change',function() {
        $("#itemTypes").hide();
    });

    $('input[type=radio][value=receive]').on('change',function() {
        $("#itemTypes").show();
    });

    $("#cbItemTypes").change(function() {
        itemType_id = $(this).val();
        var itemType = this.options[this.selectedIndex].text;

        $.getJSON('/receipients?itemType='+itemType, function(data, status){

            var container = $('#receipientsContainer'),
              table = $('<table style="margin-left:100px;" class="table table-striped">');


             container.empty();
              var th = $('<thead>');
              th.append('<th>Name</th>');
              th.append('<th>Address</th>');
              th.append('<th> </th>');
              th.append('</thead>');
              table.append(th);

            data.forEach(function(user) {


              var tr = $('<tr>');
              ['name', 'address_line1'].forEach(function(attr) {
                tr.append('<td>' + user[attr] + '</td>');
              });
              tr.append('<td><input type="checkbox" name="' + user.id + '" id="' + user.id + '"/></td>')
              table.append(tr);
            });
            container.append('<h6>Interested NGOs</h6>')
            container.append(table);
                $("#receipientsContainer").show();
        });
    });

    $('body').on('change', 'input[type="checkbox"]', function() {
        let receipientId = $(this).attr("id");
        if(!intendedReceipients.includes(receipientId)){
            intendedReceipients.push(receipientId);
        }
    });

    $('form').submit(function(eventObj) {
        var values = [];
        $('input[type="checkbox"]:checked').each(function(i,v){
          values.push($(v).attr("id"));
        });

      $('#donate').prop("disabled",true);
      $('#register').prop("disabled",true);

      $('<input />').attr('type', 'hidden')
          .attr('name', "preferences")
          .attr('value', values)
          .appendTo('form');

    $('<input />').attr('type', 'hidden')
      .attr('name', "intended_receipients")
      .attr('value', intendedReceipients)
      .appendTo('form');

    $('<input />').attr('type', 'hidden')
      .attr('name', "itemtype_id")
      .attr('value', itemType_id)
      .appendTo('form');
      return true;
    });

});

function acceptDonation(userId, donationId){
    $('#accept-'+donationId).prop('disabled',true);
    $('#reject-'+donationId).prop('disabled',true);
    $.post('/users/'+userId+'/donations/'+donationId+'/accept',function(data,status){
        console.log(data);
        location.reload(true);
    });
}

function rejectDonation(userId, donationId){
    $('#accept-'+donationId).prop('disabled',true);
    $('#reject-'+donationId).prop('disabled',true);
    $('#complete-'+donationId).prop('disabled',true);
    $.post('/users/'+userId+'/donations/'+donationId+'/reject',function(data,status){
        console.log(data);
        location.reload(true);
    });
}

function completeDonation(userId, donationId){
    $('#complete-'+donationId).prop('disabled',true);
    $('#reject-'+donationId).prop('disabled',true);
    $.post('/users/'+userId+'/donations/'+donationId+'/complete',function(data,status){
        console.log(data);
        location.reload(true);
    });
}


