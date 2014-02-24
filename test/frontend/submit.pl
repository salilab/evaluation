#!/usr/bin/perl -w

use saliweb::Test;
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

    $cgi->param('model_file', \*FH);
    $cgi->param('job_name', 'test');
    $cgi->param('modkey', '***REMOVED***');
    my $ret = $self->get_submit_page();
    like($ret, '/Your job has been submitted to the server! Your ' .
         'job ID is testjob/ms',
         "submit page HTML");
    chdir('/');
}

