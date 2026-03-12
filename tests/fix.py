with open('index.html', 'r') as f:
    content = f.read()

import re

search_ref = "  const isNavigatingRef = useRef(false);"
replace_ref = "  const isNavigatingRef = useRef(false);\n  const navigationTimeoutRef = useRef(null);"

if search_ref in content:
    content = content.replace(search_ref, replace_ref)

search_nav = """        // Suspend IntersectionObserver during programmatic smooth scroll (approx 500ms-700ms)
        isNavigatingRef.current = true;
        setTimeout(() => { isNavigatingRef.current = false; }, 800);"""

replace_nav = """        // Suspend IntersectionObserver during programmatic smooth scroll (approx 500ms-700ms)
        isNavigatingRef.current = true;
        if (navigationTimeoutRef.current) clearTimeout(navigationTimeoutRef.current);
        navigationTimeoutRef.current = setTimeout(() => { isNavigatingRef.current = false; }, 800);"""

if search_nav in content:
    content = content.replace(search_nav, replace_nav)

with open('index.html', 'w') as f:
    f.write(content)

print("Replaced successfully in index.html")
