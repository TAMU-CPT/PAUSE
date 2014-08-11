# This script generates a PNG picture of a 10K region containing a
# set of red features and a set of blue features. Call it like this:
#         red_and_blue.pl > redblue.png
# you can now view the picture with your favorite image application


# This script parses a GenBank or EMBL file named on the command
# line and produces a PNG rendering of it.  Call it like this:
# render.pl my_file.embl | display -

use strict;
use Bio::Graphics;
use Bio::SeqIO;
use Bio::SeqFeature::Generic;

my $file = shift                       or die "provide a sequence file as the argument";
my $io = Bio::SeqIO->new(-file=>$file) or die "could not create Bio::SeqIO";
my $seq = $io->next_seq                or die "could not find a sequence in the file";

my @features = $seq->all_SeqFeatures;

# sort features by their primary tags
my %sorted_features;
for my $f (@features) {
  my $tag = $f->primary_tag;
  push @{$sorted_features{$tag}},$f;
}

my $wholeseq = Bio::SeqFeature::Generic->new(-start=>1,-end=>$seq->length);

my $panel = Bio::Graphics::Panel->new(
                                     -length    => $seq->length,
                                     -key_style => 'between',
                                     -width     => 800,
                                     -pad_left  => 10,
                                     -pad_right => 10,
                                     );
$panel->add_track($wholeseq,
                 -glyph => 'arrow',
                 -bump => 0,
                 -double=>1,
                 -tick => 2);


$panel->add_track(undef,
                 -glyph  => 'wiggle_xyplot',
		 -basedir => '.',
		 -wigfile => 'angus.gff3',
                 -bgcolor => 'blue',
                 -label  => 1,
                );

# general case
my @colors = qw(cyan orange blue purple green chartreuse magenta yellow aqua);
my $idx    = 0;
for my $tag (sort keys %sorted_features) {
  my $features = $sorted_features{$tag};
  $panel->add_track($features,
                   -glyph    =>  'generic',
                   -bgcolor  =>  $colors[$idx++ % @colors],
                   -fgcolor  => 'black',
                   -font2color => 'red',
                   -key      => "${tag}s",
                   -bump     => +1,
                   -height   => 8,
                   -label    => 1,
                   -description => 1,
                  );
}

print $panel->png;
exit 0;
