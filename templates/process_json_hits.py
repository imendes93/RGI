#!/usr/bin/env python3

import io
import os
import json 
import fnmatch
import pandas as pd
import numpy as np
#from pretty_html_table import build_table
import matplotlib
from collections import defaultdict, Counter
import seaborn as sns
import matplotlib.pyplot as plt

__version__ = "0.0.2"
__build__ = "14.01.2021"
__template__ = "PROCESS_RGI_HEATMAP-nf"

if __file__.endswith(".command.sh"):
    JSON_REPORTS = "$JSON_HITS".split()
    print("Running {} with parameters:".format(
        os.path.basename(__file__)))
    print("JSON_REPORTS: {}".format(JSON_REPORTS))

aro_link_template = '<a href="https://card.mcmaster.ca/aro/{0}">{0}</a>'

def create_categories(class_dict, df):
    """Reformats the dataframe to handle categorization data"""
    for model in class_dict:
        if len(class_dict[model]) > 1:
            df = df.append([df.loc[model]]*(len(class_dict[model])-1))

    # Assigns a unique identifier to each entry to index the dataframe without duplicates
    count = Counter(df.index.values)
    new_labels = df.index.tolist() # Add * to the models with duplicates
    new_index = []
    counted = {}
    for model in list(df.index.values):
        if count[model] > 1:
            idx = new_labels.index(model)
            new_labels[idx] = "%s*" % (model)

    for i, v in enumerate(list(df.index.values)):
        if v in counted:
            counted[v] += 1
            new_index.append(v+"_"+str(counted[v]))
        else:
            counted[v] = 0
            new_index.append(v+"_0")

    df.index = new_labels
    df = df.assign(uID=new_index)
    df = df.reset_index().set_index("uID")
    return df

def create_class_series(class_dict, name):
    """Create a pandas series for the classification chosen"""
    class_df = pd.Series(class_dict, name=name)
    class_df.index.name = "model_name"
    class_df = class_df.apply(tuple)
    class_df.reset_index()
    return class_df

def main(json_reports):
    sample_id = []
    genelist = [] # List of unique genes
    genes = {} # Will become the dataframe
    resist_mech = {} # key: gene, value: resistance mechanism
    drug_class = {} # key: gene, value: drug class
    gene_family = {} # key: gene, value: gene family
    aro = {} # key: gene, value: aro html url link
    excluded = [] # incompletely curated models

    for jsonfile in json_reports:
        # {json file: {Model: type_hit}}
        accession = os.path.basename(jsonfile).split(".")[0]
        sample_id.append(accession) # Don't take whole file name
        
        genes[accession] = {}
        with open(jsonfile) as data:
            rgi_data = json.load(data)
        try:  # remove undeeded stuff
            del rgi_data["_metadata"]
        except:
            pass

        try:
            tophits = {}
            # Top hit of each ORF
            for key,value in rgi_data.items():
                if isinstance(value, dict):
                    contig_id = key
                    hsp = max(value.keys(), key=(lambda key: value[key]['bit_score']))

                    # Flag to exclude loose hits
                    if value[hsp]["type_match"] != "Loose":
                        topmodel = value[hsp]["model_name"]
                        tophits[topmodel] = value[hsp]["type_match"]

                        # Build dictionary of model names and their classifications
                        try:                                
                            rm = 0
                            gf = 0
                            dc = 0
                            for entry in value[hsp]["ARO_category"]:
                                # ARO Accession
                                aro_accession = [value[hsp]["ARO_category"][entry]["category_aro_accession"]]
                                aro[value[hsp]["model_name"]] = aro_link_template.format(aro_accession)

                                # Resistance Mechanism classification
                                if value[hsp]["ARO_category"][entry]["category_aro_class_name"] == "Resistance Mechanism":
                                    rm += 1
                                    if value[hsp]["model_name"] not in resist_mech:
                                        resist_mech[value[hsp]["model_name"]] = [value[hsp]["ARO_category"][entry]["category_aro_name"]]
                                    else:
                                        if value[hsp]["ARO_category"][entry]["category_aro_name"] not in resist_mech[value[hsp]["model_name"]]:
                                            resist_mech[value[hsp]["model_name"]].append(value[hsp]["ARO_category"][entry]["category_aro_name"])

                                # Drug classes classification
                                elif value[hsp]["ARO_category"][entry]["category_aro_class_name"] == "Drug Class":
                                    dc += 1
                                    if value[hsp]["model_name"] not in drug_class:
                                        drug_class[value[hsp]["model_name"]] = [value[hsp]["ARO_category"][entry]["category_aro_name"]]
                                    else:
                                        if value[hsp]["ARO_category"][entry]["category_aro_name"] not in drug_class[value[hsp]["model_name"]]:
                                            drug_class[value[hsp]["model_name"]].append(value[hsp]["ARO_category"][entry]["category_aro_name"])

                                # Gene Family classification
                                elif value[hsp]["ARO_category"][entry]["category_aro_class_name"] == "AMR Gene Family":
                                    gf += 1
                                    if value[hsp]["model_name"] not in gene_family:
                                        gene_family[value[hsp]["model_name"]] = [value[hsp]["ARO_category"][entry]["category_aro_name"]]
                                    else:
                                        if value[hsp]["ARO_category"][entry]["category_aro_name"] not in gene_family[value[hsp]["model_name"]]:
                                            gene_family[value[hsp]["model_name"]].append(value[hsp]["ARO_category"][entry]["category_aro_name"])

                            # Flag to exclude model if it doesn't have classification for rm, gf, or dc
                            if any(x == 0 for x in [rm, gf, dc]):
                                del tophits[topmodel]
                                if topmodel not in excluded:
                                    excluded.append(topmodel)
                                try:
                                    del resist_mech[topmodel]
                                except:
                                    pass
                                try:
                                    del gene_family[topmodel]
                                except:
                                    pass
                                try:
                                    del drug_class[topmodel]
                                except:
                                    pass
                                # print(jsonfile, hsp)
                                # print("NOTE: %s excluded because it is missing complete categorization information." % (topmodel))

                        except Exception as e:
                            print(e)
                    else:
                        #print("Loose hit encountered. Not being added.")
                        pass
                        
            # Populates the matrix of typehits
            genes[accession] = tophits
            for x in tophits:
                if x not in genelist:
                    genelist.append(x)
        # except Exception as e:
        #     print(e)
        except:
            pass

    for e in excluded:
        print("NOTE: %s excluded because it is missing complete categorization information." % (e))

    genelist = sorted(genelist)

    # Create a dictionary that will convert type of hit to num. value
    conversion = {"Perfect": 2, "Strict": 1}

    # Apply conversion so hit criteria is number based
    for sample in genes:
        for gene in genes[sample]:
            genes[sample][gene] = conversion[genes[sample][gene]]
            #genes[sample][gene] = genes[sample][gene]
        for thing in genelist:
            if thing not in genes[sample]:
                genes[sample][thing] = 0

    # Create dataframe from genes dictionary
    df = pd.DataFrame.from_dict(genes)
    df.to_csv("card_hits.csv")

    # Fixed colourmap values (white, gray-blue, bright blue)
    cmap_values = [0, 1, 2, 3]
    custom_cmap = matplotlib.colors.ListedColormap(['#ffffff', '#5a6e92', '#04a0fc'])
    norm = matplotlib.colors.BoundaryNorm(cmap_values, custom_cmap.N)

    # Create 3 series, one for each classification type
    class_df1 = create_class_series(drug_class, "drug_class")
    class_df2 = create_class_series(resist_mech, "resistance_mechanism")
    class_df3 = create_class_series(gene_family, "gene_family")
    class_aro = create_class_series(aro, "aro_accession")

    # create plot
    sns.heatmap(df, cmap=custom_cmap, cbar=False, norm=norm)
    sns.set_style("white")
    plt.savefig("card_hits_headmap.png", bbox_inches="tight", format="png", pad_inches=0.5)

    # create table with classification - DataFrame

    results_table = pd.concat([df, class_df1, class_df2, class_df3, class_aro], axis=1, join='inner')
    results_table = results_table.drop(columns=df.columns).reset_index()
    results_table.to_csv("results_hits.csv", index=False)


if __name__ == '__main__':
    main(JSON_REPORTS)
