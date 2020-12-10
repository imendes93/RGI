#!/usr/bin/env python3

JSON_REPORTS = "$json_files".split()

html_template = """
<!DOCTYPE html>
<html>
<title>RGI-nf Report</title>
<head><meta charset="utf-8" />
</head>
<body>

<div>
<h1 style='text-align: center' id="RGI-nf-Report">RGI-nf Report<a class="anchor-link" href="#RGI-nf-Report">&#182;</a></h1>
<p>RGI-nf integrates <a href="https://github.com/arpcard/rgi">The Resistance Gene Identifier (RGI)</a> package to to predict resistome(s) from nucleotide data based on homology and SNP models. The application uses reference data from the <a href="https://card.mcmaster.ca/">Comprehensive Antibiotic Resistance Database (CARD)</a>.</p>
</div>

<div>
<h2 id="Results-Summary">Results Summary<a class="anchor-link" href="#Results-Summary">&#182;</a></h2>
<p style='text-align: center'>{0}</p>
</div>

<div>
<h3 id="Drug-Class">Drug Class<a class="anchor-link" href="#Drug-Class">&#182;</a></h3>
<p>AMR genes categorised by Drug Class. Yellow represents a perfect hit, teal represents a strict hit, purple represents no hit.
{1}</p>
</div>

<div>
<h3 id="Resistance-Mechanism">Resistance Mechanism<a class="anchor-link" href="#Resistance-Mechanism">&#182;</a></h3>
<p>AMR genes categorised by Resistance Mechanism. Yellow represents a perfect hit, teal represents a strict hit, purple represents no hit.
{2}</p>
</div>

<div>
<h3 id="Gene-Family">Gene Family<a class="anchor-link" href="#Gene-Family">&#182;</a></h3>
<p>AMR genes categorised by Resistance Mechanism. Yellow represents a perfect hit, teal represents a strict hit, purple represents no hit.
{3}</p>
</div>

</body>
</html>
"""

def main(summary_file):

    # TODO - load RGI Logo?

    # TODO - Results Summary
    with open(summary_file) as summary_fh:
        summary_table_html = summary_fh.read()

    f = open('multiqc_report.html','wb')
    f.write(html_template.format(summary_table_html, '', '', ''))
    f.close()

if __name__ == "__main__":
    main("/Users/inesmendes/lifebit/git/RGI/work/11/4336ce521c9fe7b59991515aa83131/results_summary.html")