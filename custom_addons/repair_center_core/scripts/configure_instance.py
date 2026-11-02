company = env.ref("base.main_company")
syp = env.ref("base.SYP")
usd = env.ref("base.USD")
syp.write({"active": True, "symbol": "ل.س", "position": "after"})
usd.write({"active": True, "symbol": "$", "position": "before"})
company.write(
    {
        "name": "BASSAM JARI Service Hub",
        "currency_id": syp.id,
        "repair_brand_name": "BASSAM JARI Service Hub",
        "repair_owner_name": "Engineer BASSAM JARI",
        "repair_tagline": "Smart service. Trusted results.",
        "repair_support_email": "support@bassamjari.local",
    }
)

syria = env.ref("base.sy")
company_partner = company.partner_id
company_partner.write(
    {
        "name": "BASSAM JARI Service Hub",
        "street": False,
        "street2": False,
        "city": False,
        "zip": False,
        "state_id": False,
        "country_id": syria.id,
    }
)
company.write(
    {
        "repair_support_phone": company_partner.phone,
        "repair_support_email": company_partner.email or "admin@example.com",
    }
)

admin_user = env["res.users"].browse(2).exists()
if admin_user:
    admin_user.partner_id.write(
        {
            "name": "Engineer BASSAM JARI",
            "parent_id": company_partner.id,
            "phone": company_partner.phone,
            "street": False,
            "street2": False,
            "city": False,
            "zip": False,
            "state_id": False,
            "country_id": syria.id,
        }
    )

websites = env["website"].search([])
websites.write({"name": "BASSAM JARI Service Hub", "company_id": company.id})

main_branch = env.ref("repair_center_core.branch_main")
orders_without_branch = env["repair.center.order"].search(
    [("company_id", "=", company.id), ("branch_id", "=", False)]
)
orders_without_branch.write({"branch_id": main_branch.id})
env["repair.center.order"].search([("currency_id", "=", False)]).write(
    {"currency_id": syp.id}
)
env["repair.center.service"].search([("currency_id", "=", False)]).write(
    {"currency_id": syp.id}
)

arabic = env["res.lang"].with_context(active_test=False).search(
    [("code", "=", "ar_SY")],
    limit=1,
)
if arabic and not arabic.active:
    env["base.language.install"].create(
        {
            "lang_ids": [(6, 0, arabic.ids)],
            "overwrite": True,
        }
    ).lang_install()
else:
    modules = env["ir.module.module"].search(
        [("name", "in", ["repair_center_core", "repair_center_portal"])]
    )
    modules._update_translations("ar_SY", overwrite=True)

env.cr.commit()
print("BASSAM JARI Service Hub configured; Arabic (Syria) is active.")
