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
use Bio::Graphics::Wiggle;

my $file = shift                       or die "provide a sequence file as the argument";

my $wholeseq = Bio::SeqFeature::Generic->new(-start=>1,-end=>40_500);


my $wig = Bio::Graphics::Wiggle->new($file,0);

my $panel = Bio::Graphics::Panel->new(
                                     -length    => 40_500,
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

$panel->add_track($wig,
		 -glyph  => 'wiggle_xyplot',
		 -bgcolor => 'blue',
		 -label  => 1,
		);


print $panel->png;
exit 0;
