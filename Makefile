
angus.starts.f.wig:
	python pause_starts_to_wiggle.py angus.bam

angus.coverage.f.wig:
	python pause_coverage_to_wiggle.py angus.bam

angus.f.highlights.wig: angus.starts.f.wig
	python pause_analysis.py --starts angus.starts.f.wig --starts angus.starts.r.wig --bam_file angus.bam

out.svg: angus.f.highlights.wig angus.coverage.f.wig angus.starts.f.wig
	python pause_plotter.py --coverage angus.coverage.f.wig --coverage angus.coverage.r.wig --starts angus.starts.f.wig --starts angus.starts.r.wig  --highlights angus.f.highlights.wig --highlights angus.r.highlights.wig ; scp out.svg esr@cpt:/var/www/out.svg 

clean:
	@rm -f *.wig out.svg
