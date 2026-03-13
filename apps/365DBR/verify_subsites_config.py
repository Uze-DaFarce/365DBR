import re
import os
import sys

def check_permissions_policy_override(root_htaccess, subsite_htaccess, subsite_name):
    """
    Checks if a sub-site overrides the Permissions-Policy of the root.
    If the root policy is stricter (contains more restrictions) than the sub-site,
    the sub-site MUST have an override.
    """
    try:
        with open(root_htaccess, 'r') as f:
            root_content = f.read()

        # If sub-site file doesn't exist, it's a critical failure for 365DBR
        if not os.path.exists(subsite_htaccess):
            if subsite_name == "365DBR":
                 print(f"❌ CRITICAL: {subsite_name} is missing its .htaccess file! This is a production-critical app.")
                 return False
            else:
                 print(f"⚠️ Warning: {subsite_name} is missing its .htaccess file.")
                 return True # Non-critical for now, but good to note

        with open(subsite_htaccess, 'r') as f:
            sub_content = f.read()

        # Extract root policy
        root_match = re.search(r'Header set Permissions-Policy "(.*?)"', root_content)
        root_policy = root_match.group(1) if root_match else ""

        # Extract sub-site policy
        sub_match = re.search(r'Header set Permissions-Policy "(.*?)"', sub_content)
        sub_policy = sub_match.group(1) if sub_match else None

        # Logic: If root has a policy, sub-site MUST have an override to be safe from inheritance
        # especially if we are hardening root.
        if root_policy and sub_policy is None:
            print(f"❌ {subsite_name} INHERITS root Permissions-Policy!")
            print(f"   The root policy is: {root_policy}")
            print(f"   {subsite_name} likely needs features (sensors, midi, webauthn) that root disables.")
            print(f"   ACTION: Add 'Header set Permissions-Policy ...' to {subsite_htaccess} to protect it.")
            return False

        if sub_policy:
            print(f"✅ {subsite_name} correctly overrides Permissions-Policy.")

        return True

    except Exception as e:
        print(f"Error checking {subsite_name}: {e}")
        return False

def verify_all_subsites():
    root_htaccess = ".htaccess"
    subsites = [
        ("365DBR", "365DBR/.htaccess"),
        ("HeIsRisen", "HeIsRisen/.htaccess"),
        ("m", "m/.htaccess")
    ]

    all_passed = True
    print("🛡️ Sentinel: Verifying Sub-Site Protection against Root Policy Changes...\n")

    for name, path in subsites:
        if not check_permissions_policy_override(root_htaccess, path, name):
            all_passed = False

    if all_passed:
        print("\n✅ All sub-sites are protected from root .htaccess inheritance.")
        sys.exit(0)
    else:
        print("\n❌ VERIFICATION FAILED: One or more sub-sites are at risk of breaking.")
        print("   Do NOT merge changes to root .htaccess until sub-sites are protected.")
        sys.exit(1)

if __name__ == "__main__":
    verify_all_subsites()
