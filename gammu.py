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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import threading
import time
import psycopg2

from datetime import datetime

import openerp

from openerp import models, fields, api ,  SUPERUSER_ID, netsvc
from openerp import tools

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _
from openerp.modules import load_information_from_description_file


import re 
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__) 

def str2tuple(s):
    return eval('tuple(%s)' % (s or ''))

class gammu(models.Model):
    _name = 'gammu'

    _description = "gammu data"
    _auto = False



    def ex_init(self, cr):

        cr.execute("""
            -- 
            --
            -- Function declaration for updating timestamps
            --
            CREATE OR REPLACE FUNCTION update_timestamp() RETURNS trigger AS $update_timestamp$
              BEGIN
                NEW."UpdatedInDB" := LOCALTIMESTAMP(0);
                RETURN NEW;
              END;
            $update_timestamp$ LANGUAGE plpgsql;

            -- --------------------------------------------------------

            --
            -- Sequence declarations for tables' primary keys
            --

              --CREATE SEQUENCE inbox_ID_seq;

            --CREATE SEQUENCE outbox_ID_seq;

            --CREATE SEQUENCE outbox_multipart_ID_seq;

            --CREATE SEQUENCE pbk_groups_ID_seq;

            --CREATE SEQUENCE sentitems_ID_seq;

            -- --------------------------------------------------------

            --
            -- Index declarations for tables' primary keys
            --

            --CREATE UNIQUE INDEX inbox_pkey ON inbox USING btree ("ID");

            --CREATE UNIQUE INDEX outbox_pkey ON outbox USING btree ("ID");

            --CREATE UNIQUE INDEX outbox_multipart_pkey ON outbox_multipart USING btree ("ID");

            --CREATE UNIQUE INDEX pbk_groups_pkey ON pbk_groups USING btree ("ID");

            --CREATE UNIQUE INDEX sentitems_pkey ON sentitems USING btree ("ID");

            -- --------------------------------------------------------
            -- 
            -- Table structure for table "daemons"
            -- 

            CREATE TABLE daemons (
              "Start" text NOT NULL,
              "Info" text NOT NULL
            );

            -- 
            -- Dumping data for table "daemons"
            -- 


            -- --------------------------------------------------------

            -- 
            -- Table structure for table "gammu"
            -- 

            CREATE TABLE gammu (
              "Version" smallint NOT NULL DEFAULT '0'ER
            );

            -- 
            -- Dumping data for table "gammu"
            -- 

            INSERT INTO gammu ("Version") VALUES (15);

            -- --------------------------------------------------------

            -- 
            -- Table structure for table "inbox"
            -- 

            CREATE TABLE inbox (
              "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "ReceivingDateTime" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "Text" text NOT NULL,
              "SenderNumber" varchar(20) NOT NULL DEFAULT '',
              "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
              "UDH" text NOT NULL,
              "SMSCNumber" varchar(20) NOT NULL DEFAULT '',
              "Class" integer NOT NULL DEFAULT '-1',
              "TextDecoded" text NOT NULL DEFAULT '',
              "ID" serial PRIMARY KEY,
              "RecipientID" text NOT NULL,
              "Processed" boolean NOT NULL DEFAULT 'false',
              CHECK ("Coding" IN 
              ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression')) 
            );

            -- 
            -- Dumping data for table "inbox"
            -- 

            -- --------------------------------------------------------

            --
            -- Create trigger for table "inbox"
            --

            CREATE TRIGGER update_timestamp BEFORE UPDATE ON inbox FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

            -- --------------------------------------------------------

            -- 
            -- Table structure for table "outbox"
            -- 

            CREATE TABLE outbox (
              "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "InsertIntoDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "SendingDateTime" timestamp NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "SendBefore" time NOT NULL DEFAULT '23:59:59',
              "SendAfter" time NOT NULL DEFAULT '00:00:00',
              "Text" text,
              "DestinationNumber" varchar(20) NOT NULL DEFAULT '',
              "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
              "UDH" text,
              "Class" integer DEFAULT '-1',
              "TextDecoded" text NOT NULL DEFAULT '',
              "ID" serial PRIMARY KEY,
              "MultiPart" boolean NOT NULL DEFAULT 'false',
              "RelativeValidity" integer DEFAULT '-1',
              "SenderID" varchar(255),
              "SendingTimeOut" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "DeliveryReport" varchar(10) DEFAULT 'default',
              "CreatorID" text NOT NULL,
              "Retries" integer DEFAULT '0',
              CHECK ("Coding" IN 
              ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression')),
              CHECK ("DeliveryReport" IN ('default','yes','no'))
            );

            CREATE INDEX outbox_date ON outbox("SendingDateTime", "SendingTimeOut");
            CREATE INDEX outbox_sender ON outbox("SenderID");

            -- 
            -- Dumping data for table "outbox"
            -- 

            -- --------------------------------------------------------

            --
            -- Create trigger for table "outbox"
            --

            CREATE TRIGGER update_timestamp BEFORE UPDATE ON outbox FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

            -- --------------------------------------------------------

            -- 
            -- Table structure for table "outbox_multipart"
            -- 

            CREATE TABLE outbox_multipart (
              "Text" text,
              "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
              "UDH" text,
              "Class" integer DEFAULT '-1',
              "TextDecoded" text DEFAULT NULL,
              "ID" serial,
              "SequencePosition" integer NOT NULL DEFAULT '1',
              PRIMARY KEY ("ID", "SequencePosition"),
              CHECK ("Coding" IN 
              ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression'))
            );

            -- 
            -- Dumping data for table "outbox_multipart"
            -- 


            -- --------------------------------------------------------

            -- 
            -- Table structure for table "pbk"
            -- 

            CREATE TABLE pbk (
              "ID" serial PRIMARY KEY,
              "GroupID" integer NOT NULL DEFAULT '-1',
              "Name" text NOT NULL,
              "Number" text NOT NULL
            );

            -- 
            -- Dumping data for table "pbk"
            -- 


            -- --------------------------------------------------------

            -- 
            -- Table structure for table "pbk_groups"
            -- 

            CREATE TABLE pbk_groups (
              "Name" text NOT NULL,
              "ID" serial PRIMARY KEY
            );

            -- 
            -- Dumping data for table "pbk_groups"
            -- 


            -- --------------------------------------------------------

            -- 
            -- Table structure for table "phones"
            -- 

            CREATE TABLE phones (
              "ID" text NOT NULL,
              "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "InsertIntoDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "TimeOut" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "Send" boolean NOT NULL DEFAULT 'no',
              "Receive" boolean NOT NULL DEFAULT 'no',
              "IMEI" varchar(35) PRIMARY KEY NOT NULL,
              "NetCode" varchar(10) DEFAULT 'ERROR',
              "NetName" varchar(35) DEFAULT 'ERROR',
              "Client" text NOT NULL,
              "Battery" integer NOT NULL DEFAULT -1,
              "Signal" integer NOT NULL DEFAULT -1,
              "Sent" integer NOT NULL DEFAULT 0,
              "Received" integer NOT NULL DEFAULT 0
            );

            -- 
            -- Dumping data for table "phones"
            -- 

            -- --------------------------------------------------------

            --
            -- Create trigger for table "phones"
            --

            CREATE TRIGGER update_timestamp BEFORE UPDATE ON phones FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

            -- --------------------------------------------------------

            -- 
            -- Table structure for table "sentitems"
            -- 

            CREATE TABLE sentitems (
              "UpdatedInDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "InsertIntoDB" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "SendingDateTime" timestamp(0) WITHOUT time zone NOT NULL DEFAULT LOCALTIMESTAMP(0),
              "DeliveryDateTime" timestamp(0) WITHOUT time zone NULL,
              "Text" text NOT NULL,
              "DestinationNumber" varchar(20) NOT NULL DEFAULT '',
              "Coding" varchar(255) NOT NULL DEFAULT 'Default_No_Compression',
              "UDH" text NOT NULL,
              "SMSCNumber" varchar(20) NOT NULL DEFAULT '',
              "Class" integer NOT NULL DEFAULT '-1',
              "TextDecoded" text NOT NULL DEFAULT '',
              "ID" serial,
              "SenderID" varchar(255) NOT NULL,
              "SequencePosition" integer NOT NULL DEFAULT '1',
              "Status" varchar(255) NOT NULL DEFAULT 'SendingOK',
              "StatusError" integer NOT NULL DEFAULT '-1',
              "TPMR" integer NOT NULL DEFAULT '-1',
              "RelativeValidity" integer NOT NULL DEFAULT '-1',
              "CreatorID" text NOT NULL,
              CHECK ("Status" IN 
              ('SendingOK','SendingOKNoReport','SendingError','DeliveryOK','DeliveryFailed','DeliveryPending',
              'DeliveryUnknown','Error')),
              CHECK ("Coding" IN 
              ('Default_No_Compression','Unicode_No_Compression','8bit','Default_Compression','Unicode_Compression')),
              PRIMARY KEY ("ID", "SequencePosition")
            );

            CREATE INDEX sentitems_date ON sentitems("DeliveryDateTime");
            CREATE INDEX sentitems_tpmr ON sentitems("TPMR");
            CREATE INDEX sentitems_dest ON sentitems("DestinationNumber");
            CREATE INDEX sentitems_sender ON sentitems("SenderID");

            -- 
            -- Dumping data for table "sentitems"
            -- 

            -- --------------------------------------------------------

            --
            -- Create trigger for table "sentitems"
            --

            CREATE TRIGGER update_timestamp BEFORE UPDATE ON sentitems FOR EACH ROW EXECUTE PROCEDURE update_timestamp();
        """)





class gammu_outbox(models.Model):
    _name = 'gammu.outbox'

    _description = "gammu outbox"
    _auto = False

    name=fields.Char(string="Destination Number")
    text=fields.Text(string="msg")
    sending_datetime=fields.Datetime(string="Sending Date Time",default=fields.Datetime.now())
    send_before=fields.Char(string="Send Before",default="23:59:59")
    send_after=fields.Char(string="Send After",default="00:00:00")
    creatorid=fields.Text(string="Creator ID",default="odoo")
    multipart=fields.Boolean(string="MultiPart")
    senderid=fields.Char(string="senderID",default="")
    sending_time_out=fields.Datetime(string="Sending time out",default=fields.Datetime.now())
    retries=fields.Integer(string="Retries",default=0)

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'gammu_outbox')

        cr.execute("""create or replace view  gammu_outbox as (
            select "ID" as id, "InsertIntoDB" as create_date ,"UpdatedInDB" as write_date , "DestinationNumber" as name,
            "TextDecoded" as text , "SendingDateTime" as sending_datetime,"SendBefore" as send_before ,"SendAfter" as send_after,
            "CreatorID" as creatorid,"MultiPart" as multipart,"SenderID" as senderid,"SendingTimeOut" as sending_time_out,
            "Retries" as retries
            from outbox

        )""")

    @api.multi
    def unlink(self):
      for sms in self :
        self._cr.execute("""delete from  outbox where "ID" = %f """%(sms.id))


    @api.model
    def send_test_now(self, phone,text):

      return self.create({
              'name':phone,
              'text':text,
              'sending_datetime':fields.Datetime.now(),
              'send_before':"23:59:59",
              'send_after':"00:00:00",
              'creatorid':'odoo',
              'multipart':False,
              'sending_time_out':fields.Datetime.now(),
              })




    @api.model
    def create(self,vals):

        if len(vals['text'])> 160:
          vals['multipart']=True
        
        text=[vals['text'][ind:ind+160] for ind in range(0, len(vals['text']), 160)]
        first_part=text.pop(0)

        self._cr.execute("""insert into outbox (
            "InsertIntoDB","UpdatedInDB","DestinationNumber","TextDecoded","SendingDateTime",
            "SendBefore","SendAfter","CreatorID","MultiPart","SenderID","SendingTimeOut","Retries"
            ) values (now(),now(),%s,%s,%s,%s,%s,%s,%s,'',%s,0) RETURNING "ID" """, (vals['name'],vals['text'],
            vals['sending_datetime'],vals['send_before'],vals['send_after'],vals['creatorid'],vals['multipart'],
            vals['sending_time_out']
            ))


        id_new, = self._cr.fetchone()
        secuence=2
        for multipart_text in text :
              self._cr.execute("""insert into outbox_multipart ("ID","SequencePosition","TextDecoded") 
                                  values
                                  ("""+str(id_new)  + ","+str(secuence) + ",%s)" , (multipart_text,))
              secuence = secuence +1


        recs = self.browse(id_new)

        
        return recs
    """
    @api.one
    def resend_errors(self,msg,days=4):
      errors=self.env['gammu.sentitems'].search([('status','=','SendingError'),
                                                 ('sending_datetime','>',datetime.datetime.now() -relativedelta(day=days)) ),
                                                 ('text','ilike',msg)

                                                ])
    """


class gammu_sentitems(models.Model):
    _name = 'gammu.sentitems'

    _description = "gammu sentitems"
    _auto = False


    name=fields.Char(string="Destination Number")
    text=fields.Text(string="msg")
    sending_datetime=fields.Datetime(string="Sending Date Time")
    delivery_datetime=fields.Datetime(string="delivery Date Time")
    creatorid=fields.Text(string="Creator ID")
    senderid=fields.Char(string="senderid")
    status=fields.Char(string="Status")

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'gammu_sentitems')

        cr.execute("""create or replace view  gammu_sentitems as (
            select "ID" as id, "InsertIntoDB" as create_date ,"UpdatedInDB" as write_date , "DestinationNumber" as name,
            "TextDecoded" as text , "SendingDateTime" as sending_datetime,"DeliveryDateTime" as delivery_datetime, 
            "CreatorID" as creatorid,"SenderID" as senderid,"Status" as status
            from sentitems s1 where "SequencePosition" =1

        )""")   


class gammu_inbox(models.Model):
    _name = 'gammu.inbox'

    _description = "gammu inbox"
    _auto = False


    name=fields.Char(string="Sender Number")
    text=fields.Text(string="msg")
    processed=fields.Boolean(string="Processed")
    create_date=fields.Datetime()
    write_date=fields.Datetime()


    @api.model
    def create(self,vals):
      #TODO add raise
      return False 
                                                                                                                                                                                                                                                                                                                                                                                                                                    
    @api.model
    def write(self,ids,vals):
      for inbox_id in ids : 
        if  vals.get('processed',None) !=None:
          self._cr.execute("""update inbox set "Processed"=%s where "ID"= %d """ % (vals['processed'],inbox_id))
      return ids 

    @api.model
    def process_inbox(self):
      _logger.info('Inicio Proceso')
      unprocess_items=self.search_read([('processed','=',False)],['name','text'])
      expected_responses_obj=self.env['gammu.expected.responses']
      llamadaPerdida=re.compile('Recibiste.*llamada')

      for unprocess in unprocess_items:
        # Recorro Items sin procesar

        response_ids=expected_responses_obj.search_read([('processed','=',False),('name','=',unprocess['name'])],['model', 'function', 'args'])
        # Existe respuesta y no es una  llamada perdida
        if response_ids and not llamadaPerdida.search(unprocess['text']):
          for response_id in response_ids:
            #Recorro las respuestas
            response = self._callback_response(response_id['model'], response_id['function'], response_id['args'],unprocess['text'])
            if response != False :
              self.write([unprocess['id']],{'processed':True})
        else :
          say_ok=  re.compile('.*[ok|OK|Ok|oK].*')
          if not say_ok.search(unprocess['text']) : 
            #TODO orphan funtion
            msg={
                'name':unprocess['name'],
                'text':'Este es un servicio automatizado. Por cualquier consulta comuniquese al 0810 666 8964. BLANCOAMOR',
                'sending_datetime': datetime.now(),
                'send_before':'23:59:59',
                'send_after':'00:00:00',
                'creatorid':'odoo',
                'multipart':False,
                'sending_time_out':datetime.now(),
            }
            self.env['gammu.outbox'].create(msg)
            self.write([unprocess['id']],{'processed':True})
            
    @api.model
    def _callback_response(self,model_name, method_name, args,msg):
      _logger.info('Ejecuto el callback')
      args = str2tuple(args)
      openerp.modules.registry.RegistryManager.check_registry_signaling(self._cr.dbname)
      registry = openerp.registry(self._cr.dbname)
      if model_name in registry:
          model = registry[model_name]
          if hasattr(model, method_name):
            
            response = getattr(model, method_name)(self._cr, self._uid, msg,*args)
            openerp.modules.registry.RegistryManager.signal_caches_change(self._cr.dbname)
            return response
          else:
            msg = "Method `%s.%s` does not exist." % (model_name, method_name)
            _logger.warning(msg)


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'gammu_inbox')

        cr.execute("""create or replace view  gammu_inbox as (
            select "ID" as id, "ReceivingDateTime" as create_date ,"UpdatedInDB" as write_date , "SenderNumber" as name,
            "TextDecoded" as text , "Processed" as processed
            from inbox

        )""") 





class gammu_expected_responses(models.Model):
    _name = 'gammu.expected.responses'

    _description = "gammu responses"

    name=fields.Char(string="Sender Number")
    text=fields.Text(string="msg")
    timeout=fields.Datetime(string="Time outbox")
    inbox_id=fields.Many2one( comodel_name='gammu.inbox',string="Inbox" )    
    model=fields.Char(string="Object", help="Model name on which the method to be called is located, e.g. 'res.partner'.")
    function=fields.Char(string="Method", help="Name of the method to be called when this job is processed.")
    args=fields.Text(string="Arguments", help="Arguments to be passed to the method, e.g. (uid,).")

    creatorid=fields.Text(string="Creator ID")
    processed=fields.Boolean(string="Processed")

    def create(self,cr,uid,vals,context=None):
      # Antes de crear un nuevo expeted response Marco como procesadas las anteriores para evitar solapamiento de respues
      # porque suelen disponer de el mismo set.
      # La respuesta valida es siempre la ultima
      # TODO: agregar un campo de set o tipo de respuesta esperada para filtrar y poder dejar el expeted viejo si procesar
      # en caso de ser una respuesta que no selape con la actual

      args=[('name','=',vals['name']),('processed','=',False)]
      olds_id=self.search(cr,uid,args)
      if olds_id:
        self.write(cr,uid,olds_id,{'processed':True})

      return super(gammu_expected_responses,self).create(cr,uid,vals,context)

    def dummie(self,cr,uid,msn):
      _logger.info('dummie')
      return  True

    def clean_phone(self,number):
      exp="([54|\+54|\+549])([15|15])()"

    def _callback_response(self,model_name, method_name, args,msg):
      args = str2tuple(args)
      openerp.modules.registry.RegistryManager.check_registry_signaling(self._cr.dbname)
      registry = openerp.registry(self._cr.dbname)
      if model_name in registry:
          model = registry[model_name]
          if hasattr(model, method_name):
            
            response = getattr(model, method_name)(self._cr, self._uid, msg,*args)
            openerp.modules.registry.RegistryManager.signal_caches_change(self._cr.dbname)
            return response
          else:
            msg = "Method `%s.%s` does not exist." % (model_name, method_name)
            _logger.warning(msg)

