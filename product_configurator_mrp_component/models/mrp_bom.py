# Copyright (C) 2022-Today Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MRPBoM(models.Model):
    _inherit = "mrp.bom"

    bom_line_config_ids = fields.One2many(
        "mrp.bom.line.config", "bom_id", string="Configurable Components"
    )
    available_config_components = fields.Many2many(
        "product.template",
        compute="_compute_available_config_components",
        store=True,
    )

    @api.depends("bom_line_config_ids", "product_tmpl_id")
    def _compute_available_config_components(self):
        """Compute list of products available for configurable components"""
        if self.config_ok and not self.product_id:
            for bom in self:
                bom.available_config_components = False
                products = self.env["product.template"].search(
                    [
                        ("config_ok", "=", True),
                        ("id", "!=", bom.product_tmpl_id.id),
                        (
                            "id",
                            "!=",
                            bom.bom_line_config_ids.mapped("product_tmpl_id").ids,
                        ),
                    ]
                )
                for prod in products:
                    prod_vals = prod.mapped("attribute_line_ids.value_ids")
                    bom_tmpl_values = bom.product_tmpl_id.mapped(
                        "attribute_line_ids.value_ids"
                    )
                    if all(att_val in bom_tmpl_values for att_val in prod_vals):
                        bom.available_config_components = [(4, prod.id)]
