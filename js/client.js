/*global WebSocket, JSON, $, window, console, alert*/
//"use strict";
/**
 * Function calls across the background TCP socket. Uses JSON RPC + a queue.
 * (I've added this extra logic to simplify expanding this)
 */

 $(document).ready(function() {
    var buttonpressed;

    $("#l1nodes-btn").on("click", function() {
        buttonpressed = $(this);
    });

    $("#l1nodes-unassign-btn").on("click", function() {
        buttonpressed = $(this);
    });

    $("#l1links-unassign-btn").on("click", function() {
        buttonpressed = $(this);
    });

    $("#l1links-degree-btn").on("click", function() {
        buttonpressed = $(this);
    });

    $("#l1links-conduit-btn").on("click", function() {
        buttonpressed = $(this);
    });

    $("#l1links-degree-btn").on("click", function() {
        buttonpressed = $(this);
    });

    $("#update-btn").on("click", function() {
        buttonpressed = $(this);
    });

    $("#collectform").on("submit", function() {
        console.log("Collection button run_collection called from form submit!");
        if(document.getElementById('srlg_check').checked) {
            document.getElementById('srlg_check_hidden').disabled = true;
        }
        run_collection($(this));
        return false;
    });

    $("#l1nodes-form").on("submit", function() {
        console.log("L1nodes assign button called from form submit!");
        btn_text = buttonpressed.text();
        l1nodes_srlg($(this),buttonpressed,btn_text);
        return false;
    });

    $("#l1nodes-unassign-form").on("submit", function() {
        console.log("L1nodes unassign button called from form submit!");
        btn_text = buttonpressed.text();
        l1nodes_srlg($(this),buttonpressed,btn_text);
        return false;
    });

    $("#l1links-degree-form").on("submit", function() {
        console.log("L1Links degree assign button called from form submit!");
        btn_text = buttonpressed.text();
        l1links_assign_srlg($(this),buttonpressed,btn_text);
        return false;
    });

    $("#l1links-conduit-form").on("submit", function() {
        console.log("L1Links conduit assign button called from form submit!");
        btn_text = buttonpressed.text();
        l1links_assign_srlg($(this),buttonpressed,btn_text);
        return false;
    });

    $("#l1links-unassign-form").on("submit", function() {
        console.log("L1Links unassign button called from form submit!");
        l1links_unassign_srlg($(this));
        return false;
    });

    $("#epnm-form").on("submit", function() {
        console.log("EPNM update form submitted!");
        btn_text = buttonpressed.text();
        epnm_update($(this),buttonpressed,btn_text);
        return false;
    });
//    TODO Add code to spin spinners on AJAX call

    //Open a websocket to the server (used only on home page for now)
    client.connect(8002);
    console.log("Document ready!");
 });

function epnm_update(form,btn,btn_text) {
    var request = form.form2Dict();
    console.log("EPNM update");
//    var btn = $("#update-btn");
    var btn_spinner_html = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="spinner"></span>' + btn_text;
    btn.html(btn_spinner_html);
    btn.attr("disabled","disabled");
    jQuery().postJSON("/ajax", request, function(response) {
        console.log("Callback to EPNM update request!");
        console.log(response);
        btn.empty();
        btn.text(btn_text);
        btn.removeAttr("disabled");
    });
}

function run_collection(form) {
    var message = form.form2Dict();
    var btn = $("#collect-btn");
    var btn_spinner_html = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="spinner"></span>Collect';
    btn.html(btn_spinner_html);
    btn.attr("disabled","disabled");
    $("#updatefield").append("Requesting SRLG collection...</br>");
    jQuery().postJSON("/ajax", message, function(response) {
        console.log("Callback!!!");
        $("#updatefield").append(response.status + "<br/>");
        var textfield = document.getElementById('textfield');
        textfield.scrollTop = textfield.scrollHeight;
        console.log(response);
        btn.empty();
        btn.text("Collect");
        btn.removeAttr("disabled");
    });
}

function l1nodes_srlg(form,btn,btn_text) {
    var formdata = form.form2Dict();
    var btn_spinner_html = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="spinner"></span>' + btn_text;
    btn.html(btn_spinner_html);
    btn.attr("disabled","disabled");
    var request={};
    request['pool-name'] = formdata['pool-name'];
    request['action'] = formdata['action'];
    request['type'] = formdata['type'];
    var fdns = [];
    //TODO Learn how jQuery filtering works like in next line of code
    $('#nodes_table').find('tr').filter(':has(:checkbox:checked)').each(function(){
//        var id=$(this).attr('id');
        console.log(this.id);
        fdns.push(this.id);
    });
    request['fdns'] = fdns;
    console.log(request);
    jQuery().postJSON("/ajax", request, function(response) {
        console.log("Callback to assign-srrg request!");
        console.log(response);
        if (response.status == 'failed') {
                $('#failed').show();
        }
        var newrequest = {};
        newrequest['action'] = "get-l1nodes";
        jQuery().postJSON("/ajax", newrequest, function(response) {
            console.log("Callback to l1nodes srrg request!");
            console.log(response);
            $("#nodes_table thead").remove();
            $("#nodes_table tbody").remove();
            client.buildL1nodesTable(response);
        });
        btn.empty();
        btn.text(btn_text);
        btn.removeAttr("disabled");
    });
}

//function l1nodes_unassign_srlg(form,btn,btn_text) {
//    var formdata = form.form2Dict();
//    var btn_spinner_html = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="spinner"></span>' + btn_text;
//    btn.html(btn_spinner_html);
//    btn.attr("disabled","disabled");
//    var request={};
//    request['options'] = formdata['options'];
//    request['action'] = formdata['action'];
//    request['type'] = formdata['type'];
//    var fdns = [];
////    //TODO Learn how jQuery filtering works like in next line of code
//    $('#nodes_table').find('tr').filter(':has(:checkbox:checked)').each(function(){
//        console.log(this.id);
//        fdns.push(this.id);
//    });
//    request['fdns'] = fdns;
//    console.log(request);
//    jQuery().postJSON("/ajax", request, function(response) {
//        console.log("Callback to unassign-srrg request!");
//        console.log(response);
//        var newrequest = {};
//        newrequest['action'] = "get-l1nodes";
//        jQuery().postJSON("/ajax", newrequest, function(response) {
//            console.log("Callback to assign-srrg request!");
//            console.log(response);
//            $("#nodes_table th").remove();
//            $("#nodes_table tr").remove();
//            client.buildL1nodesTable(response);
//        });
//        btn.empty();
//        btn.text(btn_text);
//        btn.removeAttr("disabled");
//    });
//}

function l1links_assign_srlg(form,btn,btn_text) {
    var formdata = form.form2Dict();
//    var btn = $("#l1links-btn");
    var btn_spinner_html = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="spinner"></span>' + btn_text;
    btn.html(btn_spinner_html);
    btn.attr("disabled","disabled");
    var request={};
    request['pool-name'] = formdata['pool-name'];
    request['action'] = "assign-srrg";
    request['type'] = formdata['type'];
    var fdns = [];
    //TODO Learn how jQuery filtering works like in next line of code
    $('#links_table').find('tr').filter(':has(:checkbox:checked)').each(function(){
//        var id=$(this).attr('id');
        console.log(this.id);
        fdns.push(this.id);
    });
    request['fdns'] = fdns;
    console.log(request);
    jQuery().postJSON("/ajax", request, function(response) {
        console.log("Callback to assign-srrg request!");
        console.log(response);
        var newrequest = {};
        newrequest['action'] = "get-l1links";
        jQuery().postJSON("/ajax", newrequest, function(response) {
            console.log("Callback to assign-srrg request!");
            console.log(response);
            $("#links_table thead").remove();
            $("#links_table tbody").remove();
            client.buildL1linksTable(response);
        });
        btn.empty();
        btn.text(btn_text);
        btn.removeAttr("disabled");
    });
}

function l1links_unassign_srlg(form) {
    var formdata = form.form2Dict();
    var btn = $("#l1links-unassign-btn");
    var btn_spinner_html = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" id="spinner"></span>Unassign';
    btn.html(btn_spinner_html);
    btn.attr("disabled","disabled");
    var request={};
    request['type'] = formdata['type'];
    request['action'] = "unassign-srrg";
    var fdns = [];
//    //TODO Learn how jQuery filtering works like in next line of code
    $('#links_table').find('tr').filter(':has(:checkbox:checked)').each(function(){
//        var id=$(this).attr('id');
        console.log(this.id);
        fdns.push(this.id);
    });
    request['fdns'] = fdns;
    console.log(request);
    jQuery().postJSON("/ajax", request, function(response) {
        console.log("Callback to unassign-srrg request!");
        console.log(response);
        var newrequest = {};
        newrequest['action'] = "get-l1links";
        jQuery().postJSON("/ajax", newrequest, function(response) {
            console.log("Callback to assign-srrg request!");
            console.log(response);
            $("#links_table th").remove();
            $("#links_table tr").remove();
            client.buildL1linksTable(response);
        });
        btn.empty();
        btn.text("Unassign");
        btn.removeAttr("disabled");
    });
}

//jQuery extended functions defined...
jQuery.fn.extend({
    form2Dict: function() {
        var fields = this.serializeArray();
        var json = {};
        $.each(fields, function(i,v) {
            json[fields[i].name] = fields[i].value;
        });
        if (json.next) delete json.next;
        return json;
    },
    postJSON: function(url, args, callback) {
//        args._xsrf = getCookie("_xsrf");
//        json_body = JSON.stringify(args);
        json_body = $.param(args);
//        $.ajax({url: url, traditional: true, data: $.param(args), dataType: "json", type: "POST",
          $.ajax({url: url, data: json_body, type: "POST",
//                beforeSend: function() {
//                    $("#loading-indicator").show();
//                },
                success: function(response) {
//                foo = eval("(" + response + ")"); //foo and bar are equivalent ways to convert JSON string to JSON object
//                bar = JSON.parse(response);
                    if (callback) callback(JSON.parse(response));
                },
                error: function(response) {
                    console.log("ERROR:", response);
                }
        });
    },
});

// Web client javascript functions (including websocket client code)...
var client = {
    queue: {},

    // Connects to Python through the websocket
    connect: function (port) {
        var self = this;
        console.log("Opening websocket to ws://" + window.location.hostname + ":" + port + "/websocket")
        this.socket = new WebSocket("ws://" + window.location.hostname + ":" + port + "/websocket");

        this.socket.onopen = function () {
            console.log("Connected!");
        };

        this.socket.onmessage = function (messageEvent) {
            var router, current, updated, jsonRpc;
            console.log("Got a message...");
            $("#updatefield").append(messageEvent.data + "<br/>");
            var textfield = document.getElementById('textfield');
            textfield.scrollTop = textfield.scrollHeight;
            console.log(messageEvent.data);
        };
        return this.socket;
    },

    // Generates a unique identifier for request ids
    // Code from http://stackoverflow.com/questions/105034/
    // how-to-create-a-guid-uuid-in-javascript/2117523#2117523
    uuid: function () {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
            return v.toString(16);
        });
    },

//    waitForSocketConnection: function(socket, queue, callback) {
    waitForSocketConnection: function(socket, callback) {
    setTimeout(
        function () {
            if (socket.readyState === 1) {
                console.log("Connection is made");
                if(callback != null){
                    callback();
                }
                return;

            } else {
                console.log("wait for connection...");
                waitForSocketConnection(callback);
            }

        }, 5); // wait 5 milisecond for the connection...
    },

    // Placeholder function. It adds one to things.
//    count: function (data) {
//        var uuid = this.uuid();
//        console.log("Called count method...");
//        console.log("Sending message over Websocket: " + JSON.stringify({method: "count", id: uuid, params: {number: data}}));
//        this.socket.send(JSON.stringify({method: "count", id: uuid, params: {number: data}}));
//        this.queue[uuid] = "count";
//    },
//
//    buildtable: function () {
//        var uuid = this.uuid();
//        var socket = this.socket;
//        var queue = this.queue;
//        this.waitForSocketConnection(socket, function() {
//            console.log("Sending message to getl1nodes...");
//            console.log("UUID is: " + uuid);
//            socket.send(JSON.stringify({method: "getl1nodes", id: uuid, params: {}}));
//            queue[uuid] = "getl1nodes";
//        });
//    },
//
//    srlgtable: function (srlg) {
//        console.log("srlgtable function called...");
//        var uuid = this.uuid();
//        var socket = this.socket;
//        var queue = this.queue;
//        this.waitForSocketConnection(this.socket, function() {
//            console.log("Sending message to getsrlg...")
//            console.log("UUID is: " + uuid)
//            socket.send(JSON.stringify({method: "getsrlg", id: uuid, params: {srlg: srlg}}));
//            queue[uuid] = "getsrlg";
//        });
//    },
    set_region_select: function (region) {
        $("#region-select").val(region);
    },

    buildtopolinkstable: function (topo_link_data) {
        var table = $('#topo_links_table'), row = null, data = null;
        var origin   = window.location.origin;   // Returns base URL
        $('<th onclick="javascript:client.sortTable(0,\'topo_links_table\')">Node A</th> \
        <th onclick="javascript:client.sortTable(1,\'topo_links_table\')">Node B</th> \
        <th onclick="javascript:client.sortTable(2,\'topo_links_table\')">fdn</th> \
        <th onclick="javascript:client.sortTable(3,\'topo_links_table\')">Add/Drop SRLG</th> \
        <th onclick="javascript:client.sortTable(4,\'topo_links_table\')">Line Card SRLG</th>').appendTo(table);
        var topo_link_data_json = JSON.parse(topo_link_data);
        $.each(topo_link_data_json, function(k1, v1) {
            var node_a = "<td>"+v1['Nodes'][0]['node'] + "/" + v1['Nodes'][0]['ctp'].split('&')[0].split(';')[0]+"</td>";
            var node_b = "<td>"+v1['Nodes'][1]['node'] + "/" + v1['Nodes'][1]['ctp'].split('&')[0].split(';')[0]+"</td>";
            var fdn = "<td>"+v1['fdn'].split('=')[2]+"</td>";
            row = $('<tr></tr>');
            $(node_a).appendTo(row);
            $(node_b).appendTo(row);
            $(fdn).appendTo(row);
            try {
                var srrg_ad = v1['srrgs-ad'][0].split('=')[2];
                var srrg_ad_url = '<td><a href="'+origin+'/srlg/'+srrg_ad+'" name = "'+srrg_ad+'">'+srrg_ad+'</a></td>';
                $(srrg_ad_url).appendTo(row);
            }
            catch {
                console.log("No AD SRRG!");
                $('<td></td>').appendTo(row);
            }
            try {
                var srrg_lc = v1['srrgs-lc'][0].split('=')[2];
                var srrg_lc_url = '<td><a href="'+origin+'/srlg/'+srrg_lc+'" name = "'+srrg_lc+'">'+srrg_lc+'</a></td>';
                $(srrg_lc_url).appendTo(row);
            }
            catch {
                console.log("No LC SRRG!");
                $('<td></td>').appendTo(row);
            }
            row.appendTo(table);
        });
    },

//    buildL1nodesTable: function (l1nodes_data) {
//        var pathname = window.location.pathname;
//        var url = window.location.href;     // Returns full URL
//        var origin   = window.location.origin;   // Returns base URL
//        var table = $('#nodetable'), row = null, data = null;
//        $('<th>Node Name</th><th>EPNM FDN</th><th>SRLGs</th>').appendTo(table);
//        var l1nodes_data_json = JSON.parse(l1nodes_data);
//        $.each(l1nodes_data_json, function(k1, v1) {
//            var srrg = v1['srrgs'][0];
//            try {
//                var srrg_parsed = srrg.split('=')[2];
//                var srrg_url = '<td><a href="'+origin+'/srlg/'+srrg_parsed+'" name = "'+srrg_parsed+'">'+srrg_parsed+'</a></td>';
//            }
//            catch (err) {
//                var srrg_parsed = "none";
//            }
//            row = $('<tr></tr>');
//            $('<td>'+v1['Name']+'</td>').appendTo(row);
//            $('<td>'+v1['fdn']+'</td>').appendTo(row);
//                        $(srrg_url).appendTo(row);
//            row.appendTo(table);
//        });
//    },
    buildL1nodesTable: function (l1nodes_data) {
        var table = $('#nodes_table'), row = null, data = null;
        var thead = $('<thead><th style="text-align: center; vertical-align: middle;"><input type="checkbox" class="form-check-input" id="select-all-nodes"></th><th>Node Name</th><th>FDN</th><th>Node SRLG</th><th>Default/Incorrect SRLGs</th></thead>');
        thead.appendTo(table);
        var tbody = $('<tbody></tbody>');
        tbody.appendTo(table);
        var l1nodes_data_json = JSON.parse(l1nodes_data);
        $.each(l1nodes_data_json, function(k1, v1) {
            var pathname = window.location.pathname;
            var url      = window.location.href;     // Returns full URL
            var origin   = window.location.origin;   // Returns base URL

            var row = $('<tr id="'+v1['fdn']+'"></tr>');
            var checkbox_html = '<td style="text-align: center; vertical-align: middle;"><input type="checkbox" class="form-check-input" id="'+v1['fdn']+'"></td>';
            $(checkbox_html).appendTo(row);
            $('<td>'+v1['Name']+'</td>').appendTo(row);
            $('<td>'+v1['fdn']+'</td>').appendTo(row);

            var parsed_url_list = [];
            $.each(v1['srrgs'], function(k2,v2) {
                var parsed = v2.split('=')[2];
                parsed_url_list += '<a href="'+origin+'/srlg/'+parsed+'" name = "'+parsed+'">'+parsed+'</a></br>';
            });
            if (parsed_url_list.length > 0) {
                var parsed_url = "<td>"+ parsed_url_list + "</td>";
                $(parsed_url).appendTo(row);
            }
            else {
                $('<td></td>').appendTo(row);
            }

            parsed_url_list = [];
            $.each(v1['srrgs-incorrect'], function(k2,v2) {
                var parsed = v2.split('=')[2];
                parsed_url_list += '<a href="'+origin+'/srlg/'+parsed+'" name = "'+parsed+'">'+parsed+'</a></br>';
            });
            if (parsed_url_list.length > 0) {
                var parsed_url = "<td>"+ parsed_url_list + "</td>";
                $(parsed_url).appendTo(row);
            }
            else {
                $('<td></td>').appendTo(row);
            }
            row.appendTo(tbody);
        });
        $('#select-all-nodes').click(function (e) {
            $(this).closest('#nodes_table').find('td input:checkbox').prop('checked', this.checked);
        });

        $(".form-check-input").click(function (e) {
            var btn_assign = $("#l1nodes-btn");
            var btn_unassign = $("#l1nodes-unassign-btn");
            if ($(".form-check-input").is(":checked")) {
                btn_assign.prop('disabled', false);
                btn_unassign.prop('disabled', false);
            }
            else {
                btn_assign.prop('disabled', true);
                btn_unassign.prop('disabled', true);
            }
        });
    },

    buildL1linksTable: function (l1links_data) {
        var table = $('#links_table'), row = null, data = null;
        var thead = $('<thead><th style="text-align: center; vertical-align: middle;"><input type="checkbox" class="form-check-input" id="select-all-links"></th><th>Node A</th><th>Node B</th><th>FDN</th><th>Degree SRLG</th><th>Conduit SRLGs</th><th>Default/Incorrect SRLGs</th></thead>');
        thead.appendTo(table);
        var tbody = $('<tbody></tbody>');
        tbody.appendTo(table);
        var l1links_data_json = JSON.parse(l1links_data);
        $.each(l1links_data_json, function(k1, v1) {
            var pathname = window.location.pathname;
            var url      = window.location.href;     // Returns full URL
            var origin   = window.location.origin;   // Returns base URL

            var row = $('<tr id="'+v1['fdn']+'"></tr>');
            var checkbox_html = '<td style="text-align: center; vertical-align: middle;"><input type="checkbox" class="form-check-input" id="'+v1['fdn']+'"></td>';
            $(checkbox_html).appendTo(row);
            $('<td>'+v1['Nodes'][0]+'</td>').appendTo(row);
            $('<td>'+v1['Nodes'][1]+'</td>').appendTo(row);
            $('<td>'+v1['fdn']+'</td>').appendTo(row);

            var parsed_url_list = [];
            $.each(v1['srrgs'], function(k2,v2) {
                var parsed = v2.split('=')[2];
                parsed_url_list += '<a href="'+origin+'/srlg/'+parsed+'" name = "'+parsed+'">'+parsed+'</a></br>';
            });
            if (parsed_url_list.length > 0) {
                var parsed_url = "<td>"+ parsed_url_list + "</td>";
                $(parsed_url).appendTo(row);
            }
            else {
                $('<td></td>').appendTo(row);
            }

            parsed_url_list = [];
            $.each(v1['srrgs-conduit'], function(k2,v2) {
                var parsed = v2.split('=')[2];
                parsed_url_list += '<a href="'+origin+'/srlg/'+parsed+'" name = "'+parsed+'">'+parsed+'</a></br>';
            });
            if (parsed_url_list.length > 0) {
                var parsed_url = "<td>"+ parsed_url_list + "</td>";
                $(parsed_url).appendTo(row);
            }
            else {
                $('<td></td>').appendTo(row);
            }

            parsed_url_list = [];
            $.each(v1['srrgs-incorrect'], function(k2,v2) {
                var parsed = v2.split('=')[2];
                parsed_url_list += '<a href="'+origin+'/srlg/'+parsed+'" name = "'+parsed+'">'+parsed+'</a></br>';
            });
            if (parsed_url_list.length > 0) {
                var parsed_url = "<td>"+ parsed_url_list + "</td>";
                $(parsed_url).appendTo(row);
            }
            else {
                $('<td></td>').appendTo(row);
            }
            row.appendTo(tbody);
        });

        $('#select-all-links').click(function (e) {
            $(this).closest('#links_table').find('td input:checkbox').prop('checked', this.checked);
        });

        //Handle enabling the submit button on L1links page when radio buttons are selected
//        $("input[name='options']").on('change', function(){
//            var btn = $("#l1links-unassign-btn");
//            btn.prop('disabled', false);
//        });

        $(".form-check-input").click(function (e) {
            var btn_assign_degree = $("#l1links-degree-btn");
            var btn_assign_conduit = $("#l1links-conduit-btn");
            var btn_unassign = $("#l1links-unassign-btn");
            if ($(".form-check-input").is(":checked")) {
                btn_assign_degree.prop('disabled', false);
                btn_assign_conduit.prop('disabled', false);
                if ($("input[name='type']").is(":checked")) {
                    btn_unassign.prop('disabled', false);
                }
            }
            else {
                btn_assign_degree.prop('disabled', true);
                btn_assign_conduit.prop('disabled', true);
                btn_unassign.prop('disabled', true);
            }
        });
    },

    buildSRLGTable: function (srlg_data) {
        var table = $('#srlgtable'), row = null, data = null;
        var srlg_data_json = JSON.parse(srlg_data);
        $.each(srlg_data_json, function(k1, v1) {
            if (typeof v1 !== 'object') {
                row = $('<tr></tr>');
                $('<td>'+k1+'</td>').appendTo(row);
                $('<td>'+v1+'</td>').appendTo(row);
                row.appendTo(table);
            }
            else {
                row = $('<tr></tr>');
                $('<td>'+k1+'</td>').appendTo(row);
                var fdn_string = "";
//                var fdns = v1['srrg-resource'];
                $.each(v1, function(k2, v2) {
                    $.each(v2, function(k3,v3) {
                        fdn_string += v3;
                    });
                });
                $('<td>'+fdn_string+'</td>').appendTo(row);
                row.appendTo(table);
            }
        });
    },

    sortTable: function (n, table_id) {
        var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
//        table = document.getElementById("topo_links_table");
        table = document.getElementById(table_id);
        switching = true;
        // Set the sorting direction to ascending:
        dir = "asc";
        /* Make a loop that will continue until
        no switching has been done: */
        while (switching) {
            // Start by saying: no switching is done:
            switching = false;
            rows = table.rows;
            /* Loop through all table rows (except the
            first, which contains table headers): */
            for (i = 0; i < (rows.length - 1); i++) {
              // Start by saying there should be no switching:
              shouldSwitch = false;
              /* Get the two elements you want to compare,
              one from current row and one from the next: */
              x = rows[i].getElementsByTagName("TD")[n];
              y = rows[i + 1].getElementsByTagName("TD")[n];
              /* Check if the two rows should switch place,
              based on the direction, asc or desc: */
              if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                  // If so, mark as a switch and break the loop:
                  shouldSwitch = true;
                  break;
                }
              } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                  // If so, mark as a switch and break the loop:
                  shouldSwitch = true;
                  break;
                }
              }
            }
            if (shouldSwitch) {
              /* If a switch has been marked, make the switch
              and mark that a switch has been done: */
              rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
              switching = true;
              // Each time a switch is done, increase this count by 1:
              switchcount ++;
            } else {
              /* If no switching has been done AND the direction is "asc",
              set the direction to "desc" and run the while loop again. */
              if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
              }
            }
        }
    }

};

