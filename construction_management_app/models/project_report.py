from odoo import api, models, fields


class ProjectReport(models.AbstractModel):
    _name = 'report.construction_management_app.project_report_id'

    def get_details(self, data):
        res = {}
        material_list = []
        labour_list = []
        if data.project_task_ids:
            for task in data.project_task_ids:
                for m_cons in task.consumed_material_ids:
                    product_exists = next(filter(lambda d: d.get('id') == m_cons.product_id.id, material_list), None)
                    if not product_exists:
                        material = {
                            'id': m_cons.product_id.id,
                            'product': m_cons.product_id.name,
                            'qty': m_cons.product_uom_qty,
                            'rate': m_cons.price,
                            'total': m_cons.total_price
                        }
                        material_list.append(material)
                    else:
                        product_exists['qty'] = product_exists['qty'] + m_cons.product_uom_qty
                        product_exists['total'] = product_exists['total'] + m_cons.total_price
                for l_cons in task.timesheet_ids:
                    labour_exists = next(filter(lambda d: d.get('id') == l_cons.employee_id.id and d.get('task_id') == task.id, labour_list), None)
                    if not labour_exists:
                        labour = {
                            'id': l_cons.employee_id.id,
                            'task_id': task.id,
                            'task': task.name,
                            'name': l_cons.employee_id.name,
                            'time': l_cons.unit_amount,
                            'price': l_cons.price_unit,
                            'total': l_cons.total_price
                        }
                        labour_list.append(labour)
                    else:
                        labour_exists['time'] = labour_exists['time'] + l_cons.unit_amount
                        labour_exists['total'] = labour_exists['total'] + l_cons.total_price

        res['materials'] = material_list
        res['labours'] = labour_list
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        record = self.env['project.project'].browse(docids)
        return {
            'doc_ids': record.ids,
            'docs': record,
            'doc_model': self.env['project.project'],
            'get_details': self.get_details(record)
        }
