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

# Test get_start_html_parameters
{
    my $self = $t->make_frontend();
    my %param = $self->get_start_html_parameters("test");
    is($param{-style}->{-src}->[-1], "html/modeval.css");
}

# Test get_page_is_responsive
{
    my $self = $t->make_frontend();
    my $resp = $self->get_page_is_responsive();
    is($resp, 1);
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

# Test get_submit_parameter_help
{
    my $self = $t->make_frontend();
    my $help = $self->get_submit_parameter_help();
    isa_ok($help, 'ARRAY', 'get_submit_parameter_help links');
    is(scalar(@$help), 5, 'get_submit_parameter_help length');
}
