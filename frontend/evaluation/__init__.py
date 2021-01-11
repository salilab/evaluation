from flask import render_template, request, send_from_directory, abort
import werkzeug.datastructures
import saliweb.frontend
from saliweb.frontend import get_completed_job, Parameter, FileParameter
import os
from . import submit, results_page


parameters = [Parameter("name", "Job name", optional=True),
              Parameter("modkey", "MODELLER license key"),
              FileParameter("pdb_file",
                            "PDB file containing model to be evaluated"),
              FileParameter("alignment_file", "Alignment file in PIR format",
                            optional=True),
              Parameter("seq_ident", "Target-template sequence identity",
                        optional=True)]
app = saliweb.frontend.make_application(__name__, parameters)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/job', methods=['GET', 'POST'])
def job():
    if request.method == 'GET':
        return saliweb.frontend.render_queue_page()
    else:
        return submit.handle_new_job()


@app.route('/results.cgi/<name>')  # compatibility with old perl-CGI scripts
@app.route('/job/<name>')
def results(name):
    # Simulate setting the HTTP Accept header if force_xml=True (for
    # backwards compatibility)
    if request.args.get('force_xml'):
        request.accept_mimetypes = werkzeug.datastructures.MIMEAccept(
            [('application/xml', 1.0)])
    job = get_completed_job(name, request.args.get('passwd'),
                            still_running_template='running.html')
    if any(os.path.exists(job.get_path(p))
           for p in ('input.tsvmod.pred', 'input.pred', 'input.pdb.results')):
        return results_page.show_results_page(job)
    else:
        return saliweb.frontend.render_results_template("results_failed.html",
                                                        job=job)


@app.route('/job/<name>/<path:fp>')
def results_file(name, fp):
    job = get_completed_job(name, request.args.get('passwd'))
    if (fp in ("evaluation.xml", "dope_profile.A.png", "modeller.log")
            or "dope_profile" in fp or "input.profile" in fp):
        return send_from_directory(job.directory, fp)
    else:
        abort(404)
