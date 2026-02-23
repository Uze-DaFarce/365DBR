# Mt. Sinai LLC

**Faith-Centered Business Services & Ethical AI**

Mt. Sinai LLC is dedicated to providing professional business services that honor God. We specialize in ethical AI implementation, bookkeeping, web design, and application solutions, serving Christians nationwide with integrity and technical excellence.

## Mission

"Each task, even the most ordinary, is sacred when done for God. We are called to work with excellence, integrity, and devotion, knowing that Christ Himself is whom we serve as we serve our clients."

## Services

We offer a range of services tailored to small and medium businesses:

*   **Bookkeeping Services**: Professional financial management by a QuickBooks ProAdvisor (Gold Tier).
*   **Web Design**: Custom, responsive websites that reflect your brand values.
*   **AI Workflows**: Ethical AI implementation to enhance human dignity and automate business processes.
*   **Application Implementations**: Expert setup and customization of DocuSign, Salesforce, and other business tools.

## Ministry Projects

Beyond our business services, we develop resources to support the Christian community.

*   **[365DBR](https://mt-sin.ai/365DBR/)**: A "Read the Bible in a Year" plan that takes less than 15 minutes a day. This project has its own repository and is hosted as a sub-site.
*   **[He Is Risen! Game](/HeIsRisen/)**: An interactive Christian Easter Egg Hunt game featuring P.A.L. We are currently adding the repository for this project.
*   **[DayByDayKids](https://daybydaykids.com)**: Christian education resources for children. Currently hosted on Canva, we plan to recreate and migrate this site to our self-hosted GoDaddy environment in the near future.

## Technical Overview

This website is a static site built with HTML, CSS, and vanilla JavaScript.

*   **Hosting**: GoDaddy
*   **Build Process**: None required. The site is served directly from the source files.
*   **Structure**:
    *   `index.html`: Main landing page.
    *   `css/`: Stylesheets (including `404.css`).
    *   `js/`: JavaScript logic (`script.js`).
    *   `pics/`: Images and assets.

## Production Architecture & 365DBR

⚠️ **CRITICAL: The directory structure here is a simplified view of production.**

In the live environment (`html_public` on GoDaddy), **365DBR** (our most critical application) exists as a fully populated subdirectory at `mt-sin.ai/365DBR/`.

*   **DO NOT** assume `365DBR` is empty or a typo because the folder is sparse in this repo.
*   **DO NOT** modify the root `.htaccess` without verifying `365DBR/.htaccess` overrides any strict policies (like `Permissions-Policy` or CSP).
*   Changes to the root configuration propagate to sub-sites (`365DBR`, `HeIsRisen`, `m`) via Apache inheritance. Always ensure sub-sites are explicitly protected from breaking changes.

## Contact

*   **Email**: [truth@mt-sin.ai](mailto:truth@mt-sin.ai)
*   **Phone**: (206) 718-9780
*   **Location**: Conrad, MT
