import html

def generate_portfolio_html(portfolio_data):
    # --- Data Extraction ---
    hero_name = portfolio_data.get("hero_name", "Portfolio") or "Portfolio"
    # Split name for the visual accent effect (First word white, rest gradient)
    name_parts = hero_name.split(' ')
    first_name = name_parts[0] if name_parts else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
    
    hero_title = portfolio_data.get("hero_title", "") or ""
    hero_summary = portfolio_data.get("hero_summary", "") or ""
    about_me = portfolio_data.get("about_me", "") or ""
    profile_image = portfolio_data.get("profile_image", "") or ""

    education = portfolio_data.get("education", []) or []
    experience = portfolio_data.get("experience", []) or []
    projects = portfolio_data.get("projects", []) or []
    
    # Normalize skills
    skills = portfolio_data.get("skills", {})
    if isinstance(skills, list):
        skills = {"technical": skills, "soft": []}

    certifications = portfolio_data.get("certifications", []) or []

    contact_email = portfolio_data.get("contact_email", "") or ""
    contact_linkedin = portfolio_data.get("contact_linkedin", "") or ""
    contact_github = portfolio_data.get("contact_github", "") or ""
    resume_link = portfolio_data.get("resume_link", "") or ""

    # Calculate Stats for Hero Section
    years_exp = len(experience)
    cert_count = len(certifications)
    # Attempt to find a CGPA/GPA in education to display, else show project count
    hero_stat_number = str(len(projects)) + "+"
    hero_stat_label = "Projects"
    
    for edu in education:
        if isinstance(edu, dict):
            details = edu.get("details", "")
            if "GPA" in details or "CGPA" in details:
                # Naive extraction for demo purposes
                hero_stat_number = details.split(":")[-1].strip()
                hero_stat_label = "CGPA/GPA"
                break

    # --- HTML Component Generators ---

    # 1. Education
    edu_html = ""
    for edu in education:
        if isinstance(edu, dict):
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            period = edu.get("period") or edu.get("year", "")
            details = edu.get("details", "")
            
            edu_html += f"""
            <div class="edu-card">
                <h3>Education</h3>
                <div class="edu-details">
                    <div class="edu-degree">{html.escape(str(degree))}</div>
                    <div class="edu-field">{html.escape(str(institution))}</div>
                    <div class="edu-duration">{html.escape(str(period))}</div>
                    <div class="edu-cgpa">{html.escape(str(details))}</div>
                </div>
            </div>
            """
        elif isinstance(edu, str):
             edu_html += f"""<div class="edu-card"><div class="edu-details"><div class="edu-degree">{html.escape(edu)}</div></div></div>"""

    # 2. Skills
    tech_skills = skills.get("technical", []) or []
    soft_skills = skills.get("soft", []) or []
    
    def generate_skill_list(skill_list):
        items = ""
        for skill in skill_list:
            if not isinstance(skill, str) or not skill.strip(): continue
            # Generic SVG icon for skills
            items += f"""
            <div class="skill-item-new">
                <div class="skill-header">
                    <div class="skill-name-icon">
                        <span class="skill-icon-new">
                            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 512 512" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M480 256c0 123.4-100.5 223.9-223.9 223.9S32.1 379.4 32.1 256 132.6 32.1 256.1 32.1 480 132.5 480 256zm-364.6-45.9c0-10.6-6.4-15.5-16.7-15.5-11.8 0-17.6 5.8-17.6 15.6s5.8 15.6 17.6 15.6c10.3.1 16.7-4.8 16.7-15.7zm65.6 102.7c-9.1 0-14.7 4.5-14.7 13.9 0 8.7 5.8 14.5 15 14.5 8.7 0 14.2-6.1 14.2-14.5 0-9.4-5.5-13.9-14.5-13.9zm161 14.2c0 8.4 5.5 14.5 14.2 14.5 9.2 0 15-5.8 15-14.5 0-9.4-5.6-13.9-14.7-13.9-9 0-14.5 4.5-14.5 13.9z"></path></svg>
                        </span>
                        <span class="skill-name-new">{html.escape(skill)}</span>
                    </div>
                </div>
            </div>
            """
        return items

    tech_skills_html = generate_skill_list(tech_skills)
    soft_skills_html = generate_skill_list(soft_skills)

    # 3. Experience
    exp_html = ""
    # Cycle colors for markers
    colors = ["rgb(16, 185, 129)", "rgb(139, 92, 246)", "rgb(59, 130, 246)"]
    
    for i, e in enumerate(experience):
        title = e.get("title", "")
        company = e.get("company", "")
        period = e.get("period", "")
        bullets = e.get("bullets", [])
        
        li_items = "".join([f"<li>{html.escape(b)}</li>" for b in bullets if isinstance(b, str)])
        marker_color = colors[i % len(colors)]
        
        exp_html += f"""
        <div class="exp-card">
            <div class="exp-marker" style="background-color: {marker_color};"></div>
            <div class="exp-content">
                <div class="exp-header">
                    <div>
                        <h3 class="exp-role">{html.escape(title)}</h3>
                        <div class="exp-company">{html.escape(company)}</div>
                    </div>
                    <div class="exp-duration">{html.escape(period)}</div>
                </div>
                <ul class="exp-points">
                    {li_items}
                </ul>
            </div>
        </div>
        """

    # 4. Projects
    projects_html = ""
    # Cycle gradients for headers
    gradients = [
        "linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%)",
        "linear-gradient(135deg, rgb(240, 147, 251) 0%, rgb(245, 87, 108) 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
    ]

    for i, p in enumerate(projects):
        name = p.get("name", "")
        duration = p.get("duration", "")
        tech_stack = p.get("tech_stack", [])
        highlights = p.get("highlights", [])
        github_link = p.get("github_link", "")
        
        desc = highlights[0] if highlights else ""
        tags_html = "".join([f"<span class='project-tag'>{html.escape(t)}</span>" for t in tech_stack])
        bg_style = gradients[i % len(gradients)]
        
        link_html = ""
        if github_link:
            link_html = f"""<a href="{github_link}" target="_blank" class="project-link-icon" title="View Code"><svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 496 512" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8z"></path></svg></a>"""

        projects_html += f"""
        <div class="project-card-new">
            <div class="project-header" style="background: {bg_style};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 class="project-title-new">{html.escape(name)}</h3>
                    {link_html}
                </div>
                <p class="project-duration-new">{html.escape(duration)}</p>
            </div>
            <div class="project-body">
                <p class="project-desc">{html.escape(desc)}</p>
                <div class="project-tags">
                    {tags_html}
                </div>
            </div>
        </div>
        """

    # 5. Certifications
    cert_html = ""
    for c in certifications:
        name = ""
        issuer = ""
        date = ""
        url = "#"
        
        if isinstance(c, dict):
            name = c.get("name") or c.get("title", "")
            issuer = c.get("issuer") or c.get("organization", "")
            date = c.get("date") or c.get("year", "")
            url = c.get("url") or c.get("link", "#")
        elif isinstance(c, str):
            name = c
            
        cert_html += f"""
        <a href="{url}" target="_blank" rel="noopener noreferrer" class="cert-card-new">
            <div class="cert-header">
                <h4 class="cert-name">{html.escape(name)}</h4>
            </div>
            <div class="cert-issuer">{html.escape(issuer)}</div>
            <div class="cert-date">{html.escape(date)}</div>
        </a>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(hero_name)} - Portfolio</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&family=Fira+Sans:wght@300;400;500;600&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{
            font-family: 'Fira Sans', sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            overflow-x: hidden;
            line-height: 1.6;
        }}
        
        /* Navbar */
        .navbar {{
            position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
            display: flex; justify-content: space-between; align-items: center;
            padding: 1.5rem 5%; background: rgba(10, 10, 10, 0.95);
            backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .nav-brand {{
            font-family: 'Manrope', sans-serif; font-size: 1.8rem; font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-link {{
            text-decoration: none; color: #b0b0b0; font-size: 0.95rem; font-weight: 500;
            transition: color 0.3s ease; position: relative; padding: 0.5rem 0;
        }}
        .nav-link:hover {{ color: #ffffff; }}
        .nav-link::after {{
            content: ''; position: absolute; bottom: 0; left: 0; width: 0; height: 2px;
            background: linear-gradient(90deg, #667eea, #764ba2); transition: width 0.3s ease;
        }}
        .nav-link:hover::after {{ width: 100%; }}
        
        /* Hero */
        .hero-new {{
            min-height: 100vh; display: flex; align-items: center; padding: 8rem 5% 4rem;
            position: relative; overflow: hidden;
        }}
        .hero-bg-pattern {{
            position: absolute; inset: 0; z-index: 0;
            background: radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.15) 0%, transparent 50%);
        }}
        .hero-container {{
            max-width: 1400px; margin: 0 auto; display: grid; grid-template-columns: 1.2fr 1fr;
            gap: 4rem; align-items: center; position: relative; z-index: 1; width: 100%;
        }}
        .hero-title-new {{
            font-family: 'Manrope', sans-serif; font-size: clamp(3rem, 7vw, 5.5rem);
            font-weight: 800; line-height: 1.1; margin-bottom: 1rem;
            display: flex; flex-direction: column;
        }}
        .hero-name-accent {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .hero-subtitle-new {{
            font-size: clamp(1.1rem, 2vw, 1.4rem); color: #b0b0b0; margin-bottom: 2.5rem;
        }}
        .hero-stats {{ display: flex; gap: 3rem; margin-bottom: 2.5rem; }}
        .stat-number {{
            font-family: 'Manrope', sans-serif; font-size: 2.5rem; font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .stat-label {{ font-size: 0.85rem; color: #b0b0b0; text-transform: uppercase; margin-top: 0.25rem; }}
        
        /* Buttons */
        .btn-primary, .btn-secondary {{
            padding: 1rem 2rem; border-radius: 12px; font-size: 1rem; font-weight: 600;
            cursor: pointer; transition: all 0.3s ease; display: inline-flex; align-items: center;
            gap: 0.5rem; text-decoration: none; border: none;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5); }}
        .btn-secondary {{
            background: transparent; color: white; border: 2px solid rgba(255, 255, 255, 0.2);
        }}
        .btn-secondary:hover {{ border-color: rgba(255, 255, 255, 0.5); background: rgba(255, 255, 255, 0.05); }}

        /* Image Profile */
        .profile-frame {{
            position: relative; width: 100%; max-width: 450px; aspect-ratio: 1; margin: 0 auto;
        }}
        .profile-frame::before {{
            content: ''; position: absolute; inset: -5px;
            background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
            border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
            animation: morphing 8s ease-in-out infinite; z-index: -1;
        }}
        .profile-img-new {{
            width: 100%; height: 100%; object-fit: cover;
            border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
            animation: morphing 8s ease-in-out infinite;
        }}
        @keyframes morphing {{
            0%, 100% {{ border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; }}
            50% {{ border-radius: 70% 30% 30% 70% / 70% 70% 30% 30%; }}
        }}

        /* General Sections */
        .section-new {{ padding: 6rem 5%; position: relative; }}
        .container-new {{ max-width: 1200px; margin: 0 auto; }}
        .section-header {{ text-align: center; margin-bottom: 4rem; }}
        .section-tag {{
            display: inline-block; padding: 0.5rem 1rem; background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 50px;
            color: #667eea; font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem;
            text-transform: uppercase; letter-spacing: 1px;
        }}
        .section-title-new {{
            font-family: 'Manrope', sans-serif; font-size: clamp(2.5rem, 5vw, 3.5rem);
            font-weight: 800; margin-bottom: 1rem;
        }}

        /* About */
        .about-new {{ background: linear-gradient(180deg, #0a0a0a 0%, #0f0f0f 100%); }}
        .about-content-new {{ display: grid; grid-template-columns: 1.5fr 1fr; gap: 3rem; align-items: start; }}
        .about-text p {{ font-size: 1.1rem; color: #b0b0b0; margin-bottom: 1.5rem; text-align: justify; }}
        .edu-card {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px; padding: 2rem; backdrop-filter: blur(10px);
        }}
        .edu-card h3 {{ font-family: 'Manrope', sans-serif; font-size: 1.5rem; margin-bottom: 1.5rem; }}
        .edu-details {{ display: flex; flex-direction: column; gap: 0.75rem; }}
        .edu-degree {{ font-size: 1.1rem; font-weight: 600; }}
        .edu-field {{ font-size: 1rem; color: #667eea; font-weight: 500; }}
        .edu-cgpa {{ color: #10b981; font-weight: 600; margin-top: 0.5rem; }}

        /* Skills */
        .skills-new {{ background: #0a0a0a; }}
        .skills-grid-new {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; }}
        .skills-list {{ display: flex; flex-direction: column; gap: 1.5rem; }}
        .skill-item-new {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px; padding: 1.5rem; transition: all 0.3s ease;
        }}
        .skill-item-new:hover {{
            background: rgba(255, 255, 255, 0.05); border-color: rgba(102, 126, 234, 0.3);
            transform: translateX(5px);
        }}
        .skill-name-icon {{ display: flex; align-items: center; gap: 0.75rem; }}
        .skill-icon-new {{ font-size: 1.5rem; color: #667eea; display: flex; }}

        /* Experience */
        .experience-new {{ background: linear-gradient(180deg, #0f0f0f 0%, #0a0a0a 100%); }}
        .experience-timeline {{
            display: flex; flex-direction: column; gap: 2rem; position: relative; padding-left: 2rem;
        }}
        .experience-timeline::before {{
            content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 2px;
            background: linear-gradient(180deg, #667eea, #764ba2);
        }}
        .exp-card {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px; padding: 2rem; position: relative; transition: all 0.3s ease;
        }}
        .exp-card:hover {{
            background: rgba(255, 255, 255, 0.05); border-color: rgba(102, 126, 234, 0.3);
            transform: translateX(10px);
        }}
        .exp-marker {{
            position: absolute; left: -2.65rem; top: 2rem; width: 18px; height: 18px;
            border-radius: 50%; border: 3px solid #0a0a0a;
        }}
        .exp-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 1.5rem; }}
        .exp-role {{ font-family: 'Manrope', sans-serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .exp-company {{ font-size: 1.1rem; color: #667eea; font-weight: 500; }}
        .exp-duration {{
            font-size: 0.9rem; color: #b0b0b0; padding: 0.5rem 1rem;
            background: rgba(255, 255, 255, 0.05); border-radius: 50px; white-space: nowrap;
        }}
        .exp-points {{ padding-left: 0; list-style: none; }}
        .exp-points li {{ position: relative; padding-left: 1.5rem; margin-bottom: 0.75rem; color: #b0b0b0; }}
        .exp-points li::before {{ content: '▹'; position: absolute; left: 0; color: #667eea; font-weight: bold; }}

        /* Projects */
        .projects-new {{ background: #0a0a0a; }}
        .projects-grid-new {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; }}
        .project-card-new {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px; overflow: hidden; transition: all 0.3s ease; display: flex; flex-direction: column;
        }}
        .project-card-new:hover {{
            transform: translateY(-10px); border-color: rgba(102, 126, 234, 0.3);
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
        }}
        .project-header {{ padding: 2rem; color: white; }}
        .project-title-new {{ font-family: 'Manrope', sans-serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .project-link-icon {{ color: white; font-size: 1.2rem; opacity: 0.8; transition: opacity 0.2s; }}
        .project-link-icon:hover {{ opacity: 1; }}
        .project-body {{ padding: 2rem; flex: 1; display: flex; flex-direction: column; }}
        .project-desc {{ color: #b0b0b0; margin-bottom: 1.5rem; flex: 1; }}
        .project-tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .project-tag {{
            padding: 0.4rem 0.8rem; background: rgba(102, 126, 234, 0.2);
            border: 1px solid rgba(102, 126, 234, 0.3); border-radius: 50px;
            font-size: 0.8rem; color: #667eea; font-weight: 500;
        }}

        /* Certifications */
        .certifications-new {{ background: linear-gradient(180deg, #0f0f0f 0%, #0a0a0a 100%); }}
        .cert-grid-new {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
        .cert-card-new {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px; padding: 1.5rem; text-decoration: none; display: block;
            transition: all 0.3s ease;
        }}
        .cert-card-new:hover {{
            background: rgba(255, 255, 255, 0.05); border-color: rgba(102, 126, 234, 0.3);
            transform: translateY(-5px);
        }}
        .cert-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem; }}
        .cert-name {{ font-size: 1.1rem; font-weight: 600; color: #ffffff; flex: 1; }}
        .cert-icon {{ color: #667eea; font-size: 1.2rem; opacity: 0.7; transition: all 0.3s ease; }}
        .cert-card-new:hover .cert-icon {{ opacity: 1; transform: translate(3px, -3px); }}
        .cert-issuer {{ font-size: 0.95rem; color: #667eea; font-weight: 500; margin-bottom: 0.5rem; }}
        .cert-date {{ font-size: 0.85rem; color: #b0b0b0; }}

        /* Contact & Footer */
        .contact-new {{ background: #0a0a0a; padding: 6rem 5% 4rem; text-align: center; }}
        .contact-text {{ font-size: 1.2rem; color: #b0b0b0; margin-bottom: 3rem; max-width: 700px; margin-left: auto; margin-right: auto; }}
        .social-links-new {{ display: flex; justify-content: center; gap: 2rem; }}
        .social-btn {{
            display: flex; align-items: center; gap: 0.75rem; padding: 1rem 2rem;
            border-radius: 12px; text-decoration: none; font-size: 1rem; font-weight: 600;
            transition: all 0.3s ease; border: 2px solid;
        }}
        .linkedin-btn {{ background: rgba(10, 102, 194, 0.2); border-color: #0a66c2; color: #0a66c2; }}
        .linkedin-btn:hover {{ background: #0a66c2; color: white; transform: translateY(-3px); }}
        .github-btn {{ background: rgba(255, 255, 255, 0.1); border-color: #ffffff; color: #ffffff; }}
        .github-btn:hover {{ background: #ffffff; color: #0a0a0a; transform: translateY(-3px); }}
        .footer-new {{
            padding: 2rem 5%; text-align: center; border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #b0b0b0; font-size: 0.9rem;
        }}

        @media (max-width: 1024px) {{
            .hero-container {{ grid-template-columns: 1fr; text-align: center; }}
            .hero-content-new {{ order: 2; }}
            .hero-image-new {{ order: 1; max-width: 350px; margin: 0 auto; }}
            .hero-buttons, .hero-stats {{ justify-content: center; }}
            .about-content-new, .skills-grid-new {{ grid-template-columns: 1fr; }}
            .nav-links {{ display: none; }}
        }}
        @media (max-width: 768px) {{
            .section-new {{ padding: 4rem 5%; }}
            .projects-grid-new, .cert-grid-new {{ grid-template-columns: 1fr; }}
            .exp-header {{ flex-direction: column; gap: 0.5rem; }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">Portfolio</div>
    </nav>

    <section id="home" class="hero-new">
        <div class="hero-bg-pattern"></div>
        <div class="hero-container">
            <div class="hero-content-new">
                <h1 class="hero-title-new">
                    <span class="hero-name-main">{html.escape(first_name)}</span>
                    <span class="hero-name-accent">{html.escape(last_name)}</span>
                </h1>
                
                <div class="hero-stats">
                    <div class="stat-item">
                        <div class="stat-number">{hero_stat_number}</div>
                        <div class="stat-label">{hero_stat_label}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{years_exp}+</div>
                        <div class="stat-label">Internships</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">{cert_count}+</div>
                        <div class="stat-label">Certifications</div>
                    </div>
                </div>

                <div class="hero-buttons">
                    <a href="{resume_link}" target="_blank" class="btn-primary">
                        <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 512 512" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M216 0h80c13.3 0 24 10.7 24 24v168h87.7c17.8 0 26.7 21.5 14.1 34.1L269.7 378.3c-7.5 7.5-19.8 7.5-27.3 0L90.1 226.1c-12.6-12.6-3.7-34.1 14.1-34.1H192V24c0-13.3 10.7-24 24-24zm296 376v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h146.7l49 49c20.1 20.1 52.5 20.1 72.6 0l49-49H488c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z"></path></svg> 
                        Download Resume
                    </a>
                    <a href="#contact" class="btn-secondary">Get In Touch</a>
                </div>
            </div>
            <div class="hero-image-new">
                <div class="profile-frame">
                    <img src="{profile_image}" alt="{html.escape(hero_name)}" class="profile-img-new">
                </div>
            </div>
        </div>
    </section>

    <section id="about" class="section-new about-new">
        <div class="container-new">
            <div class="section-header">
                <span class="section-tag">Get to know me</span>
                <h2 class="section-title-new">About Me</h2>
            </div>
            <div class="about-content-new">
                <div class="about-text">
                    <p>{html.escape(hero_summary)}</p>
                    <p>{html.escape(about_me)}</p>
                </div>
                <div class="about-education">
                    {edu_html}
                </div>
            </div>
        </div>
    </section>

    <section id="skills" class="section-new skills-new">
        <div class="container-new">
            <div class="section-header">
                <span class="section-tag">What I'm good at</span>
                <h2 class="section-title-new">Skills & Expertise</h2>
            </div>
            <div class="skills-grid-new">
                <div class="skills-category-new">
                    <h3 style="margin-bottom:2rem;">Technical Skills</h3>
                    <div class="skills-list">
                        {tech_skills_html}
                    </div>
                </div>
                <div class="skills-category-new">
                    <h3 style="margin-bottom:2rem;">Soft Skills</h3>
                    <div class="skills-list">
                        {soft_skills_html}
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="experience" class="section-new experience-new">
        <div class="container-new">
            <div class="section-header">
                <span class="section-tag">My Journey</span>
                <h2 class="section-title-new">Work Experience</h2>
            </div>
            <div class="experience-timeline">
                {exp_html}
            </div>
        </div>
    </section>

    <section id="projects" class="section-new projects-new">
        <div class="container-new">
            <div class="section-header">
                <span class="section-tag">What I've built</span>
                <h2 class="section-title-new">Featured Projects</h2>
            </div>
            <div class="projects-grid-new">
                {projects_html}
            </div>
        </div>
    </section>

    <section id="certifications" class="section-new certifications-new">
        <div class="container-new">
            <div class="section-header">
                <span class="section-tag">Achievements</span>
                <h2 class="section-title-new">Certifications</h2>
            </div>
            <div class="cert-grid-new">
                {cert_html}
            </div>
        </div>
    </section>

    <section id="contact" class="section-new contact-new">
        <div class="container-new">
            <div class="section-header">
                <span class="section-tag">Get in touch</span>
                <h2 class="section-title-new">Let's Connect</h2>
            </div>
            <p class="contact-text">I'm always interested in hearing about new opportunities and projects. Feel free to reach out!</p>
            <div class="social-links-new">
                <a href="{contact_linkedin}" target="_blank" class="social-btn linkedin-btn">
                    <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 448 512" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M416 32H31.9C14.3 32 0 46.5 0 64.3v383.4C0 465.5 14.3 480 31.9 480H416c17.6 0 32-14.5 32-32.3V64.3c0-17.8-14.4-32.3-32-32.3zM135.4 416H69V202.2h66.5V416zm-33.2-243c-21.3 0-38.5-17.3-38.5-38.5S80.9 96 102.2 96c21.2 0 38.5 17.3 38.5 38.5 0 21.3-17.2 38.5-38.5 38.5zm282.1 243h-66.4V312c0-24.8-.5-56.7-34.5-56.7-34.6 0-39.9 27-39.9 54.9V416h-66.4V202.2h63.7v29.2h.9c8.9-16.8 30.6-34.5 62.9-34.5 67.2 0 79.7 44.3 79.7 101.9V416z"></path></svg>
                    LinkedIn
                </a>
                <a href="{contact_github}" target="_blank" class="social-btn github-btn">
                    <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 496 512" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"></path></svg>
                    GitHub
                </a>
                
            </div>
        </div>
    </section>

    <footer class="footer-new">
        <p>© 2025 {html.escape(hero_name)}. All rights reserved.</p>
    </footer>

    <script>
        // Navbar Blur Effect on Scroll
        window.addEventListener('scroll', () => {{
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {{
                navbar.classList.add('scrolled');
            }} else {{
                navbar.classList.remove('scrolled');
            }}
        }});
    </script>
</body>
</html>
    """