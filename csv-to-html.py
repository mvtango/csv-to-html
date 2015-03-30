import csv
import json
import sys
import re
import io
import slugify
import jinja2
import datetime

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='iso-8859-1')

template=jinja2.Template("""
<html>
 <head><title>bestellungen {{ now }} </title>
 <link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.5/css/jquery.dataTables.css">
<script src="//code.jquery.com/jquery-1.11.1.min.js"></script>
<script src="//cdn.datatables.net/1.10.5/js/jquery.dataTables.min.js"></script>

 <script>
$(document).ready(function() {
    var oTable = $('#table').dataTable( {
        "oLanguage": {
            "sSearch": "Search all columns:"
        }
    } );
    var asInitVals=[];

    $('#loader').fadeOut();
    $('#table').fadeIn();
     
    $("thead input").keyup( function () {
        /* Filter on the column (the index) of this element */
        oTable.fnFilter( this.value, $("thead input").index(this) );
    } ).on("click",function(e) { 
        if ( this.className == "search_init" )
        {
            this.className = "";
            this.value = "";
        }
        e.stopPropagation() 
    });
     
     
     
    /*
     * Support functions to provide a little bit of 'user friendlyness' to the textboxes in
     * the footer
     */
    $("thead input").each( function (i) {
        asInitVals[i] = this.value;
    } );
     
    $("thead input").focus( function () {
        if ( this.className == "search_init" )
        {
            this.className = "";
            this.value = "";
        }
    } );
     
    $("thead input").blur( function (i) {
        if ( this.value == "" )
        {
            this.className = "search_init";
            this.value = asInitVals[$("thead input").index(this)];
        }
    } );
} );


 </script>
 <style>
   * { font-family: Verdana, Helvetica, Sans-Serif; font-size: 12px }
   body { margin-left: 10%; margin-right: 10%; }
   .nr-in-bestellung { float: right; color: #808080 }
 </style>

 </head>
 <body>
 <!--
    {{data[0]|pprint}}
 -->
 <div id="loader" style="position: absolute; width: 100%; text-align: center; height: 100px; background-color: #ffffff">
    <h1>Loading ...</h1>
 </div>
 <h3>Stand {{now}} </h3>
 <table style="display:none" id="table" class="display" width="100%" data-page-length="10" data-order="[[ 0, &quot;desc&quot; ]]">
    <thead>
    <tr>
        <th>Datum
            <br /><input type="text" name="search_date" value="Filtern nach Datum" class="search_init">
        </th>
        <th>Besteller
            <br /><input type="text" name="search_besteller" value="Filtern nach Besteller" class="search_init">
        </th>
        <th>Abonnent
            <br /><input type="text" name="search_abonnent" value="Filtern nach Abonnent" class="search_init">
        </th>
        <th>Bestellnr.
            <br /><input type="text" name="search_bestnr" value="Filtern nach Bestellnr." class="search_init">
        </th>
        <th>Produkt
            <br /><input type="text" name="search_product" value="Filtern nach Produkt" class="search_init">
        </th>
    </tr>
    </thead>
    {% for row in data %}
    <tr>
        <td>{{row.datum}}</td>
        <td data-search="{{row.besteller_id}}" data-sort="{{row.besteller_id}}">{{row.besteller}}</td>
        <td data-search="{{row.abonnent_id}}" data-sort="{{row.abonnent_id}}">{{row.abonnent}} <span class="nr-in-bestellung">{{row['nr-in-bestellung']}}</span></td>
        <td data-search="{{row.bestellnr_id}}" data-sort="{{row.bestellnr_id}}">{{row.bestellnr}}</td>
        <td data-search="{{row.produkt}}">{{row.produkte|default(1)}} x {{row.produkt}}</td>

    </tr>

    {% endfor %}

 </table>
 </body>
</html>
""")



def HYPERLINK(t,s) :
    try :
        s="%05i" % int(s)
    except ValueError :
        pass
    return(('<a target="_blank" href="{t}">{s}</a>'.format(**locals())),s)





def do_map(d) :
    dd={}
    for (k,v) in d.items() :
        s=slugify.slugify(k)
        while s in dd :
            s="%s_" % s
        if v.find("=HYPERLINK")==0 :
            v=v.replace(";",",")
            (dd[s],dd["%s_id" % s ])=eval(v[1:])
        else :
            dd[s]=d[k]
    return dd


def read_data() :
    reader=csv.DictReader(input_stream,delimiter=";")
    ks=[] 
    for row in reader :
        ks.append(do_map(row))
    return ks

    


if __name__=="__main__" :
    sys.stdout.write(template.render(dict(data=read_data(),now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))))




