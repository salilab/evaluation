#!/usr/bin/perl -w

use saliweb::Test;
use Test::More 'no_plan';
use Test::Exception;
use File::Temp qw(tempdir);

BEGIN {
    use_ok('evaluation');
    use_ok('saliweb::frontend');
}

my $t = new saliweb::Test('evaluation');

# Check results page

# Test allow_file_download
{
    my $self = $t->make_frontend();
    is($self->allow_file_download('bad.log'), 0,
       "allow_file_download bad file");

    is($self->allow_file_download('test_dope_profile.txt'), 1,
       "                    good file 1");
    is($self->allow_file_download('evaluation.xml'), 1,
       "                    good file 2");
    is($self->allow_file_download('dope_profile.A.png'), 1,
       "                    good file 3");
    is($self->allow_file_download('modeller.log'), 1,
       "                    good file 4");
}

# Test display_ok_job
{
    my $self = $t->make_frontend();
    my $tmpdir = tempdir(CLEANUP=>1);
    ok(chdir($tmpdir), "change to tmpdir");
    my $job = new saliweb::frontend::CompletedJob($self,
                        {name=>'testjob', passwd=>'foo', directory=>$tmpdir,
                         archive_time=>'2009-01-01 08:45:00'});
    ok(open(FH, "> input.tsvmod.pred"), "open tsvmod file");
    print FH <<END;
Modelfile|Chain|TSVMod type|Feature Count|Relax Count|Size|Predicted RMSD|Predicted NO35|GA341|Pair|Surf|Comb|z-Dope
input.pdb|A|MatchBySS|Reduced|1|420|18.314|0.104|0.694712|-0.6143005|-0.3749842|-0.6870231|0.1793957
END
    ok(close(FH), "close tsvmod file");
    ok(open(FH, "> modeller.results"), "open modeller file");
    print FH <<END;

A SeqIdent 30.000000

A ZDOPE 1.793957

A GA341 1.000000
A Z-PAIR -6.143005
A Z-SURF -3.749842
A Z-COMBI -6.870231
A Compactness 0.145962
END
    ok(close(FH), "close modeller file");
    my $ret = $self->get_results_page($job);
    like($ret, '/Predicted RMSD.*18\.314.*z-DOPE:.*1\.794.*' .
               'DOPE Profile not available/ms', "ok job, no DOPE profile");
    chdir('/')
}

# Test display_failed_job
{
    my $self = $t->make_frontend();
    my $tmpdir = tempdir(CLEANUP=>1);
    ok(chdir($tmpdir), "change to tmpdir");
    my $job = new saliweb::frontend::CompletedJob($self,
                        {name=>'testjob', passwd=>'foo', directory=>$tmpdir,
                         archive_time=>'2009-01-01 08:45:00'});
    my $ret = $self->get_results_page($job);
    like($ret, '/Your ModEval job.*failed to produce results/ms', "failed job");
    chdir('/')
}
