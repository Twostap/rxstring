################################################################################
#
#© Copyright 2025, Tyler Ostapyk
#This program is free software: you can redistribute it and/or modify it
#under the terms of the GNU General Public License as published by the Free
#Software Foundation, either version 3 of the License, or (at your option)
#any later version.
#
#This program is distributed in the hope that it will be useful, but WITHOUT
#ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You may have received a copy of the GNU General Public License along with
#this program. If not, see <https://www.gnu.org/licenses/>.
#
#################################################################################

#Name: RxString
#Description: This code produces a flask app that queries data sources for drug terms and creates a search string for use in bibliographic database searching
#Author: Tyler Ostapyk (tyler.ostapyk@umanitoba.ca)
#Date: December 3, 2025

# importing Flask and other modules
from flask import Flask, request, render_template
from unidecode import unidecode
from collections import OrderedDict
import requests
import csv
import sys
from bs4 import BeautifulSoup

# Flask constructor
app = Flask(__name__)  

#Google Analytics
googleanalytics = r"""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-EESD1S9033"></script>
<script src="/static/analytics.js"></script>
"""
#Get info from HTML form
@app.route('/', methods =["GET", "POST"])
def drugdata():
    if request.method == "POST":
       efile = request.files.get("emtreefile")
       # getting input with name = fname in HTML form
       drug = request.form.get("dname").lower()
       drug = drug.replace('"',"")
       MeSHSearch = request.form.get("MeSHSearch")
       RXSearch = request.form.get("RXSearch")
       WikidataSearch = request.form.get("WikidataSearch")
       PubChemSearch = request.form.get("PubChemSearch")
       DrugBankSearch = request.form.get("DrugBankSearch")
       LOCSearch = request.form.get("LOCSearch")
       EmtreeSearch = request.form.get("EmtreeSearch")
       PhraseSearch = request.form.get("PhraseSearch")
       TruncationSymbol = request.form.get("TruncationSymbol")
       TruncationFirst = request.form.get("TruncationFirst")
       TruncationSecond = request.form.get("TruncationSecond")
       drugallcaps = drug.upper()
       drugcapital = drug.capitalize()
       drugtitle = drug.title()
      
#Can use test if in virtual environment, noted out for now
       #if sys.prefix != sys.base_prefix:
       #     print("virtual")

       #elif sys.prefix == sys.base_prefix:
       #     print("not virtual")


#Check if search term was entered into the HTML form, if not then output notice asking them to enter a search again
       if drug=="":
            completestring = "Did not enter a search term. Please enter a search term and try again."
            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto;} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em;'><h2>Query Responses</h2>" + completestring + "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='window.history.go(-1)'></form>" + "</div><div style='margin-top: auto'><p style='font-size:.6em;'><br><br>© Copyright 2025 Tyler Ostapyk</p></div>"
            return FormattedPage

#When a search term was entered
       else:

             #MESH
#Check if MESH was selsect as a source
             if MeSHSearch=="on":

                   MESHterms = []
#MESH SPARQL Query for finding terms
                   MESHURL = "https://id.nlm.nih.gov/mesh/sparql?query=PREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%20PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%20PREFIX%20xsd%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%20PREFIX%20owl%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%20PREFIX%20meshv%3A%20%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2Fvocab%23%3E%20PREFIX%20mesh%3A%20%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F%3E%20PREFIX%20mesh2024%3A%20%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2024%2F%3E%20PREFIX%20mesh2023%3A%20%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2023%2F%3E%20PREFIX%20mesh2022%3A%20%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2022%2F%3E%20SELECT%20DISTINCT%20%3Fdescriptor%20FROM%20%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%3E%20WHERE%20%7B%20values%20%3Fdrug%20%7B%22" + drug +"%22%40en%20%22" + drugtitle + "%22%40en%20%22" + drugallcaps + "%22%40en%20%22" + drugcapital + "%22%40en%7D%20.%20%20%20%20%20%20%20%20%20%3Fterm%20meshv%3AaltLabel%7Cmeshv%3AprefLabel%20%3Fdrug%20.%20%20%20%20%20%20%20%20%20%3Fconcept%20meshv%3Aterm%7Cmeshv%3ApreferredTerm%20%3Fterm%20.%20%20%20%20%20%20%20%20%20%3Fconcept%20a%20meshv%3AConcept%20.%20%20%20%20%20%20%20%20%20%3Fdescriptor%20meshv%3Aconcept%7Cmeshv%3ApreferredConcept%20%3Fconcept%20.%20%20%20%20%20%20%20%20%20%20%3Fdescriptor%20a%20meshv%3ATopicalDescriptor%20.%7D&format=JSON&inference=false&offset=0&limit=1000"

                   MESHresponse = requests.get(url = MESHURL)
                   MESHdata = MESHresponse.json()
                   for result in MESHdata["results"]["bindings"]:
                               MESHnode = result["descriptor"]["value"]
#Testing if the query identified a term. If it did, get entry terms and append to MESHTerms array.
                               if MESHnode.startswith("http://id.nlm.nih"):
                                          MESHURL2 = "https://id.nlm.nih.gov/mesh/lookup/details"
                                          MESHPARAMS2 = {'descriptor':MESHnode,'includes':'terms'}
                                          MESHentryresponse = requests.get(url = MESHURL2, params = MESHPARAMS2)

                                          MESHentrydata = MESHentryresponse.json()

                                          for meshentry in MESHentrydata["terms"]:
                                                      MESHentrynode = meshentry["label"]
                                                      MESHterms.append(MESHentrynode)
                                          MESHterms = sorted(MESHterms)       
                                          MESHtermstring = ' OR '.join(MESHterms)
                                          MESHtermstring = MESHtermstring.replace("(","")
                                          MESHtermstring = MESHtermstring.replace(")","")
                                          MESHtermstring = MESHtermstring.replace(".","")
                                          MESHtermstring = MESHtermstring.replace(",","")
                                          MESHtermcheck = 1              
#Check if MESHterms array is still empty, and if it is pass 0 and "no results in MESH"
                   if MESHterms==[]:
                               MESHtermcheck = 0
                               MeshMatch = "No results in MESH"    

#If a MeSH term was found, query for the MESH id
                   if MESHtermcheck==1:
                               MESHURL3 = "https://id.nlm.nih.gov/mesh/lookup/label"
                               MESHPARAMS3 = {'resource':MESHnode}
                               MESHtermresponse = requests.get(url = MESHURL3, params = MESHPARAMS3)
                               MESHterm = MESHtermresponse.json()
                               MESHtermreplaced = "".join(MESHterm)

#If MeSH wasn't selected as a source return MESHterm check 0 and "did not search MeSH" text
             else:

                   MESHtermcheck = 0
                   MeshMatch = "Did not search MeSH"

             ###RXNorm

             if RXSearch=="on":
             
                 URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json"

                 PARAMS = {'name':drug}

                 rxnorm = requests.get(url = URL, params = PARAMS)

                 data = rxnorm.json()

                 rxresults = []

                 for rxnorm in data["idGroup"]:
                           for key, rxnormId in data.items():  
                               rxid = rxnormId["rxnormId"]
                               rxresults.append(rxid)

                 if rxresults==[]:
                           RXMatch = "No results in RXNorm"
                           rxnormstring = 0
                 else:
                           idstring = str(rxresults)
                           idnumber = idstring.split("'")[1]

                           rxalt = []

                           URL2 = "https://rxnav.nlm.nih.gov/REST/rxcui/" + idnumber + "/related.json"

                           relators = "has_tradename tradename_of consists_of has_precise_ingredient precise_ingredient_of"

                           PARAMS2 = {'rela':relators}

                           rxrelated = requests.get(url = URL2, params = PARAMS2)

                           relateddata = rxrelated.json()

                           testrelated = "{'relatedGroup': {'rxcui': None}}"

                           relateddatastring = str(relateddata)

                           if (testrelated)==relateddatastring:

                               RXMatch = "No Synonyms in RxNorm"
                               rxnormstring = 0

                           else:

                               for rxreturnedrelated in relateddata["relatedGroup"]["conceptGroup"]:
                                         for relate in rxreturnedrelated["conceptProperties"]:
                                                    node = relate["name"]
                                                    rxalt.append(node)

                               URL3 = "https://rxnav.nlm.nih.gov/REST/rxcui/" + idnumber + "/properties.json"

                               rxsynonyms = requests.get(url = URL3)

                               rxsyndata = rxsynonyms.json()

                               synnode = rxsyndata["properties"]["synonym"]
                               if synnode:
                                         rxalt.append(synnode)
                               rxalt = sorted(rxalt)
                               rxnormstring = ' OR '.join(rxalt)
                               rxnormstring = rxnormstring.replace(".","")
                               rxnormstring = rxnormstring.replace(",","")

             else:
                 rxnormstring = 0
                 RXMatch = "Did not search RXNorm"
             
             
             ##Querying Wikidata
             
             if WikidataSearch=="on":
                 QID = []  
                 from SPARQLWrapper import SPARQLWrapper, JSON

                 sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent="rxstring/1.0;(https://rxstring.ca; tyler.ostapyk@umanitoba.ca)")

                 #Match drug term, may want to limit to specific property, e.g. pharmaceutical products
                 term = '"' + drug + '"@en'
                 drugcapitalterm = '"' + drugcapital + '"@en'    
                 drugallcapsterm = '"' + drugallcaps + '"@en'  
                 drugtitleterm = '"' + drugtitle + '"@en'  
#Wikidata Query - looks for the drug term all caps and no caps in alt label or label and is "instance of" or "subclass of" drug, medication, or chemical compound or "has use" of medication
                 queryterm = f" select distinct ?item where {{values ?drug {{{term} {drugcapitalterm} {drugtitleterm} {drugallcapsterm}}}. ?item rdfs:label|skos:altLabel ?drug. values ?type {{wd:Q8386 wd:Q12140 wd:Q11173}}. {{?item wdt:P31*/wdt:P279* ?type}} UNION {{?item wdt:P366 wd:Q12140}}.}} LIMIT 1000"
                 sparql.setQuery(queryterm)
                 sparql.setReturnFormat(JSON)
                 ret = sparql.query().convert()
                 results = []
                 for r in ret["results"]["bindings"]:
                           for key, value in r.items():
                               u = value["value"]
                               q = u.split("http://www.wikidata.org/entity/")[1]
                               results.append(q)
                 altvalue = []
                 ingredientin = []
                 activeingredient = []
#For Wikidata items found, get QIDs
                 for n, num in enumerate(results):
                          if n==0:
                             QID1 = num
                             QID1 = "<a target='blank' href='https://www.wikidata.org/wiki/" + QID1 + "'>" + QID1 + "</a>"
                             QID.append(QID1)
                          elif n==1:
                             QID2 = num
                             QID2 = "<a target='blank' href='https://www.wikidata.org/wiki/" + QID2 + "'>" + QID2 + "</a>"
                             QID.append(QID2)
                          elif n==3:
                             QID3 = num
                             QID3 = "<a target='blank' href='https://www.wikidata.org/wiki/" + QID3 + "'>" + QID3 + "</a>"
                             QID.append(QID3)
                          elif n==4:
                             QID4 = num
                             QID4 = "<a target='blank' href='https://www.wikidata.org/wiki/" + QID4 + "'>" + QID4 + "</a>"
                             QID.append(QID4)
                          elif n==5:
                             QID5 = num
                             QID5 = "<a target='blank' href='https://www.wikidata.org/wiki/" + QID5 + "'>" + QID5 + "</a>"
                             QID.append(QID5)                              
                 QID = ", ".join(QID)

#For Wikidata items found, get alt labels, used in, and active ingredient terms, then join them
                 #AltLabels
                 for i in results:
                           query = f" select ?altLabel where {{wd:{i} skos:altLabel|rdfs:label ?altLabel. FILTER(LANG(?altLabel) = 'en').}} "
                           sparql.setQuery(query)
                           sparql.setReturnFormat(JSON)
                           alts = sparql.query().convert()
                           for altlabel in alts["results"]["bindings"]:
                               for key, value in altlabel.items():
                                         v = value["value"]
                                         altvalue.append(v)
   
                 ###Terms from UsedIn
                 for j in results:
                           query3 = f" select ?usedinLabel where {{?usedin wdt:P3781|wdt:P3780 wd:{j}. SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'en'. }} }} "
                           sparql.setQuery(query3)
                           sparql.setReturnFormat(JSON)
                           usedins = sparql.query().convert()
                           for usedlabels in usedins["results"]["bindings"]:
                               for key, value in usedlabels.items():
                                         u = value["value"]
                                         ingredientin.append(u)

                 ###Terms for active ingredient
                 for a in results:
                           query4 = f" select ?activeLabel where {{?active wdt:P3780 wd:{a}. SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'en'. }} }} "
                           sparql.setQuery(query4)
                           sparql.setReturnFormat(JSON)
                           active = sparql.query().convert()
                           for activelabels in active["results"]["bindings"]:
                               for key, value in activelabels.items():
                                         y = value["value"]
                                         activeingredient.append(y)


                 #Combine lists and convert to strings
                 if len(altvalue)!= 0 and leng(ingredientin)!=0 and len(activeingredient)!=0:
                           combinedwikidatalist = altvalue + ingredientin + activeingredient
                           combinedwikidatalist = sorted(combinedwikidatalist)
                           combined = ' OR '.join(combinedwikidatalist)
                           combined = combined.replace(".","")
                           combined = combined.replace("(","")
                           combined = combined.replace(")","")
                           combined = combined.replace("@","")
                           combined = combined.replace('"','')
                 elif len(altvalue)!=0 and len(ingredientin)!=0:
                           combinedwikidatalist = altvalue + ingredientin
                           combinedwikidatalist = sorted(combinedwikidatalist)
                           combined = ' OR '.join(combinedwikidatalist)
                           combined = combined.replace(".","")
                           combined = combined.replace("(","")
                           combined = combined.replace(")","")
                           combined = combined.replace("@","")
                           combined = combined.replace('"','')
                 elif len(ingredientin)!=0 and len(activeingredient)!=0:
                           combinedwikidatalist = ingredientin + activeingredient
                           combinedwikidatalist = sorted(combinedwikidatalist)
                           combined = ' OR '.join(combinedwikidatalist)
                           combined = combined.replace(".","")
                           combined = combined.replace("(","")
                           combined = combined.replace(")","")
                           combined = combined.replace("@","")
                           combined = combined.replace('"','')
                 elif len(altvalue!=0) and len(activeingredient)!=0:
                           combinedwikidatalist = altvalue + activeingredient
                           combinedwikidatalist = sorted(combinedwikidatalist)
                           combined = ' OR '.join(combinedwikidatalist)
                           combined = combined.replace(".","")
                           combined = combined.replace("(","")
                           combined = combined.replace(")","")
                           combined = combined.replace("@","")
                           combined = combined.replace('"','')
                 elif len(altvalue)!=0:
                           combinedwikidatalist = altvalue
                           combinedwikidatalist = sorted(combinedwikidatalist)
                           combined = ' OR '.join(combinedwikidatalist)
                           combined = combined.replace(".","")
                           combined = combined.replace("(","")
                           combined = combined.replace(")","")
                           combined = combined.replace("@","")
                           combined = combined.replace('"','')
                 elif len(ingredientin)!=0:
                           combinedwikidatalist = ingredientin
                           combinedwikidatalist = sorted(combinedwikidatalist)
                           combined = ' OR '.join(combinedwikidatalist)
                           combined = ing
                           combined = combined.replace(".","")
                           combined = combined.replace("(","")
                           combined = combined.replace(")","")
                           combined = combined.replace("@","")
                           combined = combined.replace('"','')
                 elif len(activeingredient)!=0:
                           combinedwikidatalist = activeingredient
                           combinedwikidatalist = sorted(combinedwikidatalist)
                           combined = ' OR '.join(combinedwikidatalist)
                           combined = combined.replace(".","")
                           combined = combined.replace("(","")
                           combined = combined.replace(")","")
                           combined = combined.replace("@","")
                           combined = combined.replace('"','')
                 else:
                           WikiMatch = "No results in Wikidata"
                           combined = 0

             else:
                 combined = 0
                 WikiMatch = "Did not search Wikidata"

             #PubChem
             #Could potentially search substances, this just searches compounds right now
             if PubChemSearch=="on":
                 
                 PubChemURL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/" + drug + "/synonyms/JSON"
                 PubChemResponse = requests.get(url = PubChemURL)
                 
                 if PubChemResponse.status_code==404:
                           PubTerms = 0
                           PubMatch = "No results in PubChem"

                 else:

                           PubChemData = PubChemResponse.json()


                           for pub in PubChemData["InformationList"]["Information"]:
                                         PubNode = pub["Synonym"]
                                
                           for cid in PubChemData["InformationList"]["Information"]:
                                         cidInt = cid["CID"]
                                         cidNode = str(cidInt)
                           PubTerms = ' OR '.join(PubNode)
                           PubTerms = PubTerms.replace("="," ")
                           PubTerms = PubTerms.replace("[","")
                           PubTerms = PubTerms.replace("]","")
                           PubTerms = PubTerms.replace("]"," ")
                           PubTerms = PubTerms.replace("'","")
                           PubTerms = PubTerms.replace("/","-")
                           PubTerms = PubTerms.replace(".","")
                           PubTerms = PubTerms.replace(":","-")
                           PubTerms = PubTerms.replace("{","")
                           PubTerms = PubTerms.replace("}","")
                           PubTerms = PubTerms.replace(";","")
                           PubTerms = PubTerms.replace(">","")
                           PubTerms = PubTerms.replace("<","")
                           PubTerms = PubTerms.replace(".","")
                           PubTerms = PubTerms.replace("(","")
                           PubTerms = PubTerms.replace(")","")
                           PubTerms = PubTerms.replace("@","")
                           PubTerms = PubTerms.replace('"','')
                           PubTerms = PubTerms.replace('^','')
                           PubTerms = PubTerms.replace(',','')
                           PubTerms = PubTerms.replace('?','')
                 
             else:

                 PubTerms = 0
                 PubMatch = "Did not search PubChem"             

             #DrugBank
             if DrugBankSearch=="on":
               DrugBankTerms = 0
               with open('drugbankvocabulary.csv', 'r', encoding="utf-8") as csv_file:
                 for row in csv.reader(csv_file):
                            if DrugBankTerms==0:
                                lowerrow = row[2].lower()
                                lowersyn = row[5].lower()
                                if lowerrow == drug:
                                          synonym = row[5]
                                          DrugBankTerms = synonym.replace(" | "," OR ")
                                          DrugBankTerms = DrugBankTerms.replace("[","")
                                          DrugBankTerms = DrugBankTerms.replace("]","")
                                          DrugBankTerms = DrugBankTerms.replace(", ","-")
                                          DrugBankTerms = DrugBankTerms.replace(".","")
                                          DrugBankTerms = DrugBankTerms.replace("(","")
                                          DrugBankTerms = DrugBankTerms.replace(")","")
                                          DrugBankid = row[0]
                                elif drug in lowersyn:
                                          synonym = row[5]
                                          DrugBankTerms = synonym.replace(" | "," OR ")
                                          DrugBankTerms = DrugBankTerms.replace("[","")
                                          DrugBankTerms = DrugBankTerms.replace("]","")
                                          DrugBankTerms = DrugBankTerms.replace(",","")
                                          DrugBankTerms = DrugBankTerms.replace(".","")
                                          DrugBankTerms = DrugBankTerms.replace("(","")
                                          DrugBankTerms = DrugBankTerms.replace(")","")
                                          DrugBankid = row[0]                            
               if DrugBankTerms==0:
                 DrugBankMatch = "No results in DrugBank"                            
             else:
               DrugBankTerms = 0
               DrugBankMatch = "Did not search DrugBank"

             if LOCSearch=="on":
             
                 LOCURL = "https://id.loc.gov/authorities/subjects/suggest2"

                 LOCPARAMS = {'q':drug}

                 LOC = requests.get(url = LOCURL, params = LOCPARAMS)
                                
                 LOCdata = LOC.json()

                 LOCTerms = []
                 
                 for LOCresult in LOCdata["hits"]:
                           LOCURI = LOCresult["uri"]
                           LOCid = LOCURI.replace("http://id.loc.gov/authorities/subjects/","")
                           LOCtermcheck = 1
                           for LOCalts in LOCresult["more"]["variantLabels"]:
                               LOCTerms.append(LOCalts)
                 
                 if LOCTerms==[]:
                           LOCMatch = "No results in Library of Congress"
                           LOCtermcheck = 0

                 if LOCtermcheck==1:
                           LOCTerms = " OR ".join(LOCTerms)
                           LOCTerms = LOCTerms.replace(" (Trademark)","")
                 
             else:
                 LOCtermcheck = 0
                 LOCMatch = "Did not search Library of Congress"

	     #Emtree

             if EmtreeSearch=="on":
               etreefile = efile.read()
               efilename = efile.filename.split(".")[0]   
               if efilename=="":
                 EmtreeTerms = 0
                 EmtreeMatch = "No Emtree file uploaded."
               else:
                 soup = BeautifulSoup(etreefile, 'html.parser')
                 target = soup.find('div',string='Used For:')
                 for etrees in target.find_next_siblings():
                            if etrees.name=="div":
                                          break
                            else:
                                          EmtreeTerms = etrees.text
                                          EmtreeTerms = EmtreeTerms.replace(u'\xa0', u'')
                                          EtreeQualifier = "(" + drug + ")" 
                                          EmtreeTerms = EmtreeTerms.replace(EtreeQualifier,"")
                                          EmtreeTerms = EmtreeTerms.replace("[Drug Trade Name]","")
                                          EmtreeTerms = EmtreeTerms.replace("(drug)","")
                                          EmtreeTerms = EmtreeTerms.replace("[","")
                                          EmtreeTerms = EmtreeTerms.replace("]","")
                                          EmtreeTerms = EmtreeTerms.replace(", ","-")
                                          EmtreeTerms = EmtreeTerms.replace(".","")
                                          EmtreeTerms = EmtreeTerms.replace("(","")
                                          EmtreeTerms = EmtreeTerms.replace(")"," ")
                                          EmtreeTerms = EmtreeTerms.replace("+","")
                                          EmtreeTerms = EmtreeTerms.replace(","," ")
                                          EmtreeTerms = EmtreeTerms.replace("'","")
                                          EmtreeTerms = ("\n".join(EmtreeTerms.split("\n")[:-3]))
                                          EmtreeTerms = EmtreeTerms.strip()
                                          EmtreeTerms = " OR ".join((EmtreeTerms).split("\n"))

             else:
               EmtreeTerms = 0
               EmtreeMatch = "Did not search Emtree"
                 

#Build results page based on values passed from each section above
             if MeSHSearch==None and RXSearch==None and WikidataSearch==None and PubChemSearch==None and DrugBankSearch==None and EmtreeSearch==None and LOCSearch==None:
                 completestring = "No sources were searched. Please select a data source for your query."
                 FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto;} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completestring +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='window.history.go(-1)'></form>"
             elif combined==0 and MESHtermcheck==0 and rxnormstring==0 and PubTerms==0 and DrugBankTerms==0 and EmtreeTerms==0 and LOCtermcheck==0:
                 completestring = "Search term returned no results in selected resources.<p>No Emtree file was uploaded.</p>"
                 FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto;} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completestring +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='window.history.go(-1)'></form>"
             else:
                 completestringarray = []
                 if MESHtermcheck!=0:
                  MESHHTML = "<b>MeSH  term:</b> " + "<a target='blank' href='" + MESHnode + "'>" + MESHtermreplaced + "</a>" + " <button id='MeSHButton' onclick='seeMeSHresults()' type='button' style='background-color:white; font-size: .8em; min-width:17px;'>+</button>" + "<div style='display: none;' id='MeSHSeparateResults'><br>" + MESHtermstring + "</div>"
                  completestringarray.append(MESHtermstring)
                 else:
                  MESHHTML = MeshMatch
                 if rxnormstring!=0:
                  RxHTML = "<br><br><b>RXCUI:</b> " + "<a target='blank' href='https://mor.nlm.nih.gov/RxNav/search?searchBy=RXCUI&searchTerm=" + idnumber + "'>" + idnumber + "</a>" + " <button id='RXNormButton' onclick='seeRXNormresults()' type='button' style='background-color:white; font-size: .8em; min-width:17px;'>+</button>" + "<div style='display: none;' id='RXNormSeparateResults'><br>" + rxnormstring + "</div>"
                  completestringarray.append(rxnormstring)
                 else:
                  RxHTML = "<br><br>" + RXMatch
                 if combined!=0:
                  WikidataHTML = "<br><br><b>Wikidata QID:</b> " + QID + " <button id='WikidataButton' onclick='seeWikidataresults()' type='button' style='background-color:white; font-size: .8em; min-width:17px;'>+</button>" + "<div style='display: none;' id='WikidataSeparateResults'><br>" + combined + "</div>"
                  completestringarray.append(combined)
                 else:
                  WikidataHTML = "<br><br>" + WikiMatch 
                 if PubTerms!=0:
                  PubHTML = "<br><br><b>CID:</b> "  + "<a target='blank' href='https://pubchem.ncbi.nlm.nih.gov/compound/" + cidNode + "'>" + cidNode + "</a>"
                  completestringarray.append(PubTerms)
                 else:
                    PubHTML = "<br><br>" + PubMatch                 
                 if DrugBankTerms!=0:
                  DrugBankHTML = "<br><br><b>DrugBank ID:  </b>" + "<a target='blank' href='https://go.drugbank.com/drugs/" + DrugBankid  + "'>" + DrugBankid + "</a>"
                  completestringarray.append(DrugBankTerms)
                 else:
                  DrugBankHTML = "<br><br>" + DrugBankMatch
                 if LOCtermcheck!=0:
                  LOCHTML = "<br><br><b>LCSH ID: </b>" + "<a target='blank' href='https://id.loc.gov/authorities/subjects/" + LOCid + "'>" + LOCid + "</a>"
                  completestringarray.append(LOCTerms)
                 else:
                  LOCHTML = "<br><br>" + LOCMatch		     
                 if EmtreeTerms!=0:
                  EmtreeHTML = "<br><br>" + "<b>Emtree Term: </b>" + efilename
                  completestringarray.append(EmtreeTerms)
                 else:
                  EmtreeHTML = "<br><br>" + EmtreeMatch
                 completestringjoined = " OR ".join(completestringarray)
				 
#Unidecode is a module that converts diacritics/greek to corresponding latin alphabet             
                 completestringjoined = unidecode(completestringjoined)
                 completestringjoined = completestringjoined.replace("(r)","")
                 completestringjoined = completestringjoined.replace("[","")
                 completestringjoined = completestringjoined.replace("|","")
                 completestringjoined = completestringjoined.replace("]","")
                 completestringjoined = completestringjoined.replace("~","-")
                 completestringjoined = completestringjoined.replace("#","")
                 completestringjoined = completestringjoined.replace("_","-")
                 completestringjoined = completestringjoined.replace(",","")
                 completestringjoined = completestringjoined.replace("+-","")
                 completestringjoined = completestringjoined.replace("-+","")
                 completestringjoined = completestringjoined.replace("+","")
                 completestringjoined = completestringjoined.replace("|","")
                 completestringjoined = completestringjoined.replace("/"," ")
                 completestringjoined = completestringjoined.lower()
                 completestringlist = completestringjoined.split(" or ")
                 completestringlist.append(drug)
                 dedupedlist = list(dict.fromkeys(completestringlist))
                 dedupedlist = sorted(dedupedlist)
                 completeintro = MESHHTML + RxHTML + WikidataHTML + PubHTML + DrugBankHTML + LOCHTML + EmtreeHTML
	       
                
           
           
#If phrase search is on put quotation marks around each separate term when joining
                 if PhraseSearch=="on":
                     if TruncationSymbol=="on":
                            dedupedstring = '*" OR "'.join(dedupedlist)
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + '"' + dedupedstring + '*"' 
                     elif TruncationSecond=="on":
                            TwoWordList = []
                            for x in dedupedlist:
                               TwoWordCheck = len(x.split())     
                               if TwoWordCheck >=2:           
                                          TwoWordTerm = x.split()[:2]
                                          TwoWordTerm = " ".join(TwoWordTerm)
                                          TwoWordList.append(TwoWordTerm)
                               else:
                                          TwoWordTerm = x.split()[:1] 
                                          TwoWordTerm = "".join(TwoWordTerm)                                          
                                          TwoWordList.append(TwoWordTerm)                                         
                            dedupedlist = list(dict.fromkeys(TwoWordList))
                            dedupedstring = '*" OR "'.join(dedupedlist)
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + '"' + dedupedstring + '*"'

                     elif TruncationFirst=="on":
                            OneWordList = [x.split()[0] for x in dedupedlist]
                            dedupedlist = list(dict.fromkeys(OneWordList))
                            dedupedstring = '*" OR "'.join(dedupedlist)
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + '"' + dedupedstring + '*"'
                     else:  
                            dedupedstring = '" OR "'.join(dedupedlist)
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + '"' + dedupedstring + '"'                         

                 elif PhraseSearch==None:

                     if TruncationSymbol=="on":
                            dedupedstring = "* OR ".join(dedupedlist)
                            dedupedstring = dedupedstring.replace("+-","")
                            dedupedstring = dedupedstring.replace("-+","")
                            dedupedstring = dedupedstring.replace(' and ',' "and" ')
                            dedupedstring = dedupedstring.replace(' or ',' "or" ')
                            dedupedstring = dedupedstring.replace(' not ',' "not" ')
                            dedupedstring = dedupedstring.replace(' LE ',' "LE" ')
                            dedupedstring = dedupedstring.replace(' PM ',' "PM" ')
                            dedupedstring = dedupedstring.replace(' PT ',' "PT" ')
                            dedupedstring = dedupedstring.replace('S2-','"S2"-')
                            dedupedstring = dedupedstring.replace('S1-','"S1"-')
                            dedupedstring = dedupedstring.replace('s2-','"s2"-')
                            dedupedstring = dedupedstring.replace('s1-','"s1"-')
                            dedupedstring = dedupedstring.replace('-s1','-"s1"')
                            dedupedstring = dedupedstring.replace('-S1','-"S1"')
                            dedupedstring = dedupedstring.replace(' CT ',' "CT" ')
                            dedupedstring = dedupedstring.replace(' RP ',' "RP" ')
                            dedupedstring = dedupedstring.replace(' use ',' "use" ')
                            dedupedstring = dedupedstring.replace("/"," ")
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + dedupedstring + "*" 
                     elif TruncationSecond=="on":
                            TwoWordList = []
                            for x in dedupedlist:
                               TwoWordCheck = len(x.split())     
                               if TwoWordCheck >=2:           
                                          TwoWordTerm = x.split()[:2]
                                          TwoWordTerm = " ".join(TwoWordTerm)
                                          TwoWordList.append(TwoWordTerm)
                               else:
                                          TwoWordTerm = x.split()[:1] 
                                          TwoWordTerm = "".join(TwoWordTerm)                                          
                                          TwoWordList.append(TwoWordTerm)    
                            dedupedlist = list(dict.fromkeys(TwoWordList))
                            dedupedstring = "* OR ".join(dedupedlist)
                            dedupedstring = dedupedstring.replace("+-","")
                            dedupedstring = dedupedstring.replace("-+","")
                            dedupedstring = dedupedstring.replace(' and ',' "and" ')
                            dedupedstring = dedupedstring.replace(' or ',' "or" ')
                            dedupedstring = dedupedstring.replace(' not ',' "not" ')
                            dedupedstring = dedupedstring.replace(' LE ',' "LE" ')
                            dedupedstring = dedupedstring.replace(' PM ',' "PM" ')
                            dedupedstring = dedupedstring.replace(' PT ',' "PT" ')
                            dedupedstring = dedupedstring.replace('S2-','"S2"-')
                            dedupedstring = dedupedstring.replace('S1-','"S1"-')
                            dedupedstring = dedupedstring.replace('s2-','"s2"-')
                            dedupedstring = dedupedstring.replace('s1-','"s1"-')
                            dedupedstring = dedupedstring.replace('-s1','-"s1"')
                            dedupedstring = dedupedstring.replace('-S1','-"S1"')
                            dedupedstring = dedupedstring.replace(' CT ',' "CT" ')
                            dedupedstring = dedupedstring.replace(' RP ',' "RP" ')
                            dedupedstring = dedupedstring.replace(' use ',' "use" ')
                            dedupedstring = dedupedstring.replace("/"," ")
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + dedupedstring + "*"

                     elif TruncationFirst=="on":
                            OneWordList = [x.split()[0] for x in dedupedlist]
                            dedupedlist = list(dict.fromkeys(OneWordList))
                            dedupedstring = "* OR ".join(dedupedlist)
                            dedupedstring = dedupedstring.replace("+-","")
                            dedupedstring = dedupedstring.replace("-+","")
                            dedupedstring = dedupedstring.replace(' and ',' "and" ')
                            dedupedstring = dedupedstring.replace(' or ',' "or" ')
                            dedupedstring = dedupedstring.replace(' not ',' "not" ')
                            dedupedstring = dedupedstring.replace(' LE ',' "LE" ')
                            dedupedstring = dedupedstring.replace(' PM ',' "PM" ')
                            dedupedstring = dedupedstring.replace(' PT ',' "PT" ')
                            dedupedstring = dedupedstring.replace('S2-','"S2"-')
                            dedupedstring = dedupedstring.replace('S1-','"S1"-')
                            dedupedstring = dedupedstring.replace('s2-','"s2"-')
                            dedupedstring = dedupedstring.replace('s1-','"s1"-')
                            dedupedstring = dedupedstring.replace('-s1','-"s1"')
                            dedupedstring = dedupedstring.replace('-S1','-"S1"')
                            dedupedstring = dedupedstring.replace(' CT ',' "CT" ')
                            dedupedstring = dedupedstring.replace(' RP ',' "RP" ')
                            dedupedstring = dedupedstring.replace(' use ',' "use" ')
                            dedupedstring = dedupedstring.replace("/"," ")
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + dedupedstring + "*"
                     else:  
                            dedupedstring = " OR ".join(dedupedlist)
                            dedupedstring = dedupedstring.replace("+-","")
                            dedupedstring = dedupedstring.replace("-+","")
                            dedupedstring = dedupedstring.replace(' and ',' "and" ')
                            dedupedstring = dedupedstring.replace(' or ',' "or" ')
                            dedupedstring = dedupedstring.replace(' not ',' "not" ')
                            dedupedstring = dedupedstring.replace(' LE ',' "LE" ')
                            dedupedstring = dedupedstring.replace(' PM ',' "PM" ')
                            dedupedstring = dedupedstring.replace(' PT ',' "PT" ')
                            dedupedstring = dedupedstring.replace('S2-','"S2"-')
                            dedupedstring = dedupedstring.replace('S1-','"S1"-')
                            dedupedstring = dedupedstring.replace('s2-','"s2"-')
                            dedupedstring = dedupedstring.replace('s1-','"s1"-')
                            dedupedstring = dedupedstring.replace('-s1','-"s1"')
                            dedupedstring = dedupedstring.replace('-S1','-"S1"')
                            dedupedstring = dedupedstring.replace(' CT ',' "CT" ')
                            dedupedstring = dedupedstring.replace(' RP ',' "RP" ')
                            dedupedstring = dedupedstring.replace(' use ',' "use" ')
                            dedupedstring = dedupedstring.replace("/"," ")
                            FormattedPage = "<html><head><title>RxString Results</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>h2 {font-size:1.4em;} .resultslogo {float:left;} .responsecontent {margin-left:120px; margin-top:25px;} @media only screen and (max-width: 600px) {.resultslogo {grid-area: 1 / span 3; float:none; height:auto;} .responsecontent {grid-area: 2 / span 3; margin-left:auto; margin-top:auto} .resultsfooter {grid-area: 3 / span 3;} .resultslogoimage {display:block; margin-left:auto; margin-right: auto;}</style>" + googleanalytics + "</head><body>" + "<div class='resultslogo' style='margin-top:10px'><img class='resultslogoimage' width='100px' src='https://raw.githubusercontent.com/Twostap/rxstring/refs/heads/main/rxstringcropped.png'/></div><div class='responsecontent' style='font-family:arial; font-size:.8em'><h2>Query Responses</h2>" + completeintro +  "<br><br>" +  "<form><input type='button' style='color: white; background-color: #01789f; border:1px solid black; padding:4px 10px' value='New search' onclick='history.go(-1)'></form>" + "<h2>Search string</h2>" + dedupedstring                         

                            sectionjavascript = """<script>
                            function seeMeSHresults() { 
                				if (document.getElementById('MeSHSeparateResults').style.display == 'none') { 
                    				document.getElementById('MeSHSeparateResults').style.display = 'block';
                    				document.getElementById('MeSHButton').innerHTML = '-';
                    			} 
                				else { 
                   					document.getElementById('MeSHSeparateResults').style.display = 'none';
                   					document.getElementById('MeSHButton').innerHTML = '+';
                   					}                 
                				}
                
             			function seeRXNormresults() { 
                			if (document.getElementById('RXNormSeparateResults').style.display == 'none') { 
                    			document.getElementById('RXNormSeparateResults').style.display = 'block';
                    			document.getElementById('RXNormButton').innerHTML = '-';
                    		} 
                			else { 
                   				document.getElementById('RXNormSeparateResults').style.display = 'none';
                   				document.getElementById('RXNormButton').innerHTML = '+';
                   				}                 
                			}

             			function seeWikidataresults() { 
                			if (document.getElementById('WikidataSeparateResults').style.display == 'none') { 
                    			document.getElementById('WikidataSeparateResults').style.display = 'block';
                    			document.getElementById('WikidataButton').innerHTML = '-';
                    		} 
                			else { 
                   				document.getElementById('WikidataSeparateResults').style.display = 'none';
                   				document.getElementById('WikidataButton').innerHTML = '+';
                   				}                 
                			}
                           
                
                            </script>"""
		   
#Add copyright after running unidecode or it will appear as (c)
             FormattedPage = FormattedPage + "</div><div style='margin-top: auto;'><p style='font-size:.6em'><br><br>© Copyright 2025 Tyler Ostapyk</p></div></body></html>" + sectionjavascript
             
             return FormattedPage
    return render_template("form.html")

if __name__=='__main__':
   app.run()








































