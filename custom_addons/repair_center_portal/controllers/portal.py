from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class RepairCustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "repair_count" in counters:
            repair_orders = request.env["repair.center.order"]
            values["repair_count"] = (
                repair_orders.search_count([])
                if repair_orders.has_access("read")
                else 0
            )
        return values

    @http.route(
        ["/my/repairs", "/my/repairs/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_repairs(self, page=1, sortby="date", **kwargs):
        values = self._prepare_portal_layout_values()
        repair_orders = request.env["repair.center.order"]

        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "date_received desc"},
            "name": {"label": _("Reference"), "order": "name desc"},
            "state": {"label": _("Status"), "order": "state, date_received desc"},
        }
        if sortby not in searchbar_sortings:
            sortby = "date"

        repair_count = repair_orders.search_count([])
        pager = portal_pager(
            url="/my/repairs",
            url_args={"sortby": sortby},
            total=repair_count,
            page=page,
            step=self._items_per_page,
        )
        repairs = repair_orders.search(
            [],
            order=searchbar_sortings[sortby]["order"],
            limit=self._items_per_page,
            offset=pager["offset"],
        )
        request.session["my_repairs_history"] = repairs.ids[:100]

        values.update(
            {
                "repairs": repairs,
                "page_name": "repair",
                "default_url": "/my/repairs",
                "pager": pager,
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("repair_center_portal.portal_my_repairs", values)

    @http.route(
        "/my/repairs/<int:repair_id>",
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_repair(self, repair_id, **kwargs):
        try:
            repair_sudo = self._document_check_access(
                "repair.center.order", repair_id
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        return request.render(
            "repair_center_portal.portal_my_repair",
            {
                "repair": repair_sudo,
                "page_name": "repair",
            },
        )
