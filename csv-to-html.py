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
 <head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
 <title>bestellungen {{ now }} </title>
 <link rel="stylesheet" type="text/css" href="//cdn.datatables.net/1.10.5/css/jquery.dataTables.css">
<script src="//code.jquery.com/jquery-1.11.1.min.js"></script>
<script src="//cdn.datatables.net/1.10.5/js/jquery.dataTables.min.js"></script>

 <script>
$(document).ready(function() {
    var oTable = $('#table').dataTable( {
        "oLanguage": {
            "sSearch": "Search all columns:"
        },
        "columns": [
            { "width": "10%" }, /* Name */
            { "width": "5%" },  /* Gruppe */
            { "width": "5" },
            { "width": "5%" },
            { "width": "5%" },
            { "width": "5%" },
            { "width": "10%" },
        ]
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
   input[type=text] { width: 100%; }
   .small { font-size: 80% }
   .datum { color: #808080; }
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
 <table style="display:none" id="table" class="display" width="100%" data-page-length="10" data-order="[[ 2, &quot;desc&quot; ]]">
    <thead>
    <tr>
        <th>Name
            <br /><input type="text" name="search_name" value="Filtern nach Name" class="search_init">
        </th>
        <th>Gruppe
            <br /><input type="text" name="search_group" value="nach Gruppe" class="search_init">
        </th>
        <th>Datum
            <br /><input type="text" name="search_date" value="nach Datum" class="search_init">
        </th>
        <th>Abonnent
            <br /><input type="text" name="search_abonnent" value="nach Abonnent" class="search_init">
        </th>
        <th>Besteller
            <br /><input type="text" name="search_besteller" value="nach Besteller" class="search_init">
        </th>
        <th>Bestellnr.
            <br /><input type="text" name="search_bestnr" value="Bestellnr." class="search_init">
        </th>
        <th>Produkt
            <br /><input type="text" name="search_product" value="Produkt" class="search_init">
        </th>
    </tr>
    </thead>
    {% for row in data %}
    <tr>
        <td>{{row.first_name}} {{row.last_name}}
        </td>
        <td>
            <span class="small">{{row.groups|replace(",","<br/>")}}</span>
        </td>
        <td>{{row.htmldate}}</td>
        {% if row.abonnent_id %} 
            <td data-search="{{row.abonnent_id}}" data-sort="{{row.abonnent_id}}">{{row.abonnent|default(row.user_login)}} <span class="nr-in-bestellung">{{row['nr-in-bestellung']}}</span></td>
            <td data-search="{{row.besteller_id}}" data-sort="{{row.besteller_id}}"><a target="_blank" title="{{row.besteller_id}}" href="http://versicherungsmonitor.de/wp-admin/admin.php?page=wpsg-Customer&amp;s={{row.besteller_id}}">{{row.besteller_id|truncate(10,true)}}</a></td>
            <td data-search="{{row.bestellnr_id}}" data-sort="{{row.bestellnr_id}}">{{row.bestellnr}}</td>
            <td data-search="{{row.produkt}}" title="{{row.produkt}}">{{row.produkte|default(1)}} x {{row.produkt|truncate(30)}}</td>
        {% else %}
            <td data-search="{{row.user_login}}"><a target="_blank" href="http://versicherungsmonitor.de/wp-admin/users.php?s={{row.user_login}}">{{row.user_login}}</a></td>
            <td>-</td>
            <td data-search="xxx">xxx</td>
            <td>-</td>
        {% endif %}
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
    dd["abonnent_id"]=dd["abonnent_id"].lower()
    dd["htmldate"]=datetime.datetime.strptime(dd["datum"],"%Y-%m-%d %H:%M:%S").strftime('<span class="datum" title="%Y-%m-%d %H:%M:%S">%Y-%m-%d</span>')
    return dd


def read_data() :
    reader=csv.DictReader(input_stream,delimiter=";")
    ks=[] 
    for row in reader :
        ks.append(do_map(row))
    return ks

def read_reference(filename,index=lambda a: a["fieldname"]) :
    snif=csv.Sniffer()
    sniffed=snif.sniff(open(filename).read())
    reader=csv.DictReader(open(filename,"r",encoding="utf-8"),dialect=sniffed)
    res={}
    for row in reader :
        res[index(row)]=row
    return res

    


if __name__=="__main__" :
    bymail=read_reference(sys.argv[1],index=lambda r:r["@user_email"].lower())
    data=read_data()
    for obj in data :
        h=obj["abonnent_id"]
        if h in bymail :
            obj.update(bymail[h].copy())
            if "touched" in bymail[h] :
                bymail[h]["touched"]=bymail[h]["touched"]+1
            else :
                bymail[h]["touched"]=1
    for obj in bymail.values() :
        if "touched" not in obj :
            data.append(obj)
    sys.stdout.write(template.render(dict(data=data,now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))))




