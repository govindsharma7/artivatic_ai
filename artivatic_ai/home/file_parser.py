from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings

from apps.common.data_uploader import (
    upload_product_master, upload_store_master,
    upload_festivals, upload_warehouse, upload_warehouse_inventory,
    upload_primary_sale, upload_current_store_inventory,
    upload_in_transit_inventory, upload_daily_sale,
    upload_store_lead_time, upload_attribute_ratios,
    upload_range_plan, upload_festive_uplift,
    upload_optional_availability,
    upload_temporal_ratio, upload_first_allocation,
    upload_availability_decay_rate,
    upload_temporary_first_allocation
)
from apps.common.boto_config import upload_to_s3
from apps.client.models import Document
from apps.users.models import User

import pandas as pd
from pandas.errors import EmptyDataError
import os


DATA_UPLOADER_FUNCTIONS = {
    1: upload_store_master,
}


class ParseData(object):
    """
    All data manipulation should happen here.
    """
    CHUNK_SIZE = 10000
    VALID_FILE_EXTENSIONS = ['csv']

    def __init__(self, file_name, file_type, func_id,
                 document, date_time=None):

        self.file_name = self.validate_file_extension(file_name)
        self.file_type = file_name.split('.')[-1].strip()
        self.func_name = DATA_UPLOADER_FUNCTIONS[func_id]
        self.document = document
        self.date_time = date_time

    def parse(self):
        if self.file_type == 'csv':
            self.parse_csv()
        else:
            self.parse_excel()

    def validate_file_extension(self, file_name):
        file_ext = file_name.split('/')[-1].split('.')[-1].strip()
        if not file_ext in self.VALID_FILE_EXTENSIONS:
            raise ValidationError("Invalid file extension (file_ext)",
                                  params={'file_ext': file_ext})
        return file_name

    def parse_csv(self):
        """
        CHUNK IS A DATAFRAME
        """
        for chunk in pd.read_csv(self.file_name, chunksize=self.CHUNK_SIZE):
            columns = self.strip_headers(chunk)
            self.rename_column_headers_for_db(chunk)
            try:
                if self.func_name.__name__ == 'upload_temporary_first_allocation':
                    error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user, self.job_id))
                elif self.func_name.__name__ == 'upload_temporal_ratio':
                    error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user, self.temporal_ratio_type))
                elif self.func_name.__name__ == 'upload_current_store_inventory':
                    error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user, self.date_time,
                        self.channel))
                elif self.channel and self.date_time:
                    error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user, self.date_time, self.channel))
                elif self.channel or self.func_name.__name__ in ['upload_primary_sale', 'upload_daily_sale']:
                    error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user, self.channel))
                elif self.date_time:
                    error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user, self.date_time))
                else:
                    if self.func_name == upload_product_master:
                        error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user, self.new_data))
                    else:
                        error_rows.extend(self.func_name(chunk, self.tenant, self.client_attribute, self.user))
                success_row_count += len(chunk)
            except Exception as e:
                # TODO(ANUBHAV): IMPLEMENT LOGGING
                try:
                    self.document.status = Document.FAILED
                    self.document.errors = {'parser_error': 'Error encountered in parser',
                                            'error_details': e.args[0]}
                    self.document.save()
                except AttributeError:
                    pass
                return False

        if not self.func_name.__name__ in ['upload_attribute_ratios',
                                           'upload_festive_uplift',
                                           'upload_temporal_ratio',
                                           'upload_optional_availability',
                                           'upload_availability_decay_rate']:
            upload_to_s3(self.file_name)
            os.remove(self.file_name)

        try:
            default_from_email = settings.EMAIL_HOST_USER
            error_row_count = len(error_rows)
            success_row_count -= error_row_count
            if error_rows:
                error_df = pd.DataFrame(error_rows)
                error_file_name = self.file_name.split('/')[-1].split('.')[0] + '_error.csv'
                error_df.to_csv(error_file_name)
                destination_path = settings.ERROR_FILE_PATH + error_file_name
                upload_to_s3(error_file_name, destination_path)
                os.remove(error_file_name)
                self.document.error_file_path = destination_path
                # error_rows = json.dumps(error_rows)
                # self.document.errors = error_rows
                self.document.success_row_count = success_row_count
                self.document.error_row_count = error_row_count
                self.document.status = Document.COMPLETED_WITH_ERRORS
            else:
                self.document.success_row_count = success_row_count
                self.document.status = Document.COMPLETED
            self.document.save()
            user = User.objects.get(id=self.user)
            plain_text = get_template('email_alerts/upload_success.txt')
            html_text = get_template('email_alerts/upload_success.html')
            context = {'username': user.first_name,
                       'file_name': self.file_name}
            text_content = plain_text.render(context)
            html_content = html_text.render(context)
            subject = '{} File Upload Processed'.format(self.file_name)
            msg = EmailMultiAlternatives(
                subject, text_content,
                default_from_email, [user.email],
                reply_to=[settings.CLIENT_SUPPORT])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except:
            pass
        return True

    def parse_excel(self):
        """
        convert excel to csv then parse data.
        """

        # TODO (ANUBHAV): MODIFY THE FOLLOWING LOGIC AS PER:
        # https://stackoverflow.com/questions/20105118/convert-xlsx-to-csv-correctly-using-python
        try:
            data_excel = pd.read_excel(self.file_name)
            file_name = self.file_name.split('.')[0] + '.csv'
            data_excel.to_csv(file_name, encoding='utf-8', index=False)
            self.file_name = file_name
            self.parse_csv()
            return True
        except Exception as e:
            # TODO(ANUBHAV): IMPLEMENT LOGGING
            return False
        finally:
            os.remove(self.file_name)

    def strip_headers(self, chunk):
        columns = chunk.columns.tolist()
        for column in columns:
            chunk.rename(columns={'{}'.format(column): '{}'.format(column.strip())}, inplace=True)
        return chunk.columns.tolist()
