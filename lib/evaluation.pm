package evaluation;

use saliweb::frontend;

use strict;

our @ISA = "saliweb::frontend";

sub new {
    return saliweb::frontend::new(@_, @CONFIG@);
}

sub get_navigation_links {
    my $self = shift;
    my $q = $self->cgi;
    return [
        $q->a({-href=>$self->index_url}, "ModEval Home"),
        $q->a({-href=>$self->queue_url}, "Current queue"),
        $q->a({-href=>$self->help_url}, "Help"),
        $q->a({-href=>$self->contact_url}, "Contact")
        ];
}

sub get_project_menu {
    my $self = shift;
    my $version = $self->version_link;
    return <<MENU;
        <p>&nbsp;</p>
<h4><small>Authors:</small></h4>
<p>David Eramian<br />
Min-Yi Shen<br />
Francisco Melo</p>
<p>Ursula Pieper<br />
Ben Webb</p>
<br />
<h4><small>Corresponding Author:</small></h4>
<p>Andrej Sali</p>
<p><i>Version $version</i></p>
MENU
}

sub get_footer {
    my ($self) = @_;
    my $footer="<p>For more information, please consult the following publications:"
              ." <b>TSVMod</b>: D. Eramian, N. Eswar, M.Y. Shen, A. Sali. How well can the accuracy of comparative protein structure models be predicted? Protein Sci 17, 1881-1893, 2008<a href=\"//salilab.org/pdf/Eramian_ProteinSci_2008.pdf\"><img width=\"12px\" src=\"//salilab.org/img/pdf.gif\" border=\"0\" alt=\"PDF\" /></a>. "
              ."<b>DOPE</b>: M.Y. Shen, A. Sali. Statistical potential for assessment and prediction of protein structures. Protein Sci 15, 2507-2524, 2006<a href=\"//salilab.org/pdf/Colubri_JMolBiol_2006.pdf\"><img width=\"12px\" src=\"//salilab.org/img/pdf.gif\" border=\"0\" alt=\"PDF\" /></a>. "
              ."<b>GA341</b>: 	F. Melo, R. Sanchez, A. Sali. Statistical potentials for fold assessment. Protein Sci 11, 430-448, 2002<a href=\"//salilab.org/pdf/Melo_ProteinSci_2002.pdf\"><img width=\"12px\" src=\"//salilab.org/img/pdf.gif\" border=\"0\" alt=\"PDF\" /></a></p>. ";
    return "$footer";
}

sub get_page_is_responsive {
    my ($self, $page_name) = @_;
    return $self->SUPER::get_page_is_responsive($page_name)
           || $page_name eq 'index';
}

sub get_index_page {
    my ($self) = @_;
    my $q = $self->cgi;
    my $return=$q->h3("ModEval Model Evaluation Server");
    $return.=$q->h5("An evaluation tool for protein structure models");
    $return.=$q->start_multipart_form({-name=>"evaluationform",-method=>"post",-action=>$self->submit_url});

    my @table;
    push @table,
                $q->Tr(
                    $q->td("Job Name",$self->help_link("jobname")),
                    $q->td($q->textfield({-name=>"name",-size=>"20",-maxlength=>"200"}))),
                $q->Tr(
                    $q->td("Modeller Key",$self->help_link("modkey")),
                    $q->td($q->textfield({-name=>"modkey",
                                          -value=>$self->modeller_key,
                                          -size=>"20",-maxlength=>"200"}))),
                $q->Tr(
                    $q->td("Email Address (optional)",$self->help_link("email")),
                    $q->td($q->textfield({-name=>"email",-size=>"20",-maxlength=>"200"}))),
                $q->Tr(     
                    $q->td("Upload Model File (PDB Format)",$self->help_link("model_file")),
                    $q->td($q->filefield({-name=>"model_file",-size=>"20",-maxlength=>"200"}))),
                $q->Tr(
                    $q->td("Upload Alignment File (PIR Format, recommended)",
                          $self->help_link("alignment_file")),
                    $q->td($q->filefield({-name=>"alignment_file",-size=>"20",-maxlength=>"200"}))),
                $q->Tr(
                    $q->td("Target-Template Sequence Identity <br />(for GA341 score)",
                          $self->help_link("seq_ident")),
                    $q->td($q->textfield({-name=>"seq_ident",-size=>"20",-maxlength=>"200"})));

    push @table, $q->Tr( $q->td("&nbsp;"),$q->td({-align=>"left"},
                                  $q->submit(-label=>'Start evaluating'),
                                 $q->reset({-label=>' Reset '})));
    my $table="<table>".join("",@table)."</table>";
       
               
    return $return.$table.$q->end_form()."";
 
}

sub get_submit_parameter_help {
    my $self = shift;
    return [
        $self->parameter("name", "Job name", 1),
        $self->parameter("modkey", "MODELLER license key"),
        $self->file_parameter("model_file",
                              "PDB file containing model to be evaluated"),
        $self->file_parameter("alignment_file", "Alignment file in PIR format",
                              1),
        $self->parameter("seq_ident", "Target-template sequence identity", 1)
    ];
}

sub get_submit_page {

    my ($self) = @_;
    my $q = $self->cgi;
    my $model_file      = $q->upload('model_file');    # uploaded pdb file handle
    my $alignment_file= $q->upload('alignment_file');  # uploaded alignment file handle
    my $job_name      = $q->param('name')||"";         # user-provided job name
    my $email         = $q->param('email')||undef;     # user's e-mail
    my $modkey        = $q->param('modkey')||"";       # MODELLER key
    my $seq_ident     = $q->param('seq_ident')||"";       # Sequence Identity

    check_optional_email($email);
    check_modeller_key($modkey);

    my $job = $self->make_job($job_name, $email);
    my $jobdir = $job->directory;
    my $pdb_input = "$jobdir/input.pdb";
    my $job_summary = "$jobdir/summary.txt";
    $seq_ident=~s/%//g;
    if (!$seq_ident) {
       $seq_ident=30;
    }
    if ( !($seq_ident =~ /^\d+$/ )) { 
       throw saliweb::frontend::InputValidationError("Sequence identity must be an "
                                             ."integer between 0 and 100");
    }
    if ($seq_ident < 1) {
       $seq_ident=$seq_ident*100;
    }
    if (($seq_ident > 100 ) || ($seq_ident < 0)) {
       throw saliweb::frontend::InputValidationError("Sequence identity must be an "
                                             ."integer between 0 and 100");
    }

    open(SUM, ">$job_summary")
       or throw saliweb::frontend::InternalError("Cannot open $job_summary: $!");
    print SUM "JobName\t$job_name\n";
    if (defined($email)) {
        print SUM "Email\t$email\n";
    }
    print SUM "ModKey\t$modkey\n";
    print SUM "SeqIdent\t$seq_ident\n";
    print SUM "ModelFile\t$model_file\n";
    if (defined($alignment_file)) {
        print SUM "AlignmentFile\t$alignment_file\n";
    }
    close (SUM);

    open(INPDB, ">$pdb_input")
       or throw saliweb::frontend::InternalError("Cannot open $pdb_input: $!");
    while (my $line=<$model_file>) {
        print INPDB $line;
    }
    close INPDB
       or throw saliweb::frontend::InternalError("Cannot close $pdb_input: $!");
    if ($seq_ident) {
        open ("PAR",">$jobdir/parameters.txt");
        print PAR "SequenceIdentity:${seq_ident}\n";
        close PAR;
    }
    if ($alignment_file) {
        my $alignment_input = "$jobdir/alignment.pir";
        my $pdb_input = "$jobdir/alignment.pir";
        open(INALI, ">$alignment_input")
          or throw saliweb::frontend::InternalError("Cannot open $alignment_input: $!");
        while (my $line=<$alignment_file>){
            print INALI $line;
        }
        close INALI
           or throw saliweb::frontend::InternalError("Cannot close $pdb_input: $!");
    }
    
    $job->submit();

    my $return=
      $q->h1("Job Submitted") .
      $q->hr .
      $q->p("Your job has been submitted to the server! " .
            "Your job ID is " . $job->name . ".") .
      $q->p("Results will be found at <a href=\"" .
            $job->results_url . "\">".$job->results_url ."</a>.");
    if ($email) {
        $return.=$q->p("You will be notified at $email when job results " .
                       "are available.");
    }

    $return .=
      $q->p("You can check on your job at the " .
            "<a href=\"" . $self->queue_url .
            "\">Server queue status page</a>.").
      $q->p("The estimated execution time per request is ~1 min, depending on the server load.").
      $q->p("If you experience a problem or you do not receive the results " .
            "for more than 12 hours, please <a href=\"" .
            $self->contact_url . "\">contact us</a>.") .
      $q->p("Thank you for using our server and good luck in your research!").

    return "$return";
}

sub get_results_page {
    my ($self,$job) = @_;
    my $q = $self->cgi;
    my ($model_pdbfile,$path);
    if ((-e 'input.tsvmod.pred') || (-e 'input.pred') || (-e 'input.pdb.results')) {
        return $self->display_ok_job($q,$job);
    } else {
        return $self->display_failed_job($q,$job);
    }
}

sub display_ok_job {
    my ($self, $q, $job) = @_;
    my ($return,@table);
    my $error = 0;
    $return= $q->p("Job '<b>" . $job->name . "</b>' has completed.")."<p>";
    push @table,$q->Tr($q->td({-colspan=>"2"},"<h4><br />TSVMod Results</h4>"));
    
    my $tsvmod_file="input.tsvmod.pred";
    if (!(-e $tsvmod_file)) {
        $tsvmod_file="input.pred";
    }
    open ("PRED","$tsvmod_file")
       or throw saliweb::frontend::InternalError("Cannot open TSVMod file: $!");
    # Modelfile|Chain|TSVMod type|Feature Count|Relax Count|Size|Predicted RMSD|Predicted NO35|GA341|Pair|Surf|Comb|z-Dope
    # ../tests/model.pdb|_|MatchByTemplate|ALL|1|89|2.740|0.880|1.000000|-0.601924|-0.5387405|-0.7910116|-0.0515078
    my $newformat=0;
    my $tsvmod_ok=0;
    while (my $line=<PRED>) {
        (my $junk, my $chain, my $matchtype, my $featurecount, my $relaxcount, my $size, my $rmsd, my $no35, my @junk)=split(/\|/,$line);
        if ($chain eq "Chain") {
            $newformat=1;
        } elsif ($newformat == 1) {
            $tsvmod_ok=1;
            if ($chain eq "_") {$chain="A"};
            push @table,$q->Tr($q->th({-colspan=>"2"},"Chain $chain".$self->help_link("chain")),$q->td({-width=>"300px"},"&nbsp;"));
            push @table,$q->Tr($q->td("Match Type:".$self->help_link("matchtype")),$q->td(" $matchtype"));
            push @table,$q->Tr($q->td("Features Used:".$self->help_link("features")),$q->td(" $featurecount"));
            push @table,$q->Tr($q->td("Relax Count:".$self->help_link("relaxcount")),$q->td(" $relaxcount"));
            push @table,$q->Tr($q->td("Set Size:".$self->help_link("setsize")),$q->td(" $size"));
            push @table,$q->Tr($q->td("&nbsp;<br />Predicted RMSD:".$self->help_link("predrmsd")),$q->td("&nbsp;<br />$rmsd"));
            push @table,$q->Tr($q->td("Predicted Native Overlap (3.5):".$self->help_link("predno35")),$q->td(" $no35"));
            if (!$featurecount) {
                push @table,$q->Tr($q->td({-colspan=>"3"},$q->b($line)));
            }
               
        }
    }
    if (($tsvmod_ok == 0 ) && ($newformat == 1)) {
        # job failed
        push @table,$q->Tr($q->td("TSVMod failed on input PDB file".$self->help_link("tsvmod_failed")));
        $error++;
    }
    if ($newformat == 0) {
        open ("PRED","input.pdb.results")
            or throw saliweb::frontend::InternalError(
                       "Cannot open input.pdb.results: $!");
        while (my $line=<PRED>) {
            (my $key,my $value)=split(/\s+/,$line);
            unless ($key eq "Input_PDB:") {
                if ($key eq "Match_Type:") {
                    push @table,$q->Tr($q->td("Match Type:".$self->help_link("matchtype")),$q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
                } elsif ($key eq "Features_Used:") {
                    push @table,$q->Tr($q->td("Features Used:".$self->help_link("features")),$q->td(" $value"));
                } elsif ($key eq "Relax_count:") {
                    push @table,$q->Tr($q->td("Relax Count:".$self->help_link("relaxcount")),$q->td(" $value"));
                } elsif ($key eq "Set_size:") {
                    push @table,$q->Tr($q->td("Set Size:".$self->help_link("setsize")),$q->td(" $value"));
                } elsif ($key eq "Predicted_RMSD:") {
                    push @table,$q->Tr($q->td("&nbsp;<br />Predicted RMSD:".$self->help_link("predrmsd")),$q->td("&nbsp;<br />$value"));
                } elsif ($key eq "Pred_NO35:") {
                    push @table,$q->Tr($q->td("Predicted Native Overlap (3.5):".$self->help_link("predno35")),$q->td(" $value"));
                } elsif ($key eq "input.pdb") {
                   push @table,$q->Tr($q->td({-colspan=>"3"},$line));
                } elsif ($key eq "Error") {
                   push @table,$q->Tr($q->td({-colspan=>"3"},$q->b($line)));
                }

            }
        }
    }
    push @table,$q->Tr($q->td({-colspan=>"2"},"<h4><br />Modeller Scoring Results</h4>"));
    open ("PRED","modeller.results")
       or throw saliweb::frontend::InternalError(
                            "Cannot open modeller.results: $!");
    my @chains;
    my $oldchain="";
    while (my $line=<PRED>) {
         # Skip blank lines
         if ($line =~ /^\s*$/) {
            next;
         }
        (my $chain,my $key,my $value)=split(/\s+/,$line);
         push @chains,$chain;
         $value=sprintf "%.3f",$value;
         if ($chain eq "Error") {
            $error++;
            push @table,$q->Tr($q->td({-colspan=>"2"},$line.$self->help_link("modeller_error")));
         } elsif (($chain ne $oldchain) && ($chain ne "")) {
             push @table,$q->Tr($q->td({-colspan=>"2"},"<h4>Chain ${chain}</h4>"));
             $oldchain=$chain;
         }
         if ($key eq "ZDOPE") {
            push @table,$q->Tr($q->td("z-DOPE:".$self->help_link("z-dope")."<br />&nbsp;"),
                               $q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
         } elsif ($key eq "GA341") {
            push @table,$q->Tr($q->td("GA341:".$self->help_link("ga341")),
                               $q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
         } elsif ($key eq "Z-PAIR") {
            push @table,$q->Tr($q->td("z-pair:".$self->help_link("z-pair")),
                               $q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
         } elsif ($key eq "Z-SURF") {
            push @table,$q->Tr($q->td("z-surf:".$self->help_link("z-surf")),
                               $q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
         } elsif ($key eq "Z-COMBI") {
            push @table,$q->Tr($q->td("z-combi:".$self->help_link("z-combi")),
                               $q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
         } elsif ($key eq "SeqIdent") {
            push @table,$q->Tr($q->td("Sequence Identity".$self->help_link("seq_ident")."<br />&nbsp;"),
                               $q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
         } elsif ($key eq "Input_SeqIdent") {
            push @table,$q->Tr($q->td("Sequence Identity".$self->help_link("seq_ident")
                                      ."<br />(provided by user)<br />&nbsp;"),
                               $q->td(" $value"),$q->td({-width=>"300px"},"&nbsp;"));
         } 
    }
    my $profile="";
    my %saw;
    @saw{@chains} = ();
    my @unique_chains = sort keys %saw;  # remove sort if undesired

    my $xmlurl=$job->get_results_file_url("evaluation.xml");
    if (-f "dope_profile.svg") {
        push @table,$q->Tr($q->td({-colspan=>"2"},"<h4><br />DOPE Profile".$self->help_link("dope_profile")."</h4>"));
        my $imageurl=$job->get_results_file_url("dope_profile.svg");
        $profile=$q->Tr($q->td({-colspan=>3},"<img src=$imageurl class=\"big\"/>"));
    } elsif (-f "dope_profile.png") {
        push @table,$q->Tr($q->td({-colspan=>"2"},"<h4><br />DOPE Profile".$self->help_link("dope_profile")."</h4>"));
        my $imageurl=$job->get_results_file_url("dope_profile.png");
        $profile=$q->Tr($q->td({-colspan=>3},"<img src=$imageurl class=\"big\"/>"));
    } else {
        $error++;
        push @table,$q->Tr($q->td({-colspan=>"2"},"<p><br />DOPE Profile not available".$self->help_link("dope_profile")."</p>"));
    }
    push @table,$profile;
    if ($error >= 3) {
        push @table,$q->Tr($q->td({-colspan=>"2"},"<p><font color=red>Multiple Errors occurred! Please check your input PDB file.</font></p>"));
    }
    $return.=$q->table({-width=>"300px"},join("",@table));
    $return .= "<br />".$job->get_results_available_time();
    return $return;
}


sub display_failed_job {
    my ($self, $q, $job) = @_;
    my $return= $q->p("Your ModEval job '<b>" . $job->name .
                      "</b>' failed to produce results.");
    $return.=$q->p("For a discussion of some common input errors, please see " .
                   "the ". $q->a({-href=>$self->help_url . "#errors"}, "help page") .
                   ".");
    return $return;
}

sub allow_file_download {
    my ($self,$file) =@_;
    return $file eq "evaluation.xml" || $file eq 'dope_profile.A.png'
           || $file eq 'modeller.log' || grep/dope_profile/,$file;
}

