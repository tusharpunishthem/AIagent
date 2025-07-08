if resume is not None:
    result = analyze_fn(resume, jd_pdf.read().decode("latin1"), cutoff) if jd_pdf else analyze_fn(resume, role, cutoff)
