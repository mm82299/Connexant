# -*- coding: utf-8 -*-
# from odoo import http


# class IcsRas(http.Controller):
#     @http.route('/ics_ras/ics_ras/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ics_ras/ics_ras/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ics_ras.listing', {
#             'root': '/ics_ras/ics_ras',
#             'objects': http.request.env['ics_ras.ics_ras'].search([]),
#         })

#     @http.route('/ics_ras/ics_ras/objects/<model("ics_ras.ics_ras"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ics_ras.object', {
#             'object': obj
#         })
