#!/usr/bin/perl -w

use saliweb::Test;
use saliweb::frontend;
use Test::More 'no_plan';
use Test::Exception;
use File::Temp;

BEGIN {
    use_ok('evaluation');
}

my $t = new saliweb::Test('evaluation');

# Check job submission
{
    my $self = $t->make_frontend();
    my $cgi = $self->cgi;

    my $tmpdir = File::Temp::tempdir(CLEANUP=>1);
    ok(chdir($tmpdir), "chdir into tempdir");

    ok(mkdir("incoming"), "mkdir incoming");
    ok(open(FH, "> test.pdb"), "Open test.pdb");
    print FH "REMARK\nATOM      2  CA  ALA     1      26.711  14.576   5.091\n";
    ok(close(FH), "Close test.pdb");
    open(FH, "test.pdb");

    throws_ok { $self->get_submit_page() }
              saliweb::frontend::InputValidationError,
              "no key";

    $cgi->param('seq_ident', 'garbage');
    throws_ok { $self->get_submit_page() }
              saliweb::frontend::InputValidationError,
              "non-integer sequence identity";
    $cgi->param('seq_ident', '200');
    throws_ok { $self->get_submit_page() }
              saliweb::frontend::InputValidationError,
              "out of range sequence identity";
    $cgi->param('seq_ident', '30');

    $cgi->param('model_file', \*FH);
    $cgi->param('job_name', 'test');
    $cgi->param('modkey', get_modeller_key());
    my $ret = $self->get_submit_page();
    like($ret, '/Your job has been submitted to the server! Your ' .
         'job ID is testjob/ms',
         "submit page HTML");
    chdir('/');
}

# Check job submission with alignment
{
    my $self = $t->make_frontend();
    my $cgi = $self->cgi;

    my $tmpdir = File::Temp::tempdir(CLEANUP=>1);
    ok(chdir($tmpdir), "chdir into tempdir");

    ok(mkdir("incoming"), "mkdir incoming");

    ok(open(FH, "> test.pdb"), "Open test.pdb");
    print FH "REMARK\nATOM      2  CA  ALA     1      26.711  14.576   5.091\n";
    ok(close(FH), "Close test.pdb");
    open(FH, "test.pdb");

    ok(open(FHA, "> test.ali"), "Open test.ali");
    print FHA "\n";
    ok(close(FHA), "Close test.ali");
    open(FHA, "test.ali");

    $cgi->param('model_file', \*FH);
    $cgi->param('alignment_file', \*FHA);
    $cgi->param('job_name', 'test');
    $cgi->param('email', 'test@test.com');
    $cgi->param('modkey', get_modeller_key());
    my $ret = $self->get_submit_page();
    like($ret, '/Your job has been submitted to the server! Your ' .
         'job ID is testjob.*' .
         'notified at test\@test.com when job results are available/ms',
         "submit page HTML");
    chdir('/');
}
