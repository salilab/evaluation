#!/usr/bin/perl -w

use saliweb::Test;
use Test::More 'no_plan';

BEGIN {
    use_ok('evaluation');
}

my $t = new saliweb::Test('evaluation');

# Test get_navigation_links
{
    my $self = $t->make_frontend();
    my $links = $self->get_navigation_links();
    isa_ok($links, 'ARRAY', 'navigation links');
    like($links->[0], qr#<a href="http://modbase/top/">ModEval Home</a>#,
         'Index link');
    like($links->[1],
         qr#<a href="http://modbase/top/queue.cgi">Current queue</a>#,
         'Queue link');
}

# Test get_project_menu
{
    my $self = $t->make_frontend();
    my $txt = $self->get_project_menu();
    like($txt, qr/Authors.*Corresponding Author:.*Version testversion/ms,
         'get_project_menu');
}

# Test get_footer
{
    my $self = $t->make_frontend();
    my $txt = $self->get_footer();
    like($txt, qr/D\. Eramian.*Protein Sci 17.*F\. Melo.*Protein Sci/ms,
         'get_footer');
}

# Test get_index_page
{
    my $self = $t->make_frontend();
    my $txt = $self->get_index_page();
    like($txt, qr/evaluation tool for protein structure models/ms,
         'get_index_page');
}
