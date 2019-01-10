/*global WebSocket, JSON, $, window, console, alert*/
//"use strict";
/**
 * Function calls across the background TCP socket. Uses JSON RPC + a queue.
 * (I've added this extra logic to simplify expanding this)
 */

 $(document).ready(function() {

    $("#collectform").on("submit", function() {
        console.log("newMessage called from form submit!");
        newMessage($(this));
        return false;
    });

//    $("#collect").on("click", function() {
//        console.log("newMessage called from button click!");
//        $("#dropdownMenuLink").dropdown('toggle');
//        newMessage($("#dropdownform"));
//        return false;
//    });
//    $("#l1nodes_link").css('pointer-events', 'none');

//    $("#spinner").remove();
    client.connect(8002);
    console.log("Document ready!");
 });

function newMessage(form) {
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
//    btn.empty();
//    btn.text("Collect");
//    btn.attr('data-btn-text', "Collect");
}

//jQuery extended functions defined...
jQuery.fn.extend({
    form2Dict: function() {
        var fields = this.serializeArray();
        var json = {};
        $.each(fields, function(i,v) {
            json[fields[i].name] = fields[i].value;
        });
//        for (var i = 0; i < fields.length; i++) {
//            json[fields[i].name] = fields[i].value;
//        }
        if (json.next) delete json.next;
        return json;
    },
    postJSON: function(url, args, callback) {
//        args._xsrf = getCookie("_xsrf");
        json_body = JSON.stringify(args);
        json_body = $.param(args);
//        $.ajax({url: url, traditional: true, data: $.param(args), dataType: "json", type: "POST",
          $.ajax({url: url, data: json_body, type: "POST",
//                beforeSend: function() {
//                    $("#loading-indicator").show();
//                },
                success: function(response) {
//                foo = eval("(" + response + ")"); //foo and bar are equivalent ways to convert JSON string to JSON object
//                bar = JSON.parse(response);
//                    $("#loading-indicator").hide();
                    if (callback) callback(JSON.parse(response));
                },
                error: function(response) {
//                    $("#loader-indicator").hide();
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

    srlgtable: function (srlg) {
        console.log("srlgtable function called...");
        var uuid = this.uuid();
        var socket = this.socket;
        var queue = this.queue;
        this.waitForSocketConnection(this.socket, function() {
            console.log("Sending message to getsrlg...")
            console.log("UUID is: " + uuid)
            socket.send(JSON.stringify({method: "getsrlg", id: uuid, params: {srlg: srlg}}));
            queue[uuid] = "getsrlg";
        });
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
            var srrg_ad = v1['srrgs-ad'][0].split('=')[2];
            var srrg_lc = v1['srrgs-lc'][0].split('=')[2];
            row = $('<tr></tr>');
            $(node_a).appendTo(row);
            $(node_b).appendTo(row);
            $(fdn).appendTo(row);
            var srrg_ad_url = '<td><a href="'+origin+'/srlg/'+srrg_ad+'" name = "'+srrg_ad+'">'+srrg_ad+'</a></td>';
            $(srrg_ad_url).appendTo(row);
            var srrg_lc_url = '<td><a href="'+origin+'/srlg/'+srrg_lc+'" name = "'+srrg_lc+'">'+srrg_lc+'</a></td>';
            $(srrg_lc_url).appendTo(row);
            row.appendTo(table);
        });
    },

    buildL1nodesTable: function (l1nodes_data) {
        var pathname = window.location.pathname;
        var url = window.location.href;     // Returns full URL
        var origin   = window.location.origin;   // Returns base URL
        var table = $('#nodetable'), row = null, data = null;
        $('<th>Node Name</th><th>EPNM FDN</th><th>SRLGs</th>').appendTo(table);
        var l1nodes_data_json = JSON.parse(l1nodes_data);
        $.each(l1nodes_data_json, function(k1, v1) {
            var srrg = v1['srrgs'][0];
            try {
                var srrg_parsed = srrg.split('=')[2];
                var srrg_url = '<td><a href="'+origin+'/srlg/'+srrg_parsed+'" name = "'+srrg_parsed+'">'+srrg_parsed+'</a></td>';
            }
            catch (err) {
                var srrg_parsed = "none";
            }
            row = $('<tr></tr>');
            $('<td>'+v1['Name']+'</td>').appendTo(row);
            $('<td>'+v1['fdn']+'</td>').appendTo(row);
                        $(srrg_url).appendTo(row);
            row.appendTo(table);
        });
    },

    buildL1linksTable: function (l1links_data) {
        var table = $('#links_table'), row = null, data = null;
        $('<th>Node A</th><th>Node B</th><th>SRLG<th>').appendTo(table);
        var l1links_data_json = JSON.parse(l1links_data);
        $.each(l1links_data_json, function(k1, v1) {
            var srrg = v1['srrgs'][0];
            var srrg_parsed = srrg.split('=')[2];
            var pathname = window.location.pathname;
            var url      = window.location.href;     // Returns full URL
            var origin   = window.location.origin;   // Returns base URL
            row = $('<tr></tr>');
            $('<td>'+v1['Nodes'][0]+'</td>').appendTo(row);
            $('<td>'+v1['Nodes'][1]+'</td>').appendTo(row);
//            $('<td>'+v1['Name']+'</td>').appendTo(row);
//            $('<td>'+v1['fdn']+'</td>').appendTo(row);
            var srrg_url = '<td><a href="'+origin+'/srlg/'+srrg_parsed+'" name = "'+srrg_parsed+'">'+srrg_parsed+'</a></td>';
            $(srrg_url).appendTo(row);
            row.appendTo(table);
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
                $('<td>Its an object!!!</td>').appendTo(row);
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

