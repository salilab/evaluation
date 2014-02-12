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
