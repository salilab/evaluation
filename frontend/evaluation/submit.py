from flask import request
import saliweb.frontend
from werkzeug.utils import secure_filename
import werkzeug.datastructures


def handle_new_job():
    force_results_xml = False
    model_file = request.files.get("model_file")
    # Assume a request using the old name for PDB file is using the old REST
    # API, so force XML output of both this and the results page
    if model_file:
        force_results_xml = True
        request.accept_mimetypes = werkzeug.datastructures.MIMEAccept(
            [('application/xml', 1.0)])
    else:
        model_file = request.files.get("pdb_file")
    alignment_file = request.files.get("alignment_file")
    job_name = request.form.get("name")
    email = request.form.get("email")
    modkey = request.form.get("modkey")
    seq_ident = request.form.get("seq_ident", "")

    saliweb.frontend.check_email(email, required=False)
    saliweb.frontend.check_modeller_key(modkey)

    seq_ident = handle_seq_ident(seq_ident)

    if not model_file:
        raise saliweb.frontend.InputValidationError(
            "No coordinate file specified")

    job = saliweb.frontend.IncomingJob(job_name)
    with open(job.get_path('summary.txt'), 'w', encoding='utf-8') as fh:
        fh.write("JobName\t%s\n" % job_name)
        if email:
            fh.write("Email\t%s\n" % email)
        fh.write("ModKey\t%s\n" % modkey)
        fh.write("SeqIdent\t%d\n" % seq_ident)
        fh.write("ModelFile\t%s\n" % secure_filename(model_file.filename))
        if alignment_file:
            fh.write("AlignmentFile\t%s\n"
                     % secure_filename(alignment_file.filename))

    model_file.save(job.get_path('input.pdb'))
    with open(job.get_path('parameters.txt'), 'w') as fh:
        fh.write("SequenceIdentity:%d\n" % seq_ident)

    if alignment_file:
        alignment_file.save(job.get_path('alignment.pir'))

    job.submit(email, force_results_xml=force_results_xml)
    return saliweb.frontend.redirect_to_results_page(job)


def handle_seq_ident(seq_ident):
    # Strip % if a percentage was given
    seq_ident = seq_ident.replace('%', '')

    # Default to 30%
    if not seq_ident:
        return 30

    try:
        seq_ident = int(seq_ident)
    except ValueError:
        raise saliweb.frontend.InputValidationError(
               "Sequence identity must be an integer between 0 and 100")
    if seq_ident > 100 or seq_ident < 0:
        raise saliweb.frontend.InputValidationError(
               "Sequence identity must be an integer between 0 and 100")
    return seq_ident
