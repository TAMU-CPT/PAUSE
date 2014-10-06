INPUT=t/angus.bam

wig.starts.f.txt:
	pause_starts_to_wiggle.py --bam_file $(INPUT)

wig.coverage.f.txt:
	pause_coverage_to_wiggle.py --bam_file $(INPUT)

wig.highlights.f.txt: wig.starts.f.txt
	pause_analysis.py --starts wig.starts.f.txt --starts wig.starts.f.txt --bam_file $(INPUT)

out.svg: wig.highlights.f.txt wig.coverage.f.txt wig.starts.f.txt
	pause_plotter.py --coverage wig.coverage.f.txt --coverage wig.coverage.r.txt --starts wig.starts.f.txt --starts wig.starts.r.txt  --highlights wig.pause.f.txt --highlights wig.pause.r.txt
	mv pause_plot.txt out.svg

.PHONY: send clean

send: out.svg
	scp out.svg esr@cpt:/var/www/out.svg

clean:
	@rm -f wig*.txt out.svg
