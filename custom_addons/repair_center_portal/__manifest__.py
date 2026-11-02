{
    "name": "BASSAM JARI Customer Portal",
    "summary": "Let customers securely track their repair orders",
    "version": "19.0.2.0.0",
    "category": "Services",
    "author": "Engineer BASSAM JARI",
    "license": "LGPL-3",
    "depends": ["repair_center_core", "portal", "website"],
    "data": [
        "security/repair_portal_security.xml",
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
        "views/website_branding_templates.xml",
    ],
    "demo": [
        "demo/repair_portal_demo.xml",
    ],
    "installable": True,
}
