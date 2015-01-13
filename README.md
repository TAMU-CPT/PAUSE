# PAUSE v2

This is a comlpete re-write of PAUSE based on more standard technologies like
Wig/BigWig and bx-python

# Notes on the Software

All principles of analysis from PAUSE v1 are retained, PAUSE v2 only simplifies
them and makes the code neater. Originally there were multiple steps of
`samtools` required to pre-process the data for PAUSE, now there is only one
step which process BAM data into coverage/start coverage data.

All files are now standard formats, i.e. Wig, instead of custom CSV/TSV files.
This should make it easier to load results into WebApollo/JBrowse/GBrowse for
further analysis.

There is a makefile provided which will execute the entire workflow (please
change the name in the header or pass `INPUT=filename.bam GENOME=filename.fa`)

# Analysis Notes

This portion is, as of now, mostly unimplemented. Eventually we'd like to
automatically annotate the regions (perhaps in GFF, with an IDA code) based on
prior knowledge of what each phage type looks like.

The `pause_analysis.py` tool analyses and calls peaks in the wig data. It
additionally produces a file named `pause_report.txt` which contains lots of
information regarding which peaks were called and which regions were examined
for possibly being repeat regions

# Installation

For developers:

```console
virtualenv env
. env/bin/activate
pip install -r requirements.txt
python setup.py develop
```

For end users:

```console
sudo pip install -r requirements.txt
sudo python setup.py install
```
