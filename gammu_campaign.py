# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along wittemh this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import threading
import time
import psycopg2
import re


from datetime import datetime , timedelta


from openerp import models, fields, api ,  SUPERUSER_ID, netsvc
from openerp import tools

from urllib import urlencode, quote as quote

import logging
_logger = logging.getLogger(__name__) 



#from https://github.com/SythilBlade/sythil-odoo-test/blob/8.0/entity_sms/esms_templates.py

try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': quote,
        'urlencode': urlencode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': reduce,
        'map': map,
        'round': round,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")





class gammu_campaign(models.Model):
    _name = 'gammu.campaign'

    _description = "gammu campaign"

    name=fields.Char(string="Name")
    template_text=fields.Text(string="template")
    state=fields.Selection(selection=[('draft', 'Borrador'),('sending', 'Enviando'),('send', 'Enviado')],default='draft')
    sms=fields.One2many(comodel_name='gammu.campaign.sms', inverse_name='gammu_campaign_id')
    opportunity_user_id =  fields.Many2one(comodel_name='res.users',string="Crear una oportunidad a")




    @api.one
    def send(self):
        self.state='sending'
        item_minute = 10
        item_count = 0

        for sms in self.sms :
            if sms.name:
                item_count = item_count + 1
                
                delay = datetime.now() + timedelta(minutes=int(item_count/item_minute)) 

                outbox={'name':sms.name,
                        'text':sms.text,
                        'sending_datetime':delay,'creatorid':'odoo','sending_time_out':delay,
                        'send_before':'23:00:00','send_after':'00:00:00','multipart':False}
                outbox_id=self.env['gammu.outbox'].sudo().create(outbox)

                if self.opportunity_user_id:
                    response=self.env['gammu.expected.responses'].sudo().create({
                        'name':sms.name,
                        'timeout':datetime.now(),
                        'model':'gammu.campaign',
                        'function':'response',
                        'args':'([%d,"%s",%d])' % (self.opportunity_user_id.id,sms.name,sms.partner_id.id) })

        self.state='send'

    @api.one
    def response(self,user_id,phone,partner_id):
        lead=self.env['crm.lead'].create({
            'name':'Respuesta la la campaña'   ,
            'user_id':user_id,
            'partner_id':partner_id,
            'phone':phone,
            'type':'opportunity',
            'description' : self[0],
            })


            #return True
        return False


    @api.one
    def presupuestos(self):

        self.env.cr.execute("""select distinct partner_id
                       from sale_order where date_order > '2016-09-01'  and partner_id not in (
                            select distinct partner_id from account_invoice  where date_due > '2016-09-01' 
        )""")

        partner_list = self.env.cr.fetchall()
        _logger.info("partner_list %r" , partner_list)
        if partner_list : 
            for partner_id in partner_list :
                    sms = self.env['gammu.campaign.sms'].create({'gammu_campaign_id': self.id,'partner_id':partner_id[0]})
                    sms._partner_get_phone()

        

class gammu_campaign_sms(models.Model):
    _name = 'gammu.campaign.sms'

    _description = "gammu campaign sms"
    
    @api.depends('gammu_campaign_id')
    @api.one
    def _compute_text (self):
        self.text = self.render_template(self.gammu_campaign_id.template_text   , 'res.partner', self.partner_id.id)


    gammu_campaign_id =  fields.Many2one(comodel_name='gammu.campaign')
    name=fields.Char(string="To")    
    partner_id=fields.Many2one( comodel_name='res.partner',string="partner" )    
    text=fields.Text(string="msg" , compute=_compute_text)


    def render_template(self, template, model, res_id):
        """Render the given template text, replace mako expressions ``${expr}``
           with the result of evalua_compute_textting these expressions with
           an evaluation context containing:
                * ``user``: browse_record of the current user
                * ``object``: browse_record of the document record this mail is
                              related to
                * ``context``: the context passed to the mail composition wizard
           :param str template: the template text to render
           :param str model: model name of the document record this mail is related to.
           :param int res_id: id of document records those mails are related to.
        """
        
        # try to load the template
        #try:
        template = mako_template_env.from_string(tools.ustr(template))
        #except Exception:
        #    _logger.error("Failed to load template %r", template)
        #    return False

        # prepare template variables
        user = self.env.user
        record = self.env[model].browse(res_id)
        
        variables = {
            'user': user
        }
        
        
        
        variables['object'] = record
        try:
            render_result = template.render(variables)
        except Exception:
            _logger.error("Failed to render template %r using values %r" % (template, variables))
            render_result = u""
        if render_result == u"False":
            render_result = u""

        return render_result


            



    @api.onchange('partner_id')
    def _partner_get_phone(self):

        if self.partner_id.mobile:
            phone=self.clean_mobile(self.partner_id.mobile)
            if phone : 
                self.name =  phone
                return 

        if self.partner_id.phone :
            phone=self.clean_phone(self.partner_id.phone)
            if phone : 
                self.name = phone 
                return 

        self.name = self.partner_id.mobile

    def clean_mobile(self,phone):
            
        mob=re.compile('(\+)*(54)*(9)*(0)*(299|291|11|294)*(15)*([4|5|6])([0-9][0-9][0-9][0-9][0-9][0-9])')
        mobiles=mob.findall(re.sub("\D", "",phone))

        for mobile in mobiles:
            if  mobile[6] != '' and len(mobile[7])==6:
                caracteristica = "299" if  mobile[4] == '' else  mobile[4]

                return '+549' + str(caracteristica)  + str(mobile[6])+ str(mobile[7])
        return False

    def clean_phone(self,phone):
        
        mob=re.compile('(\+)*(54)*(9)*(0)*(299|291|11|294)*(15)*([4|5|6])([0-9][0-9][0-9][0-9][0-9][0-9])')
        mobiles=mob.findall(re.sub("\D", "",phone))

        for mobile in mobiles:
            if mobile[5] != '' and mobile[6] != '' and len(mobile[7])==6:
                caracteristica = "299" if  mobile[4] == '' else  mobile[4]

                return '+549' + str(caracteristica)  + str(mobile[6])+ str(mobile[7])
        return False


            
class campain_from_dni(models.TransientModel):
    _name = 'campain.from.dni'
    phone_list=fields.Text(string="phones",required=True)
    gammu_campaign_id =  fields.Many2one(comodel_name='gammu.campaign',required=True)

    @api.multi
    def by_phone(self):
        phones=[]
        phones= filter(None,[x.strip() for x in self.phone_list.split('\n')])
        if phones : 

            partner_ids = self.env['res.partner'].search(['|',('phone' ,'in',phones),('mobile' ,'in',phones)])
            for partner_id in partner_ids:
                sms = self.env['gammu.campaign.sms'].create({'gammu_campaign_id': self.gammu_campaign_id.id,'partner_id':partner_id.id})
                sms._partner_get_phone()
        
    @api.multi
    def by_dni(self):
        phones=[]

        phones= filter(None,[re.sub("[^0-9]", "",x) for x in self.phone_list.split('\n')])
        if phones : 
            partner_ids = self.env['res.partner'].search([('document_number' ,'in',phones)])
            for partner_id in partner_ids:
                sms = self.env['gammu.campaign.sms'].create({'gammu_campaign_id': self.gammu_campaign_id.id,'partner_id':partner_id.id})
                sms._partner_get_phone()
        


