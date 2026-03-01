#!/usr/bin/env python3
"""
Genetic Health Analysis — Web Application

A Flask web app that lets users upload VCF or 23andMe genome files
and generates 6 comprehensive health reports.

Usage:
    python3 app.py
    # Local-only default: http://localhost:8000
    python3 app.py --share-lan
    # Shared on LAN: http://<your-ip>:8000
"""

import os
import sys
import uuid
import json
import threading
import zipfile
import io
import shutil
import traceback
from pathlib import Path
from datetime import datetime, timedelta

from flask import (Flask, request, render_template, jsonify,
                   send_file, redirect, url_for, send_from_directory)

# === Configuration ===
BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"
JOBS_DIR = BASE_DIR / ".tmp" / "jobs"

# Add scripts directory to Python path
sys.path.insert(0, str(SCRIPTS_DIR))

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB max upload

# In-memory job tracking
jobs = {}
jobs_lock = threading.Lock()


def update_job(job_id, **kwargs):
    """Thread-safe job update."""
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(kwargs)


def get_job(job_id):
    """Thread-safe job read."""
    with jobs_lock:
        return dict(jobs.get(job_id, {}))


def cleanup_old_jobs(max_age_hours=24):
    """Remove job directories older than max_age_hours."""
    if not JOBS_DIR.exists():
        return
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    for job_dir in JOBS_DIR.iterdir():
        if job_dir.is_dir():
            try:
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(job_dir)
                    with jobs_lock:
                        jobs.pop(job_dir.name, None)
            except Exception:
                pass


# =============================================================================
# ANALYSIS WORKER
# =============================================================================

def run_analysis_job(job_id, file_path, subject_name, is_vcf):
    """Background thread that runs the full genetic analysis pipeline."""
    try:
        job_dir = JOBS_DIR / job_id
        reports_dir = job_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        update_job(job_id, status='running', progress=5,
                   message='Starting analysis...')

        # --- Step 1: VCF conversion if needed ---
        if is_vcf:
            update_job(job_id, progress=8, message='Converting VCF to analysis format...')
            from vcf_to_23andme import convert_vcf_to_23andme
            genome_path = job_dir / "genome_converted.txt"
            convert_vcf_to_23andme(str(file_path), str(genome_path))
            update_job(job_id, progress=18, message='VCF conversion complete')
        else:
            genome_path = file_path

        # --- Step 2: Load genome ---
        update_job(job_id, progress=22, message='Loading genome data...')
        from run_full_analysis import (
            load_genome, load_pharmgkb, analyze_lifestyle_health,
            load_clinvar_and_analyze, generate_exhaustive_genetic_report,
            generate_disease_risk_report, generate_actionable_protocol
        )

        genome_by_rsid, genome_by_position = load_genome(genome_path)
        snp_count = len(genome_by_rsid)
        update_job(job_id, progress=32,
                   message=f'Loaded {snp_count:,} SNPs')

        # --- Step 3: Load PharmGKB ---
        update_job(job_id, progress=38, message='Loading drug interaction database...')
        pharmgkb = load_pharmgkb()
        update_job(job_id, progress=44,
                   message=f'Loaded {len(pharmgkb):,} drug interactions')

        # --- Step 4: Lifestyle/Health analysis ---
        update_job(job_id, progress=48, message='Analyzing lifestyle & health SNPs...')
        health_results = analyze_lifestyle_health(genome_by_rsid, pharmgkb)
        finding_count = len(health_results['findings'])
        pharmgkb_count = len(health_results['pharmgkb_findings'])
        update_job(job_id, progress=55,
                   message=f'Found {finding_count} health findings, {pharmgkb_count} drug interactions')

        # Save intermediate JSON
        results_json = {
            'findings': health_results['findings'],
            'pharmgkb_findings': health_results['pharmgkb_findings'],
            'summary': health_results['summary'],
        }
        with open(reports_dir / "comprehensive_results.json", 'w') as f:
            json.dump(results_json, f, indent=2)

        # --- Step 5: Generate exhaustive genetic report ---
        update_job(job_id, progress=58, message='Generating genetic report...')
        genetic_report_path = reports_dir / "EXHAUSTIVE_GENETIC_REPORT.md"
        generate_exhaustive_genetic_report(health_results, genetic_report_path, subject_name)

        # --- Step 6: ClinVar disease analysis ---
        update_job(job_id, progress=62, message='Scanning ClinVar disease database (341K+ variants)...')
        disease_findings, disease_stats = load_clinvar_and_analyze(genome_by_position)
        path_count = len(disease_findings.get('pathogenic', [])) if disease_findings else 0
        update_job(job_id, progress=72,
                   message=f'ClinVar scan complete — {path_count} pathogenic variants found')

        # --- Step 7: Generate disease risk report ---
        update_job(job_id, progress=75, message='Generating disease risk report...')
        if disease_findings:
            disease_report_path = reports_dir / "EXHAUSTIVE_DISEASE_RISK_REPORT.md"
            generate_disease_risk_report(disease_findings, disease_stats, snp_count,
                                         disease_report_path, subject_name)

        # --- Step 8: Generate actionable protocol ---
        update_job(job_id, progress=78, message='Generating health protocol...')
        protocol_path = reports_dir / "ACTIONABLE_HEALTH_PROTOCOL_V3.md"
        generate_actionable_protocol(health_results, disease_findings, protocol_path, subject_name)

        # --- Step 9: Generate additional reports ---
        update_job(job_id, progress=80, message='Generating simple report...')
        from generate_additional_reports import (
            generate_simple_report,
            generate_complete_easy_report,
            generate_swot_report,
            generate_prenatal_report
        )
        generate_simple_report(health_results, disease_findings, disease_stats,
                               str(reports_dir), subject_name)

        update_job(job_id, progress=85, message='Generating easy-to-read report...')
        generate_complete_easy_report(health_results, disease_findings, disease_stats,
                                      str(reports_dir), subject_name)

        update_job(job_id, progress=89, message='Generating SWOT analysis...')
        generate_swot_report(health_results, disease_findings, disease_stats,
                              str(reports_dir), subject_name)

        # --- Step 10: Generate prenatal report (Indian context) ---
        update_job(job_id, progress=93, message='Generating prenatal screening report (Indian context)...')
        generate_prenatal_report(health_results, disease_findings, disease_stats,
                                 str(reports_dir), subject_name)

        # --- Step 11: Collect reports ---
        report_files = sorted([f.name for f in reports_dir.iterdir()
                               if f.suffix == '.md'])

        stats_str = (f"{snp_count:,} SNPs analyzed | "
                     f"{finding_count} health findings | "
                     f"{pharmgkb_count} drug interactions | "
                     f"{path_count} disease variants")

        update_job(job_id,
                   status='complete',
                   progress=100,
                   message='Analysis complete!',
                   reports=report_files,
                   subject_name=subject_name or 'Subject',
                   stats=stats_str)

    except Exception as e:
        traceback.print_exc()
        update_job(job_id,
                   status='error',
                   error=f"{type(e).__name__}: {str(e)}")


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Upload page."""
    cleanup_old_jobs()
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload and start analysis."""
    # Validate file
    if 'genome_file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['genome_file']
    if file.filename == '':
        return redirect(url_for('index'))

    subject_name = request.form.get('subject_name', '').strip() or 'Subject'

    # Create job
    job_id = str(uuid.uuid4())[:8]
    job_dir = JOBS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    filename = file.filename
    file_path = job_dir / filename
    file.save(str(file_path))

    # Detect file type
    is_vcf = filename.lower().endswith('.vcf')

    # Initialize job
    with jobs_lock:
        jobs[job_id] = {
            'status': 'queued',
            'progress': 0,
            'message': 'File uploaded, starting analysis...',
            'reports': [],
            'error': None,
            'subject_name': subject_name,
            'stats': '',
            'created': datetime.now().isoformat()
        }

    # Start background analysis
    thread = threading.Thread(
        target=run_analysis_job,
        args=(job_id, file_path, subject_name, is_vcf),
        daemon=True
    )
    thread.start()

    return redirect(url_for('results', job_id=job_id))


@app.route('/status/<job_id>')
def status(job_id):
    """Return job status as JSON (polled by frontend)."""
    job = get_job(job_id)
    if not job:
        return jsonify({'status': 'not_found'}), 404
    return jsonify(job)


@app.route('/results/<job_id>')
def results(job_id):
    """Results page — shows progress or completed reports."""
    job = get_job(job_id)
    if not job:
        return redirect(url_for('index'))
    return render_template('results.html', job_id=job_id)


@app.route('/preview/<job_id>/<report_name>')
def preview(job_id, report_name):
    """Preview a markdown report rendered as HTML."""
    report_path = JOBS_DIR / job_id / "reports" / report_name
    if not report_path.exists():
        return "Report not found", 404

    markdown_content = report_path.read_text(encoding='utf-8')
    return render_template('preview.html',
                           job_id=job_id,
                           report_name=report_name,
                           markdown_content=markdown_content)


@app.route('/download/<job_id>/<report_name>')
def download(job_id, report_name):
    """Download a single report file."""
    report_path = JOBS_DIR / job_id / "reports" / report_name
    if not report_path.exists():
        return "Report not found", 404
    return send_file(str(report_path), as_attachment=True,
                     download_name=report_name)


@app.route('/download-all/<job_id>')
def download_all(job_id):
    """Download all reports as a ZIP file."""
    reports_dir = JOBS_DIR / job_id / "reports"
    if not reports_dir.exists():
        return "Reports not found", 404

    job = get_job(job_id)
    subject = job.get('subject_name', 'Subject').replace(' ', '_')

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for report_file in reports_dir.iterdir():
            if report_file.suffix in ('.md', '.json'):
                zf.write(report_file, report_file.name)

    zip_buffer.seek(0)
    zip_name = f"Genetic_Health_Reports_{subject}_{datetime.now().strftime('%Y%m%d')}.zip"
    return send_file(zip_buffer, as_attachment=True,
                     download_name=zip_name, mimetype='application/zip')


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    share_lan = "--share-lan" in sys.argv or os.getenv("GENETIC_HEALTH_SHARE_LAN") == "1"
    host = "0.0.0.0" if share_lan else "127.0.0.1"

    # Get local IP for display
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "localhost"

    print()
    print("=" * 60)
    print("  GENETIC HEALTH ANALYSIS — Web Application")
    print("=" * 60)
    print()
    print(f"  Local:   http://localhost:8000")
    if share_lan:
        print(f"  Network: http://{local_ip}:8000")
        print()
        print("  LAN sharing enabled for this run (--share-lan)")
    else:
        print("  LAN sharing disabled (default)")
        print("  Use --share-lan or GENETIC_HEALTH_SHARE_LAN=1 to share")
    print("  Press Ctrl+C to stop the server")
    print()
    print("=" * 60)

    app.run(host=host, port=8000, debug=False, threaded=True)
